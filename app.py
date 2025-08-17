import os
import json
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
DATA_FILE = 'dividend_data.json'

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    """Load existing dividend data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'initial_investment': 0,
        'total_dividends': 0,
        'principal_recovered': False,
        'recovery_date': None,
        'post_recovery_gains': 0,
        'transactions': [],
        'monthly_totals': {}
    }

def save_data(data):
    """Save dividend data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def parse_robinhood_csv(file_path):
    """Parse Robinhood CSV and extract dividend transactions"""
    try:
        # Simple approach: read CSV and drop any extra columns beyond the first 9
        # This handles the 10th column issue you mentioned
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
            # Try to provide helpful error message
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
    total_before = data['total_dividends']
    
    for transaction in new_transactions:
        data['total_dividends'] += transaction['amount']
        data['transactions'].append(transaction)
        
        # Track monthly totals - handle multiple date formats
        date_str = transaction['date']
        date_obj = None
        
        # Try different date formats
        date_formats = [
            '%m/%d/%Y',    # 8/1/2025
            '%m-%d-%Y',    # 08-01-2025
            '%Y-%m-%d',    # 2025-08-01
            '%m/%d/%y',    # 8/1/25
            '%m-%d-%y'     # 08-01-25
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        
        if date_obj is None:
            # If no format works, skip this transaction
            continue
            
        month_key = date_obj.strftime('%Y-%m')
        if month_key not in data['monthly_totals']:
            data['monthly_totals'][month_key] = 0
        data['monthly_totals'][month_key] += transaction['amount']
    
    # Check for principal recovery
    if not data['principal_recovered'] and data['total_dividends'] >= data['initial_investment']:
        data['principal_recovered'] = True
        data['recovery_date'] = datetime.now().strftime('%Y-%m-%d')
        data['post_recovery_gains'] = data['total_dividends'] - data['initial_investment']
    elif data['principal_recovered']:
        data['post_recovery_gains'] = data['total_dividends'] - data['initial_investment']
    
    return data['total_dividends'] - total_before

@app.route('/')
def dashboard():
    """Main dashboard showing dividend tracking information"""
    data = load_data()
    
    # Calculate progress percentage
    progress_percentage = 0
    if data['initial_investment'] > 0:
        progress_percentage = min(100, (data['total_dividends'] / data['initial_investment']) * 100)
    
    # Prepare monthly data for charts
    monthly_data = []
    for month, amount in sorted(data['monthly_totals'].items()):
        monthly_data.append({
            'month': month,
            'amount': amount
        })
    
    return render_template('dashboard.html', 
                         data=data, 
                         progress_percentage=progress_percentage,
                         monthly_data=monthly_data)

@app.route('/upload', methods=['GET', 'POST'])
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
                data = load_data()
                new_total = update_dividend_totals(data, new_transactions)
                save_data(data)
                
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
def settings():
    """Settings page for initial investment amount"""
    data = load_data()
    
    if request.method == 'POST':
        try:
            initial_investment = float(request.form['initial_investment'])
            if initial_investment < 0:
                flash('Initial investment amount must be positive', 'error')
                return redirect(request.url)
            
            data['initial_investment'] = initial_investment
            
            # Recalculate principal recovery status
            if data['total_dividends'] >= initial_investment:
                data['principal_recovered'] = True
                if not data['recovery_date']:
                    data['recovery_date'] = datetime.now().strftime('%Y-%m-%d')
                data['post_recovery_gains'] = data['total_dividends'] - initial_investment
            else:
                data['principal_recovered'] = False
                data['recovery_date'] = None
                data['post_recovery_gains'] = 0
            
            save_data(data)
            flash('Initial investment amount updated successfully', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError:
            flash('Please enter a valid number for initial investment', 'error')
            return redirect(request.url)
    
    return render_template('settings.html', data=data)

@app.route('/api/monthly-data')
def api_monthly_data():
    """API endpoint for monthly dividend data (for charts)"""
    data = load_data()
    return jsonify(data['monthly_totals'])

@app.route('/reset', methods=['POST'])
def reset_data():
    """Reset all dividend data (use with caution)"""
    if request.form.get('confirm') == 'yes':
        # Backup existing data
        if os.path.exists(DATA_FILE):
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.rename(DATA_FILE, backup_name)
        
        # Create fresh data structure
        fresh_data = {
            'initial_investment': 0,
            'total_dividends': 0,
            'principal_recovered': False,
            'recovery_date': None,
            'post_recovery_gains': 0,
            'transactions': [],
            'monthly_totals': {}
        }
        save_data(fresh_data)
        flash('All data has been reset. A backup was created.', 'success')
    else:
        flash('Reset cancelled', 'info')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
