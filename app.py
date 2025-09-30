import os
import json
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, DividendData, DividendTransaction, MonthlyTotal
from forms import LoginForm, RegistrationForm, SettingsForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dividend_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_or_create_user_data():
    """Get or create dividend data for current user"""
    if not current_user.is_authenticated:
        return None
    
    data = DividendData.query.filter_by(user_id=current_user.id).first()
    if not data:
        data = DividendData(user_id=current_user.id)
        db.session.add(data)
        db.session.commit()
    return data

def parse_robinhood_csv(file_path):
    """Parse Robinhood CSV and extract dividend transactions"""
    try:
        # Read CSV and drop any extra columns beyond the first 9
        df = pd.read_csv(file_path, on_bad_lines='skip')
        
        # If we have more than 9 columns, keep only the first 9
        if len(df.columns) > 9:
            df = df.iloc[:, :9]
        
        # Updated column names to match actual Robinhood CSV format
        possible_date_cols = ['Date', 'date', 'Date/Time', 'date/time', 'Activity Date', 'Process Date', 'Settle Date']
        possible_desc_cols = ['Description', 'description', 'Details', 'details']
        possible_amount_cols = ['Amount', 'amount', 'Net Amount', 'net amount']
        possible_instrument_cols = ['Instrument', 'instrument', 'Symbol', 'symbol', 'Security', 'security']
        
        # Find the actual column names
        date_col = next((col for col in possible_date_cols if col in df.columns), None)
        desc_col = next((col for col in possible_desc_cols if col in df.columns), None)
        amount_col = next((col for col in possible_amount_cols if col in df.columns), None)
        instrument_col = next((col for col in possible_instrument_cols if col in df.columns), None)
        
        if not all([date_col, desc_col, amount_col]):
            available_cols = list(df.columns)
            raise ValueError(f"Could not identify required columns. Available columns: {available_cols}. "
                           f"Looking for date column (one of {possible_date_cols}), "
                           f"description column (one of {possible_desc_cols}), "
                           f"and amount column (one of {possible_amount_cols})")
        
        dividend_transactions = []
        
        for index, row in df.iterrows():
            try:
                description = str(row[desc_col]).lower()
                amount = row[amount_col]
                
                # Look for dividend-related keywords
                dividend_keywords = ['dividend', 'div', 'distribution']
                if any(keyword in description for keyword in dividend_keywords):
                    # Convert amount to float, handling any currency formatting
                    try:
                        if isinstance(amount, str):
                            # Remove currency symbols and commas
                            amount = amount.replace('$', '').replace(',', '').strip()
                            amount = float(amount)
                        else:
                            amount = float(amount)
                        
                        # Only include positive dividend amounts
                        if amount > 0:
                            # Create a clean description with symbol and amount
                            symbol = str(row[instrument_col]) if instrument_col and instrument_col in row else "Unknown"
                            clean_description = f"{symbol} Dividend - ${amount:.2f}"
                            
                            dividend_transactions.append({
                                'date': str(row[date_col]),
                                'description': clean_description,
                                'amount': amount,
                                'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                    except (ValueError, TypeError) as e:
                        # Skip this transaction if amount can't be parsed
                        continue
                        
            except Exception as e:
                # Skip problematic rows
                continue
        
        return dividend_transactions
    
    except Exception as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")

def update_dividend_totals(data, new_transactions):
    """Update dividend totals and check for principal recovery"""
    total_before = data.total_dividends
    
    for transaction_data in new_transactions:
        # Parse date with multiple formats
        date_str = transaction_data['date']
        date_obj = None
        
        date_formats = [
            '%m/%d/%Y',    # 8/1/2025
            '%m-%d-%Y',    # 08-01-2025
            '%Y-%m-%d',    # 2025-08-01
            '%m/%d/%y',    # 8/1/25
            '%m-%d-%y'     # 08-01-25
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt).date()
                break
            except ValueError:
                continue
        
        if date_obj is None:
            continue
        
        # Create transaction record
        transaction = DividendTransaction(
            dividend_data_id=data.id,
            date=date_obj,
            description=transaction_data['description'],
            amount=transaction_data['amount']
        )
        db.session.add(transaction)
        
        # Update totals
        data.total_dividends += transaction_data['amount']
        
        # Track monthly totals
        month_key = date_obj.strftime('%Y-%m')
        monthly_total = MonthlyTotal.query.filter_by(
            dividend_data_id=data.id, 
            month=month_key
        ).first()
        
        if monthly_total:
            monthly_total.amount += transaction_data['amount']
        else:
            monthly_total = MonthlyTotal(
                dividend_data_id=data.id,
                month=month_key,
                amount=transaction_data['amount']
            )
            db.session.add(monthly_total)
    
    # Check for principal recovery
    if not data.principal_recovered and data.total_dividends >= data.initial_investment:
        data.principal_recovered = True
        data.recovery_date = datetime.utcnow()
        data.post_recovery_gains = data.total_dividends - data.initial_investment
    elif data.principal_recovered:
        data.post_recovery_gains = data.total_dividends - data.initial_investment
    
    data.updated_at = datetime.utcnow()
    db.session.commit()
    
    return data.total_dividends - total_before

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Main application routes
@app.route('/')
@login_required
def dashboard():
    """Main dashboard showing dividend tracking information"""
    data = get_or_create_user_data()
    
    # Calculate progress percentage
    progress_percentage = 0
    if data.initial_investment > 0:
        progress_percentage = min(100, (data.total_dividends / data.initial_investment) * 100)
    
    # Prepare monthly data for charts
    monthly_data = []
    for monthly_total in data.monthly_totals:
        monthly_data.append({
            'month': monthly_total.month,
            'amount': monthly_total.amount
        })
    monthly_data.sort(key=lambda x: x['month'])
    
    return render_template('dashboard.html', 
                         data=data, 
                         progress_percentage=progress_percentage,
                         monthly_data=monthly_data)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """Handle CSV file upload and processing"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            try:
                # Parse the CSV file
                new_transactions = parse_robinhood_csv(file_path)
                
                if not new_transactions:
                    flash('No dividend transactions found in the uploaded file', 'warning')
                    return redirect(url_for('dashboard'))
                
                # Load existing data and update
                data = get_or_create_user_data()
                new_total = update_dividend_totals(data, new_transactions)
                
                flash(f'Successfully processed {len(new_transactions)} dividend transactions. '
                      f'Total new dividends: ${new_total:.2f}', 'success')
                
                # Clean up uploaded file
                os.remove(file_path)
                
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                if os.path.exists(file_path):
                    os.remove(file_path)
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a CSV file.', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Settings page for initial investment amount"""
    data = get_or_create_user_data()
    form = SettingsForm()
    
    if form.validate_on_submit():
        data.initial_investment = form.initial_investment.data
        
        # Recalculate principal recovery status
        if data.total_dividends >= form.initial_investment.data:
            data.principal_recovered = True
            if not data.recovery_date:
                data.recovery_date = datetime.utcnow()
            data.post_recovery_gains = data.total_dividends - form.initial_investment.data
        else:
            data.principal_recovered = False
            data.recovery_date = None
            data.post_recovery_gains = 0
        
        data.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Initial investment amount updated successfully', 'success')
        return redirect(url_for('dashboard'))
    
    # Pre-populate form with current value
    form.initial_investment.data = data.initial_investment
    return render_template('settings.html', form=form, data=data)

@app.route('/api/monthly-data')
@login_required
def api_monthly_data():
    """API endpoint for monthly dividend data (for charts)"""
    data = get_or_create_user_data()
    monthly_totals = {mt.month: mt.amount for mt in data.monthly_totals}
    return jsonify(monthly_totals)

@app.route('/reset', methods=['POST'])
@login_required
def reset_data():
    """Reset all dividend data (use with caution)"""
    if request.form.get('confirm') == 'yes':
        data = get_or_create_user_data()
        
        # Delete all related data
        DividendTransaction.query.filter_by(dividend_data_id=data.id).delete()
        MonthlyTotal.query.filter_by(dividend_data_id=data.id).delete()
        
        # Reset main data
        data.initial_investment = 0
        data.total_dividends = 0
        data.principal_recovered = False
        data.recovery_date = None
        data.post_recovery_gains = 0
        data.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('All data has been reset.', 'success')
    else:
        flash('Reset cancelled', 'info')
    
    return redirect(url_for('dashboard'))

# Initialize database
def create_tables():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)