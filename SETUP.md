# DivTrack Setup Guide

## Quick Start (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Application
```bash
python start.py
```
*or*
```bash
python app.py
```

### 3. Open Your Browser
Go to: http://localhost:5000

## First Time Setup

1. **Set Initial Investment**: 
   - Go to Settings page
   - Enter your total initial investment amount
   - Click "Save Settings"

2. **Upload Your First CSV**:
   - Go to Upload CSV page
   - Download your Robinhood account history CSV
   - Drag & drop or browse to upload
   - The app will extract dividend transactions automatically

3. **View Your Dashboard**:
   - See your dividend progress
   - Monitor principal recovery
   - View monthly trends

## Getting Your Robinhood CSV

1. Log into Robinhood
2. Go to **Account → History**
3. Click **"Export"** or **"Download CSV"**
4. Select date range (recommend monthly exports)
5. Download the CSV file

## Features Overview

### Dashboard
- **Statistics Cards**: Initial investment, total dividends, recovery progress, post-recovery gains
- **Progress Bar**: Visual representation of principal recovery
- **Monthly Chart**: Dividend income trends over time
- **Recent Transactions**: Latest dividend payments
- **Quick Actions**: Easy access to upload and settings

### Upload Page
- **Drag & Drop**: Easy file upload
- **Instructions**: Step-by-step guide for getting Robinhood CSV
- **Security Info**: Explains data privacy
- **Processing**: Automatic dividend extraction

### Settings Page
- **Investment Configuration**: Set/update initial investment amount
- **Current Status**: Real-time progress overview
- **FAQ**: Common questions and answers
- **Help**: Detailed explanations of concepts

## Data Storage

- **Local Storage**: All data stored in `dividend_data.json`
- **Automatic Backups**: Created when resetting data
- **No Cloud**: Your data stays on your device
- **CSV Processing**: Files are processed and deleted immediately

## Troubleshooting

### Common Issues

**App won't start:**
```bash
pip install -r requirements.txt
python app.py
```

**No dividends found:**
- Ensure CSV is from Robinhood account history
- Check that file contains dividend transactions
- Verify CSV format matches expected columns

**Upload errors:**
- Make sure file is valid CSV format
- Check file size (should be reasonable)
- Ensure proper file permissions

**Chart not showing:**
- Enable JavaScript in browser
- Check browser console for errors
- Refresh the page

### Getting Help

1. Check this setup guide
2. Review the FAQ in Settings page
3. Check the main README.md file
4. Run the test script: `python test_app.py`

## Security Notes

- ✅ No Robinhood credentials stored
- ✅ CSV files processed and deleted
- ✅ All data stored locally
- ✅ No internet connection required after setup

## Monthly Workflow

1. Download new Robinhood CSV (monthly)
2. Upload to DivTrack
3. View updated progress on dashboard
4. Repeat next month

---

**DivTrack** - Making dividend tracking simple and secure! 🎯
