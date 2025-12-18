# Zerodha Kite Connect Trading Bot

Automated trading system for Zerodha using the KiteConnect API with advanced RSI monitoring, Donchian Channel strategy, and email/Discord alerts, designed for headless terminal reliability.

## ✨ Latest Features

- **Email & Discord Alerts**: Unified notification system supporting both email (SMTP) and Discord webhooks. Configure via `.env` file.
- **Heikin Ashi Candle Support**: Both NatgasMini RSI and GOLDPETAL Donchian monitors now support Heikin Ashi candles. Users can select candle type in the CLI menus.
- **Commodity Strategy Monitoring**: Dedicated monitors for NatgasMini (RSI) and GOLDPETAL (Donchian).
- **Headless Optimized**: Zero GUI dependencies, perfect for Raspberry Pi and server deployments.
- **Float Log Formatting**: All float values in logs are normalized.
- **Improved Logging**: Value color set to white, spacing added.

## How to Use Heikin Ashi Feature

- In the Strategy Monitors menu, select your strategy and contract.
- Choose candle type when prompted (Heikin Ashi or Normal).
- Launch the monitor.

## 📑 Table of Contents

- Key Features
- Project Structure
- Quick Start
- Authentication
- Strategy Usage
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

- **Enhanced CLI: Feature-complete terminal interface**
- All trading features in CLI: portfolio, trading, strategy monitors, notifications
- Perfect for headless servers and Raspberry Pi deployments
- Simple CLI: Basic interactive menu
- Launcher script for unified access

### Developer Tools

- Example scripts: basic orders, limit orders, websocket streaming
- Utility functions: position sizing, portfolio analysis, CSV export
- Comprehensive documentation
- Test scripts for setup

## 📁 Project Structure

```
my-trade-py/
├── Core_Modules/          # Core trading modules
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── auth.py            # Authentication & session management
│   ├── trader.py          # Main trading operations
│   ├── websocket_ticker.py # Real-time data streaming
│   ├── strategies.py      # Trading strategies
│   └── utils.py           # Utility functions
│
├── Application/           # Main applications
│   ├── __init__.py
│   ├── main_enhanced.py   # Main CLI trading terminal
│   ├── authenticate.py    # Authentication script
│   └── verify_setup.py    # Environment verification script
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
│   └── .gitignore         # Git ignore rules
│
├── Documentation/         # Documentation files
│   ├── README.md          # Main documentation
│   ├── QUICKSTART.md      # Quick start guide
│   ├── PROJECT_OVERVIEW.md # Detailed project overview
│   ├── ENHANCED_CLI_GUIDE.md # CLI Documentation
│   ├── AUTO_AUTH_SETUP.md # Automated auth setup guide
│   ├── ALERTS_QUICK_REFERENCE.md # Alerts reference
│   ├── EMAIL_DISCORD_ALERTS_SETUP.md # Alerts setup guide
│   └── DONCHIAN_STRATEGY_GUIDE.md # Donchian strategy documentation
│
├── README.md              # Root README (quick reference)
├── launcher.py            # Main launcher script
├── run.sh                 # Quick launch script
└── launcher.py            # Main launcher script
```

````

## 🚀 Quick Start

1. Install dependencies:

```bash
pip3.9 install -r Configuration/requirements.txt
````

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

Or launch the enhanced CLI (recommended for Raspberry Pi):

```bash
./run.sh
# Select Option 3 (Start Enhanced Trading Application)
# OR
python3.9 Application/main_enhanced.py
```

## 🔐 Authentication

- Built-in OAuth authentication in CLI
- Access token saved to `.env` (valid for 24 hours)
- Manual authentication: `python3.9 Application/authenticate.py`

## 📈 Strategy Usage

- NatgasMini RSI: Select future, launch monitor, receive email and Discord alerts
- GOLDPETAL Donchian: Select future, launch monitor, receive email and Discord alerts

## 📚 Documentation

- Quick Start: `Documentation/QUICKSTART.md`
- Full Docs: `Documentation/README.md`
- Project Overview: `Documentation/PROJECT_OVERVIEW.md`
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

- **Positions Fix**:
  - Day and net positions displayed correctly in CLI.

## ⚠️ Important Notes

- Access tokens expire daily; re-authenticate each day
- All order examples are commented out by default
- Use Python 3.9 for all commands
- Use `Core_Modules/` (underscore) for active code
- Configure email and Discord settings in `Configuration/.env`
- For Gmail: use App Password instead of regular password (<https://myaccount.google.com/apppasswords>)

## 🔧 Troubleshooting

- Check `logs/` directory for detailed error messages
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
