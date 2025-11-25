# Zerodha Kite Connect Trading Bot

Automated trading system for Zerodha using the KiteConnect API with advanced RSI monitoring, Donchian Channel strategy, email and Discord alerts, and a modern GUI.

## ✨ Latest Features

- **Email & Discord Alerts**: Unified notification system supporting both email (SMTP) and Discord webhooks. Configure via `.env` file.
- **Heikin Ashi Candle Support**: Both NatgasMini RSI and GOLDPETAL Donchian monitors now support Heikin Ashi candles. Users can select candle type via radio buttons (default: Heikin Ashi) in the GUI.
- **Commodity Strategy Tabs**: Dedicated tabs for NatgasMini (RSI) and GOLDPETAL (Donchian) with auto-loaded MCX futures.
- **Simplified UI**: No exchange dropdowns; all commodity contracts auto-populate.
- **Float Log Formatting**: All float values in logs are normalized (no np.float64).
- **Pre-commit Hooks Removed**: No pre-commit logic in repo.
- **Improved Logging**: Value color set to white, spacing added.

## How to Use Heikin Ashi Feature

- In the NatgasMini and GOLDPETAL tabs, select your contract and interval.
- Choose candle type using the radio button (Heikin Ashi or Normal).
- Launch the monitor; RSI or Donchian logic will use the selected candle type.

## 📑 Table of Contents

- Key Features
- Project Structure
- Quick Start
- Modern Trading Terminal (DearPyGui)
- Authentication
- Strategy Usage
- Classic GUI (tkinter)
- Documentation
- Recent Updates
- Important Notes
- Troubleshooting
- API Documentation

---

## ✨ Key Features

### Trading Capabilities

- Real-time quotes, LTP, OHLC, historical data
- Market, Limit, Stop Loss orders
- Portfolio tracking: positions, holdings, margins, P&L
- WebSocket streaming for tick-by-tick data
- Auto authentication (OAuth2 flow)

### Strategy Monitoring

- RSI strategy: automated calculation, overbought/oversold alerts
- Donchian Channel: breakout/breakdown detection for GOLDPETAL
- Commodity focus: dedicated monitors for NATGASMINI and GOLDPETAL
- Hourly analysis, email and Discord alerts, sound notifications

### User Interfaces

- Modern GUI: DearPyGui-based trading terminal (recommended)
- Dark theme, multiple tabs, dashboard, positions, orders, strategies
- Classic GUI: tkinter-based alternative
- CLI application: interactive menu
- Launcher script for unified access

### Developer Tools

- Example scripts: basic orders, limit orders, websocket streaming
- Utility functions: position sizing, portfolio analysis, CSV export
- Comprehensive documentation
- Test scripts for setup and GUI

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
│   ├── DONCHIAN_STRATEGY_GUIDE.md # Donchian strategy documentation
│   ├── STRUCTURE.md       # Detailed project structure
│   ├── QUICK_REFERENCE.md # Quick command reference
│   ├── BUGFIX_POSITIONS.md # Positions tab bug fix documentation
│   ├── ENHANCEMENT_AUTO_REFRESH.md # Auto-refresh feature documentation
│   └── GUI-Comparision.jpg # GUI comparison screenshot
│
├── launcher.py            # CLI launcher script
├── run.sh                 # Main launcher wrapper
├── run_gui_modern.sh      # Modern GUI launcher (DearPyGui)
├── run_gui.sh             # Legacy GUI launcher (tkinter)
├── test_minimal.py        # DearPyGui minimal test script
└── README.md              # This file - Project overview
```

## 🚀 Quick Start

1. Install dependencies:

```bash
pip3.9 install -r Configuration/requirements.txt
```

2. Configure API credentials in `Configuration/.env`:

```bash
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here

# Email alerts (optional)
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=recipient@example.com

