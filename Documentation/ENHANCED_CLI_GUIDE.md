# Enhanced CLI Application Guide

## Overview

The Enhanced CLI (`main_enhanced.py`) provides complete feature parity with the Modern GUI (`gui_modern.py`) in a terminal-based interface. Perfect for headless deployments, Raspberry Pi, and remote server environments.

## Features

### ✅ Complete Feature Parity

All features from the Modern GUI are available:

- **Portfolio Management**: Summary, positions, holdings, margins
- **Trading Operations**: Market, limit, and bracket orders
- **Strategy Monitors**: NatgasMini RSI and GOLDPETAL Donchian with background threads
- **Email & Discord Alerts**: Full notification support
- **Tools**: Position size calculator, CSV exports
- **Colored Output**: Green/red P&L, formatted tables

### 🎨 Enhanced User Experience

- **Colored Terminal Output**: Using `colorama` for cross-platform color support
- **Formatted Tables**: Using `tabulate` for professional data display
- **Background Monitors**: Strategy monitors run in daemon threads
- **Graceful Shutdown**: Signal handlers for clean exit (Ctrl+C)
- **Clear Navigation**: Intuitive menu system with submenus

## Quick Start

### Installation

```bash
# Install dependencies (includes colorama and tabulate)
pip3.9 install -r Configuration/requirements.txt

# Make launcher executable
chmod +x run_cli_enhanced.sh
```

### Running

```bash
# Using launcher script
./run_cli_enhanced.sh

# Or directly
python3.9 Application/main_enhanced.py
```

## Menu Structure

```
Main Menu:
1.  Portfolio Summary
2.  Positions
3.  Holdings
4.  Orders (submenu)
5.  Margins
6.  Market Data
7.  Strategy Monitors (submenu)
8.  Tools (submenu)
9.  Settings (submenu)
10. Exit
```

### Orders Submenu

- View Orders
- Place Market Order
- Place Limit Order
- Place Bracket Order
- Cancel Order

### Strategy Monitors Submenu

- **NatgasMini RSI Monitor**
  - Select from available MCX futures
  - Choose candle type (Heikin Ashi / Normal)
  - Runs in background thread
  - Email + Discord alerts
- **GOLDPETAL Donchian Monitor**

  - Select from available MCX futures
  - Choose candle type (Heikin Ashi / Normal)
  - Runs in background thread
  - Email + Discord alerts

- Stop All Monitors

### Tools Submenu

- Position Size Calculator
- Export Portfolio to CSV
- Export Positions to CSV
- Export Holdings to CSV

### Settings Submenu

- Re-authenticate
- Clear Screen
- Toggle Auto-Refresh

## Strategy Monitors

### How They Work

Strategy monitors run in **background daemon threads**, allowing you to:

- Continue using other menu options while monitors are active
- Monitor multiple strategies simultaneously (RSI + Donchian)
- Receive real-time alerts via email and Discord
- View current monitor status in the main menu

### Starting a Monitor

1. Select **7. Strategy Monitors**
2. Choose **1. NatgasMini RSI** or **2. GOLDPETAL Donchian**
3. Select a futures contract from the list
4. Choose candle type (Heikin Ashi recommended)
5. Monitor starts immediately and runs in background

### Monitor Status

The main menu shows active monitors:

```
Status: Authenticated ✓
Active Monitors: RSI (NATGASMINI25NOVFUT), Donchian (GOLDPETAL25DECFUT)
```

### Stopping Monitors

- **Individual**: Return to Strategy Monitors menu and select the running monitor
- **All**: Select **3. Stop All Monitors** from Strategy Monitors menu
- **On Exit**: All monitors stop automatically when exiting the application

## Notifications

Both email and Discord notifications work exactly as in the GUI:

- **Monitor Started**: Blue notification
- **RSI Overbought (>70)**: Red alert
- **RSI Oversold (<30)**: Green alert
- **Donchian Bullish Breakout**: Green alert
- **Donchian Bearish Breakdown**: Red alert
- **Monitor Stopped**: Gray notification

Configure in `Configuration/.env`:

```env
EMAIL_ENABLED=true
DISCORD_ENABLED=true
```

## Color Scheme

