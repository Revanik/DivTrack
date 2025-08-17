# DivTrack - Dividend Income Tracker

A local web application that helps track dividend income from investments, focusing on recovering the original principal and monitoring gains after recovery.

## Features

- **CSV Upload**: Upload Robinhood account history CSV files to extract dividend transactions
- **Dividend Parsing**: Automatically identifies dividend payments from ETFs like MSTY, JEPQ, and others
- **Principal Tracking**: Tracks total dividends earned against your initial investment
- **Recovery Detection**: Flags when dividends equal or exceed your initial investment
- **Post-Recovery Gains**: Monitors income earned after principal recovery
- **Persistent Data**: Saves all data locally so you don't need to re-upload old files
- **Beautiful Dashboard**: Modern UI with progress bars, charts, and statistics
- **Monthly Tracking**: Visualizes dividend income trends over time

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application which will automatically open a localhost server in your default browser:
   ```bash
   python start.py
   ```

### First Time Setup

1. **Set Initial Investment**: Go to Settings and enter your total initial investment amount
2. **Upload CSV**: Download your Robinhood account history CSV and upload it
3. **Monitor Progress**: View your dashboard to see dividend tracking progress

## How to Use

### Getting Your Robinhood CSV

1. Log into your Robinhood account
2. Navigate to **Account → History → Reports and Statements**
3. Select your desired date range
5. Download the CSV file

### Uploading Files

1. Go to the **Upload CSV** page
2. Drag and drop your CSV file or click to browse
3. The app will automatically extract dividend transactions
4. View results on the dashboard

### Understanding the Dashboard

- **Initial Investment**: Your total original investment amount
- **Total Dividends**: Cumulative dividend income received
- **Recovery Progress**: Percentage of principal recovered through dividends
- **Post-Recovery Gains**: Income earned after recovering your principal
- **Monthly Chart**: Visual representation of dividend income over time

## Security & Privacy

- **Local Storage**: All data is stored locally on your device
- **No Credentials**: The app never stores Robinhood login information
- **File Processing**: CSV files are processed and immediately deleted
- **Self-Hosted**: Run entirely on your own machine or server

## Dividend Detection

The app identifies dividend transactions by looking for these keywords in the description:
- `dividend`
- `div`
- `distribution`


## Troubleshooting

### Common Issues

1. **No dividends found in CSV**
   - Ensure the CSV contains dividend transactions
   - Check that the file is from Robinhood account history
   - Verify the CSV format matches expected columns

2. **Upload errors**
   - Make sure the file is a valid CSV
   - Check file size
   - Ensure proper file permissions

3. **Chart not displaying**
   - Requires JavaScript enabled in browser
   - Check browser console for errors
   - Ensure Chart.js is loading properly

### Data Backup

The app automatically creates backups when resetting data:
- Backup files are named: `backup_YYYYMMDD_HHMMSS.json`
- Keep these files safe if you need to restore data

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve DivTrack.

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the FAQ in the Settings page
3. Open an issue on the project repository

---

**DivTrack** - Making dividend tracking simple and secure.