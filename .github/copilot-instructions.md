# Copilot Instructions for my-trade-py

## Project Overview
Automated trading system for Zerodha's KiteConnect API. Architecture follows a separation between core trading logic (`Core_Modules/`), user-facing applications (`Application/`), and learning examples (`Examples/`).

## Critical Architecture Patterns

### Authentication Flow
- **Daily token refresh required**: Zerodha access tokens expire every 24 hours
- Authentication is 2-step OAuth2: `auth.open_login_page()` → user authorizes → `auth.generate_session(request_token)`
- Access tokens saved to `Configuration/.env` automatically by `auth._save_access_token()`
- Always use `KiteAuth` class, never instantiate `KiteConnect` directly

### Module Import Pattern
All scripts use path manipulation to import `Core_Modules`:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from Core_Modules.trader import KiteTrader
```
This enables running scripts from project root while maintaining package structure.

### Trader Initialization
`KiteTrader()` automatically initializes authenticated session via `KiteAuth`:
```python
trader = KiteTrader()  # Auth handled internally, no parameters needed
```

### Safety-First Order Placement
ALL order placement code must be commented out by default. Pattern:
```python
# UNCOMMENT ONLY WHEN READY TO PLACE ACTUAL ORDERS
"""
order_id = trader.buy_market('INFY', quantity=1, exchange='NSE', product='CNC')
"""
```

## Key Components

### Core_Modules/ (Never modify trader.py lightly)
- `config.py`: Single source of truth for API credentials via `.env`, defaults for exchange/product/order_type
- `auth.py`: OAuth2 flow, session persistence, profile retrieval
- `trader.py`: Thin wrapper over KiteConnect SDK with convenience methods (`buy_market`, `sell_limit`, etc.)
- `websocket_ticker.py`: Real-time streaming with callback architecture
- `strategies.py`: Pre-built strategies (bracket orders, momentum, trailing SL, **Heikin Ashi conversion**)
- `utils.py`: Pure functions for position sizing, CSV export, portfolio summaries

### Application/ (User interfaces)
- `gui_modern.py`: DearPyGui trading terminal (GPU-accelerated, recommended)
    - **Commodity tabs (NatgasMini RSI, GOLDPETAL Donchian) with Heikin Ashi candle support**
    - **Radio buttons for candle type selection (default: Heikin Ashi)**
- `gui.py`: Legacy tkinter GUI
- `main.py`: Interactive CLI with menu-driven workflow
- `authenticate.py`: Standalone auth script for daily login

### Examples/ (Learning resources)
Demonstrate patterns without live trading risk - always have orders commented out.

## Development Workflows

### First-Time Setup
```bash
pip3.9 install -r Configuration/requirements.txt
# Edit Configuration/.env with API_KEY and API_SECRET
python3.9 Application/verify_setup.py
python3.9 Application/authenticate.py
```

### Daily Trading Workflow
1. Authenticate (tokens expire): `python3.9 Application/authenticate.py`
2. Launch GUI: `./run_gui_modern.sh` OR CLI: `python3.9 Application/main.py`

### Running Code
- **Always** run from project root: `python3.9 Application/main.py`
- **Never** use `python` - use `python3.9` explicitly (dependency installations are Python 3.9-specific)
- Launcher provides unified entry: `python3.9 launcher.py`

### Testing Changes
Use `Examples/basic_order.py` to test functionality - it fetches quotes/positions without placing orders.

## Project-Specific Conventions

### Exchange and Product Types
- **NSE/BSE**: Stock exchanges - use `exchange='NSE'` default
- **CNC**: Cash & Carry (delivery) - default for holdings
- **MIS**: Margin Intraday Square-off - for day trading
- Always specify product type explicitly: `trader.buy_market(..., product='CNC')`

### Order Placement Helpers
Prefer convenience methods over raw `place_order()`:
```python
trader.buy_market(symbol, quantity, exchange='NSE', product='CNC')  # ✓ Use this
trader.place_order(symbol, 'NSE', 'BUY', quantity, ...)  # ✗ Avoid unless needed
```

### Error Handling
All trading operations raise exceptions on failure - wrap in try/except:
```python
try:
    order_id = trader.buy_market('INFY', 1)
except Exception as e:
    logger.error(f"Order failed: {e}")
