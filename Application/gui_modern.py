#!/usr/bin/env python3
"""
Modern GUI Application for Zerodha Trading Bot using DearPyGui
Provides a professional trading terminal interface with real-time charts
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import dearpygui.dearpygui as dpg
import threading
from datetime import datetime
import webbrowser
from Core_Modules.trader import KiteTrader
from Core_Modules.auth import KiteAuth
from Core_Modules.utils import (
    get_portfolio_summary,
    export_positions_to_csv,
    export_holdings_to_csv
)


class ModernTradingGUI:
    def __init__(self):
        self.trader = None
        self.is_authenticated = False
        self.current_view = "welcome"
        
        # Data storage for charts
        self.portfolio_data = {
            'labels': [],
            'values': []
        }
        
        # Initialize DearPyGui
        dpg.create_context()
        
        # Configure for 4K/HiDPI displays
        dpg.configure_app(docking=True, docking_space=True)
        
        self.setup_theme()
        self.setup_ui()
        
        # Try to authenticate on startup (after UI is set up)
        threading.Timer(0.1, self.authenticate).start()
        threading.Timer(0.2, self.show_welcome).start()
    
    def setup_theme(self):
        """Setup custom theme for professional trading terminal look"""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (15, 15, 20))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (20, 20, 25))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 30, 35))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (40, 40, 45))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (50, 50, 55))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (10, 10, 15))
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (20, 20, 30))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (40, 120, 200))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (50, 140, 220))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (30, 100, 180))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (40, 120, 200))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (50, 140, 220))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (30, 100, 180))
                dpg.add_theme_color(dpg.mvThemeCol_Tab, (30, 30, 40))
                dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (50, 140, 220))
                dpg.add_theme_color(dpg.mvThemeCol_TabActive, (40, 120, 200))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
                
                # Increased sizes for 4K displays
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 12, 8)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 16, 10)
                dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 8, 6)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 18)
                dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 12)
        
        dpg.bind_theme(global_theme)
        
        # Set global font scaling for 4K displays
        dpg.set_global_font_scale(1.5)
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create the main window - don't use tags, just position it
        with dpg.window(label="Zerodha Trading Terminal", width=1400, height=900, pos=(50, 50)):
            
            # Status bar at top
            with dpg.group(horizontal=True):
                dpg.add_text("Status:", color=(150, 150, 150))
                dpg.add_text("Not Authenticated", tag="status_text", color=(255, 100, 100))
                dpg.add_spacer(width=20)
                dpg.add_button(label="🔐 Authenticate", callback=self.show_auth_dialog)
                dpg.add_button(label="🔄 Refresh", callback=self.refresh_view)
            
            dpg.add_separator()
            
            # Tab bar for different views
            with dpg.tab_bar(tag="main_tabs"):
                
                # Dashboard Tab
                with dpg.tab(label="📊 Dashboard"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Welcome to Trading Terminal", tag="dashboard_title")
                        dpg.add_separator()
                        dpg.add_text("", tag="dashboard_content", wrap=800)
                
                # Portfolio Tab
                with dpg.tab(label="💼 Portfolio"):
                    with dpg.child_window(height=-1):
                        self.setup_portfolio_view()
                
                # Positions Tab
                with dpg.tab(label="📈 Positions"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Current Positions", tag="positions_title")
                        dpg.add_separator()
                        with dpg.table(tag="positions_table", header_row=True, 
                                      resizable=True, borders_innerH=True, 
                                      borders_innerV=True, borders_outerH=True,
                                      borders_outerV=True):
                            dpg.add_table_column(label="Symbol")
                            dpg.add_table_column(label="Quantity")
                            dpg.add_table_column(label="Avg Price")
                            dpg.add_table_column(label="LTP")
                            dpg.add_table_column(label="P&L")
                
                # Holdings Tab
                with dpg.tab(label="🏢 Holdings"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Holdings", tag="holdings_title")
                        dpg.add_separator()
                        with dpg.table(tag="holdings_table", header_row=True,
                                      resizable=True, borders_innerH=True,
                                      borders_innerV=True, borders_outerH=True,
                                      borders_outerV=True):
                            dpg.add_table_column(label="Symbol")
                            dpg.add_table_column(label="Quantity")
                            dpg.add_table_column(label="Avg Price")
                            dpg.add_table_column(label="LTP")
                            dpg.add_table_column(label="Investment")
                            dpg.add_table_column(label="Current Value")
                            dpg.add_table_column(label="P&L")
                
                # Orders Tab
                with dpg.tab(label="📋 Orders"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Order History", tag="orders_title")
                        dpg.add_separator()
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="🎯 Place Order", callback=self.show_place_order_dialog)
                            dpg.add_button(label="⚡ Bracket Order", callback=self.show_bracket_order_dialog)
                        dpg.add_separator()
                        with dpg.table(tag="orders_table", header_row=True,
                                      resizable=True, borders_innerH=True,
                                      borders_innerV=True, borders_outerH=True,
                                      borders_outerV=True):
                            dpg.add_table_column(label="Time")
                            dpg.add_table_column(label="Symbol")
                            dpg.add_table_column(label="Type")
                            dpg.add_table_column(label="Qty")
                            dpg.add_table_column(label="Price")
                            dpg.add_table_column(label="Status")
                
                # Market Data Tab
                with dpg.tab(label="📉 Market"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Market Data", tag="market_title")
                        dpg.add_separator()
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(label="Symbols (comma-separated)", 
                                             tag="market_symbols",
                                             default_value="NSE:INFY,NSE:TCS,NSE:RELIANCE",
                                             width=400)
                            dpg.add_button(label="Fetch Quotes", callback=self.fetch_market_data)
                        dpg.add_separator()
                        dpg.add_text("", tag="market_data_display", wrap=800)
                
                # Tools Tab
                with dpg.tab(label="🛠️ Tools"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Trading Tools", tag="tools_title")
                        dpg.add_separator()
                        
                        with dpg.collapsing_header(label="Position Size Calculator", default_open=True):
                            dpg.add_input_float(label="Account Size (₹)", tag="calc_account", default_value=100000)
                            dpg.add_input_float(label="Risk % per trade", tag="calc_risk", default_value=1.0)
                            dpg.add_input_float(label="Entry Price (₹)", tag="calc_entry", default_value=0)
                            dpg.add_input_float(label="Stop Loss (₹)", tag="calc_sl", default_value=0)
                            dpg.add_button(label="Calculate", callback=self.calculate_position_size)
                            dpg.add_text("", tag="calc_result", wrap=600)
                        
                        dpg.add_separator()
                        
                        with dpg.collapsing_header(label="Export Data"):
                            dpg.add_button(label="💾 Export Portfolio", callback=self.export_portfolio)
                            dpg.add_text("", tag="export_status")
        
        # Don't call show_welcome here - it will be called after viewport is shown
    
    def setup_portfolio_view(self):
        """Setup portfolio view with charts"""
        dpg.add_text("Portfolio Summary", tag="portfolio_title")
        dpg.add_separator()
        
        # Summary metrics in a group
        with dpg.group(tag="portfolio_metrics"):
            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=120):
                    dpg.add_text("Available Margin", color=(150, 150, 150))
                    dpg.add_text("₹0.00", tag="margin_available", color=(100, 200, 100))
                
                dpg.add_spacer(width=20)
                
                with dpg.child_window(width=300, height=120):
                    dpg.add_text("Total P&L", color=(150, 150, 150))
                    dpg.add_text("₹0.00", tag="pnl_total", color=(100, 200, 100))
            
            dpg.add_spacer(height=10)
            
            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=120):
                    dpg.add_text("Day Positions P&L", color=(150, 150, 150))
                    dpg.add_text("₹0.00", tag="pnl_day", color=(100, 200, 100))
                
                dpg.add_spacer(width=20)
                
                with dpg.child_window(width=300, height=120):
                    dpg.add_text("Holdings P&L", color=(150, 150, 150))
                    dpg.add_text("₹0.00", tag="pnl_holdings", color=(100, 200, 100))
        
        dpg.add_separator()
        
        # P&L Chart placeholder
        with dpg.plot(label="Portfolio Performance", height=300, width=-1, tag="portfolio_chart"):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="", tag="portfolio_x_axis")
            dpg.add_plot_axis(dpg.mvYAxis, label="P&L (₹)", tag="portfolio_y_axis")
    
    def authenticate(self):
        """Try to authenticate with existing token"""
        try:
            self.update_status("Authenticating...", (255, 200, 0))
            self.trader = KiteTrader()
            self.is_authenticated = True
            self.update_status("Authenticated ✓", (100, 255, 100))
        except Exception as e:
            self.is_authenticated = False
            self.update_status("Not Authenticated ✗", (255, 100, 100))
    
    def update_status(self, text, color=(255, 255, 255)):
        """Update status bar text"""
        if dpg.does_item_exist("status_text"):
            dpg.set_value("status_text", text)
            dpg.configure_item("status_text", color=color)
    
    def show_welcome(self):
        """Show welcome message"""
        welcome_text = """Welcome to the Zerodha Trading Terminal!

