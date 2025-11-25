#!/usr/bin/env python3
"""
Enhanced CLI Application for Zerodha Trading Bot
Provides feature parity with gui_modern.py in a terminal interface
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import signal
import threading
import time
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style
from tabulate import tabulate

from Core_Modules.trader import KiteTrader
from Core_Modules.config import Config
from Core_Modules.logger import setup_logging, get_logger
from Core_Modules.utils import (
    get_portfolio_summary,
    export_positions_to_csv,
    export_holdings_to_csv
)
from Core_Modules.notifications import create_notification_manager_from_config
from Core_Modules.strategies import TradingStrategies

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Setup structured logging
setup_logging(log_level="INFO", log_file="logs/trading_app_enhanced.log")
logger = get_logger(__name__)


class EnhancedTradingCLI:
    """Enhanced CLI with all GUI features"""
    
    def __init__(self):
        self.trader = None
        self.is_authenticated = False
        self.notifier = create_notification_manager_from_config()
        self.strategies = None
        
        # Monitor states
        self.rsi_monitor_running = False
        self.rsi_monitor_thread = None
        self.rsi_stop_event = threading.Event()
        self.rsi_current_value = None
        self.rsi_last_alert = None
        self.rsi_symbol = None
        self.rsi_alerted_candles = set()
        
        self.donchian_monitor_running = False
        self.donchian_monitor_thread = None
        self.donchian_stop_event = threading.Event()
        self.donchian_current_price = None
        self.donchian_upper_band = None
        self.donchian_lower_band = None
        self.donchian_last_alert = None
        self.donchian_symbol = None
        self.donchian_alerted_candles = set()
        
        # Settings
        self.auto_refresh = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n\n{Fore.YELLOW}Shutting down gracefully...")
        self.stop_all_monitors()
        print(f"{Fore.GREEN}Goodbye!")
        sys.exit(0)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self, text):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}{text.center(70)}")
        print(f"{Fore.CYAN}{'='*70}\n")
    
    def print_success(self, text):
        """Print success message"""
        print(f"{Fore.GREEN}✓ {text}")
    
    def print_error(self, text):
        """Print error message"""
        print(f"{Fore.RED}✗ {text}")
    
    def print_info(self, text):
        """Print info message"""
        print(f"{Fore.BLUE}ℹ {text}")
    
    def print_warning(self, text):
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠ {text}")
    
    def authenticate(self):
        """Authenticate with existing token"""
        try:
            print(f"{Fore.YELLOW}Authenticating...")
            self.trader = KiteTrader()
            self.strategies = TradingStrategies()
            self.is_authenticated = True
            self.print_success("Authenticated successfully!")
            return True
        except Exception as e:
            self.print_error(f"Authentication failed: {str(e)}")
            self.is_authenticated = False
            return False
    
    def check_auth(self):
        """Check if authenticated"""
        if not self.is_authenticated:
            self.print_error("Not authenticated! Please authenticate first.")
            return False
        return True
    
    def display_main_menu(self):
        """Display the main menu"""
        self.print_header("ZERODHA TRADING TERMINAL (Enhanced CLI)")
        
        # Show authentication status
        if self.is_authenticated:
            print(f"{Fore.GREEN}Status: Authenticated ✓")
        else:
            print(f"{Fore.RED}Status: Not Authenticated ✗")
        
        # Show monitor status
        monitors_active = []
        if self.rsi_monitor_running:
            monitors_active.append(f"RSI ({self.rsi_symbol})")
        if self.donchian_monitor_running:
            monitors_active.append(f"Donchian ({self.donchian_symbol})")
        
        if monitors_active:
            print(f"{Fore.CYAN}Active Monitors: {', '.join(monitors_active)}")
        
        print(f"\n{Fore.WHITE}Main Menu:")
        print(f"{Fore.YELLOW}1.  {Fore.WHITE}Portfolio Summary")
        print(f"{Fore.YELLOW}2.  {Fore.WHITE}Positions")
        print(f"{Fore.YELLOW}3.  {Fore.WHITE}Holdings")
        print(f"{Fore.YELLOW}4.  {Fore.WHITE}Orders")
        print(f"{Fore.YELLOW}5.  {Fore.WHITE}Margins")
        print(f"{Fore.YELLOW}6.  {Fore.WHITE}Market Data")
        print(f"{Fore.YELLOW}7.  {Fore.WHITE}Strategy Monitors")
        print(f"{Fore.YELLOW}8.  {Fore.WHITE}Tools")
        print(f"{Fore.YELLOW}9.  {Fore.WHITE}Settings")
        print(f"{Fore.YELLOW}10. {Fore.WHITE}Exit")
        print(f"{Fore.CYAN}{'='*70}\n")
    
    def view_portfolio_summary(self):
        """Display portfolio summary"""
        if not self.check_auth():
            return
        
        self.print_header("Portfolio Summary")
        
        try:
            summary = get_portfolio_summary(self.trader)
            
            # Create summary table
            data = [
                ["Available Margin", f"₹{summary['available_margin']:,.2f}"],
                ["Capital Used", f"₹{summary['capital_used']:,.2f}"],
                ["Position P&L", self._format_pnl(summary['positions_pnl'])],
                ["Holdings P&L", self._format_pnl(summary['holdings_pnl'])],
                ["Total P&L", self._format_pnl(summary['total_pnl'])],
            ]
            
            print(tabulate(data, headers=["Metric", "Value"], tablefmt="grid"))
            
        except Exception as e:
            self.print_error(f"Failed to load portfolio: {str(e)}")
            logger.error("portfolio_load_failed", error=str(e), exc_info=True)
    
    def _format_pnl(self, value):
        """Format P&L with color"""
        if value >= 0:
            return f"{Fore.GREEN}₹{value:,.2f}"
        else:
            return f"{Fore.RED}₹{value:,.2f}"
    
    def view_positions(self):
        """Display positions"""
        if not self.check_auth():
            return
        
        self.print_header("Positions")
        
        try:
            positions = self.trader.get_positions()
            
            day_positions = [p for p in positions.get('day', []) if p['quantity'] != 0]
            net_positions = [p for p in positions.get('net', []) if p['quantity'] != 0]
            
            # Filter out duplicates
            day_symbols = {p['tradingsymbol'] for p in day_positions}
            net_only = [p for p in net_positions if p['tradingsymbol'] not in day_symbols]
            
            if not day_positions and not net_only:
                self.print_info("No positions found")
                return
            
            print(f"{Fore.CYAN}Total Positions: {len(day_positions) + len(net_only)}")
            print(f"  Day (MIS): {len(day_positions)}")
            print(f"  Net (NRML): {len(net_only)}\n")
            
            total_pnl = 0
            
            if day_positions:
                print(f"{Fore.YELLOW}DAY POSITIONS (MIS):")
                headers = ["Symbol", "Qty", "Avg Price", "LTP", "Invested", "P&L"]
                data = []
                
                for pos in day_positions:
                    invested = abs(pos['quantity']) * pos['average_price']
                    data.append([
                        pos['tradingsymbol'],
                        pos['quantity'],
                        f"₹{pos['average_price']:.2f}",
                        f"₹{pos['last_price']:.2f}",
                        f"₹{invested:,.2f}",
                        self._format_pnl(pos['pnl'])
                    ])
                    total_pnl += pos['pnl']
                
                print(tabulate(data, headers=headers, tablefmt="grid"))
                print()
            
            if net_only:
                print(f"{Fore.YELLOW}NET POSITIONS (NRML/Carry-forward):")
                headers = ["Symbol", "Qty", "Avg Price", "LTP", "Invested", "P&L"]
                data = []
                
                for pos in net_only:
                    invested = abs(pos['quantity']) * pos['average_price']
                    data.append([
                        pos['tradingsymbol'],
                        pos['quantity'],
                        f"₹{pos['average_price']:.2f}",
                        f"₹{pos['last_price']:.2f}",
                        f"₹{invested:,.2f}",
                        self._format_pnl(pos['pnl'])
                    ])
                    total_pnl += pos['pnl']
                
                print(tabulate(data, headers=headers, tablefmt="grid"))
                print()
            
            print(f"{Fore.CYAN}Total P&L: {self._format_pnl(total_pnl)}")
            
        except Exception as e:
            self.print_error(f"Failed to load positions: {str(e)}")
            logger.error("positions_load_failed", error=str(e), exc_info=True)
    
    def view_holdings(self):
        """Display holdings"""
        if not self.check_auth():
            return
        
        self.print_header("Holdings")
        
        try:
            holdings = self.trader.get_holdings()
            
            if not holdings:
                self.print_info("No holdings found")
                return
            
            print(f"{Fore.CYAN}Total Holdings: {len(holdings)}\n")
            
            headers = ["Symbol", "Qty", "Avg Price", "LTP", "Investment", "Current Value", "P&L", "Returns %"]
            data = []
            
            total_investment = 0
            total_current = 0
            
            for holding in holdings:
                investment = holding['average_price'] * holding['quantity']
                current_value = holding['last_price'] * holding['quantity']
                pnl = holding['pnl']
                returns_pct = (pnl / investment * 100) if investment > 0 else 0
                
                data.append([
                    holding['tradingsymbol'],
                    holding['quantity'],
                    f"₹{holding['average_price']:.2f}",
                    f"₹{holding['last_price']:.2f}",
                    f"₹{investment:,.2f}",
                    f"₹{current_value:,.2f}",
                    self._format_pnl(pnl),
                    f"{returns_pct:+.2f}%"
                ])
                
                total_investment += investment
                total_current += current_value
            
            print(tabulate(data, headers=headers, tablefmt="grid"))
            
            total_pnl = total_current - total_investment
            total_returns = (total_pnl / total_investment * 100) if total_investment > 0 else 0
            
            print(f"\n{Fore.CYAN}Summary:")
            print(f"  Total Investment: ₹{total_investment:,.2f}")
            print(f"  Current Value: ₹{total_current:,.2f}")
            print(f"  Total P&L: {self._format_pnl(total_pnl)}")
            print(f"  Returns: {total_returns:+.2f}%")
            
        except Exception as e:
            self.print_error(f"Failed to load holdings: {str(e)}")
            logger.error("holdings_load_failed", error=str(e), exc_info=True)
    
    def orders_menu(self):
        """Orders submenu"""
        while True:
            self.print_header("Orders Menu")
            print(f"{Fore.YELLOW}1. {Fore.WHITE}View Orders")
            print(f"{Fore.YELLOW}2. {Fore.WHITE}Place Market Order")
            print(f"{Fore.YELLOW}3. {Fore.WHITE}Place Limit Order")
            print(f"{Fore.YELLOW}4. {Fore.WHITE}Place Bracket Order")
            print(f"{Fore.YELLOW}5. {Fore.WHITE}Cancel Order")
            print(f"{Fore.YELLOW}6. {Fore.WHITE}Back to Main Menu")
            
            choice = input(f"\n{Fore.CYAN}Enter choice (1-6): {Fore.WHITE}").strip()
            
            if choice == '1':
                self.view_orders()
            elif choice == '2':
                self.place_market_order()
            elif choice == '3':
                self.place_limit_order()
            elif choice == '4':
                self.place_bracket_order()
            elif choice == '5':
                self.cancel_order()
            elif choice == '6':
                break
            else:
                self.print_error("Invalid choice")
            
            if choice != '6':
                input(f"\n{Fore.CYAN}Press Enter to continue...")
    
    def view_orders(self):
        """Display order history"""
        if not self.check_auth():
            return
        
        self.print_header("Order History")
        
        try:
            orders = self.trader.get_orders()
            
            if not orders:
                self.print_info("No orders found")
                return
            
            # Show last 20 orders
            recent_orders = orders[-20:]
            
            print(f"{Fore.CYAN}Showing last {len(recent_orders)} orders:\n")
            
            headers = ["Time", "Symbol", "Type", "Qty", "Price", "Status"]
            data = []
            
            for order in recent_orders:
                order_time = order['order_timestamp'].strftime('%H:%M:%S') if hasattr(order['order_timestamp'], 'strftime') else str(order['order_timestamp'])
                data.append([
                    order_time,
                    order['tradingsymbol'],
                    f"{order['transaction_type']} {order['order_type']}",
                    order['quantity'],
                    f"₹{order.get('price', order.get('average_price', 0)):.2f}",
                    order['status']
                ])
            
            print(tabulate(data, headers=headers, tablefmt="grid"))
            
        except Exception as e:
            self.print_error(f"Failed to load orders: {str(e)}")
            logger.error("orders_load_failed", error=str(e), exc_info=True)
    
    def place_market_order(self):
        """Place a market order"""
        if not self.check_auth():
            return
        
        self.print_header("Place Market Order")
        self.print_warning("This will place a REAL order!")
        
        confirm = input(f"{Fore.YELLOW}Continue? (yes/no): {Fore.WHITE}").strip().lower()
        if confirm != 'yes':
            self.print_info("Order cancelled")
            return
        
        try:
            symbol = input(f"{Fore.CYAN}Symbol (e.g., INFY): {Fore.WHITE}").strip().upper()
            exchange = input(f"{Fore.CYAN}Exchange (NSE/BSE) [NSE]: {Fore.WHITE}").strip().upper() or 'NSE'
            transaction = input(f"{Fore.CYAN}Transaction (BUY/SELL): {Fore.WHITE}").strip().upper()
            quantity = int(input(f"{Fore.CYAN}Quantity: {Fore.WHITE}").strip())
            product = input(f"{Fore.CYAN}Product (CNC/MIS/NRML) [CNC]: {Fore.WHITE}").strip().upper() or 'CNC'
            
            # Confirm
            print(f"\n{Fore.YELLOW}Order Summary:")
            print(f"  Symbol: {symbol}")
            print(f"  Exchange: {exchange}")
            print(f"  Transaction: {transaction}")
            print(f"  Quantity: {quantity}")
            print(f"  Type: MARKET")
            print(f"  Product: {product}")
            
            final_confirm = input(f"\n{Fore.YELLOW}Confirm order? (yes/no): {Fore.WHITE}").strip().lower()
            if final_confirm != 'yes':
                self.print_info("Order cancelled")
                return
            
            order_id = self.trader.place_order(
                symbol=symbol,
                exchange=exchange,
                transaction_type=transaction,
                quantity=quantity,
                order_type='MARKET',
                product=product
            )
            
            self.print_success(f"Order placed successfully! Order ID: {order_id}")
            
        except Exception as e:
            self.print_error(f"Order placement failed: {str(e)}")
            logger.error("order_placement_failed", error=str(e), exc_info=True)
    
    def place_limit_order(self):
        """Place a limit order"""
        if not self.check_auth():
            return
        
        self.print_header("Place Limit Order")
        self.print_warning("This will place a REAL order!")
        
        confirm = input(f"{Fore.YELLOW}Continue? (yes/no): {Fore.WHITE}").strip().lower()
        if confirm != 'yes':
            self.print_info("Order cancelled")
            return
        
        try:
            symbol = input(f"{Fore.CYAN}Symbol (e.g., INFY): {Fore.WHITE}").strip().upper()
            exchange = input(f"{Fore.CYAN}Exchange (NSE/BSE) [NSE]: {Fore.WHITE}").strip().upper() or 'NSE'
            transaction = input(f"{Fore.CYAN}Transaction (BUY/SELL): {Fore.WHITE}").strip().upper()
            quantity = int(input(f"{Fore.CYAN}Quantity: {Fore.WHITE}").strip())
            price = float(input(f"{Fore.CYAN}Limit Price: {Fore.WHITE}").strip())
            product = input(f"{Fore.CYAN}Product (CNC/MIS/NRML) [CNC]: {Fore.WHITE}").strip().upper() or 'CNC'
            
            # Confirm
            print(f"\n{Fore.YELLOW}Order Summary:")
            print(f"  Symbol: {symbol}")
            print(f"  Exchange: {exchange}")
            print(f"  Transaction: {transaction}")
            print(f"  Quantity: {quantity}")
            print(f"  Type: LIMIT")
            print(f"  Price: ₹{price:.2f}")
            print(f"  Product: {product}")
            
            final_confirm = input(f"\n{Fore.YELLOW}Confirm order? (yes/no): {Fore.WHITE}").strip().lower()
            if final_confirm != 'yes':
                self.print_info("Order cancelled")
                return
            
            order_id = self.trader.place_order(
                symbol=symbol,
                exchange=exchange,
                transaction_type=transaction,
                quantity=quantity,
                order_type='LIMIT',
                product=product,
                price=price
            )
            
            self.print_success(f"Order placed successfully! Order ID: {order_id}")
            
        except Exception as e:
            self.print_error(f"Order placement failed: {str(e)}")
            logger.error("order_placement_failed", error=str(e), exc_info=True)
    
    def place_bracket_order(self):
        """Place a bracket order"""
        if not self.check_auth():
            return
        
        self.print_header("Place Bracket Order")
        self.print_warning("This will place a REAL order with SL and Target!")
        
        confirm = input(f"{Fore.YELLOW}Continue? (yes/no): {Fore.WHITE}").strip().lower()
        if confirm != 'yes':
            self.print_info("Order cancelled")
            return
        
        try:
            symbol = input(f"{Fore.CYAN}Symbol (e.g., INFY): {Fore.WHITE}").strip().upper()
            exchange = input(f"{Fore.CYAN}Exchange (NSE/BSE) [NSE]: {Fore.WHITE}").strip().upper() or 'NSE'
            transaction = input(f"{Fore.CYAN}Transaction (BUY/SELL): {Fore.WHITE}").strip().upper()
            quantity = int(input(f"{Fore.CYAN}Quantity: {Fore.WHITE}").strip())
            price = float(input(f"{Fore.CYAN}Entry Price: {Fore.WHITE}").strip())
            stoploss = float(input(f"{Fore.CYAN}Stop Loss Price: {Fore.WHITE}").strip())
            target = float(input(f"{Fore.CYAN}Target Price: {Fore.WHITE}").strip())
            
            # Confirm
            print(f"\n{Fore.YELLOW}Bracket Order Summary:")
            print(f"  Symbol: {symbol}")
            print(f"  Exchange: {exchange}")
            print(f"  Transaction: {transaction}")
            print(f"  Quantity: {quantity}")
            print(f"  Entry Price: ₹{price:.2f}")
            print(f"  Stop Loss: ₹{stoploss:.2f}")
            print(f"  Target: ₹{target:.2f}")
            
            final_confirm = input(f"\n{Fore.YELLOW}Confirm bracket order? (yes/no): {Fore.WHITE}").strip().lower()
            if final_confirm != 'yes':
                self.print_info("Order cancelled")
                return
            
            order_id = self.trader.place_bracket_order(
                symbol=symbol,
                exchange=exchange,
                transaction_type=transaction,
                quantity=quantity,
                price=price,
                stoploss=stoploss,
                target=target
            )
            
            self.print_success(f"Bracket order placed successfully! Order ID: {order_id}")
            
        except Exception as e:
            self.print_error(f"Bracket order placement failed: {str(e)}")
            logger.error("bracket_order_placement_failed", error=str(e), exc_info=True)
    
    def cancel_order(self):
        """Cancel an order"""
        if not self.check_auth():
            return
        
        self.print_header("Cancel Order")
        
        try:
            # Show pending orders first
            orders = self.trader.get_orders()
            pending = [o for o in orders if o['status'] in ['OPEN', 'TRIGGER PENDING']]
            
            if not pending:
                self.print_info("No pending orders to cancel")
                return
            
            print(f"{Fore.CYAN}Pending Orders:\n")
            for i, order in enumerate(pending, 1):
                print(f"{i}. Order ID: {order['order_id']}")
                print(f"   Symbol: {order['tradingsymbol']}")
                print(f"   Type: {order['transaction_type']} {order['order_type']}")
                print(f"   Quantity: {order['quantity']}")
                print(f"   Status: {order['status']}\n")
            
            order_id = input(f"{Fore.CYAN}Enter Order ID to cancel: {Fore.WHITE}").strip()
            
            confirm = input(f"{Fore.YELLOW}Confirm cancellation? (yes/no): {Fore.WHITE}").strip().lower()
            if confirm != 'yes':
                self.print_info("Cancellation aborted")
                return
            
            self.trader.cancel_order(order_id=order_id)
            self.print_success(f"Order {order_id} cancelled successfully!")
            
        except Exception as e:
            self.print_error(f"Order cancellation failed: {str(e)}")
            logger.error("order_cancellation_failed", error=str(e), exc_info=True)
    
    def view_margins(self):
        """Display margin details"""
        if not self.check_auth():
            return
        
        self.print_header("Account Margins")
        
        try:
            margins = self.trader.get_margins()
            
            for segment, data in margins.items():
                print(f"\n{Fore.YELLOW}{segment.upper()}:")
                
                margin_data = [
                    ["Available Cash", f"₹{data['available']['cash']:,.2f}"],
                    ["Available Margin", f"₹{data['available']['live_balance']:,.2f}"],
                    ["Used Margin", f"₹{data['utilised']['debits']:,.2f}"],
                    ["Collateral", f"₹{data['available'].get('collateral', 0):,.2f}"],
                ]
                
                print(tabulate(margin_data, headers=["Metric", "Value"], tablefmt="grid"))
            
        except Exception as e:
            self.print_error(f"Failed to load margins: {str(e)}")
            logger.error("margins_load_failed", error=str(e), exc_info=True)
    
    def view_market_data(self):
        """Display market quotes"""
        if not self.check_auth():
            return
        
        self.print_header("Market Data")
        
        symbols_input = input(f"{Fore.CYAN}Enter symbols (e.g., NSE:INFY,NSE:TCS): {Fore.WHITE}").strip()
        
        if not symbols_input:
            self.print_error("No symbols entered")
            return
        
        symbols = [s.strip() for s in symbols_input.split(',')]
        
        try:
            quote = self.trader.get_quote(*symbols)
            
            headers = ["Symbol", "LTP", "Open", "High", "Low", "Close", "Volume", "Change %"]
            data = []
            
            for symbol in symbols:
                if symbol in quote:
                    q = quote[symbol]
                    change_pct = ((q['last_price'] - q['ohlc']['close']) / q['ohlc']['close'] * 100) if q['ohlc']['close'] > 0 else 0
                    
                    data.append([
                        symbol,
                        f"₹{q['last_price']:.2f}",
                        f"₹{q['ohlc']['open']:.2f}",
                        f"₹{q['ohlc']['high']:.2f}",
                        f"₹{q['ohlc']['low']:.2f}",
                        f"₹{q['ohlc']['close']:.2f}",
                        f"{q.get('volume', 0):,}",
                        f"{change_pct:+.2f}%"
                    ])
            
            print(tabulate(data, headers=headers, tablefmt="grid"))
            
        except Exception as e:
            self.print_error(f"Failed to fetch market data: {str(e)}")
            logger.error("market_data_fetch_failed", error=str(e), exc_info=True)
    
    def strategy_monitors_menu(self):
        """Strategy monitors submenu"""
        while True:
            self.print_header("Strategy Monitors")
            
            # Show current status
            if self.rsi_monitor_running:
                print(f"{Fore.GREEN}RSI Monitor: RUNNING ({self.rsi_symbol})")
                if self.rsi_current_value:
                    print(f"  Current RSI: {self.rsi_current_value:.2f}")
                if self.rsi_last_alert:
                    print(f"  Last Alert: {self.rsi_last_alert}")
            else:
                print(f"{Fore.RED}RSI Monitor: STOPPED")
            
            if self.donchian_monitor_running:
                print(f"{Fore.GREEN}Donchian Monitor: RUNNING ({self.donchian_symbol})")
                if self.donchian_current_price:
                    print(f"  Current Price: ₹{self.donchian_current_price:.2f}")
                if self.donchian_upper_band:
                    print(f"  Upper Band: ₹{self.donchian_upper_band:.2f}")
                if self.donchian_lower_band:
                    print(f"  Lower Band: ₹{self.donchian_lower_band:.2f}")
                if self.donchian_last_alert:
                    print(f"  Last Alert: {self.donchian_last_alert}")
            else:
                print(f"{Fore.RED}Donchian Monitor: STOPPED")
            
            print(f"\n{Fore.YELLOW}1. {Fore.WHITE}NatgasMini RSI Monitor")
            print(f"{Fore.YELLOW}2. {Fore.WHITE}GOLDPETAL Donchian Monitor")
            print(f"{Fore.YELLOW}3. {Fore.WHITE}Stop All Monitors")
            print(f"{Fore.YELLOW}4. {Fore.WHITE}Back to Main Menu")
            
            choice = input(f"\n{Fore.CYAN}Enter choice (1-4): {Fore.WHITE}").strip()
            
            if choice == '1':
                self.rsi_monitor_menu()
            elif choice == '2':
                self.donchian_monitor_menu()
            elif choice == '3':
                self.stop_all_monitors()
                self.print_success("All monitors stopped")
            elif choice == '4':
                break
            else:
                self.print_error("Invalid choice")
            
            if choice != '4':
                input(f"\n{Fore.CYAN}Press Enter to continue...")
    
    def rsi_monitor_menu(self):
        """RSI monitor configuration and control"""
        if not self.check_auth():
            return
        
        self.print_header("NatgasMini RSI Monitor")
        
        if self.rsi_monitor_running:
            self.print_warning("Monitor is already running!")
            stop = input(f"{Fore.YELLOW}Stop monitor? (yes/no): {Fore.WHITE}").strip().lower()
            if stop == 'yes':
                self.stop_rsi_monitor()
                self.print_success("RSI monitor stopped")
            return
        
        # Get MCX NATGASMINI futures
        print(f"{Fore.CYAN}Fetching NATGASMINI futures...")
        
        try:
            from kiteconnect import KiteConnect
            kite = KiteConnect(api_key=Config.API_KEY)
            kite.set_access_token(Config.ACCESS_TOKEN)
            
            instruments = kite.instruments(exchange="MCX")
            natgas_futures = [
                inst['tradingsymbol'] for inst in instruments
                if 'NATGASMINI' in inst['tradingsymbol'] and inst['instrument_type'] == 'FUT'
            ]
            natgas_futures.sort()
            
            if not natgas_futures:
                self.print_error("No NATGASMINI futures found")
                return
            
            print(f"\n{Fore.CYAN}Available Contracts:")
            for i, contract in enumerate(natgas_futures, 1):
                print(f"{i}. {contract}")
            
            contract_idx = int(input(f"\n{Fore.CYAN}Select contract (1-{len(natgas_futures)}): {Fore.WHITE}").strip()) - 1
            if contract_idx < 0 or contract_idx >= len(natgas_futures):
                self.print_error("Invalid selection")
                return
            
            symbol = natgas_futures[contract_idx]
            
            # Candle type selection
            print(f"\n{Fore.CYAN}Candle Type:")
            print(f"1. Heikin Ashi (Recommended)")
            print(f"2. Normal")
            candle_choice = input(f"{Fore.CYAN}Select candle type (1-2) [1]: {Fore.WHITE}").strip() or '1'
            candle_type = "Heikin Ashi" if candle_choice == '1' else "Normal"
            
            # Start monitor
            self.start_rsi_monitor(symbol, candle_type)
            
        except Exception as e:
            self.print_error(f"Failed to start RSI monitor: {str(e)}")
            logger.error("rsi_monitor_start_failed", error=str(e), exc_info=True)
    
    def start_rsi_monitor(self, symbol, candle_type):
        """Start RSI monitoring in background thread"""
        self.rsi_symbol = symbol
        self.rsi_stop_event.clear()
        self.rsi_alerted_candles = set()
        self.rsi_monitor_running = True
        
        def rsi_worker():
            """RSI monitoring worker thread - reuses logic from gui_modern.py"""
            import pandas as pd
            from kiteconnect import KiteConnect
            import pytz
            
            logger.info("rsi_monitor_started", symbol=symbol, candle_type=candle_type)
            
            try:
                kite = KiteConnect(api_key=Config.API_KEY)
                kite.set_access_token(Config.ACCESS_TOKEN)
                
                # Resolve instrument token
                instruments = kite.instruments(exchange="MCX")
                instrument_token = None
                for inst in instruments:
                    if inst['tradingsymbol'] == symbol:
                        instrument_token = inst['instrument_token']
                        break
                
                if not instrument_token:
                    self.print_error(f"Instrument token not found for {symbol}")
                    self.rsi_monitor_running = False
                    return
                
                # Send start notification
                self.notifier.send_alert(
                    f"**RSI Monitor Started**\n\n"
                    f"**Symbol:** {symbol}\n"
                    f"**Candle Type:** {candle_type}\n"
                    f"**Interval:** 1 hour\n"
                    f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    color=0x0000FF
                )
                
                first_run = True
                
                while not self.rsi_stop_event.is_set():
                    try:
                        # Fetch historical data
                        from_date = datetime.now() - timedelta(days=30)
                        to_date = datetime.now()
                        
                        df = pd.DataFrame(kite.historical_data(
                            instrument_token=instrument_token,
                            from_date=from_date,
                            to_date=to_date,
                            interval="60minute"
                        ))
                        
                        if len(df) < 100:
                            logger.warning("not_enough_candles", count=len(df))
                            time.sleep(60)
                            continue
                        
                        # Convert to Heikin Ashi if selected
                        if candle_type == "Heikin Ashi":
                            df = TradingStrategies.heikin_ashi(df)
                            close = df['ha_close']
                        else:
                            close = df['close']
                        
                        # Calculate RSI
                        delta = close.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        
                        current_rsi = float(rsi.iloc[-1])
                        self.rsi_current_value = current_rsi
                        
                        # Check for alerts
                        candle_timestamp = df['date'].iloc[-1].isoformat()
                        
                        if candle_timestamp not in self.rsi_alerted_candles:
                            if current_rsi > 70:
                                alert_msg = (
                                    f"**RSI OVERBOUGHT ALERT**\n\n"
                                    f"**Symbol:** {symbol}\n"
                                    f"**RSI:** {current_rsi:.2f}\n"
                                    f"**Candle Type:** {candle_type}\n"
                                    f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                )
                                self.notifier.send_alert(alert_msg, color=0xFF0000)
                                self.rsi_last_alert = f"Overbought (RSI: {current_rsi:.2f})"
                                self.rsi_alerted_candles.add(candle_timestamp)
                                logger.info("rsi_overbought_alert", rsi=current_rsi, symbol=symbol)
                            
                            elif current_rsi < 30:
                                alert_msg = (
                                    f"**RSI OVERSOLD ALERT**\n\n"
                                    f"**Symbol:** {symbol}\n"
                                    f"**RSI:** {current_rsi:.2f}\n"
                                    f"**Candle Type:** {candle_type}\n"
                                    f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                )
                                self.notifier.send_alert(alert_msg, color=0x00FF00)
                                self.rsi_last_alert = f"Oversold (RSI: {current_rsi:.2f})"
                                self.rsi_alerted_candles.add(candle_timestamp)
                                logger.info("rsi_oversold_alert", rsi=current_rsi, symbol=symbol)
                        
                        logger.info("rsi_analysis_complete", rsi=current_rsi, symbol=symbol)
                        
                        # Wait for next hour boundary
                        if first_run:
                            first_run = False
                        
                        # Sleep for 1 hour
                        for _ in range(3600):
                            if self.rsi_stop_event.is_set():
                                break
                            time.sleep(1)
                    
                    except Exception as e:
                        logger.error("rsi_analysis_error", error=str(e), exc_info=True)
                        time.sleep(60)
            
            except Exception as e:
                logger.error("rsi_monitor_error", error=str(e), exc_info=True)
            finally:
                self.rsi_monitor_running = False
                self.notifier.send_alert(
                    f"**RSI Monitor Stopped**\n\n"
                    f"**Symbol:** {symbol}\n"
                    f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    color=0x808080
                )
        
        self.rsi_monitor_thread = threading.Thread(target=rsi_worker, daemon=True)
        self.rsi_monitor_thread.start()
        
        self.print_success(f"RSI monitor started for {symbol} ({candle_type})")
    
    def stop_rsi_monitor(self):
        """Stop RSI monitor"""
        if self.rsi_monitor_running:
            self.rsi_stop_event.set()
            if self.rsi_monitor_thread:
                self.rsi_monitor_thread.join(timeout=2)
            self.rsi_monitor_running = False
    
    def donchian_monitor_menu(self):
        """Donchian monitor configuration and control"""
        if not self.check_auth():
            return
        
        self.print_header("GOLDPETAL Donchian Monitor")
        
        if self.donchian_monitor_running:
            self.print_warning("Monitor is already running!")
            stop = input(f"{Fore.YELLOW}Stop monitor? (yes/no): {Fore.WHITE}").strip().lower()
            if stop == 'yes':
                self.stop_donchian_monitor()
                self.print_success("Donchian monitor stopped")
            return
        
        # Get MCX GOLDPETAL futures
        print(f"{Fore.CYAN}Fetching GOLDPETAL futures...")
        
        try:
            from kiteconnect import KiteConnect
            kite = KiteConnect(api_key=Config.API_KEY)
            kite.set_access_token(Config.ACCESS_TOKEN)
            
            instruments = kite.instruments(exchange="MCX")
            goldpetal_futures = [
                inst['tradingsymbol'] for inst in instruments
                if 'GOLDPETAL' in inst['tradingsymbol'] and inst['instrument_type'] == 'FUT'
            ]
            goldpetal_futures.sort()
            
            if not goldpetal_futures:
                self.print_error("No GOLDPETAL futures found")
                return
            
            print(f"\n{Fore.CYAN}Available Contracts:")
            for i, contract in enumerate(goldpetal_futures, 1):
                print(f"{i}. {contract}")
            
            contract_idx = int(input(f"\n{Fore.CYAN}Select contract (1-{len(goldpetal_futures)}): {Fore.WHITE}").strip()) - 1
            if contract_idx < 0 or contract_idx >= len(goldpetal_futures):
                self.print_error("Invalid selection")
                return
            
            symbol = goldpetal_futures[contract_idx]
            
            # Candle type selection
            print(f"\n{Fore.CYAN}Candle Type:")
            print(f"1. Heikin Ashi (Recommended)")
            print(f"2. Normal")
            candle_choice = input(f"{Fore.CYAN}Select candle type (1-2) [1]: {Fore.WHITE}").strip() or '1'
            candle_type = "Heikin Ashi" if candle_choice == '1' else "Normal"
            
            # Start monitor
            self.start_donchian_monitor(symbol, candle_type)
            
        except Exception as e:
            self.print_error(f"Failed to start Donchian monitor: {str(e)}")
            logger.error("donchian_monitor_start_failed", error=str(e), exc_info=True)
    
    def start_donchian_monitor(self, symbol, candle_type):
        """Start Donchian monitoring in background thread"""
        self.donchian_symbol = symbol
        self.donchian_stop_event.clear()
        self.donchian_alerted_candles = set()
        self.donchian_monitor_running = True
        
        def donchian_worker():
            """Donchian monitoring worker thread - reuses logic from gui_modern.py"""
            import pandas as pd
            from kiteconnect import KiteConnect
            import pytz
            
            upper_period = 20
            lower_period = 10
            
            logger.info("donchian_monitor_started", symbol=symbol, candle_type=candle_type)
            
            try:
                kite = KiteConnect(api_key=Config.API_KEY)
                kite.set_access_token(Config.ACCESS_TOKEN)
                
                # Resolve instrument token
                instruments = kite.instruments(exchange="MCX")
                instrument_token = None
                for inst in instruments:
                    if inst['tradingsymbol'] == symbol:
                        instrument_token = inst['instrument_token']
                        break
                
                if not instrument_token:
                    self.print_error(f"Instrument token not found for {symbol}")
                    self.donchian_monitor_running = False
                    return
                
                # Send start notification
                self.notifier.send_alert(
                    f"**Donchian Monitor Started**\n\n"
                    f"**Symbol:** {symbol}\n"
                    f"**Candle Type:** {candle_type}\n"
                    f"**Upper Period:** {upper_period}\n"
                    f"**Lower Period:** {lower_period}\n"
                    f"**Interval:** 1 hour\n"
                    f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    color=0x0000FF
                )
                
                first_run = True
                
                while not self.donchian_stop_event.is_set():
                    try:
                        # Fetch historical data
                        from_date = datetime.now() - timedelta(days=30)
                        to_date = datetime.now()
                        
                        df = pd.DataFrame(kite.historical_data(
                            instrument_token=instrument_token,
                            from_date=from_date,
                            to_date=to_date,
                            interval="60minute"
                        ))
                        
                        if len(df) < max(upper_period, lower_period):
                            logger.warning("not_enough_candles", count=len(df))
                            time.sleep(60)
                            continue
                        
                        # Convert to Heikin Ashi if selected
                        if candle_type == "Heikin Ashi":
                            df = TradingStrategies.heikin_ashi(df)
                            high = df['ha_high']
                            low = df['ha_low']
                            close = df['ha_close']
                        else:
                            high = df['high']
                            low = df['low']
                            close = df['close']
                        
                        # Calculate Donchian bands
                        upper_band = high.rolling(window=upper_period).max().iloc[-1]
                        lower_band = low.rolling(window=lower_period).min().iloc[-1]
                        current_price = float(close.iloc[-1])
                        
                        # Calculate previous candle's close
                        prev_close = float(close.iloc[-2])
                        
                        self.donchian_current_price = current_price
                        self.donchian_upper_band = float(upper_band)
                        self.donchian_lower_band = float(lower_band)
                        
                        # Check for alerts
                        candle_timestamp = df['date'].iloc[-1].isoformat()
                        
                        if candle_timestamp not in self.donchian_alerted_candles:
                            if prev_close >= upper_band:
                                alert_msg = (
                                    f"**DONCHIAN BULLISH BREAKOUT**\n\n"
                                    f"**Symbol:** {symbol}\n"
                                    f"**Price:** ₹{current_price:.2f}\n"
                                    f"**Upper Band:** ₹{upper_band:.2f}\n"
                                    f"**Candle Type:** {candle_type}\n"
                                    f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                )
                                self.notifier.send_alert(alert_msg, color=0x00FF00)
                                self.donchian_last_alert = f"Bullish Breakout (₹{current_price:.2f})"
                                self.donchian_alerted_candles.add(candle_timestamp)
                                logger.info("donchian_bullish_alert", price=current_price, symbol=symbol)
                            
                            elif prev_close <= lower_band:
                                alert_msg = (
                                    f"**DONCHIAN BEARISH BREAKDOWN**\n\n"
                                    f"**Symbol:** {symbol}\n"
                                    f"**Price:** ₹{current_price:.2f}\n"
                                    f"**Lower Band:** ₹{lower_band:.2f}\n"
                                    f"**Candle Type:** {candle_type}\n"
                                    f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                )
                                self.notifier.send_alert(alert_msg, color=0xFF0000)
                                self.donchian_last_alert = f"Bearish Breakdown (₹{current_price:.2f})"
                                self.donchian_alerted_candles.add(candle_timestamp)
                                logger.info("donchian_bearish_alert", price=current_price, symbol=symbol)
                        
                        logger.info("donchian_analysis_complete", price=current_price, symbol=symbol)
                        
                        # Wait for next hour boundary
                        if first_run:
                            first_run = False
                        
                        # Sleep for 1 hour
                        for _ in range(3600):
                            if self.donchian_stop_event.is_set():
                                break
                            time.sleep(1)
                    
                    except Exception as e:
                        logger.error("donchian_analysis_error", error=str(e), exc_info=True)
                        time.sleep(60)
            
            except Exception as e:
                logger.error("donchian_monitor_error", error=str(e), exc_info=True)
            finally:
                self.donchian_monitor_running = False
                self.notifier.send_alert(
                    f"**Donchian Monitor Stopped**\n\n"
                    f"**Symbol:** {symbol}\n"
                    f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    color=0x808080
                )
        
        self.donchian_monitor_thread = threading.Thread(target=donchian_worker, daemon=True)
        self.donchian_monitor_thread.start()
        
        self.print_success(f"Donchian monitor started for {symbol} ({candle_type})")
    
    def stop_donchian_monitor(self):
        """Stop Donchian monitor"""
        if self.donchian_monitor_running:
            self.donchian_stop_event.set()
            if self.donchian_monitor_thread:
                self.donchian_monitor_thread.join(timeout=2)
            self.donchian_monitor_running = False
    
    def stop_all_monitors(self):
        """Stop all running monitors"""
        self.stop_rsi_monitor()
        self.stop_donchian_monitor()
    
    def tools_menu(self):
        """Tools submenu"""
        while True:
            self.print_header("Tools")
            print(f"{Fore.YELLOW}1. {Fore.WHITE}Position Size Calculator")
            print(f"{Fore.YELLOW}2. {Fore.WHITE}Export Portfolio to CSV")
            print(f"{Fore.YELLOW}3. {Fore.WHITE}Export Positions to CSV")
            print(f"{Fore.YELLOW}4. {Fore.WHITE}Export Holdings to CSV")
            print(f"{Fore.YELLOW}5. {Fore.WHITE}Back to Main Menu")
            
            choice = input(f"\n{Fore.CYAN}Enter choice (1-5): {Fore.WHITE}").strip()
            
            if choice == '1':
                self.position_size_calculator()
            elif choice == '2':
                self.export_portfolio()
            elif choice == '3':
                self.export_positions()
            elif choice == '4':
                self.export_holdings()
            elif choice == '5':
                break
            else:
                self.print_error("Invalid choice")
            
            if choice != '5':
                input(f"\n{Fore.CYAN}Press Enter to continue...")
    
    def position_size_calculator(self):
        """Calculate position size based on risk"""
        self.print_header("Position Size Calculator")
        
        try:
            account_size = float(input(f"{Fore.CYAN}Account Size (₹): {Fore.WHITE}").strip())
            risk_pct = float(input(f"{Fore.CYAN}Risk % per trade: {Fore.WHITE}").strip())
            entry_price = float(input(f"{Fore.CYAN}Entry Price (₹): {Fore.WHITE}").strip())
            stop_loss = float(input(f"{Fore.CYAN}Stop Loss (₹): {Fore.WHITE}").strip())
            
            risk_amount = account_size * (risk_pct / 100)
            risk_per_share = abs(entry_price - stop_loss)
            
            if risk_per_share == 0:
                self.print_error("Stop loss cannot equal entry price")
                return
            
            position_size = int(risk_amount / risk_per_share)
            position_value = position_size * entry_price
            
            print(f"\n{Fore.CYAN}Calculation Results:")
            print(f"  Risk Amount: ₹{risk_amount:,.2f}")
            print(f"  Risk per Share: ₹{risk_per_share:.2f}")
            print(f"  Position Size: {position_size} shares")
            print(f"  Position Value: ₹{position_value:,.2f}")
            print(f"  Max Loss: ₹{risk_amount:,.2f} ({risk_pct}%)")
            
        except ValueError:
            self.print_error("Invalid input. Please enter numeric values.")
        except Exception as e:
            self.print_error(f"Calculation failed: {str(e)}")
    
    def export_portfolio(self):
        """Export portfolio summary to CSV"""
        if not self.check_auth():
            return
        
        self.print_header("Export Portfolio")
        
        try:
            summary = get_portfolio_summary(self.trader)
            
            import csv
            filename = f"portfolio_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                for key, value in summary.items():
                    writer.writerow([key, value])
            
            self.print_success(f"Portfolio exported to {filename}")
            
        except Exception as e:
            self.print_error(f"Export failed: {str(e)}")
            logger.error("portfolio_export_failed", error=str(e), exc_info=True)
    
    def export_positions(self):
        """Export positions to CSV"""
        if not self.check_auth():
            return
        
        self.print_header("Export Positions")
        
        try:
            filename = export_positions_to_csv(self.trader)
            self.print_success(f"Positions exported to {filename}")
        except Exception as e:
            self.print_error(f"Export failed: {str(e)}")
            logger.error("positions_export_failed", error=str(e), exc_info=True)
    
    def export_holdings(self):
        """Export holdings to CSV"""
        if not self.check_auth():
            return
        
        self.print_header("Export Holdings")
        
        try:
            filename = export_holdings_to_csv(self.trader)
            self.print_success(f"Holdings exported to {filename}")
        except Exception as e:
            self.print_error(f"Export failed: {str(e)}")
            logger.error("holdings_export_failed", error=str(e), exc_info=True)
    
    def settings_menu(self):
        """Settings submenu"""
        while True:
            self.print_header("Settings")
            print(f"{Fore.YELLOW}1. {Fore.WHITE}Re-authenticate")
            print(f"{Fore.YELLOW}2. {Fore.WHITE}Clear Screen")
            print(f"{Fore.YELLOW}3. {Fore.WHITE}Toggle Auto-Refresh ({Fore.GREEN}ON{Fore.WHITE} if self.auto_refresh else {Fore.RED}OFF{Fore.WHITE})")
            print(f"{Fore.YELLOW}4. {Fore.WHITE}Back to Main Menu")
            
            choice = input(f"\n{Fore.CYAN}Enter choice (1-4): {Fore.WHITE}").strip()
            
            if choice == '1':
                self.authenticate()
            elif choice == '2':
                self.clear_screen()
            elif choice == '3':
                self.auto_refresh = not self.auto_refresh
                status = f"{Fore.GREEN}enabled" if self.auto_refresh else f"{Fore.RED}disabled"
                self.print_info(f"Auto-refresh {status}")
            elif choice == '4':
                break
            else:
                self.print_error("Invalid choice")
            
            if choice != '4':
                input(f"\n{Fore.CYAN}Press Enter to continue...")
    
    def run(self):
        """Main application loop"""
        self.clear_screen()
        self.print_header("Welcome to Enhanced Trading CLI")
        
        # Auto-authenticate on startup
        if not self.authenticate():
            self.print_warning("Please authenticate manually or check your credentials")
        
        while True:
            try:
                self.display_main_menu()
                choice = input(f"{Fore.CYAN}Enter choice (1-10): {Fore.WHITE}").strip()
                
                if choice == '1':
                    self.view_portfolio_summary()
                elif choice == '2':
                    self.view_positions()
                elif choice == '3':
                    self.view_holdings()
                elif choice == '4':
                    self.orders_menu()
                elif choice == '5':
                    self.view_margins()
                elif choice == '6':
                    self.view_market_data()
                elif choice == '7':
                    self.strategy_monitors_menu()
                elif choice == '8':
                    self.tools_menu()
                elif choice == '9':
                    self.settings_menu()
                elif choice == '10':
                    self.print_info("Stopping all monitors...")
                    self.stop_all_monitors()
                    self.print_success("Goodbye!")
                    break
                else:
                    self.print_error("Invalid choice. Please try again.")
                
                if choice != '10' and choice not in ['4', '7', '8', '9']:
                    input(f"\n{Fore.CYAN}Press Enter to continue...")
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}Interrupted by user")
                self.stop_all_monitors()
                self.print_success("Goodbye!")
                break
            except Exception as e:
                self.print_error(f"An error occurred: {str(e)}")
                logger.error("application_error", error=str(e), exc_info=True)
                input(f"\n{Fore.CYAN}Press Enter to continue...")


def main():
    """Entry point"""
    try:
        app = EnhancedTradingCLI()
        app.run()
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {str(e)}")
        logger.error("fatal_error", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
