# Email & Discord Alerts - Quick Reference

## Quick Setup (5 minutes)

### 1. Configure Email (Gmail)

```bash
# Edit .env file
nano Configuration/.env
```

Add:

```env
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=your-email@gmail.com
```

**Get Gmail App Password**: https://myaccount.google.com/apppasswords

### 2. Configure Discord

```env
DISCORD_ENABLED=true
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
```

**Create Discord Webhook**: Server Settings → Integrations → Webhooks → New Webhook

### 3. Test Configuration

```bash
cd /Users/admin/Projects/my-trade-py

# Test both systems
python3.9 -c "from Core_Modules.notifications import create_notification_manager_from_config; mgr = create_notification_manager_from_config(); print(mgr.send_test_alerts())"
```

Expected: `{'email': True, 'discord': True}`

## Common Configurations

### Email Only

```env
EMAIL_ENABLED=true
DISCORD_ENABLED=false
```

### Discord Only

```env
EMAIL_ENABLED=false
DISCORD_ENABLED=true
```

### Both (Recommended)

```env
EMAIL_ENABLED=true
DISCORD_ENABLED=true
```

## Alert Types

| Event                      | Color     | Channels        |
| -------------------------- | --------- | --------------- |
| Monitor Started            | 🔵 Blue   | Email + Discord |
| RSI Overbought (>70)       | 🔴 Red    | Email + Discord |
| RSI Oversold (<30)         | 🟢 Green  | Email + Discord |
| Donchian Bullish Breakout  | 🟢 Green  | Email + Discord |
| Donchian Bearish Breakdown | 🔴 Red    | Email + Discord |
| Errors                     | 🔴 Red    | Email + Discord |
| Warnings                   | 🟠 Orange | Email + Discord |
| Monitor Stopped            | ⚪ Gray   | Email + Discord |

## Troubleshooting

### Email Not Working

**Gmail Authentication Failed**:

- Use App Password, not regular password
- Enable 2-Factor Authentication first
- Generate new App Password at: https://myaccount.google.com/apppasswords

**Emails Not Arriving**:

- Check spam/junk folder
- Verify `EMAIL_TO` address
- Test with: `python3.9 -c "from Core_Modules.notifications import EmailNotifier; ..."`

### Discord Not Working

**Webhook Not Found**:

- Verify webhook URL is complete
- Check webhook wasn't deleted in Discord
- Create new webhook if needed

**No Messages Appearing**:

- Check `DISCORD_ENABLED=true`
- Verify webhook URL in `.env`
- Check Discord channel permissions

## Multiple Recipients

```env
EMAIL_TO=primary@example.com
EMAIL_TO_ADDITIONAL=person2@example.com,person3@example.com
```

## SMTP Servers

| Provider | Server                | Port |
| -------- | --------------------- | ---- |
| Gmail    | smtp.gmail.com        | 587  |
| Outlook  | smtp-mail.outlook.com | 587  |
| Yahoo    | smtp.mail.yahoo.com   | 587  |
| Custom   | your.smtp.server      | 587  |

## Files

| File                                          | Purpose                  |
| --------------------------------------------- | ------------------------ |
| `Core_Modules/notifications.py`               | Notification system code |
| `Configuration/.env`                          | Your configuration       |
| `Configuration/.env.example`                  | Configuration template   |
| `Documentation/EMAIL_DISCORD_ALERTS_SETUP.md` | Full setup guide         |

## Support

- Full Setup Guide: `Documentation/EMAIL_DISCORD_ALERTS_SETUP.md`
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- Discord Webhooks: https://support.discord.com/hc/en-us/articles/228383668

---

**Quick Start**: Edit `.env` → Add credentials → Test → Launch GUI → Start monitor → Receive alerts! 🎉
