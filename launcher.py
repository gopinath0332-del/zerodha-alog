#!/usr/bin/env python3.9
"""
Launcher script for Zerodha Kite Trading Bot
Provides easy access to main applications
"""
import sys
import os


# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Python executable to use
PYTHON_EXE = 'python3.9'

def show_menu():
    """Display launcher menu"""
    print("\n" + "="*60)
    print("  ZERODHA KITE TRADING BOT - TERMINAL LAUNCHER")
    print("="*60)
    print("\n1. Verify Setup")
    print("2. Authenticate (First time / Daily login)")
    print("3. Start Trading Application (Terminal Mode)")
    print("4. Start Enhanced Trading Application (CLI)")
    print("5. Run Basic Order Example")
    print("6. Run Limit Order Example")
    print("7. Run WebSocket Stream Example")
    print("8. Exit")
    print("\n" + "="*60)

def main():
    """Main launcher function"""
    while True:
        show_menu()
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            print("\n--- Running Setup Verification ---\n")
            os.system(f'{PYTHON_EXE} Application/verify_setup.py')
        elif choice == '2':
            print("\n--- Starting Authentication ---\n")
            os.system(f'{PYTHON_EXE} Application/authenticate.py')
        elif choice == '3':
            print("\n--- Starting Trading Application ---\n")
            os.system(f'{PYTHON_EXE} Application/main.py')
        elif choice == '4':
            print("\n--- Starting Enhanced Trading Application ---\n")
            os.system(f'{PYTHON_EXE} Application/main_enhanced.py')
        elif choice == '5':
            print("\n--- Running Basic Order Example ---\n")
            os.system(f'{PYTHON_EXE} Examples/basic_order.py')
        elif choice == '6':
            print("\n--- Running Limit Order Example ---\n")
            os.system(f'{PYTHON_EXE} Examples/limit_order.py')
        elif choice == '7':
            print("\n--- Running WebSocket Stream Example ---\n")
            os.system(f'{PYTHON_EXE} Examples/websocket_stream.py')
        elif choice == '8':
            print("\nGoodbye!")
            break
        else:
            print("\n✗ Invalid choice. Please try again.")
        
        if choice != '8':
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
