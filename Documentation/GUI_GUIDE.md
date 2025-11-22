# Trading Bot GUI Application

## Quick Start

Launch the GUI application:

```bash
./run_gui.sh
```

Or directly with Python:

```bash
python3.9 Application/gui.py
```

## Features

The GUI provides a complete graphical interface for all trading operations:

### 📊 Portfolio Management

- **Portfolio Summary**: View complete portfolio with margins, P&L, and returns
- **Positions**: Monitor current day positions with live P&L
- **Holdings**: Track long-term holdings and investments
- **Orders**: View order history and status

### 📈 Trading Operations

- **Place Order**: User-friendly form for market and limit orders
- **Bracket Order**: Create bracket orders with automatic SL and target
- **Market Data**: Get real-time quotes for multiple symbols

### 📉 Analysis Tools

- **Top Gainers/Losers**: Identify best and worst performing positions
- **Position Sizing Calculator**: Calculate optimal position size based on risk

### 💾 Data Management

- **Export Portfolio**: Save portfolio data to CSV files
- **Refresh**: Update current view with latest data

## Interface Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Status: Authenticated ✓                                      │
├──────────────┬──────────────────────────────────────────────┤
│              │                                               │
│  📊 Menu     │         Content Area                          │
│              │                                               │
│  - Portfolio │  • Portfolio summary                          │
│  - Positions │  • Live data displays                         │
│  - Holdings  │  • Interactive forms                          │
│  - Orders    │  • Real-time updates                          │
│  - Place     │                                               │
│  - Market    │                                               │
│  - Bracket   │                                               │
│  - Gainers   │                                               │
│  - Calculator│                                               │
│  - Export    │                                               │
│  - Refresh   │                                               │
│              │                                               │
└──────────────┴──────────────────────────────────────────────┘
```

## Requirements

The GUI uses Python's built-in `tkinter` library, which is included with Python on macOS.

All other dependencies are in `Configuration/requirements.txt`:

- kiteconnect
- python-dotenv
- pandas
- requests

## Authentication

The GUI will automatically attempt to authenticate when launched. If authentication fails:

1. Run the authentication script first:

   ```bash
   python3.9 Application/authenticate.py
   ```

2. Or use the **Re-authenticate** button in the GUI

## Window Features

### Main Window

- **Status Bar**: Shows authentication status
- **Menu Sidebar**: Quick access to all features
- **Content Area**: Dynamic display area for data and forms

### Pop-up Windows

- **Place Order**: Complete order entry form
- **Bracket Order**: Advanced order with SL/Target
- **Market Data**: Multi-symbol quote viewer
- **Position Calculator**: Risk management tool

## Usage Tips

1. **Threading**: Data fetching runs in background threads, keeping the UI responsive
2. **Refresh**: Use the refresh button to update the current view
3. **Real-time**: All data is fetched live from Zerodha
4. **Error Handling**: Clear error messages with helpful context

## Keyboard Shortcuts

The GUI currently uses mouse navigation. Future enhancements may include:

- Alt+P: Portfolio
- Alt+O: Orders
- Alt+R: Refresh
- Ctrl+Q: Quit

## Troubleshooting

### GUI doesn't launch

```bash
# Check if tkinter is installed
python3.9 -m tkinter
```

### Authentication fails

Run the standalone authentication script:

```bash
python3.9 Application/authenticate.py
```

### Data not loading

- Check internet connection
- Verify authentication status
- Check if markets are open

## Technical Details

- **Framework**: tkinter (Python's standard GUI library)
- **Threading**: Background threads for API calls
- **Updates**: Manual refresh (auto-refresh can be added)
- **Platform**: Tested on macOS (works on Linux/Windows too)

## Future Enhancements

Potential features for future versions:

- Auto-refresh with configurable intervals
- Charts and graphs using matplotlib
- Watchlist management
- Strategy backtesting interface
- Live WebSocket streaming
- Multiple workspaces/tabs
- Keyboard shortcuts
- Dark/light themes
- Custom layouts
