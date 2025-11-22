# Project Overview - Zerodha Kite Trading Bot

## 📁 Project Structure

```
my-trade-py/
├── Core Modules
│   ├── config.py              # Configuration settings
│   ├── auth.py                # Authentication & session management
│   ├── trader.py              # Main trading operations
│   ├── websocket_ticker.py    # Real-time data streaming
│   ├── strategies.py          # Trading strategies
│   └── utils.py               # Utility functions
│
├── Application
│   ├── main.py                # Interactive CLI application
│   └── verify_setup.py        # Setup verification script
│
├── Examples
│   ├── examples/basic_order.py      # Basic trading examples
│   ├── examples/limit_order.py      # Limit orders with SL
│   └── examples/websocket_stream.py # WebSocket streaming demo
│
├── Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (API keys)
│   ├── .env.example          # Environment template
│   └── .gitignore            # Git ignore rules
│
└── Documentation
    ├── README.md             # Main documentation
    ├── QUICKSTART.md         # Quick start guide
    └── PROJECT_OVERVIEW.md   # This file
```

## 🔧 Core Components

### 1. Configuration (`config.py`)

- API credentials management
- Default trading parameters
- Risk management settings
- Exchange and product type defaults

### 2. Authentication (`auth.py`)

- KiteAuth class for OAuth2 login flow
- Session generation and token management
- Access token persistence
- Profile retrieval

### 3. Trader (`trader.py`)

- KiteTrader class - main trading interface
- Market data methods (quotes, LTP, OHLC, historical)
- Order management (place, modify, cancel)
- Portfolio methods (positions, holdings, margins)
- Helper methods for common order types

### 4. WebSocket Ticker (`websocket_ticker.py`)

- Real-time market data streaming
- Tick data subscription management
- Callback handlers for ticks, connection events
- Support for LTP, QUOTE, and FULL modes

### 5. Strategies (`strategies.py`)

- TradingStrategies class
- Bracket orders (entry + target + stop loss)
- Momentum strategy
- Trailing stop loss
- Square off all positions

### 6. Utilities (`utils.py`)

- Instrument search
- Top gainers/losers finder
- Position size calculator
- CSV export functions
- Portfolio summary generator
- Order monitoring

## 📊 Key Features

### Market Data

- ✅ Real-time quotes and LTP
- ✅ OHLC data
- ✅ Historical candlestick data
- ✅ WebSocket streaming
- ✅ Market depth (order book)

### Order Management

- ✅ Market orders
- ✅ Limit orders
- ✅ Stop loss orders (SL, SL-M)
- ✅ Order modification
- ✅ Order cancellation
- ✅ Order history tracking

### Portfolio Management

- ✅ View positions (day & net)
- ✅ View holdings
- ✅ Check margins
- ✅ Calculate P&L
- ✅ Export to CSV

### Trading Strategies

- ✅ Bracket orders
- ✅ Momentum trading
- ✅ Trailing stop loss
- ✅ Position sizing
- ✅ Risk management

### Utilities

- ✅ Instrument search
- ✅ Gainers/losers analysis
- ✅ Portfolio analytics
- ✅ Order monitoring
- ✅ Data export

## 🚀 Usage Patterns

### Pattern 1: Quick Market Check

```python
from trader import KiteTrader

trader = KiteTrader()
quote = trader.get_quote('NSE:INFY', 'NSE:TCS')
print(quote)
```

### Pattern 2: Place Simple Order

```python
from trader import KiteTrader

trader = KiteTrader()
order_id = trader.buy_market('INFY', quantity=1, exchange='NSE', product='CNC')
```

### Pattern 3: Real-time Monitoring

```python
from websocket_ticker import KiteWebSocket

def on_ticks(ws, ticks):
    for tick in ticks:
        print(f"{tick['instrument_token']}: ₹{tick['last_price']}")

kws = KiteWebSocket(on_ticks_callback=on_ticks)
kws.subscribe([738561])  # SBIN
kws.connect()
```

### Pattern 4: Strategy Implementation

```python
from strategies import TradingStrategies

strategy = TradingStrategies()

# Find momentum stocks
momentum = strategy.momentum_strategy(['INFY', 'TCS', 'RELIANCE'], threshold=2.0)

# Place bracket order
bracket = strategy.place_bracket_order('INFY', quantity=1, target_pct=3.0, sl_pct=1.5)
```

### Pattern 5: Portfolio Analysis

```python
from utils import get_portfolio_summary

summary = get_portfolio_summary(trader)
print(f"Total P&L: ₹{summary['total_pnl']:,.2f}")
```

## 🔐 Security & Safety

### Environment Variables

- Never commit `.env` file to version control
- `.gitignore` is configured to exclude sensitive files
- Use `.env.example` as a template

### Order Safety

- All order examples are commented by default
- Interactive confirmation for orders in `main.py`
- Clear warnings before executing real trades

### Access Tokens

- Tokens expire daily and need refresh
- Token auto-save to `.env` after authentication
- Use `auth.py` for daily re-authentication

## 📖 API References

### KiteConnect Documentation

