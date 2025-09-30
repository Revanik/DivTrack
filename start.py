"""
DivTrack Startup Script
A simple script to start the DivTrack dividend tracking application locally
"""

import os
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open the default browser to the DivTrack application"""
    webbrowser.open('http://127.0.0.1:5000/')

def main():
    print("=" * 60)
    print("DivTrack - Dividend Income Tracker")
    print("=" * 60)
    print()
    print("Starting DivTrack application...")
    print()
    print("📋 Quick Setup:")
    print("1. Set your initial investment amount in Settings")
    print("2. Upload your Robinhood CSV file")
    print("3. Monitor your dividend progress!")
    print()
    print("🌐 The application will open in your browser automatically")
    print("   If it doesn't, go to: http://localhost:5000")
    print()
    print("⏹️  Press Ctrl+C to stop the application")
    print("=" * 60)
    print()
    
    # Open browser after a short delay
    Timer(2.0, open_browser).start()
    
    # Import and run the Flask app
    try:
        from app import app, db
        # Initialize database if it doesn't exist
        with app.app_context():
            db.create_all()
            print("✅ Database ready")
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nDivTrack stopped. Thanks for using DivTrack!")
    except Exception as e:
        print(f"\n❌ Error starting DivTrack: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
