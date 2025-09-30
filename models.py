from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to user's dividend data
    dividend_data = db.relationship('DividendData', backref='user', lazy=True, uselist=False)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class DividendData(db.Model):
    """User's dividend tracking data"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    initial_investment = db.Column(db.Float, default=0.0)
    total_dividends = db.Column(db.Float, default=0.0)
    principal_recovered = db.Column(db.Boolean, default=False)
    recovery_date = db.Column(db.DateTime)
    post_recovery_gains = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to transactions
    transactions = db.relationship('DividendTransaction', backref='dividend_data', lazy=True, cascade='all, delete-orphan')
    monthly_totals = db.relationship('MonthlyTotal', backref='dividend_data', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'initial_investment': self.initial_investment,
            'total_dividends': self.total_dividends,
            'principal_recovered': self.principal_recovered,
            'recovery_date': self.recovery_date.strftime('%Y-%m-%d') if self.recovery_date else None,
            'post_recovery_gains': self.post_recovery_gains,
            'transactions': [t.to_dict() for t in self.transactions],
            'monthly_totals': {mt.month: mt.amount for mt in self.monthly_totals}
        }
    
    def __repr__(self):
        return f'<DividendData for User {self.user_id}>'

class DividendTransaction(db.Model):
    """Individual dividend transactions"""
    id = db.Column(db.Integer, primary_key=True)
    dividend_data_id = db.Column(db.Integer, db.ForeignKey('dividend_data.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description,
            'amount': self.amount,
            'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<DividendTransaction {self.description} - ${self.amount}>'

class MonthlyTotal(db.Model):
    """Monthly dividend totals for charting"""
    id = db.Column(db.Integer, primary_key=True)
    dividend_data_id = db.Column(db.Integer, db.ForeignKey('dividend_data.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False)  # Format: YYYY-MM
    amount = db.Column(db.Float, default=0.0)
    
    # Ensure unique month per user
    __table_args__ = (db.UniqueConstraint('dividend_data_id', 'month', name='unique_month_per_user'),)
    
    def __repr__(self):
        return f'<MonthlyTotal {self.month}: ${self.amount}>'