This modern interface provides:

📊 Real-time Portfolio Monitoring
   • Live P&L tracking
   • Margin analysis
   • Performance charts

📈 Trading Operations
   • Place market and limit orders
   • Create bracket orders with SL/Target
   • View and manage order history

📉 Market Analysis
   • Real-time market data
   • Multiple symbol quotes
   • Position sizing calculator

💾 Data Management
   • Export portfolio to CSV
   • Track trading history

Select a tab above to get started!
"""
        if dpg.does_item_exist("dashboard_content"):
            dpg.set_value("dashboard_content", welcome_text)
    
    def show_auth_dialog(self):
        """Show authentication dialog"""
        if dpg.does_item_exist("auth_window"):
            dpg.delete_item("auth_window")
        
        with dpg.window(label="🔐 Zerodha Authentication", modal=True, 
                       tag="auth_window", width=700, height=600):
            dpg.add_text("Authentication Steps", color=(100, 200, 255))
            dpg.add_separator()
            
            instructions = """
STEP 1: Click 'Open Login Page' below
        → Opens Zerodha login in your browser

STEP 2: Login with your Zerodha credentials
        → Use your User ID, Password, and 2FA

STEP 3: After login, copy the request_token from redirect URL
        → URL format: http://127.0.0.1:5000/callback?request_token=XXXXX
        → Copy ONLY the token value (after request_token=)