```

### Data Access Patterns
- **Positions**: `trader.get_positions()` returns `{'day': [...], 'net': [...]}`
- **Holdings**: `trader.get_holdings()` returns list
- **Margins**: `trader.get_margins('equity')` for equity segment
- Cache instruments list - fetching all instruments is expensive

## Dependencies & External Integrations

### KiteConnect SDK
Wrapped by `trader.py` - access raw SDK via `trader.kite` for advanced features not exposed by helpers.

### WebSocket Streaming
- Instrument tokens (not symbols) required for subscriptions
- Modes: `MODE_LTP`, `MODE_QUOTE`, `MODE_FULL`
- Auto-resubscribes on reconnect via `on_connect` callback

### DearPyGui (gui_modern.py)
- GPU-accelerated, requires OpenGL
- Uses callback architecture with `dpg.add_*` widgets
- Theme defined in `setup_theme()` - modify for visual changes
- **Commodity tabs (NatgasMini RSI, GOLDPETAL Donchian) with Heikin Ashi candle support**
- **Radio buttons for candle type selection (default: Heikin Ashi)**

### CSV Export
Utils provide `export_positions_to_csv()` and `export_holdings_to_csv()` - saved to project root by default.

## Common Pitfalls

1. **Running without authentication**: Always check `Config.ACCESS_TOKEN` exists or run `authenticate.py` first
2. **Hardcoding instrument tokens**: Use `search_instruments()` from utils.py to find tokens dynamically
3. **Not specifying exchange**: NSE vs BSE matters - `'INFY'` exists on both, specify `'NSE:INFY'`
4. **Forgetting product type**: MIS requires intraday square-off, CNC doesn't - wrong choice = order rejection
5. **Modifying trader.py unnecessarily**: It's a stable wrapper - extend with new methods, don't refactor internals

## Branch-Specific Features

### RSI & Donchian Monitoring (feature/rsi branch)
The modern GUI (`gui_modern.py`) includes:
- **RSI strategy monitoring with Heikin Ashi candle support**
- **Donchian Channel monitoring with Heikin Ashi candle support**
- Real-time calculation, Discord webhook alerts
- Candle type selection via radio buttons (default: Heikin Ashi)
- Launch via dedicated commodity tabs

## Directory Structure Note
- `Core Modules/` (with space) exists alongside `Core_Modules/` (underscore)
- Only `Core_Modules/` is actively used - contains working code
- Always import from `Core_Modules` (underscore version)

## GUI Architecture (gui_modern.py)

### DearPyGui Patterns
- Tag-based widget system: `tag="rsi_current_value"` for later updates via `dpg.set_value("rsi_current_value", new_val)`
- Threading for background tasks: OAuth callback server, RSI/Donchian monitoring loops
- Callback handlers specified via `callback=self.method_name` in widget creation
- Theme configured in `setup_theme()` with dark terminal aesthetics
- **Radio buttons for candle type selection (default: Heikin Ashi)**

### Commodity Tabs
- NatgasMini RSI and GOLDPETAL Donchian tabs
- Candle type selection (Heikin Ashi or Normal)
- Discord alerts for strategy signals

### OAuth Callback Server
- Embedded HTTP server (`CallbackHandler`) captures OAuth redirects on port 5000
- Request token stored in global `_request_token_holder` dict (shared between threads)
- Server runs in background thread, auto-stops after token capture
- Success/error HTML responses sent to browser

### Data Caching
- Instruments list cached in `self.instruments_cache` with timestamp in `self.instruments_cache_time`
- Avoid re-fetching instruments list on every search - expensive API call
- Cache invalidation strategy: check timestamp, refresh if stale

## External Integrations

### Discord Webhooks
- GUI sends trading alerts to Discord via webhook POST requests
- Webhook URL hardcoded in `gui_modern.py` - **SECURITY ISSUE**: move to `.env`
- Alert format: JSON with embeds (title, description, color, timestamp)
- Used for RSI/Donchian threshold breach notifications

### HTTP Callback Server
- Local server on `http://127.0.0.1:5000/callback` for OAuth redirects
- Single-purpose: capture `request_token` from query params
- Automatically started/stopped by authentication flow
- Don't bind to external interfaces - localhost only for security

## Testing Strategy

No formal test suite exists. Manual testing via:
- `Application/verify_setup.py` - validates environment
- `Examples/basic_order.py` - read-only operations (quotes, positions)
- `Examples/websocket_stream.py` - WebSocket connectivity
- Always test on paper/small quantities before scaling

## Documentation Locations

- **Quick Start**: `Documentation/QUICKSTART.md` - setup guide
- **Full Docs**: `Documentation/README.md` - comprehensive feature docs
- **Architecture**: `Documentation/PROJECT_OVERVIEW.md` - design decisions
- **File Structure**: `STRUCTURE.md` - directory breakdown

When adding features, update relevant docs and add commented examples to `Examples/`.

## Security & Configuration

### Sensitive Data in .env
Never commit to git (already in `.gitignore`):
- `API_KEY`, `API_SECRET`: Zerodha API credentials
- `ACCESS_TOKEN`: Daily session token
- **TODO**: Move Discord webhook URL to `.env` (currently hardcoded in GUI)

### CSV Export Files
- Generated by utils functions: `positions.csv`, `holdings.csv`
- Saved to project root by default (gitignored via `*.csv`)
- Location customizable via `filename` parameter

### Logging
- Standard Python `logging` module used throughout
- Level set to `INFO` by default, `DEBUG` in `websocket_ticker.py`
- No centralized log configuration - each module configures independently
- Value color set to white, spacing added
- Consider unified logging config for production use