- [Python SDK v4 Docs](https://kite.trade/docs/pykiteconnect/v4/)
- [HTTP API v3 Docs](https://kite.trade/docs/connect/v3/)
- [GitHub Repository](https://github.com/zerodha/pykiteconnect)

### Key API Endpoints Used

1. **Session Management**
   - `login_url()` - Get login URL
   - `generate_session()` - Generate access token
   - `profile()` - Get user profile

2. **Market Data**
   - `instruments()` - Get all instruments
   - `quote()` - Get full quote
   - `ltp()` - Get last traded price
   - `ohlc()` - Get OHLC data
   - `historical_data()` - Get candles

3. **Orders**
   - `place_order()` - Place new order
   - `modify_order()` - Modify existing order
   - `cancel_order()` - Cancel order
   - `orders()` - Get all orders
   - `order_history()` - Get order history

4. **Portfolio**
   - `positions()` - Get positions
   - `holdings()` - Get holdings
   - `margins()` - Get margins

5. **WebSocket**
   - `subscribe()` - Subscribe to instruments
   - `unsubscribe()` - Unsubscribe
   - `set_mode()` - Set tick mode

## 🎯 Common Workflows

### Daily Trading Workflow

1. **Morning Setup**

   ```bash
   python auth.py  # Authenticate for the day
   python main.py  # Open interactive app
   ```

2. **Check Portfolio**
   - Option 2: View Portfolio
   - Option 7: View Margins

3. **Analyze Market**
   - Option 1: View Market Data
   - Or run: `python examples/basic_order.py`

4. **Execute Trades**
   - Option 3: Place Order
   - Or use trader methods programmatically

5. **Monitor Positions**
   - Option 5: View Positions
   - Option 4: View Orders

### Strategy Development Workflow

1. **Test Strategy**

   ```python
   from strategies import TradingStrategies
   
   strategy = TradingStrategies()
   # Test with simulation mode (orders commented)
   ```

2. **Backtest** (requires historical data)

   ```python
   from trader import KiteTrader
   
   trader = KiteTrader()
   data = trader.get_historical_data(...)
   # Analyze and backtest
   ```

3. **Paper Trade**
   - Test with small quantities
   - Monitor performance
   - Adjust parameters

4. **Live Trading**
   - Implement risk management
   - Set position limits
   - Use stop losses

## ⚠️ Important Notes

### Daily Limits & Restrictions

- Access tokens expire daily at 6 AM
- Order rate limits apply (check Kite API docs)
- WebSocket has connection limits

### Product Types

- **CNC**: Delivery (long-term holding)
- **MIS**: Intraday (must square off same day)
- **NRML**: Normal (for F&O contracts)

### Order Types

- **MARKET**: Execute at market price
- **LIMIT**: Execute at specified price or better
- **SL**: Stop loss limit order
- **SL-M**: Stop loss market order

### Exchange Segments

- **NSE**: National Stock Exchange (Equity)
- **BSE**: Bombay Stock Exchange (Equity)
- **NFO**: NSE Futures & Options
- **BFO**: BSE Futures & Options
- **MCX**: Multi Commodity Exchange
- **CDS**: Currency Derivatives

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid API credentials"**
   - Check API_KEY and API_SECRET in .env
   - Verify app is enabled on Kite Connect

2. **"Token is invalid"**
   - Run `python auth.py` to get new token
   - Tokens expire daily

3. **"Order placement failed"**
   - Check margin availability
   - Verify symbol format (e.g., 'INFY' not 'NSE:INFY' for orders)
   - Check market hours

4. **"Import errors"**
   - Run: `pip install -r requirements.txt`
   - Activate virtual environment

5. **WebSocket disconnects**
   - Check internet connection
   - Verify access token is valid
   - Auto-reconnect is enabled by default

## 📈 Next Steps

### Enhancements to Consider

1. **Database Integration**
   - Store historical trades
   - Track strategy performance
   - Maintain audit logs

2. **Advanced Strategies**
   - Moving average crossovers
   - RSI/MACD indicators
   - Options strategies

3. **Risk Management**
   - Daily loss limits
   - Position concentration limits
   - Correlation analysis

4. **Notifications**
   - Email/SMS alerts
   - Telegram bot integration
   - Order execution notifications

5. **Backtesting Framework**
   - Historical data analysis
   - Strategy optimization
   - Performance metrics

6. **Web Dashboard**
   - Flask/Django web interface
   - Real-time charts
   - Trade journal

## 📚 Learning Resources

### Official Documentation

- [Zerodha Varsity](https://zerodha.com/varsity/) - Free trading education
- [Kite Connect Docs](https://kite.trade/docs/connect/v3/)
- [Python SDK Docs](https://kite.trade/docs/pykiteconnect/v4/)

### Community

- [Kite Connect Forum](https://kite.trade/forum/)
- [TradingView](https://www.tradingview.com/)

## 📄 License

MIT License - Use at your own risk. Trading involves financial risk.

## ⚖️ Disclaimer

This software is for educational purposes only. Past performance does not guarantee future results. Always:

- Trade with money you can afford to lose
- Use proper risk management
- Understand the products you trade
- Consult a financial advisor
- Test thoroughly before live trading

---

**Version**: 1.0.0  
**Last Updated**: November 22, 2025  
**Python Version**: 3.8+  
**KiteConnect SDK**: v5.0.0+