STEP 4: Paste token below and click Authenticate
        → Token expires in 1-2 minutes, use immediately!
"""
            dpg.add_text(instructions, wrap=650)
            dpg.add_separator()
            
            dpg.add_button(label="🌐 STEP 1: Open Login Page", 
                          callback=self.open_login_page, width=300)
            dpg.add_text("", tag="auth_status", wrap=650)
            
            dpg.add_spacer(height=10)
            dpg.add_input_text(label="Request Token", tag="auth_token", width=500)
            dpg.add_button(label="🔑 Authenticate", callback=self.do_authenticate, width=300)
            
            dpg.add_spacer(height=10)
            dpg.add_text("", tag="auth_result", wrap=650)
            
            dpg.add_separator()
            dpg.add_button(label="Close", callback=lambda: dpg.delete_item("auth_window"))
    
    def open_login_page(self):
        """Open Zerodha login in browser"""
        try:
            from kiteconnect import KiteConnect
            from Core_Modules.config import Config
            
            kite = KiteConnect(api_key=Config.API_KEY)
            login_url = kite.login_url()
            webbrowser.open(login_url)
            
            dpg.set_value("auth_status", "✓ Login page opened. Complete login and copy request_token.")
            dpg.configure_item("auth_status", color=(100, 255, 100))
        except Exception as e:
            dpg.set_value("auth_status", f"✗ Error: {str(e)}")
            dpg.configure_item("auth_status", color=(255, 100, 100))
    
    def do_authenticate(self):
        """Perform authentication with request token"""
        request_token = dpg.get_value("auth_token").strip()
        
        if not request_token:
            dpg.set_value("auth_result", "Please enter request token!")
            dpg.configure_item("auth_result", color=(255, 100, 100))
            return
        
        dpg.set_value("auth_result", "Authenticating...")
        dpg.configure_item("auth_result", color=(255, 200, 0))
        
        def auth_thread():
            try:
                from kiteconnect import KiteConnect
                from Core_Modules.config import Config
                
                kite = KiteConnect(api_key=Config.API_KEY)
                data = kite.generate_session(request_token, api_secret=Config.API_SECRET)
                access_token = data['access_token']
                
                # Save token
                self._save_access_token(access_token)
                
                # Setup trader
                kite.set_access_token(access_token)
                self.trader = KiteTrader.__new__(KiteTrader)
                self.trader.kite = kite
                self.is_authenticated = True
                
                self.update_status("Authenticated ✓", (100, 255, 100))
                
                result_text = f"""✓ Authentication Successful!

