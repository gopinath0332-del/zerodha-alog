# Zerodha Kite Connect Trading Bot

A Python-based automated trading system for Zerodha using the KiteConnect API.

## Features

- 🔐 **Authentication**: Easy OAuth2 login flow
- 📊 **Market Data**: Real-time quotes, OHLC, historical data
- 💹 **Order Management**: Place, modify, and cancel orders (Market, Limit, Stop Loss)
- 📈 **Portfolio Tracking**: View positions, holdings, and margins
- ⚡ **WebSocket Streaming**: Real-time market data streaming
- 🛡️ **Risk Management**: Configurable stop loss and targets

## Project Structure

my-trade-py/
├── Core_Modules/ # Core trading modules
├── Application/ # Main applications
│ ├── main_enhanced.py # Enhanced CLI trading terminal
│ └── verify_setup.py # Setup verification script
├── config.py # (Deprecated location, moved to Core_Modules)
├── requirements.txt # Python dependencies
├── .env.example # Environment variables template
├── .gitignore # Git ignore file
├── README.md # This file
├── launcher.py # Main Entry point
└── Examples/ # Example scripts
├── basic_order.py # Basic order examples
├── limit_order.py # Limit order with SL
└── websocket_stream.py # WebSocket streaming example

## Setup

### 1. Prerequisites

- Python 3.8 or higher
- Zerodha trading account
- Kite Connect API subscription

### 2. Get API Credentials

1. Visit [Kite Connect](https://developers.kite.trade/)
2. Create a new app to get your `API Key` and `API Secret`
3. Set the redirect URL (e.g., `http://127.0.0.1:5000/callback`)

### 3. Installation

```bash
# Navigate to project directory
cd /Users/admin/Projects/my-trade-py

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your credentials
# API_KEY=your_api_key_here
# API_SECRET=your_api_secret_here
```

### 5. Authentication

First time authentication:

```bash
python auth.py
```

This will:

1. Open the Kite login page in your browser
2. Ask you to login and authorize
3. Request you to enter the `request_token` from the redirect URL
4. Generate and save the `access_token` to `.env`

## Usage

### Interactive CLI Application

Run the main application for an interactive menu:

```bash
./run.sh
```

Or manually:

```bash
python Application/main_enhanced.py
```

Features:

- View market data for any symbols
- Check your portfolio summary
- Place orders interactively
- View orders, positions, holdings
- Check margin availability

### Basic Trading Examples

```python
from trader import KiteTrader

# Initialize trader
trader = KiteTrader()

# Get quote
quote = trader.get_quote('NSE:INFY')
print(quote)

# Get LTP (Last Traded Price)
ltp = trader.get_ltp('NSE:TCS')
print(ltp)

# Place market buy order
order_id = trader.buy_market(
    symbol='INFY',
    quantity=1,
    exchange='NSE',
    product='CNC'  # CNC for delivery, MIS for intraday
)

# Place limit order
order_id = trader.buy_limit(
    symbol='INFY',
    quantity=1,
    price=1500.00,
    exchange='NSE',
    product='MIS'
)

# Get all orders
orders = trader.get_orders()

# Get positions
positions = trader.get_positions()

# Get holdings
holdings = trader.get_holdings()

# Get margins
margins = trader.get_margins('equity')
```

### WebSocket Streaming

```python
from websocket_ticker import KiteWebSocket

def on_ticks(ws, ticks):
    for tick in ticks:
        print(f"LTP: {tick['last_price']}")

def on_connect(ws, response):
    # Subscribe to instruments
    ws.subscribe([738561])  # SBIN token
    ws.set_mode(ws.MODE_FULL, [738561])

kws = KiteWebSocket(
    on_ticks_callback=on_ticks,
    on_connect_callback=on_connect
)

kws.connect()
```

## Running Examples

```bash
# Basic order examples
python examples/basic_order.py

# Limit order with stop loss
python examples/limit_order.py

# WebSocket streaming
python examples/websocket_stream.py
```

## Configuration Options

Edit `config.py` to customize:

- Default exchange (NSE, BSE, NFO, etc.)
- Default product type (CNC, MIS, NRML)
- Default order type (MARKET, LIMIT)
- Risk management parameters (stop loss %, target %)
- Maximum order value and position size

## API Documentation

- [KiteConnect Python SDK](https://kite.trade/docs/pykiteconnect/v4/)
- [Kite Connect API](https://kite.trade/docs/connect/v3/)
- [GitHub Repository](https://github.com/zerodha/pykiteconnect)

## Important Notes

⚠️ **Safety First**

- All order placement code in examples is **commented out by default**
- Test thoroughly in a paper trading environment first
- Start with small quantities
- Always use stop losses
- Monitor your positions regularly

⚠️ **Access Token**

- Access tokens expire daily
- Re-authenticate each day or implement token refresh
- Store tokens securely, never commit to version control

⚠️ **Rate Limits**

- KiteConnect has rate limits on API calls
- WebSocket is recommended for real-time data
- Implement appropriate delays between API calls

## Risk Disclaimer

This software is for educational purposes only. Trading in financial markets involves substantial risk of loss. The authors and contributors are not responsible for any financial losses incurred through the use of this software. Always consult with a qualified financial advisor before making investment decisions.

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:

- KiteConnect API: [support@zerodha.com](mailto:support@zerodha.com)
- SDK Issues: [GitHub Issues](https://github.com/zerodha/pykiteconnect/issues)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