- **Green**: Positive P&L, success messages, bullish alerts
- **Red**: Negative P&L, errors, bearish alerts
- **Blue**: Informational messages, headers
- **Yellow**: Warnings, prompts
- **Cyan**: Monitor status, system info

## Raspberry Pi Deployment

Perfect for 24/7 monitoring on Raspberry Pi:

### Using screen (Recommended)

```bash
# Start a screen session
screen -S trading

# Run the enhanced CLI
./run_cli_enhanced.sh

# Start your monitors
# Press Ctrl+A, then D to detach

# Reattach later
screen -r trading
```

### Using tmux

```bash
# Start tmux session
tmux new -s trading

# Run the enhanced CLI
./run_cli_enhanced.sh

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t trading
```

### As a systemd service

See `Documentation/RASPBERRY_PI_DEPLOYMENT.md` for systemd service setup.

## Tips & Best Practices

### For 24/7 Monitoring

1. **Use screen or tmux**: Keeps monitors running after SSH disconnect
2. **Configure notifications**: Enable both email and Discord for redundancy
3. **Monitor logs**: Check `logs/trading_app_enhanced.log` for issues
4. **Set up auto-restart**: Use systemd service for automatic recovery

### For Active Trading

1. **Keep monitors running**: They won't interfere with other operations
2. **Use bracket orders**: Built-in SL and target protection
3. **Check margins first**: View margins before placing large orders
4. **Export data regularly**: Use CSV exports for record-keeping

### Performance

- **Lightweight**: Uses minimal resources compared to GUI
- **Background threads**: Monitors don't block main application
- **Efficient API calls**: Hourly analysis for strategy monitors
- **Low memory**: Perfect for 2GB Raspberry Pi

## Troubleshooting

### Colors not displaying

```bash
# Install colorama
pip3.9 install colorama

# Or disable colors in code (edit main_enhanced.py)
# Comment out: init(autoreset=True)
```

### Monitor not starting

1. Check authentication status
2. Verify futures contracts are available
3. Check logs for errors: `tail -f logs/trading_app_enhanced.log`
4. Ensure email/Discord configured correctly

### Table formatting issues

```bash
# Install tabulate
pip3.9 install tabulate

# Or terminal too narrow - resize terminal window
```

### Keyboard interrupt not working

- Press Ctrl+C twice
- Or use menu option 10 (Exit)

## Comparison: CLI vs GUI

| Feature              | Enhanced CLI | Modern GUI        |
| -------------------- | ------------ | ----------------- |
| Portfolio Management | ✅           | ✅                |
| Trading Operations   | ✅           | ✅                |
| Strategy Monitors    | ✅           | ✅                |
| Notifications        | ✅           | ✅                |
| Resource Usage       | Low          | Medium-High       |
| Headless Support     | ✅           | ❌                |
| Remote Access        | Easy (SSH)   | Complex (VNC/X11) |
| Raspberry Pi         | Perfect      | Requires display  |
| Visual Charts        | ❌           | ✅                |
| Mouse Support        | ❌           | ✅                |

## Examples

### Quick Portfolio Check

```bash
./run_cli_enhanced.sh
# Select: 1 (Portfolio Summary)
# View metrics, press Enter
# Select: 10 (Exit)
```

### Start RSI Monitor

```bash
./run_cli_enhanced.sh
# Select: 7 (Strategy Monitors)
# Select: 1 (NatgasMini RSI)
# Choose contract: 1
# Choose candle type: 1 (Heikin Ashi)
# Monitor starts - press Enter
# Select: 4 (Back to Main Menu)
# Continue using other features while monitor runs
```

### Export All Data

```bash
./run_cli_enhanced.sh
# Select: 8 (Tools)
# Select: 2 (Export Portfolio)
# Select: 3 (Export Positions)
# Select: 4 (Export Holdings)
# Select: 5 (Back)
# Select: 10 (Exit)
```

## Support

- **Main Documentation**: `README.md`
- **Raspberry Pi Guide**: `Documentation/RASPBERRY_PI_DEPLOYMENT.md`
- **Email/Discord Setup**: `Documentation/EMAIL_DISCORD_ALERTS_SETUP.md`
- **Logs**: `logs/trading_app_enhanced.log`

---

**Happy Trading from the Terminal! 📈💻**