User ID: {data.get('user_id')}
User Name: {data.get('user_name')}

Token saved. You can now start trading!"""
                
                dpg.set_value("auth_result", result_text)
                dpg.configure_item("auth_result", color=(100, 255, 100))
                
            except Exception as e:
                dpg.set_value("auth_result", f"✗ Authentication Failed!\n\n{str(e)}\n\nTry getting a fresh token.")
                dpg.configure_item("auth_result", color=(255, 100, 100))
        
        threading.Thread(target=auth_thread, daemon=True).start()
    
    def _save_access_token(self, access_token):
        """Save access token to .env file"""
        try:
            env_file = Path(__file__).parent.parent / 'Configuration' / '.env'
            
            if env_file.exists():
                with open(env_file, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            token_found = False
            for i, line in enumerate(lines):
                if line.startswith('ACCESS_TOKEN='):
                    lines[i] = f'ACCESS_TOKEN={access_token}\n'
                    token_found = True
                    break
            
            if not token_found:
                lines.append(f'ACCESS_TOKEN={access_token}\n')
            
            with open(env_file, 'w') as f:
                f.writelines(lines)
        except Exception as e:
            print(f"Warning: Could not save token: {e}")
    
    def check_auth(self):
        """Check if authenticated"""
        if not self.is_authenticated:
            self.show_auth_dialog()
            return False
        return True
    
    def refresh_view(self):
        """Refresh current view data"""
        if not self.check_auth():
            return
        
        # Determine which tab is active and refresh accordingly
        self.load_portfolio_data()
        self.load_positions_data()
        self.load_holdings_data()
        self.load_orders_data()
    
    def load_portfolio_data(self):
        """Load and display portfolio summary"""
        if not self.check_auth():
            return
        
        def fetch():
            try:
                summary = get_portfolio_summary(self.trader)
                
                # Update metrics
                dpg.set_value("margin_available", f"₹{summary['available_margin']:,.2f}")
                dpg.set_value("pnl_total", f"₹{summary['total_pnl']:,.2f}")
                dpg.set_value("pnl_day", f"₹{summary['day_positions_pnl']:,.2f}")
                dpg.set_value("pnl_holdings", f"₹{summary['holdings_pnl']:,.2f}")
                
                # Set colors based on P&L
                color_total = (100, 255, 100) if summary['total_pnl'] >= 0 else (255, 100, 100)
                color_day = (100, 255, 100) if summary['day_positions_pnl'] >= 0 else (255, 100, 100)
                color_holdings = (100, 255, 100) if summary['holdings_pnl'] >= 0 else (255, 100, 100)
                
                dpg.configure_item("pnl_total", color=color_total)
                dpg.configure_item("pnl_day", color=color_day)
                dpg.configure_item("pnl_holdings", color=color_holdings)
                
            except Exception as e:
                print(f"Error loading portfolio: {e}")
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def load_positions_data(self):
        """Load and display positions"""
        if not self.check_auth():
            return
        
        def fetch():
            try:
                positions = self.trader.get_positions()
                day_pos = [p for p in positions['day'] if p['quantity'] != 0]
                
                # Clear existing rows
                if dpg.does_item_exist("positions_table"):
                    children = dpg.get_item_children("positions_table", slot=1)
                    if children:
                        for child in children:
                            dpg.delete_item(child)
                
                # Add position rows
                for p in day_pos:
                    with dpg.table_row(parent="positions_table"):
                        dpg.add_text(p['tradingsymbol'])
                        dpg.add_text(f"{p['quantity']:,}")
                        dpg.add_text(f"₹{p['average_price']:.2f}")
                        dpg.add_text(f"₹{p['last_price']:.2f}")
                        pnl_color = (100, 255, 100) if p['pnl'] >= 0 else (255, 100, 100)
                        dpg.add_text(f"₹{p['pnl']:.2f}", color=pnl_color)
                
            except Exception as e:
                print(f"Error loading positions: {e}")
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def load_holdings_data(self):
        """Load and display holdings"""
        if not self.check_auth():
            return
        
        def fetch():
            try:
                holdings = self.trader.get_holdings()
                
                # Clear existing rows
                if dpg.does_item_exist("holdings_table"):
                    children = dpg.get_item_children("holdings_table", slot=1)
                    if children:
                        for child in children:
                            dpg.delete_item(child)
                
                # Add holding rows
                for h in holdings:
                    investment = h['average_price'] * h['quantity']
                    current_value = h['last_price'] * h['quantity']
                    
                    with dpg.table_row(parent="holdings_table"):
                        dpg.add_text(h['tradingsymbol'])
                        dpg.add_text(f"{h['quantity']:,}")
                        dpg.add_text(f"₹{h['average_price']:.2f}")
                        dpg.add_text(f"₹{h['last_price']:.2f}")
                        dpg.add_text(f"₹{investment:,.2f}")
                        dpg.add_text(f"₹{current_value:,.2f}")
                        pnl_color = (100, 255, 100) if h['pnl'] >= 0 else (255, 100, 100)
                        dpg.add_text(f"₹{h['pnl']:.2f}", color=pnl_color)
                
            except Exception as e:
                print(f"Error loading holdings: {e}")
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def load_orders_data(self):
        """Load and display order history"""
        if not self.check_auth():
            return
        
        def fetch():
            try:
                orders = self.trader.get_orders()
                
                # Clear existing rows
                if dpg.does_item_exist("orders_table"):
                    children = dpg.get_item_children("orders_table", slot=1)
                    if children:
                        for child in children:
                            dpg.delete_item(child)
                
                # Add order rows (last 20)
                for order in orders[-20:]:
                    with dpg.table_row(parent="orders_table"):
                        dpg.add_text(str(order['order_timestamp'])[:19])
                        dpg.add_text(order['tradingsymbol'])
                        dpg.add_text(f"{order['transaction_type']} {order['order_type']}")
                        dpg.add_text(f"{order['quantity']}")
                        dpg.add_text(f"₹{order.get('price', 0):.2f}")
                        dpg.add_text(order['status'])
                
            except Exception as e:
                print(f"Error loading orders: {e}")
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def fetch_market_data(self):
        """Fetch and display market quotes"""
        if not self.check_auth():
            return
        
        symbols_text = dpg.get_value("market_symbols")
        symbols = [s.strip() for s in symbols_text.split(',')]
        
        def fetch():
            try:
                quotes = self.trader.get_quote(*symbols)
                
                output = "=" * 60 + "\n"
                output += "MARKET DATA\n"
                output += "=" * 60 + "\n\n"
                
                for symbol, data in quotes.items():
                    output += f"{symbol}\n"
                    output += f"  LTP: ₹{data['last_price']:.2f}\n"
                    output += f"  Change: {data['net_change']:.2f}\n"
                    output += f"  Volume: {data.get('volume', 0):,}\n"
                    output += f"  OHLC: O:{data['ohlc']['open']:.2f} "
                    output += f"H:{data['ohlc']['high']:.2f} "
                    output += f"L:{data['ohlc']['low']:.2f} "
                    output += f"C:{data['ohlc']['close']:.2f}\n\n"
                
                dpg.set_value("market_data_display", output)
                
            except Exception as e:
                dpg.set_value("market_data_display", f"Error: {str(e)}")
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def show_place_order_dialog(self):
        """Show order placement dialog"""
        if not self.check_auth():
            return
        
        if dpg.does_item_exist("order_window"):
            dpg.delete_item("order_window")
        
        with dpg.window(label="🎯 Place Order", modal=True, tag="order_window",
                       width=500, height=500):
            dpg.add_input_text(label="Symbol", tag="order_symbol")
            dpg.add_combo(label="Exchange", items=["NSE", "BSE", "NFO", "MCX"],
                         default_value="NSE", tag="order_exchange")
            dpg.add_combo(label="Transaction", items=["BUY", "SELL"],
                         default_value="BUY", tag="order_transaction")
            dpg.add_input_int(label="Quantity", tag="order_quantity", default_value=1)
            dpg.add_combo(label="Order Type", items=["MARKET", "LIMIT"],
                         default_value="MARKET", tag="order_type")
            dpg.add_input_float(label="Price (if LIMIT)", tag="order_price")
            dpg.add_combo(label="Product", items=["MIS", "CNC", "NRML"],
                         default_value="MIS", tag="order_product")
            
            dpg.add_separator()
            dpg.add_button(label="Place Order", callback=self.place_order, width=200)
            dpg.add_text("", tag="order_result", wrap=450)
            dpg.add_separator()
            dpg.add_button(label="Close", callback=lambda: dpg.delete_item("order_window"))
    
    def place_order(self):
        """Place an order"""
        try:
            symbol = dpg.get_value("order_symbol")
            exchange = dpg.get_value("order_exchange")
            transaction = dpg.get_value("order_transaction")
            quantity = dpg.get_value("order_quantity")
            order_type = dpg.get_value("order_type")
            price = dpg.get_value("order_price") if order_type == "LIMIT" else None
            product = dpg.get_value("order_product")
            
            order_id = self.trader.place_order(
                symbol=symbol,
                exchange=exchange,
                transaction_type=transaction,
                quantity=quantity,
                order_type=order_type,
                price=price,
                product=product
            )
            
            dpg.set_value("order_result", f"✓ Order placed successfully!\nOrder ID: {order_id}")
            dpg.configure_item("order_result", color=(100, 255, 100))
            
        except Exception as e:
            dpg.set_value("order_result", f"✗ Error: {str(e)}")
            dpg.configure_item("order_result", color=(255, 100, 100))
    
    def show_bracket_order_dialog(self):
        """Show bracket order dialog"""
        if not self.check_auth():
            return
        
        if dpg.does_item_exist("bracket_window"):
            dpg.delete_item("bracket_window")
        
        with dpg.window(label="⚡ Bracket Order", modal=True, tag="bracket_window",
                       width=500, height=500):
            dpg.add_input_text(label="Symbol", tag="bracket_symbol")
            dpg.add_combo(label="Exchange", items=["NSE", "BSE", "NFO"],
                         default_value="NSE", tag="bracket_exchange")
            dpg.add_combo(label="Transaction", items=["BUY", "SELL"],
                         default_value="BUY", tag="bracket_transaction")
            dpg.add_input_int(label="Quantity", tag="bracket_quantity", default_value=1)
            dpg.add_input_float(label="Price", tag="bracket_price")
            dpg.add_input_float(label="Stop Loss (points)", tag="bracket_sl")
            dpg.add_input_float(label="Target (points)", tag="bracket_target")
            
            dpg.add_separator()
            dpg.add_button(label="Place Bracket Order", callback=self.place_bracket_order, width=200)
            dpg.add_text("", tag="bracket_result", wrap=450)
            dpg.add_separator()
            dpg.add_button(label="Close", callback=lambda: dpg.delete_item("bracket_window"))
    
    def place_bracket_order(self):
        """Place a bracket order"""
        try:
            symbol = dpg.get_value("bracket_symbol")
            exchange = dpg.get_value("bracket_exchange")
            transaction = dpg.get_value("bracket_transaction")
            quantity = dpg.get_value("bracket_quantity")
            price = dpg.get_value("bracket_price")
            sl = dpg.get_value("bracket_sl")
            target = dpg.get_value("bracket_target")
            
            order_id = self.trader.place_bracket_order(
                symbol=symbol,
                exchange=exchange,
                transaction_type=transaction,
                quantity=quantity,
                price=price,
                stoploss=sl,
                target=target
            )
            
            dpg.set_value("bracket_result", f"✓ Bracket order placed!\nOrder ID: {order_id}")
            dpg.configure_item("bracket_result", color=(100, 255, 100))
            
        except Exception as e:
            dpg.set_value("bracket_result", f"✗ Error: {str(e)}")
            dpg.configure_item("bracket_result", color=(255, 100, 100))
    
    def calculate_position_size(self):
        """Calculate position size"""
        try:
            account = dpg.get_value("calc_account")
            risk_pct = dpg.get_value("calc_risk")
            entry = dpg.get_value("calc_entry")
            sl = dpg.get_value("calc_sl")
            
            risk_amount = account * (risk_pct / 100)
            risk_per_share = abs(entry - sl)
            position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
            capital_required = position_size * entry
            
            result = f"""
