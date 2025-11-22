"""
Configuration module for Zerodha Kite Connect trading bot
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file in Configuration directory
config_dir = os.path.join(os.path.dirname(__file__), '..', 'Configuration')
env_path = os.path.join(config_dir, '.env')
load_dotenv(env_path)


class Config:
    """Configuration class for KiteConnect API"""
    
    # API Credentials
    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    REDIRECT_URL = os.getenv('REDIRECT_URL', 'http://127.0.0.1:5000/callback')
    
    # Trading parameters
    DEFAULT_EXCHANGE = 'NSE'
    DEFAULT_PRODUCT = 'CNC'  # CNC for delivery, MIS for intraday
    DEFAULT_ORDER_TYPE = 'MARKET'  # MARKET or LIMIT
    DEFAULT_VALIDITY = 'DAY'
    
    # Risk management
    MAX_ORDER_VALUE = 100000  # Maximum order value in INR
    MAX_POSITION_SIZE = 10  # Maximum number of positions
    STOP_LOSS_PERCENTAGE = 2.0  # Default stop loss percentage
    TARGET_PERCENTAGE = 5.0  # Default target percentage
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.API_KEY:
            raise ValueError("API_KEY not found in environment variables")
        if not cls.API_SECRET:
            raise ValueError("API_SECRET not found in environment variables")
        return True
