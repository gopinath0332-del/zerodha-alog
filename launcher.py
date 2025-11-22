#!/usr/bin/env python3
"""
Launcher script for Zerodha Kite Trading Bot
Provides easy access to main applications
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def show_menu():
    """Display launcher menu"""
    print("\n" + "="*60)
    print("  ZERODHA KITE TRADING BOT - LAUNCHER")
    print("="*60)
    print("\n1. Verify Setup")
    print("2. Authenticate (First time / Daily login)")
    print("3. Start Trading Application")
    print("4. Run Basic Order Example")
    print("5. Run Limit Order Example")
    print("6. Run WebSocket Stream Example")
    print("7. Exit")
    print("\n" + "="*60)

def main():
    """Main launcher function"""
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            print("\n--- Running Setup Verification ---\n")
            os.system(f'{sys.executable} Application/verify_setup.py')
        elif choice == '2':
            print("\n--- Starting Authentication ---\n")
            os.chdir('Application')
            os.system(f'{sys.executable} -c "import sys; sys.path.insert(0, \'..\'); from Core_Modules.auth import KiteAuth; auth = KiteAuth(); auth.open_login_page() if not auth.access_token else None; request_token = input(\'\\nEnter request_token: \').strip(); auth.generate_session(request_token) if request_token else print(\'No token provided\')"')
            os.chdir('..')
        elif choice == '3':
            print("\n--- Starting Trading Application ---\n")
            os.system(f'{sys.executable} Application/main.py')
        elif choice == '4':
            print("\n--- Running Basic Order Example ---\n")
            os.system(f'{sys.executable} Examples/basic_order.py')
        elif choice == '5':
            print("\n--- Running Limit Order Example ---\n")
            os.system(f'{sys.executable} Examples/limit_order.py')
        elif choice == '6':
            print("\n--- Running WebSocket Stream Example ---\n")
            os.system(f'{sys.executable} Examples/websocket_stream.py')
        elif choice == '7':
            print("\nGoodbye!")
            break
        else:
            print("\n✗ Invalid choice. Please try again.")
        
        if choice != '7':
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
