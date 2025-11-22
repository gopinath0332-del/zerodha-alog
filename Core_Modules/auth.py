"""
Authentication module for Zerodha Kite Connect
Handles login flow and session generation
"""
from kiteconnect import KiteConnect
from .config import Config
import webbrowser
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KiteAuth:
    """Handles authentication for Kite Connect API"""
    
    def __init__(self):
        """Initialize KiteConnect with API key"""
        Config.validate()
        self.kite = KiteConnect(api_key=Config.API_KEY)
        self.access_token = Config.ACCESS_TOKEN
        
        if self.access_token:
            self.kite.set_access_token(self.access_token)
    
    def get_login_url(self):
        """
        Get the login URL for manual authentication
        
        Returns:
            str: Login URL
        """
        login_url = self.kite.login_url()
        logger.info(f"Login URL: {login_url}")
        return login_url
    
    def open_login_page(self):
        """Open login page in browser"""
        login_url = self.get_login_url()
        webbrowser.open(login_url)
        logger.info("Login page opened in browser")
        return login_url
    
    def generate_session(self, request_token):
        """
        Generate session using request token
        
        Args:
            request_token (str): Request token received after login
            
        Returns:
            dict: Session data containing access_token
        """
        try:
            data = self.kite.generate_session(request_token, api_secret=Config.API_SECRET)
            self.access_token = data['access_token']
            self.kite.set_access_token(self.access_token)
            
            logger.info("Session generated successfully")
            logger.info(f"Access Token: {self.access_token}")
            logger.info(f"User ID: {data.get('user_id')}")
            logger.info(f"User Name: {data.get('user_name')}")
            
            # Save access token to .env file
            self._save_access_token(self.access_token)
            
            return data
        except Exception as e:
            logger.error(f"Session generation failed: {e}")
            raise
    
    def _save_access_token(self, access_token):
        """
        Save access token to .env file
        
        Args:
            access_token (str): Access token to save
        """
        try:
            config_dir = os.path.join(os.path.dirname(__file__), '..', 'Configuration')
            env_file = os.path.join(config_dir, '.env')
            
            # Read existing content
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Update or add ACCESS_TOKEN
            token_found = False
            for i, line in enumerate(lines):
                if line.startswith('ACCESS_TOKEN='):
                    lines[i] = f'ACCESS_TOKEN={access_token}\n'
                    token_found = True
                    break
            
            if not token_found:
                lines.append(f'ACCESS_TOKEN={access_token}\n')
            
            # Write back to file
            with open(env_file, 'w') as f:
                f.writelines(lines)
            
            logger.info("Access token saved to .env file")
        except Exception as e:
            logger.warning(f"Could not save access token to .env: {e}")
    
    def get_kite_instance(self):
        """
        Get authenticated KiteConnect instance
        
        Returns:
            KiteConnect: Authenticated KiteConnect instance
        """
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")
        return self.kite
    
    def get_profile(self):
        """
        Get user profile
        
        Returns:
            dict: User profile data
        """
        try:
            profile = self.kite.profile()
            logger.info(f"Profile: {profile}")
            return profile
        except Exception as e:
            logger.error(f"Failed to fetch profile: {e}")
            raise


if __name__ == "__main__":
    # Example usage for manual authentication
    auth = KiteAuth()
    
    # If no access token, perform login flow
    if not auth.access_token:
        print("\n=== Zerodha Kite Connect Authentication ===")
        print("\n1. Opening login page in browser...")
        auth.open_login_page()
        
        print("\n2. After successful login, you will be redirected to the callback URL")
        print("   Copy the 'request_token' from the URL")
        print("   Example: http://127.0.0.1:5000/callback?request_token=XXXXXXXX&action=login&status=success")
        
        request_token = input("\n3. Enter the request_token: ").strip()
        
        if request_token:
            data = auth.generate_session(request_token)
            print(f"\n✓ Authentication successful!")
            print(f"  Access Token: {data['access_token']}")
            print(f"  User ID: {data.get('user_id')}")
        else:
            print("No request token provided. Exiting.")
    else:
        print("Access token already available. Testing connection...")
        profile = auth.get_profile()
        print(f"✓ Connected as: {profile.get('user_name')} ({profile.get('email')})")