Position Size Calculation:
========================
Account Size: ₹{account:,.2f}
Risk per Trade: {risk_pct}%
Risk Amount: ₹{risk_amount:,.2f}

Entry Price: ₹{entry:.2f}
Stop Loss: ₹{sl:.2f}
Risk per Share: ₹{risk_per_share:.2f}

📊 Recommended Position: {position_size} shares
💰 Capital Required: ₹{capital_required:,.2f}
"""
            dpg.set_value("calc_result", result)
            dpg.configure_item("calc_result", color=(100, 200, 255))
            
        except Exception as e:
            dpg.set_value("calc_result", f"Error: {str(e)}")
            dpg.configure_item("calc_result", color=(255, 100, 100))
    
    def export_portfolio(self):
        """Export portfolio to CSV"""
        if not self.check_auth():
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            positions_file = f"positions_{timestamp}.csv"
            holdings_file = f"holdings_{timestamp}.csv"
            
            export_positions_to_csv(self.trader, positions_file)
            export_holdings_to_csv(self.trader, holdings_file)
            
            dpg.set_value("export_status", 
                         f"✓ Exported:\n{positions_file}\n{holdings_file}")
            dpg.configure_item("export_status", color=(100, 255, 100))
        except Exception as e:
            dpg.set_value("export_status", f"✗ Error: {str(e)}")
            dpg.configure_item("export_status", color=(255, 100, 100))
    
    def run(self):
        """Run the application"""
        # Create viewport - simple approach that works
        dpg.create_viewport(title="Zerodha Trading Terminal", width=1600, height=1000)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


def main():
    """Main entry point"""
    app = ModernTradingGUI()
    app.run()


if __name__ == "__main__":
    main()
