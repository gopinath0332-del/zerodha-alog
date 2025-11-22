# Zerodha Kite Connect Trading Bot

Automated trading system for Zerodha using the KiteConnect API.

## 📁 Project Structure

```
my-trade-py/
├── Core_Modules/          # Core trading modules
│   ├── config.py          # Configuration settings
│   ├── auth.py            # Authentication & session management
│   ├── trader.py          # Main trading operations
│   ├── websocket_ticker.py # Real-time data streaming
│   ├── strategies.py      # Trading strategies
│   └── utils.py           # Utility functions
│
├── Application/           # Main applications
│   ├── gui.py             # GUI trading application
│   ├── main.py            # Interactive CLI application
│   ├── authenticate.py    # Authentication script
│   └── verify_setup.py    # Setup verification script
│
├── Examples/              # Example scripts
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
├── Documentation/         # Documentation
│   ├── README.md          # Main documentation
│   ├── QUICKSTART.md      # Quick start guide
│   ├── PROJECT_OVERVIEW.md # Detailed project overview
│   └── GUI_GUIDE.md       # GUI application guide
│
├── launcher.py            # CLI launcher script
└── run_gui.sh             # GUI launcher script
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r Configuration/requirements.txt
```

### 2. Configure API Credentials

Edit `Configuration/.env` with your Kite Connect credentials:

```bash
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

### 3. Run the Launcher

```bash
python3.9 launcher.py
```

The launcher provides easy access to all features:

- Verify setup
- Authenticate
- Start trading application
- Run examples

### Alternative: Direct Commands

```bash
# Launch GUI Application
./run_gui.sh

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

## 🖥️ GUI Application

Launch the graphical interface:

```bash
./run_gui.sh
```

The GUI provides:

- 📊 Portfolio summary and analysis
- 📈 Real-time positions and holdings
- 🎯 Interactive order placement
- 📉 Market data viewer
- 🏆 Top gainers/losers
- 💰 Position sizing calculator
- 💾 CSV export functionality

See `Documentation/GUI_GUIDE.md` for detailed GUI usage.

## 📚 Documentation

For detailed documentation, see:

- **Quick Start Guide**: `Documentation/QUICKSTART.md`
- **Full Documentation**: `Documentation/README.md`
- **Project Overview**: `Documentation/PROJECT_OVERVIEW.md`

## ⚠️ Important Notes

- Access tokens expire daily - re-authenticate each day
- All order examples are commented out by default for safety
- Test with small quantities before scaling up
- Always use stop losses and proper risk management

## 📖 API Documentation

- [KiteConnect Python SDK](https://kite.trade/docs/pykiteconnect/v4/)
- [Kite Connect API](https://kite.trade/docs/connect/v3/)
- [GitHub Repository](https://github.com/zerodha/pykiteconnect)

## 📄 License

MIT License - Use at your own risk. Trading involves financial risk.

---

**Get Started**: Run `python3.9 launcher.py` to begin!
