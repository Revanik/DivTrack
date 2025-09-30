#!/usr/bin/env python3
"""
Production startup script for DivTrack
Used by Render and other cloud platforms
"""

import os
from app import app, db

if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        db.create_all()
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(host='0.0.0.0', port=port, debug=False)
