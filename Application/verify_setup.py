"""
Setup verification script
Run this to check if your environment is configured correctly
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def check_environment():
    """Check if all required packages are installed"""
    print("\n" + "="*60)
    print("  ZERODHA KITE CONNECT - SETUP VERIFICATION")
    print("="*60)
    
    # Check Python version
    print("\n1. Checking Python version...")
    if sys.version_info >= (3, 8):
        print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    else:
        print(f"   ✗ Python {sys.version_info.major}.{sys.version_info.minor} (Requires 3.8+)")
        return False
    
    # Check required packages
    print("\n2. Checking required packages...")
    required_packages = {
        'kiteconnect': 'KiteConnect SDK',
        'dotenv': 'Environment variables',
        'pandas': 'Data analysis',
        'requests': 'HTTP requests'
    }
    
    all_installed = True
    for package, description in required_packages.items():
        try:
            if package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"   ✓ {description} ({package})")
        except ImportError:
            print(f"   ✗ {description} ({package}) - NOT INSTALLED")
            all_installed = False
    
    if not all_installed:
        print("\n   Run: pip install -r requirements.txt")
        return False
    
    # Check .env file
    print("\n3. Checking configuration files...")
    env_path = os.path.join(os.path.dirname(__file__), '..', 'Configuration', '.env')
    if os.path.exists(env_path):
        print("   ✓ .env file exists")
        
        # Check if credentials are configured
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        api_key = os.getenv('API_KEY')
        api_secret = os.getenv('API_SECRET')
        
        if api_key and api_key != 'your_api_key_here':
            print("   ✓ API_KEY is configured")
        else:
            print("   ⚠ API_KEY not configured (edit .env file)")
        
        if api_secret and api_secret != 'your_api_secret_here':
            print("   ✓ API_SECRET is configured")
        else:
            print("   ⚠ API_SECRET not configured (edit .env file)")
    else:
        print("   ✗ .env file not found")
        print("   Run: cp .env.example .env")
        return False
    
    # Check if modules can be imported
    print("\n4. Checking project modules...")
    modules = ['Core_Modules.config', 'Core_Modules.auth', 'Core_Modules.trader', 
               'Core_Modules.websocket_ticker', 'Core_Modules.strategies', 'Core_Modules.utils']
    
    for module in modules:
        try:
            __import__(module)
            module_name = module.split('.')[-1]
            print(f"   ✓ {module_name}.py")
        except Exception as e:
            module_name = module.split('.')[-1]
            print(f"   ✗ {module_name}.py - Error: {e}")
            all_installed = False
    
    # Summary
    print("\n" + "="*60)
    if all_installed:
        print("  ✓ SETUP VERIFICATION PASSED")
        print("="*60)
        print("\nNext steps:")
        print("1. Edit Configuration/.env file with your Kite Connect credentials")
        print("2. Run: cd Application && python auth.py (for first-time authentication)")
        print("3. Run: cd Application && python main.py (to start trading)")
        print("\nFor detailed instructions, see Documentation/QUICKSTART.md")
    else:
        print("  ✗ SETUP VERIFICATION FAILED")
        print("="*60)
        print("\nPlease fix the issues above and try again.")
    
    print()
    return all_installed


if __name__ == "__main__":
    try:
        success = check_environment()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Verification failed with error: {e}")
        sys.exit(1)
