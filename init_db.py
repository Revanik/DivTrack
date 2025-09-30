#!/usr/bin/env python3
"""
Database initialization script for DivTrack
Run this once to create the database tables
"""

from app import app, db

def init_database():
    """Initialize the database with all tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")
        print("Tables created:")
        print("   - users")
        print("   - dividend_data") 
        print("   - dividend_transactions")
        print("   - monthly_totals")
        print("\nYou can now run the application with: python app.py")

if __name__ == '__main__':
    init_database()
