# DivTrack - Dividend Income Tracker

A multi-user web application that helps track dividend income from investments, focusing on recovering the original principal and monitoring gains after recovery. Each user has their own secure account with isolated data.

## Features

### 🔐 Multi-User Authentication
- **User Registration & Login**: Secure user accounts with password protection
- **Data Isolation**: Each user's dividend data is completely separate and private
- **Session Management**: Stay logged in across browser sessions

### 📊 Dividend Tracking
- **CSV Upload**: Upload Robinhood account history CSV files to extract dividend transactions
- **Dividend Parsing**: Automatically identifies dividend payments from ETFs like MSTY, JEPQ, and others
- **Principal Tracking**: Tracks total dividends earned against your initial investment
- **Recovery Detection**: Flags when dividends equal or exceed your initial investment
- **Post-Recovery Gains**: Monitors income earned after principal recovery
- **Persistent Data**: Saves all data locally so you don't need to re-upload old files
- **Beautiful Dashboard**: Modern UI with progress bars, charts, and statistics
- **Monthly Tracking**: Visualizes dividend income trends over time

### First Time Setup

1. **Create Account**: Register a new user account or login
2. **Set Initial Investment**: Go to Settings and enter your total initial investment amount
3. **Upload CSV**: Download your Robinhood account history CSV and upload it
4. **Monitor Progress**: View your dashboard to see dividend tracking progress

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

- **Database Storage**: All data is stored on a secure PostgreSQL database
- **No Credentials**: The app never stores Robinhood login information
- **File Processing**: CSV files are processed and immediately deleted
- **Hashed Passwords**: Passwords are stored as secure hashes in the database 

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


## Contributing

Feel free to submit issues, feature requests, or pull requests to improve DivTrack.

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the FAQ in the Settings page
3. Open an issue on the project repository

---

**DivTrack** - Making dividend tracking simple and secure.
