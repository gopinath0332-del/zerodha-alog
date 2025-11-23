# Zerodha Kite Connect Trading Bot

Automated trading system for Zerodha using the KiteConnect API with advanced RSI monitoring and Discord alerts.

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Project Statistics](#-project-statistics)
- [Modern Trading Terminal](#️-modern-trading-terminal-dearpygui)
- [Authentication](#-authentication)
- [Strategy Usage](#-strategy-usage)
- [Classic GUI](#️-classic-gui-tkinter)
- [Documentation](#-documentation)
- [Recent Updates](#-recent-updates)
- [Important Notes](#️-important-notes)
- [Troubleshooting](#-troubleshooting)
- [API Documentation](#-api-documentation)

---

## ✨ Key Features

### Trading Capabilities

- 📊 **Market Data**: Real-time quotes, LTP, OHLC, historical data
- 💹 **Order Management**: Market, Limit, Stop Loss orders
- 📈 **Portfolio Tracking**: Positions, holdings, margins, P&L
- ⚡ **WebSocket Streaming**: Real-time tick-by-tick data
- 🔐 **Auto Authentication**: OAuth flow with callback server

### Strategy Monitoring

- 📉 **RSI Strategy**: Automated RSI calculation with overbought/oversold alerts
- 📊 **Donchian Channels**: Breakout/breakdown detection for trend analysis
- 🎯 **Commodity Focus**: Dedicated monitors for NATGASMINI and GOLDPETAL
- ⏰ **Hourly Analysis**: Market boundary-aligned monitoring
- 🔔 **Discord Alerts**: Rich webhook notifications for all signals
- 🎵 **Sound Alerts**: Audio notifications for important events

### User Interfaces

- 🖥️ **Modern GUI**: DearPyGui-based professional trading terminal
- 🎨 **Dark Theme**: Optimized for extended trading sessions
- 📊 **Multiple Tabs**: Dashboard, Positions, Orders, Strategies, Settings
- 🖼️ **Classic GUI**: tkinter-based alternative interface
- 💻 **CLI Application**: Interactive command-line interface
- 🚀 **Launcher Menu**: Easy access to all features

### Developer Tools

- 📝 **Example Scripts**: Basic orders, limit orders, websocket streaming
- 🔧 **Utility Functions**: Position sizing, portfolio analysis, CSV export
- 📚 **Comprehensive Docs**: 12 documentation files covering all aspects
- 🧪 **Test Scripts**: GUI testing and setup verification

## 📁 Project Structure

```
my-trade-py/
├── Core_Modules/          # Core trading modules (active)
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── auth.py            # Authentication & session management
│   ├── trader.py          # Main trading operations
│   ├── websocket_ticker.py # Real-time data streaming
│   ├── strategies.py      # Trading strategies
│   └── utils.py           # Utility functions
│
├── Core Modules/          # Legacy directory (deprecated, use Core_Modules)
│   ├── auth.py            # Older versions of core files
│   ├── trader.py
│   ├── strategies.py
│   ├── utils.py
│   └── websocket_ticker.py
│
├── Application/           # Main applications
│   ├── __init__.py
│   ├── gui_modern.py      # Modern DearPyGui trading terminal
│   ├── gui_components/    # GUI components directory (reserved)
│   ├── gui.py             # Legacy tkinter GUI
│   ├── main.py            # Interactive CLI application
│   ├── authenticate.py    # Authentication script
│   └── verify_setup.py    # Setup verification script
│
├── Examples/              # Example scripts
│   ├── __init__.py
│   ├── basic_order.py     # Basic trading examples
│   ├── limit_order.py     # Limit orders with stop loss
│   └── websocket_stream.py # WebSocket streaming demo
│
├── Configuration/         # Configuration files
│   ├── requirements.txt   # Python dependencies
│   ├── .env               # Environment variables (API keys)
│   ├── .env.example       # Environment template
│   └── instruments_nse.csv # Cached NSE instruments
│
├── Documentation/         # Documentation
│   ├── README.md          # Main documentation
│   ├── QUICKSTART.md      # Quick start guide
│   ├── PROJECT_OVERVIEW.md # Detailed project overview
│   ├── GUI_GUIDE.md       # GUI application guide
│   ├── AUTO_AUTH_SETUP.md # Automated auth setup guide
│   └── GUI-Comparision.jpg # GUI comparison screenshot
│
├── launcher.py            # CLI launcher script
├── run.sh                 # Main launcher wrapper
├── run_gui_modern.sh      # Modern GUI launcher (DearPyGui)
├── run_gui.sh             # Legacy GUI launcher (tkinter)
├── test_minimal.py        # DearPyGui minimal test script
├── STRUCTURE.md           # Detailed project structure
├── QUICK_REFERENCE.md     # Quick command reference
└── DONCHIAN_STRATEGY_GUIDE.md # Donchian strategy documentation
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip3.9 install -r Configuration/requirements.txt
```

**Dependencies installed:**

- `kiteconnect` - Zerodha KiteConnect API SDK
- `python-dotenv` - Environment variable management
- `pandas` - Data analysis and manipulation
- `requests` - HTTP library for Discord webhooks
- `dearpygui` - Modern GPU-accelerated GUI framework

### 2. Configure API Credentials

Edit `Configuration/.env` with your Kite Connect credentials:

```bash
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

### 3. Run the Application

```bash
./run.sh
```

The launcher provides easy access to all features:

1. **Verify Setup** - Check your environment
2. **Authenticate** - First time / Daily login
3. **Start Trading Application** - Launch CLI trading app
4. **Run Basic Order Example** - Test basic operations
5. **Run Limit Order Example** - Test limit orders
6. **Run WebSocket Stream Example** - Test live data
7. **Exit**

**Note:** To launch the Modern GUI, use `./run_gui_modern.sh` directly.

### Alternative: Direct Commands

```bash
# Launch Modern GUI (DearPyGui) - RECOMMENDED
./run_gui_modern.sh
# OR
python3.9 Application/gui_modern.py

# Verify setup
python3.9 Application/verify_setup.py

# Authenticate (first time or daily)
python3.9 Application/authenticate.py

# Start CLI trading app
python3.9 Application/main.py

# Run examples
python3.9 Examples/basic_order.py
python3.9 Examples/websocket_stream.py
```

## � Project Statistics

- **Python Files**: 24 modules
- **Documentation Files**: 12 markdown files
- **Shell Scripts**: 3 launcher scripts
- **Total Lines of Code**: ~6,600+ lines
- **Core Modules**: 7 files (auth, config, trader, websocket, strategies, utils)
- **GUI Applications**: 2 (Modern DearPyGui + Legacy tkinter)
- **Example Scripts**: 3 (basic orders, limit orders, websocket streaming)

## �🖥️ Modern Trading Terminal (DearPyGui)

Launch the professional trading interface:

```bash
./run_gui_modern.sh
```

**Features:**

### Core Features

- 🎨 **Modern Dark Theme** - Professional trading terminal aesthetics
- ⚡ **GPU-Accelerated** - Smooth, fast rendering with DearPyGui
- 📊 **Real-time Charts** - Portfolio performance visualization
- 📈 **Live Data Tables** - Positions, holdings, orders
- 🎯 **Automated Authentication** - OAuth flow with callback server
- 💼 **Portfolio Dashboard** - Complete P&L overview
- 🛠️ **Trading Tools** - Position sizing calculator
- 💾 **Data Export** - CSV export functionality

### Commodity Strategy Monitors

#### NatgasMini Tab - RSI Strategy

- 📉 **Live RSI Calculation** - Using Wilder's smoothing method (period=14)
- 🔔 **Discord Webhook Alerts** - Real-time notifications for all events
- ⏰ **1-Hour Analysis Intervals** - MCX commodity market boundaries
- 🎯 **Threshold Alerts** - Overbought (>70) and Oversold (<30) detection
- 🎵 **Sound Alerts** - Cross-platform alert sounds
- 📊 **Auto-Loaded Futures** - NATGASMINI contracts auto-populated from MCX

#### GOLDPETAL Tab - Donchian Channel Strategy

- 📊 **Donchian Channel Analysis** - Upper band (20 periods) and Lower band (10 periods)
- 🔔 **Discord Webhook Alerts** - Breakout and breakdown notifications
- ⏰ **1-Hour Analysis Intervals** - MCX commodity market boundaries
- 📈 **Bullish Breakout Alerts** - Price crosses above upper band
- 📉 **Bearish Breakdown Alerts** - Price crosses below lower band
- 🎵 **Sound Alerts** - Instant audio notification on signal
- 📊 **Auto-Loaded Futures** - GOLDPETAL contracts auto-populated from MCX

### Discord Integration

Both monitors send rich alerts for:

- 🟢 **Monitor Started** - Initial values included
- 🟢 **Bullish Alerts** (NatgasMini/GOLDPETAL) - Green embeds
- 🔴 **Bearish Alerts** (NatgasMini/GOLDPETAL) - Red embeds
- ⚪ **Monitor Stopped** - Final values included
- 🔴 **Error Alerts** - Any issues during monitoring

## 🔐 Authentication

### Automated OAuth Authentication (Recommended)

The modern GUI includes built-in OAuth authentication:

1. Click "Authenticate" in Settings tab
2. Select "Auto-Authenticate (Recommended)"
3. Browser opens to Kite login page
4. Login with your credentials
5. App automatically captures token
6. You're authenticated!

The access token is saved to `.env` and works for 24 hours.

### Manual Authentication

Alternatively, use the standalone script:

```bash
python3.9 Application/authenticate.py
```

See `Documentation/AUTO_AUTH_SETUP.md` for detailed setup.

## 📈 Strategy Usage

### NatgasMini RSI Monitor

1. **Launch GUI**: `./run_gui_modern.sh`
2. **Go to NatgasMini Tab**
3. **Select Future**:
   - Click "Future" dropdown to select NATGASMINI contract
   - Symbol auto-updates
4. **Start Monitoring**: Click "Launch RSI Monitor"
5. **Monitor**:
   - View current RSI value in real-time
   - Receive Discord alerts for overbought/oversold signals
6. **Stop**: Click "Stop Monitor" when done

### GOLDPETAL Donchian Channel Monitor

1. **Launch GUI**: `./run_gui_modern.sh`
2. **Go to GOLDPETAL Tab**
3. **Select Future**:
   - Click "Future" dropdown to select GOLDPETAL contract
   - Symbol auto-updates
4. **Start Monitoring**: Click "Launch Donchian Monitor"
5. **Monitor**:
   - View current price, upper band, lower band in real-time
   - Receive Discord alerts for breakouts/breakdowns
6. **Stop**: Click "Stop Monitor" when done

## 📈 Old RSI Strategy Usage

1. **Launch GUI**: `./run_gui_modern.sh`
2. **Go to RSI Strategy Tab**
3. **Configure**:
   - Enter symbol (e.g., RELIANCE, INFY)
   - Select interval (hour/day/15minute)
   - Click "Start Monitoring"
4. **Monitor**:
   - View current RSI value in real-time
   - Receive Discord alerts for all events
   - Check terminal logs for detailed history
5. **Stop**: Click "Stop Monitoring" when done

### Discord Webhook Setup

Configure your Discord webhook URL in `Application/gui_modern.py` (line 88):

```python
self.discord_webhook_url = "YOUR_WEBHOOK_URL_HERE"
```

**How to get a Discord webhook URL:**

1. Open Discord and go to your server
2. Right-click on a channel → Edit Channel → Integrations
3. Create a new webhook and copy the URL
4. Paste it in the code above

## 🖼️ Classic GUI (tkinter)

Launch the classic interface:

```bash
./run_gui.sh
```

The classic GUI provides:

- 📊 Portfolio summary and analysis
- 📈 Real-time positions and holdings
- 🎯 Interactive order placement
- 📉 Market data viewer
- 🏆 Top gainers/losers
- 💰 Position sizing calculator
- 💾 CSV export functionality

See `Documentation/GUI_GUIDE.md` for detailed GUI usage.

**Visual Comparison:** See `Documentation/GUI-Comparision.jpg` for a side-by-side comparison of both GUIs.

## 📚 Documentation

For detailed documentation, see:

- **Quick Start Guide**: `Documentation/QUICKSTART.md`
- **Full Documentation**: `Documentation/README.md`
- **Project Overview**: `Documentation/PROJECT_OVERVIEW.md`
- **GUI Guide**: `Documentation/GUI_GUIDE.md`
- **Auto Auth Setup**: `Documentation/AUTO_AUTH_SETUP.md`
- **Donchian Strategy Guide**: `DONCHIAN_STRATEGY_GUIDE.md`
- **Project Structure**: `STRUCTURE.md`
- **Quick Reference**: `QUICK_REFERENCE.md`

## 🆕 Recent Updates

### Donchian Channel Strategy Branch (feature/donchain)

- ✅ **NatgasMini RSI Tab** - Dedicated NATGASMINI futures monitoring
  - Auto-loaded futures dropdown from MCX
  - Hourly market boundary checks
  - Real-time RSI calculation with Discord alerts
- ✅ **GOLDPETAL Donchian Tab** - GOLDPETAL futures trend analysis
  - Donchian Channel with fixed band periods (Upper: 20, Lower: 10)
  - Auto-loaded futures dropdown from MCX
  - Bullish/Bearish breakout/breakdown detection
  - Real-time Discord alerts with rich embeds
- ✅ **Commodity-Focused UI** - Simplified, dedicated monitoring interfaces
  - Tab names reflect underlying commodity
  - No exchange selection (always MCX)
  - Futures auto-selected on startup
  - Symbol fields auto-update from dropdown selection

### RSI Strategy Branch (feature/rsi)

- ✅ Live RSI monitoring with 1-hour intervals
- ✅ Discord webhook integration for all alerts
- ✅ Accurate RSI calculation using Wilder's smoothing
- ✅ Current RSI value included in all messages
- ✅ Comprehensive logging and error handling
- ✅ 24-hour instrument caching for performance

### GUI Improvements

- ✅ Automated OAuth authentication with callback server
- ✅ Modern dark theme optimized for trading
- ✅ Emoji-free UI (fixed rendering issues)
- ✅ Auto-refresh on tab changes
- ✅ Margin view with equity and commodity segments

## ⚠️ Important Notes

- **Access Tokens**: Expire daily - re-authenticate each day (auto-handled by GUI)
- **Safety First**: All order examples are commented out by default
- **Risk Management**: Always test with small quantities before scaling
- **Stop Losses**: Use proper risk management in all trades
- **RSI Monitoring**: Requires authenticated session and valid symbols
- **Python Version**: Use Python 3.9 (`python3.9`) for all commands
- **Directory Structure**: Use `Core_Modules/` (with underscore) - the `Core Modules/` directory is legacy/deprecated
- **Discord Webhook**: Configure webhook URL in `Application/gui_modern.py` line 88 for alerts

## 🔧 Troubleshooting

### GUI Not Showing

If the GUI appears blank:

1. Ensure DearPyGui is installed: `pip3.9 install dearpygui`
2. Check Python version: `python3.9 --version` (should be 3.9.x)
3. Run test: `python3.9 test_minimal.py`
4. Check terminal for errors

### Strategy Monitoring Issues

1. Verify commodity symbol is correct (e.g., `GOLDPETAL`, `NATGASMINI25DECFUT`)
2. Ensure you're authenticated
3. Check Discord webhook URL is configured
4. Review terminal logs for errors
5. Verify MCX market is open during trading hours

### Futures Not Loading

1. Check authentication is valid
2. Verify MCX exchange has available contracts
3. Check network connectivity
4. Restart the application to reload futures

### Authentication Problems

1. Check API credentials in `.env`
2. Ensure callback server port 5000 is available
3. Try manual authentication: `python3.9 Application/authenticate.py`

## 📖 API Documentation

- [KiteConnect Python SDK](https://kite.trade/docs/pykiteconnect/v4/)
- [Kite Connect API](https://kite.trade/docs/connect/v3/)
- [GitHub Repository](https://github.com/zerodha/pykiteconnect)

## 📄 License

MIT License - Use at your own risk. Trading involves financial risk.

---

**Get Started**: Run `./run.sh` to begin!

**Need Help?** Check `Documentation/` folder for detailed guides.
