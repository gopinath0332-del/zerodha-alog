# Automated Authentication Setup

The application supports automated token capture, eliminating the need to manually copy-paste request tokens.

## Setup Instructions

### 1. Configure Redirect URL in Kite Connect App

1. Go to [Kite Connect Developers Portal](https://developers.kite.trade/apps)
2. Click on your app
3. In the **Redirect URL** field, enter:

   ```
   http://127.0.0.1:8888
   ```

4. Save the changes

### 2. Update Your .env File

Edit `Configuration/.env` and add/update:

```bash
REDIRECT_URL=http://127.0.0.1:8888
```

### 3. Using Automated Authentication

1. Run the authentication script:

   ```bash
   python Application/authenticate.py
   ```

2. The script will:

   - Start a local callback server
   - Print the login URL (and try to open it)
   - Wait for the callback

3. Login in your browser.
4. Once redirected to localhost, the script will capture the token automatically.

## Manual Fallback

If automated authentication fails:

1. Use the **Manual Mode** section in the auth dialog
2. Copy the request token from the browser URL
3. Paste it in the "Request Token" field
4. Click "Authenticate Manually"

## Troubleshooting

### Port 8888 Already in Use

If you get a port conflict error, you can either:

- Stop the process using port 8888
- Or change the port in the GUI code and update your Kite app redirect URL accordingly

### Browser Doesn't Redirect

Make sure:

- The redirect URL in your Kite Connect app matches exactly: `http://127.0.0.1:8888`
- No trailing slashes or extra paths
- Port 8888 is accessible

### Token Not Captured

- Check if your browser is blocking the redirect
- Try the manual mode as fallback
- Ensure the callback server started successfully (check status messages)

## Security Note

The callback server runs locally on your machine (`127.0.0.1`) and is only accessible from your computer. It automatically shuts down after capturing one token or after 2 minutes of inactivity.