# Discord alerts (optional)
DISCORD_ENABLED=true
DISCORD_WEBHOOK_URL=your-discord-webhook-url
```

3. Run the application:

```bash
./run.sh
```

Or launch the modern GUI directly:

```bash
./run_gui_modern.sh
# OR
python3.9 Application/gui_modern.py
```

## 🖥️ Modern Trading Terminal (DearPyGui)

- Modern dark theme, GPU-accelerated
- Real-time charts, live data tables
- Automated authentication
- Portfolio dashboard, trading tools, CSV export
- **Heikin Ashi Candle Support** for both RSI and Donchian strategies

## Commodity Strategy Monitors

### NatgasMini Tab - RSI Strategy

- Live RSI calculation (period=14)
- Email and Discord webhook alerts
- 1-hour analysis intervals
- Threshold alerts (>70, <30)
- Sound alerts
- Auto-loaded MCX futures
- **Candle Type Selection**: Heikin Ashi or Normal (radio button)

### GOLDPETAL Tab - Donchian Channel Strategy

- Donchian Channel analysis (Upper: 20, Lower: 10)
- Email and Discord alerts for breakouts/breakdowns
- 1-hour intervals
- Bullish/bearish alerts
- Sound alerts
- Auto-loaded MCX futures
- **Candle Type Selection**: Heikin Ashi or Normal (radio button)

## 🔐 Authentication

- Built-in OAuth authentication in GUI
- Access token saved to `.env` (valid for 24 hours)
- Manual authentication: `python3.9 Application/authenticate.py`

## 📈 Strategy Usage

- NatgasMini RSI: Select future, launch monitor, receive email and Discord alerts
- GOLDPETAL Donchian: Select future, launch monitor, receive email and Discord alerts

## 🖼️ Classic GUI (tkinter)

- Portfolio summary, positions, holdings
- Interactive order placement
- Market data viewer
- Position sizing calculator
- CSV export

## 📚 Documentation

- Quick Start: `Documentation/QUICKSTART.md`
- Full Docs: `Documentation/README.md`
- Project Overview: `Documentation/PROJECT_OVERVIEW.md`
- GUI Guide: `Documentation/GUI_GUIDE.md`
- Donchian Strategy: `Documentation/DONCHIAN_STRATEGY_GUIDE.md`
- Project Structure: `Documentation/STRUCTURE.md`

## 🆕 Recent Updates

## 🆕 Recent Updates (Nov 2025)

- **Email Alert System:**  
 	- Unified notification system for both email (SMTP) and Discord alerts.
 	- Configurable via `.env` (supports Gmail, Outlook, custom SMTP).
 	- Alerts for RSI and Donchian signals.

- **Heikin Ashi Candle Support:**  
 	- Both NatgasMini RSI and GOLDPETAL Donchian monitors support Heikin Ashi candles.
 	- Candle type selection via radio buttons (default: Heikin Ashi).

- **Commodity Strategy Tabs:**  
 	- Dedicated tabs for NatgasMini (RSI) and GOLDPETAL (Donchian).
 	- Auto-loaded MCX futures, simplified UI (no exchange dropdowns).

- **Donchian Channel Enhancements:**  
 	- Improved breakout detection using previous candle’s close.
 	- Inclusive inequalities for signal detection.
 	- Lookback feature for missed signals and deduplication of alerts.

- **RSI Monitor Improvements:**  
 	- Lookback on startup to catch missed alerts.
 	- Deduplication of alerts for the same candle.

- **Logging & Formatting:**  
 	- Float values normalized for log output (no np.float64 issues).
 	- Value color set to white, improved spacing.
 	- Structured logging via `structlog` (feature/structlog branch).

- **UI/UX:**  
 	- Active monitor tab coloring (tabs turn green when active).
 	- Wider combo boxes for contract selection.
 	- Sound notifications for strategy signals.

- **Codebase Maintenance:**  
 	- Deprecated modules removed.
 	- Documentation files relocated to `Documentation/`.
 	- Pre-commit hooks removed.

- **Auto-Refresh:**  
 	- Automatic data refresh when switching GUI tabs.
 	- Day and net positions displayed across CLI and GUIs.

## ⚠️ Important Notes

- Access tokens expire daily; re-authenticate each day
- All order examples are commented out by default
- Use Python 3.9 for all commands
- Use `Core_Modules/` (underscore) for active code
- Configure email and Discord settings in `Configuration/.env`
- For Gmail: use App Password instead of regular password (<https://myaccount.google.com/apppasswords>)

## 🔧 Troubleshooting

- GUI issues: check DearPyGui install, Python version, run `test_minimal.py`
- Strategy issues: verify symbol, authentication, Discord webhook
- Futures not loading: check authentication, MCX contracts, network
- Authentication problems: check `.env`, callback server port

## 📖 API Documentation

- [KiteConnect Python SDK](https://kite.trade/docs/pykiteconnect/v4/)
- [Kite Connect API](https://kite.trade/docs/connect/v3/)
- [GitHub Repository](https://github.com/zerodha/pykiteconnect)

## 📄 License

MIT License - Use at your own risk. Trading involves financial risk.

---

Get Started: Run `./run.sh` to begin!
Need Help? Check `Documentation/` folder for detailed guides.
