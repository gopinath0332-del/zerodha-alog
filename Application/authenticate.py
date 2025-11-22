#!/usr/bin/env python3.9
"""
Authentication script for Zerodha Kite Connect
Run this for first-time or daily authentication
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Core_Modules.auth import KiteAuth

def main():
    """Main authentication function"""
    print("\n" + "="*60)
    print("  ZERODHA KITE CONNECT - AUTHENTICATION")
    print("="*60)
    
    try:
        auth = KiteAuth()
        
        # Check if already authenticated
        if auth.access_token:
            print("\n✓ Access token already exists")
            try:
                profile = auth.get_profile()
                print(f"✓ Connected as: {profile.get('user_name')} ({profile.get('email')})")
                
                choice = input("\nDo you want to re-authenticate? (yes/no): ").strip().lower()
                if choice != 'yes':
                    print("Using existing access token.")
                    return
            except Exception as e:
                print(f"⚠ Existing token is invalid: {e}")
                print("Re-authentication required.\n")
        
        # Start authentication flow
        print("\n=== Step 1: Opening Login Page ===")
        print("Browser will open with Zerodha login page...")
        auth.open_login_page()
        
        print("\n=== Step 2: Login and Authorize ===")
        print("1. Login with your Zerodha credentials")
        print("2. Authorize the app")
        print("3. You will be redirected to a URL like:")
        print("   http://127.0.0.1:5000/callback?request_token=XXXXXXXX&action=login&status=success")
        
        print("\n=== Step 3: Enter Request Token ===")
        request_token = input("Paste the request_token from the URL: ").strip()
        
        if not request_token:
            print("\n✗ No request token provided. Exiting.")
            return
        
        # Generate session
        print("\n=== Step 4: Generating Session ===")
        data = auth.generate_session(request_token)
        
        print("\n" + "="*60)
        print("  ✓ AUTHENTICATION SUCCESSFUL!")
        print("="*60)
        print(f"\nUser ID: {data.get('user_id')}")
        print(f"User Name: {data.get('user_name')}")
        print(f"Email: {data.get('email')}")
        print(f"\nAccess token saved to: Configuration/.env")
        print("\nYou can now use the trading application!")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print("  ✗ AUTHENTICATION FAILED")
        print("="*60)
        print(f"\nError: {e}")
        print("\nPlease try again or check your credentials.")
        print("="*60)
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAuthentication cancelled.")
        sys.exit(1)
