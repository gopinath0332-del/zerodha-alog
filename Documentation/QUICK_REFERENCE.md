# Quick Reference - Zerodha Kite Trading Bot

## 🚀 Getting Started (First Time)

### Step 1: Install Dependencies

```bash
pip3.9 install -r Configuration/requirements.txt
```

### Step 2: Configure Credentials

Edit `Configuration/.env`:

```
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

### Step 3: Run Setup Verification

```bash
python3.9 Application/verify_setup.py
```

### Step 4: Authenticate

```bash
python3.9 Application/authenticate.py
```

### Step 5: Start Trading

```bash
python3.9 Application/main.py
```

## 📋 Daily Workflow

### Morning Setup (Access tokens expire daily)

```bash
# Easy way - Use launcher
python3.9 launcher.py
# Then choose option 2 (Authenticate)

# Or direct
python3.9 Application/authenticate.py
```

### Start Trading

```bash
# Easy way
python3.9 launcher.py
# Then choose option 3 (Trading Application)

# Or direct
python3.9 Application/main.py
```

## 🔧 Common Commands

### Using the Launcher (Recommended)

```bash
python3.9 launcher.py
# or
./run.sh
```

Menu options:

1. **Verify Setup** - Check if everything is configured
2. **Authenticate** - Login and get access token
3. **Start Trading** - Main application
4. **Basic Examples** - Learn basic operations
5. **Limit Orders** - Learn limit orders with SL
6. **WebSocket** - Real-time data streaming
7. **Exit**

### Direct Commands

**Verify Setup**

```bash
python3.9 Application/verify_setup.py
```

**Authenticate**

```bash
python3.9 Application/authenticate.py
```

**Trading Application**

```bash
python3.9 Application/main.py
```

**Examples**

```bash
python3.9 Examples/basic_order.py      # Basic operations
python3.9 Examples/limit_order.py      # Limit orders
python3.9 Examples/websocket_stream.py # Live streaming
```

## 🐍 Python Scripts

### Get Market Data

```python
from Core_Modules.trader import KiteTrader

trader = KiteTrader()
quote = trader.get_quote('NSE:INFY', 'NSE:TCS')
ltp = trader.get_ltp('NSE:RELIANCE')
```

### Place Market Order (Example - Commented for Safety)

```python
from Core_Modules.trader import KiteTrader

trader = KiteTrader()
# order_id = trader.buy_market('INFY', quantity=1, exchange='NSE', product='CNC')
```

### Check Portfolio

```python
from Core_Modules.trader import KiteTrader

trader = KiteTrader()
positions = trader.get_positions()
holdings = trader.get_holdings()
margins = trader.get_margins('equity')
```

### Real-time Streaming

```python
from Core_Modules.websocket_ticker import KiteWebSocket

def on_ticks(ws, ticks):
    for tick in ticks:
        print(f"{tick['instrument_token']}: ₹{tick['last_price']}")

kws = KiteWebSocket(on_ticks_callback=on_ticks)
kws.subscribe([738561])  # SBIN
kws.connect()
```

## 📁 File Locations

### Configuration

- **API Credentials**: `Configuration/.env`
- **Dependencies**: `Configuration/requirements.txt`

### Core Modules

- **Authentication**: `Core_Modules/auth.py`
- **Trading**: `Core_Modules/trader.py`
- **WebSocket**: `Core_Modules/websocket_ticker.py`
- **Strategies**: `Core_Modules/strategies.py`
- **Utilities**: `Core_Modules/utils.py`

### Applications

- **Main App**: `Application/main.py`
- **Authentication**: `Application/authenticate.py`
- **Verification**: `Application/verify_setup.py`

### Documentation

- **Main Docs**: `Documentation/README.md`
- **Quick Start**: `Documentation/QUICKSTART.md`
- **Architecture**: `Documentation/PROJECT_OVERVIEW.md`

## 🔑 Important Constants

### Exchanges

- `NSE` - National Stock Exchange
- `BSE` - Bombay Stock Exchange
- `NFO` - NSE Futures & Options
- `MCX` - Multi Commodity Exchange

### Products

- `CNC` - Cash & Carry (Delivery)
- `MIS` - Margin Intraday Square-off
- `NRML` - Normal (F&O)

### Order Types

- `MARKET` - Market order
- `LIMIT` - Limit order
- `SL` - Stop Loss Limit
- `SL-M` - Stop Loss Market

## ⚠️ Safety Reminders

1. **Access Tokens Expire Daily** - Re-authenticate every day
2. **Test First** - All order examples are commented out
3. **Small Quantities** - Start small, scale gradually
4. **Use Stop Losses** - Always protect your capital
5. **Paper Trade** - Test strategies before live trading
6. **Review Code** - Understand what you're running

## 🆘 Troubleshooting

### "Module not found" Error

```bash
# Make sure you're using python3.9
python3.9 --version

# Reinstall packages
pip3.9 install -r Configuration/requirements.txt
```

### "Invalid access token" Error

```bash
# Access tokens expire daily
python3.9 Application/authenticate.py
```

### "API credentials not found" Error

```bash
# Edit Configuration/.env with your credentials
nano Configuration/.env
```

### Import Errors

```bash
# Always run from project root
cd /path/to/my-trade-py
python3.9 Application/main.py
```

## 📞 Support

- **KiteConnect Docs**: <https://kite.trade/docs/pykiteconnect/v4/>
- **API Reference**: <https://kite.trade/docs/connect/v3/>
- **GitHub Issues**: <https://github.com/zerodha/pykiteconnect/issues>

## 💡 Tips

1. **Use the Launcher** - Easiest way: `python3.9 launcher.py`
2. **Check Verification** - Run verify_setup.py before trading
3. **Morning Routine** - Authenticate → Trade → Monitor
4. **Keep Learning** - Read Documentation/ folder
5. **Stay Safe** - Risk management is key

---

**Quick Start**: `python3.9 launcher.py` or `./run.sh`
