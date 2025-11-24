# Email and Discord Alert System Setup Guide

This guide will help you configure and test the email and Discord alert system for your trading bot.

## Overview

The trading bot now supports **dual notification channels**:

- **Email alerts** via SMTP (Gmail, Outlook, or any SMTP server)
- **Discord alerts** via webhooks

Both systems work independently and can be enabled/disabled separately. You can receive alerts on one or both channels simultaneously.

## Features

### What Gets Alerted?

All trading signals and events are sent to your configured notification channels:

- **RSI Alerts** (NatgasMini strategy):

  - Monitor started/stopped
  - Overbought conditions (RSI > 70)
  - Oversold conditions (RSI < 30)
  - Errors and warnings

- **Donchian Channel Alerts** (GOLDPETAL strategy):
  - Monitor started/stopped
  - Bullish breakouts (price > upper band)
  - Bearish breakdowns (price < lower band)
  - Errors and warnings

### Alert Formatting

- **Email**: Rich HTML formatting with color-coded alerts

  - Green for bullish/success signals
  - Red for bearish/error signals
  - Blue for informational messages
  - Orange for warnings
  - Gray for neutral events

- **Discord**: Embedded messages with color-coded sidebars matching email colors

## Configuration

### Step 1: Edit `.env` File

Copy the example configuration and edit your `.env` file:

```bash
cd /Users/admin/Projects/my-trade-py/Configuration
cp .env.example .env  # If you don't have .env yet
nano .env  # or use your preferred editor
```

### Step 2: Configure Email (Optional)

Add these lines to your `.env` file:

```env
# Email Alert Configuration
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com
EMAIL_TO_ADDITIONAL=another@example.com,third@example.com
```

#### Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:

   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Trading Bot"
   - Copy the 16-character password
   - Use this password in `SMTP_PASSWORD` field

3. **Configuration**:
   ```env
   EMAIL_ENABLED=true
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=youremail@gmail.com
   SMTP_PASSWORD=abcd efgh ijkl mnop  # 16-char app password
   EMAIL_FROM=youremail@gmail.com
   EMAIL_TO=youremail@gmail.com
   ```

#### Outlook/Hotmail Setup

```env
EMAIL_ENABLED=true
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=youremail@outlook.com
SMTP_PASSWORD=your-password
EMAIL_FROM=youremail@outlook.com
EMAIL_TO=recipient@example.com
```

#### Custom SMTP Server

```env
EMAIL_ENABLED=true
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
EMAIL_FROM=alerts@yourdomain.com
EMAIL_TO=recipient@example.com
```

### Step 3: Configure Discord (Optional)

1. **Create Discord Webhook**:

   - Open Discord and go to your server
   - Right-click on the channel where you want alerts
   - Select "Edit Channel" → "Integrations" → "Webhooks"
   - Click "New Webhook"
   - Copy the webhook URL

2. **Add to `.env`**:
   ```env
   DISCORD_ENABLED=true
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE
   ```

### Step 4: Multiple Recipients (Email)

To send emails to multiple recipients, use comma-separated values:

```env
EMAIL_TO=primary@example.com
EMAIL_TO_ADDITIONAL=secondary@example.com,third@example.com,fourth@example.com
```

## Testing

### Test Email Configuration

Run this command to test your email setup:

```bash
cd /Users/admin/Projects/my-trade-py
python3.9 -c "from Core_Modules.notifications import create_notification_manager_from_config; mgr = create_notification_manager_from_config(); print('Email test:', mgr.email_notifier.send_test_email() if mgr.email_notifier else 'Email not configured')"
```

**Expected output**:

- Console: `Email test: True`
- Inbox: You should receive a test email

### Test Discord Configuration

```bash
python3.9 -c "from Core_Modules.notifications import create_notification_manager_from_config; mgr = create_notification_manager_from_config(); print('Discord test:', mgr.discord_notifier.send_test_alert() if mgr.discord_notifier else 'Discord not configured')"
```

**Expected output**:

- Console: `Discord test: True`
- Discord: You should see a test message in your channel

