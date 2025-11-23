# Donchian Channel Strategy Implementation Guide

## Overview

The Donchian Channel Strategy has been integrated into the Modern Trading Terminal alongside the RSI monitoring system. It provides automated detection of trend reversals and price breakouts using the Donchian Channel technical indicator.

## What are Donchian Channels?

Donchian Channels consist of three lines plotted on a price chart:

- **Upper Band**: The highest price a security reached over a specific lookback period (default: 20 periods)
- **Lower Band**: The lowest price a security reached over a specific lookback period (default: 10 periods)  
- **Middle Band**: The average of the upper and lower bands

The strategy identifies trading opportunities when the price breaks beyond these bands, signaling potential trend reversals or continuation.

## Configuration

### Default Settings for GOLDPETAL

- **Symbol**: GOLDPETAL
- **Time Interval**: 1 hour
- **Upper Band Period**: 20 (highest high over last 20 candles)
- **Lower Band Period**: 10 (lowest low over last 10 candles)

### User Interface

In the **Donchian** tab, you can:

1. **Set Symbol**: Enter the commodity symbol (e.g., `GOLDPETAL`)
2. **Upper Band Period**: Number of periods to calculate highest high (default: 20)
3. **Lower Band Period**: Number of periods to calculate lowest low (default: 10)
4. **Interval**: Choose analysis interval (currently 1hour)

## How It Works

### Real-Time Analysis

1. **Market Hour Boundary**: The monitor checks at the start of each new hour
   - First analysis runs immediately when you click "Launch Donchian Monitor"
   - Subsequent checks occur at hourly boundaries (9:00, 10:00, 11:00, etc.)

2. **Data Calculation**:
   - Fetches 30 days of historical hourly data
   - Calculates upper band = highest high over last N periods
   - Calculates lower band = lowest low over last M periods

3. **Alert Conditions**:
   - **BULLISH BREAKOUT**: Current price > Upper Band → Green alert
   - **BEARISH BREAKDOWN**: Current price < Lower Band → Red alert
   - **Normal Range**: Price between bands → No alert

### Display Information

The tab shows in real-time:

- **Current Price**: Latest closing price
- **Upper Band**: Upper resistance level
- **Lower Band**: Lower support level
- **Last Alert**: Most recent breakout/breakdown event
- **Status**: Monitor status and last check time

## Alert Notifications

### Discord Integration

All alerts are sent to your Discord webhook with:

- **Bullish Breakout** (Green): When price exceeds upper band
- **Bearish Breakdown** (Red): When price falls below lower band
- **Start/Stop** (Blue/Gray): Monitor lifecycle events

### Sound Alerts

Each breakout/breakdown triggers an audio alert to grab your attention immediately.

## Technical Implementation

### Monitoring Pattern (Same as RSI)

```
Launch Monitor
    ↓
Immediate Analysis
    ↓
Wait for Next Hour Boundary
    ↓
Repeat Analysis
    ↓
(until stopped)
```

### Market Hours

The monitor uses **hourly boundaries** (9:00 AM, 10:00 AM, etc.) for check intervals, ensuring analysis aligns with trading hour sessions.

### Thread Architecture

- Monitoring runs in a background daemon thread
- UI remains responsive during analysis
- Can launch/stop monitors without blocking
- Multiple monitors can run simultaneously (RSI + Donchian)

## Usage Example

1. Open the **Donchian** tab in the Trading Terminal
2. (Optional) Adjust band periods if desired:
   - Shorter periods = More sensitive, more alerts
   - Longer periods = Fewer alerts, better trend confirmation
3. Click **"Launch Donchian Monitor"**
4. Watch for alerts:
   - Green: Uptrend breakout (consider BUY)
   - Red: Downtrend breakdown (consider SELL)
5. Click **"Stop Monitor"** to end monitoring

## Customization

### Changing Band Periods

- **Aggressive Trading**: Upper=10, Lower=5 (more breakouts)
- **Conservative Trading**: Upper=30, Lower=20 (fewer false signals)
- **Trend Following**: Upper=50, Lower=50 (long-term trends)

### Multiple Symbols

The current implementation monitors one symbol at a time. To monitor multiple symbols:

1. Stop the current monitor
2. Change the symbol
3. Launch a new monitor

## Integration with RSI

Both RSI and Donchian monitors:

- Use the same market hour boundary logic
- Send alerts to the same Discord webhook
- Can run simultaneously for multi-indicator confirmation
- Provide real-time status updates in the UI

## Troubleshooting

### "Instrument token not found"

- Verify the symbol is correct (e.g., `GOLDPETAL`)
- Ensure the symbol exists on MCX/NCDEX exchanges

### "Not enough candles"

- The symbol has less than the required historical data
- Try reducing the band periods temporarily
- Wait for more data to accumulate

### No alerts despite breakouts

- Check if Discord webhook URL is valid
- Verify monitor is running (not paused)
- Ensure price actually crossed the band (not just touched)

## Data Source

All historical data is fetched from Zerodha's KiteConnect API:

- **Exchange**: MCX (metals/energy) or NSE (stocks)
- **Resolution**: Hourly candles
- **Lookback**: 30 days
- **Data Points Required**: Minimum (upper_period or lower_period)

## Performance Notes

- Each analysis requires one API call
- Runs every hour = ~8 API calls per trading session
- No impact on system performance (background thread)
- Recommended to run alongside other monitors

---

**Created**: 2025-11-23  
**Strategy Type**: Trend Reversal / Breakout Detection  
**Analysis Interval**: 1 Hour  
**Default Symbol**: GOLDPETAL
