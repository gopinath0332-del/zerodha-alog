# Quick Start Guide

## Step 1: Get Kite Connect API Credentials

1. Go to <https://developers.kite.trade/>
2. Login with your Zerodha credentials
3. Click on "Create new app"
4. Fill in the details:
   - App name: My Trading Bot
   - Redirect URL: `http://127.0.0.1:5000/callback`
   - Description: Automated trading bot
5. Note down your **API Key** and **API Secret**

## Step 2: Configure Your Credentials

Edit the `.env` file and add your credentials:

```bash
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
REDIRECT_URL=http://127.0.0.1:5000/callback
```

## Step 3: First Time Authentication

Run the authentication script:

```bash
python Application/authenticate.py
```

This will:

1. Open Kite login page in your browser
2. Ask you to login and authorize your app
3. Redirect you to a URL like: `http://127.0.0.1:5000/callback?request_token=XXXXXXXX&action=login&status=success`
4. Copy the `request_token` from the URL
5. Paste it in the terminal when prompted
6. Your `access_token` will be saved to `.env`

## Step 4: Test Your Setup

Run the interactive application:

```bash
./run.sh
```

Or manually:

```bash
python Application/main_enhanced.py
```

Choose option 1 to view market data for some stocks (e.g., NSE:INFY, NSE:TCS)

## Step 5: Explore Examples

### Basic Market Data

```bash
python examples/basic_order.py
```

### WebSocket Streaming

```bash
python examples/websocket_stream.py
```

## Daily Workflow

Since access tokens expire daily, you'll need to:

1. Run `python auth.py` each day to get a new access token
2. Or implement automatic token refresh in your code

## Common Issues

### Issue: "Invalid API credentials"

- Double-check your API_KEY and API_SECRET in `.env`
- Make sure there are no extra spaces

### Issue: "Access token is invalid"

- Access tokens expire daily
- Run `python auth.py` again to get a new token

### Issue: "Import Error: No module named kiteconnect"

- Make sure you've installed dependencies: `pip install -r requirements.txt`

### Issue: "Session generation failed"

- Make sure the redirect URL in your Kite app settings matches the one in `.env`
- The request_token is only valid for a few minutes, be quick!

## Safety Tips

⚠️ **Before placing real orders:**

1. Test with small quantities first
2. Always set stop losses
3. Monitor your positions regularly
4. Understand the order types (MARKET, LIMIT, SL, SL-M)
5. Know the difference between:
   - CNC: Delivery (held for multiple days)
   - MIS: Intraday (must be squared off same day)
   - NRML: Normal (for F&O)

## Next Steps

1. Read the full documentation at: <https://kite.trade/docs/pykiteconnect/v4/>
2. Explore the KiteConnect API reference
3. Build your own trading strategies
4. Implement proper risk management
5. Keep learning and stay safe!

Happy Trading! 🚀
