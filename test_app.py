"""
Simple test script for DivTrack functionality
"""

import os
import json
import pandas as pd
from datetime import datetime

# Import functions from app.py
from app import load_data, save_data, parse_robinhood_csv, update_dividend_totals

def test_data_loading():
    """Test data loading and saving"""
    print("Testing data loading...")
    
    # Test initial data structure
    data = load_data()
    assert 'initial_investment' in data
    assert 'total_dividends' in data
    assert 'principal_recovered' in data
    print("✓ Data structure is correct")
    
    # Test data saving
    test_data = {
        'initial_investment': 10000.0,
        'total_dividends': 5000.0,
        'principal_recovered': False,
        'recovery_date': None,
        'post_recovery_gains': 0.0,
        'transactions': [],
        'monthly_totals': {}
    }
    save_data(test_data)
    
    # Reload and verify
    loaded_data = load_data()
    assert loaded_data['initial_investment'] == 10000.0
    print("✓ Data saving and loading works")

def test_csv_parsing():
    """Test CSV parsing functionality"""
    print("\nTesting CSV parsing...")
    
    # Test with sample CSV
    sample_csv = """Date,Description,Amount
2024-01-15,MSTY Dividend,45.67
2024-01-20,JEPQ Dividend,23.45
2024-02-15,Buy AAPL,-100.00
2024-02-20,MSTY Dividend,46.12"""
    
    # Write sample CSV to file
    with open('test_sample.csv', 'w') as f:
        f.write(sample_csv)
    
    # Parse the CSV
    transactions = parse_robinhood_csv('test_sample.csv')
    
    # Verify results
    assert len(transactions) == 3  # Should find 3 dividend transactions
    assert transactions[0]['amount'] == 45.67
    assert transactions[1]['amount'] == 23.45
    assert transactions[2]['amount'] == 46.12
    
    print(f"✓ Found {len(transactions)} dividend transactions")
    
    # Clean up
    os.remove('test_sample.csv')

def test_dividend_totals():
    """Test dividend totals calculation"""
    print("\nTesting dividend totals...")
    
    # Load test data
    data = load_data()
    data['initial_investment'] = 10000.0
    
    # Create test transactions
    test_transactions = [
        {
            'date': '2024-01-15',
            'description': 'MSTY Dividend',
            'amount': 100.0,
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'date': '2024-02-15',
            'description': 'JEPQ Dividend',
            'amount': 200.0,
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    # Update totals
    new_total = update_dividend_totals(data, test_transactions)
    
    # Verify results
    assert data['total_dividends'] == 300.0
    assert new_total == 300.0
    assert len(data['transactions']) == 2
    assert not data['principal_recovered']  # Should not be recovered yet
    
    print("✓ Dividend totals calculation works")
    
    # Test principal recovery
    recovery_transactions = [
        {
            'date': '2024-03-15',
            'description': 'Large Dividend',
            'amount': 9700.0,  # This should trigger recovery
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    update_dividend_totals(data, recovery_transactions)
    
    assert data['principal_recovered'] == True
    assert data['post_recovery_gains'] == 0.0  # Exactly at recovery point
    
    print("✓ Principal recovery detection works")

def test_sample_file():
    """Test with the provided sample file"""
    print("\nTesting with sample_robinhood.csv...")
    
    if os.path.exists('sample_robinhood.csv'):
        transactions = parse_robinhood_csv('sample_robinhood.csv')
        total_amount = sum(t['amount'] for t in transactions)
        
        print(f"✓ Sample file contains {len(transactions)} dividend transactions")
        print(f"✓ Total dividend amount: ${total_amount:.2f}")
    else:
        print("⚠ Sample file not found")

if __name__ == "__main__":
    print("DivTrack Test Suite")
    print("=" * 50)
    
    try:
        test_data_loading()
        test_csv_parsing()
        test_dividend_totals()
        test_sample_file()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! DivTrack is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
