# Project File Structure

```
my-trade-py/
│
├── Core_Modules/              # Core trading modules
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── auth.py                # Authentication & session management
│   ├── trader.py              # Main trading operations
│   ├── websocket_ticker.py    # Real-time data streaming
│   ├── strategies.py          # Trading strategies
│   └── utils.py               # Utility functions
│
├── Application/               # Main applications
│   ├── __init__.py
│   ├── main.py                # Interactive CLI application
│   └── verify_setup.py        # Setup verification script
│
├── Examples/                  # Example scripts
│   ├── __init__.py
│   ├── basic_order.py         # Basic trading examples
│   ├── limit_order.py         # Limit orders with SL
│   └── websocket_stream.py    # WebSocket streaming demo
│
├── Configuration/             # Configuration files
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables (API keys)
│   ├── .env.example           # Environment template
│   └── .gitignore             # Git ignore rules
│
├── Documentation/             # Documentation files
│   ├── README.md              # Main documentation
│   ├── QUICKSTART.md          # Quick start guide
│   └── PROJECT_OVERVIEW.md    # Detailed project overview
│
├── README.md                  # Root README (quick reference)
└── launcher.py                # Main launcher script
```

## Directory Descriptions

### Core_Modules/

Contains all the core trading functionality:

- **config.py**: Loads environment variables and provides configuration constants
- **auth.py**: Handles Zerodha authentication and session management
- **trader.py**: Main trading class with methods for orders, positions, market data
- **websocket_ticker.py**: WebSocket client for real-time market data
- **strategies.py**: Pre-built trading strategies (bracket orders, momentum, etc.)
- **utils.py**: Helper functions (position sizing, portfolio analysis, export)

### Application/

User-facing applications:

- **main.py**: Interactive CLI with menu-driven interface
- **verify_setup.py**: Checks if environment is properly configured

### Examples/

Example scripts demonstrating various features:

- **basic_order.py**: Shows basic market data and order operations
- **limit_order.py**: Demonstrates limit orders with stop loss
- **websocket_stream.py**: Real-time data streaming example

### Configuration/

All configuration and setup files:

- **requirements.txt**: Python package dependencies
- **.env**: Your API credentials (not tracked in git)
- **.env.example**: Template for setting up .env
- **.gitignore**: Files to exclude from version control

### Documentation/

Comprehensive project documentation:

- **README.md**: Full feature documentation
- **QUICKSTART.md**: Step-by-step setup guide
- **PROJECT_OVERVIEW.md**: Architecture and design documentation

## Usage Patterns

### Running Scripts

All scripts should be run from the project root:

```bash
# From project root (my-trade-py/)
python3.9 launcher.py                    # Main launcher
python3.9 Application/verify_setup.py    # Verify setup
python3.9 Application/main.py            # Trading app
python3.9 Examples/basic_order.py        # Run examples
```

### Importing Modules

Examples use path manipulation to import from Core_Modules:

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Core_Modules.trader import KiteTrader
from Core_Modules.config import Config
```

### Configuration

All configuration is centralized in:

- **Core_Modules/config.py**: Code configuration
- **Configuration/.env**: Environment variables (API keys)

## File Counts

- **Python files**: 15 (excluding **init**.py)
- **Documentation files**: 4
- **Configuration files**: 4
- **Total lines of code**: ~2,143 lines

## Key Features by Module

### config.py (42 lines)

- API credential loading
- Trading parameter defaults
- Risk management settings
- Configuration validation

### auth.py (163 lines)

- OAuth2 login flow
- Session generation
- Access token persistence
- Profile retrieval

### trader.py (400+ lines)

- Market data retrieval
- Order placement/modification/cancellation
- Position and holdings management
- Margin queries
- Helper methods for common operations

### websocket_ticker.py (150+ lines)

- WebSocket connection management
- Real-time tick streaming
- Subscription management
- Event callbacks

### strategies.py (250+ lines)

- Bracket order implementation
- Momentum strategy
- Trailing stop loss
- Position management

### utils.py (250+ lines)

- Instrument search
- Gainers/losers analysis
- Position size calculation
- Portfolio summary
- CSV export functions

## Notes

1. **Python Version**: Use Python 3.9 (packages installed there)
2. **Working Directory**: Always run from project root
3. **Imports**: Core modules use relative imports within the package
4. **Applications**: Use sys.path manipulation to import Core_Modules
5. **Configuration**: All paths are relative to project structure