### Test Both Systems

```bash
python3.9 -c "from Core_Modules.notifications import create_notification_manager_from_config; mgr = create_notification_manager_from_config(); results = mgr.send_test_alerts(); print('Test results:', results)"
```

**Expected output**:

```
Test results: {'email': True, 'discord': True}
```

## Usage in GUI

Once configured, the notification system works automatically:

1. **Launch the GUI**:

   ```bash
   ./run_gui_modern.sh
   ```

2. **Start a Strategy Monitor**:

   - Go to "NatgasMini" or "GOLDPETAL" tab
   - Select a futures contract
   - Click "Start Monitor"

3. **Receive Alerts**:
   - Monitor start confirmation (email + Discord)
   - Trading signals (RSI/Donchian alerts)
   - Monitor stop confirmation

## Troubleshooting

### Email Issues

**Problem**: "Authentication failed" error

**Solutions**:

- For Gmail: Make sure you're using an App Password, not your regular password
- For Gmail: Enable 2-Factor Authentication first
- Check username and password are correct
- Verify SMTP server and port are correct

**Problem**: "Connection refused" error

**Solutions**:

- Check your firewall isn't blocking port 587
- Try port 465 with SSL (update code if needed)
- Verify SMTP server address is correct

**Problem**: Emails not arriving

**Solutions**:

- Check spam/junk folder
- Verify `EMAIL_TO` address is correct
- Check email server logs for delivery issues
- Try sending to a different email address

### Discord Issues

**Problem**: "Webhook not found" error

**Solutions**:

- Verify webhook URL is complete and correct
- Make sure webhook wasn't deleted in Discord
- Create a new webhook and update `.env`

**Problem**: No Discord messages appearing

**Solutions**:

- Check `DISCORD_ENABLED=true` in `.env`
- Verify webhook URL is correct
- Check Discord channel permissions

### General Issues

**Problem**: No alerts at all

**Solutions**:

- Check both `EMAIL_ENABLED` and `DISCORD_ENABLED` settings
- Verify `.env` file is in `Configuration/` directory
- Check logs for error messages
- Run test commands to verify configuration

**Problem**: Alerts delayed

**Solutions**:

- This is normal - alerts are sent asynchronously to avoid blocking the GUI
- Email delivery can take a few seconds
- Discord is usually instant

## Configuration Examples

### Email Only

```env
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=myemail@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
EMAIL_FROM=myemail@gmail.com
EMAIL_TO=myemail@gmail.com

DISCORD_ENABLED=false
```

### Discord Only

```env
EMAIL_ENABLED=false

DISCORD_ENABLED=true
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdefg
```

### Both Email and Discord

```env
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=myemail@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
EMAIL_FROM=myemail@gmail.com
EMAIL_TO=myemail@gmail.com

DISCORD_ENABLED=true
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdefg
```

## Advanced Features

### Multiple Email Recipients

Send alerts to your entire team:

```env
EMAIL_TO=trader1@company.com
EMAIL_TO_ADDITIONAL=trader2@company.com,manager@company.com,alerts@company.com
```

### Disable Notifications Temporarily

To temporarily disable notifications without removing configuration:

```env
EMAIL_ENABLED=false
DISCORD_ENABLED=false
```

### Custom Email Styling

The email HTML templates are in `Core_Modules/notifications.py`. You can customize:

- Colors for different alert types
- Email layout and styling
- Footer text
- Header format

## Security Best Practices

1. **Never commit `.env` file** to version control (it's in `.gitignore`)
2. **Use App Passwords** for Gmail instead of your main password
3. **Rotate credentials** periodically
4. **Limit webhook access** - only share with trusted team members
5. **Use separate email** for trading alerts (optional but recommended)

## Support

If you encounter issues:

1. Check the logs in `logs/` directory
2. Run the test commands above
3. Verify your `.env` configuration
4. Check the troubleshooting section

For Gmail App Password help: https://support.google.com/accounts/answer/185833
For Discord webhook help: https://support.discord.com/hc/en-us/articles/228383668

---

**Happy Trading! 📈**
