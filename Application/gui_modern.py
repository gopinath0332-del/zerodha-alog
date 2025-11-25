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
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from Core_Modules.trader import KiteTrader
from Core_Modules.auth import KiteAuth
from Core_Modules.utils import (
    get_portfolio_summary,
    export_positions_to_csv,
    export_holdings_to_csv
)
from Core_Modules.logger import get_logger
from Core_Modules.notifications import create_notification_manager_from_config

logger = get_logger(__name__)


# Global variable to store request token from callback
_request_token_holder = {'token': None}


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth callback"""
    
    def do_GET(self):
        """Handle GET request from OAuth redirect"""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        if 'request_token' in params:
            _request_token_holder['token'] = params['request_token'][0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            success_html = """
            <html>
            <head><title>Authentication Success</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">✓ Authentication Successful!</h1>
                <p>Request token captured. You can close this window.</p>
                <p>Return to the application to complete authentication.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Error: No request token found</h1>")
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass


class ModernTradingGUI:
    def __init__(self):
        self.trader = None
        self.is_authenticated = False
        self.current_view = "welcome"
        self.request_token = None
        self.callback_server = None
        self.instruments_cache = None  # Cache for instruments list
        self.instruments_cache_time = None  # When cache was created
        self.instruments_cache_exchange = None  # Which exchange is cached
        self.rsi_monitor_running = False  # Track RSI monitor state
        self.current_rsi_value = None  # Track current RSI value for alerts
        self.current_rsi_symbol = None  # Track symbol being monitored
        self.rsi_alerted_candles = set()  # Track candle timestamps that triggered RSI alerts
        self.donchian_monitor_running = False  # Track Donchian monitor state
        self.current_donchian_price = None  # Track current price
        self.current_donchian_symbol = None  # Track symbol being monitored
        self.donchian_alerted_candles = set()  # Track candle timestamps that triggered alerts
        
        # Initialize notification system (email + Discord)
        self.notifier = create_notification_manager_from_config()
        
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
        # Load NATGASMINI futures for NatgasMini tab
        threading.Timer(0.3, self.load_natgasmini_futures).start()
        # Load GOLDPETAL futures for Donchian tab
        threading.Timer(0.3, self.load_goldpetal_futures).start()
    
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

        # Theme for active monitors (Green tab)
        with dpg.theme(tag="active_monitor_theme"):
            with dpg.theme_component(dpg.mvTab):
                dpg.add_theme_color(dpg.mvThemeCol_Tab, (0, 100, 0))
                dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (0, 150, 0))
                dpg.add_theme_color(dpg.mvThemeCol_TabActive, (0, 120, 0))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255))
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create the main window - don't use tags, just position it
        with dpg.window(label="Zerodha Trading Terminal", width=1400, height=900, pos=(50, 50)):
            
            # Status bar at top
            with dpg.group(horizontal=True):
                dpg.add_text("Status:", color=(150, 150, 150))
                dpg.add_text("Not Authenticated", tag="status_text", color=(255, 100, 100))
                dpg.add_spacer(width=20)
                dpg.add_button(label="Authenticate", callback=self.show_auth_dialog)
                dpg.add_button(label="Refresh", callback=self.refresh_view)
            
            dpg.add_separator()
            
            # Tab bar for different views
            with dpg.tab_bar(tag="main_tabs", callback=self.on_tab_change):
                
                # Dashboard Tab
                with dpg.tab(label="Dashboard"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Welcome to Trading Terminal", tag="dashboard_title")
                        dpg.add_separator()
                        dpg.add_text("", tag="dashboard_content", wrap=800)
                
                # Portfolio Tab
                with dpg.tab(label="Portfolio"):
                    with dpg.child_window(height=-1):
                        self.setup_portfolio_view()
                
                # Positions Tab
                with dpg.tab(label="Positions"):
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
                            dpg.add_table_column(label="Invested")
                            dpg.add_table_column(label="LTP")
                            dpg.add_table_column(label="P&L")
                
                # Margins Tab
                with dpg.tab(label="Margins"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Account Margins", tag="margins_title")
                        dpg.add_separator()
                        
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="Refresh Margins", callback=self.refresh_margins)
                            dpg.add_spacer(width=20)
                            dpg.add_text("Last updated: --", tag="margins_last_update", color=(150, 150, 150))
                        
                        dpg.add_separator()
                        
                        # Equity Margins
                        with dpg.collapsing_header(label="Equity", default_open=True):
                            with dpg.table(header_row=True, resizable=True, 
                                         borders_innerH=True, borders_innerV=True,
                                         borders_outerH=True, borders_outerV=True):
                                dpg.add_table_column(label="Metric")
                                dpg.add_table_column(label="Value")
                                
                                with dpg.table_row():
                                    dpg.add_text("Available Cash")
                                    dpg.add_text("Rs.0.00", tag="equity_available_cash", color=(100, 255, 100))
                                
                                with dpg.table_row():
                                    dpg.add_text("Available Margin")
                                    dpg.add_text("Rs.0.00", tag="equity_available", color=(100, 200, 255))
                                
                                with dpg.table_row():
                                    dpg.add_text("Used Margin")
                                    dpg.add_text("Rs.0.00", tag="equity_used", color=(255, 200, 100))
                                
                                with dpg.table_row():
                                    dpg.add_text("Collateral")
                                    dpg.add_text("Rs.0.00", tag="equity_collateral")
                        
                        dpg.add_spacer(height=10)
                        
                        # Commodity Margins
                        with dpg.collapsing_header(label="Commodity", default_open=True):
                            with dpg.table(header_row=True, resizable=True,
                                         borders_innerH=True, borders_innerV=True,
                                         borders_outerH=True, borders_outerV=True):
                                dpg.add_table_column(label="Metric")
                                dpg.add_table_column(label="Value")
                                
                                with dpg.table_row():
                                    dpg.add_text("Available Cash")
                                    dpg.add_text("Rs.0.00", tag="commodity_available_cash", color=(100, 255, 100))
                                
                                with dpg.table_row():
                                    dpg.add_text("Available Margin")
                                    dpg.add_text("Rs.0.00", tag="commodity_available", color=(100, 200, 255))
                                
                                with dpg.table_row():
                                    dpg.add_text("Used Margin")
                                    dpg.add_text("Rs.0.00", tag="commodity_used", color=(255, 200, 100))
                                
                                with dpg.table_row():
                                    dpg.add_text("Collateral")
                                    dpg.add_text("Rs.0.00", tag="commodity_collateral")
                
                # Holdings Tab
                with dpg.tab(label="Holdings"):
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
                with dpg.tab(label="Orders"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Order History", tag="orders_title")
                        dpg.add_separator()
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="Place Order", callback=self.show_place_order_dialog)
                            dpg.add_button(label="Bracket Order", callback=self.show_bracket_order_dialog)
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
                with dpg.tab(label="Market"):
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
                with dpg.tab(label="Tools"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Trading Tools", tag="tools_title")
                        dpg.add_separator()
                        
                        with dpg.collapsing_header(label="Position Size Calculator", default_open=True):
                            dpg.add_input_float(label="Account Size (Rs.)", tag="calc_account", default_value=100000)
                            dpg.add_input_float(label="Risk % per trade", tag="calc_risk", default_value=1.0)
                            dpg.add_input_float(label="Entry Price (Rs.)", tag="calc_entry", default_value=0)
                            dpg.add_input_float(label="Stop Loss (Rs.)", tag="calc_sl", default_value=0)
                            dpg.add_button(label="Calculate", callback=self.calculate_position_size)
                            dpg.add_text("", tag="calc_result", wrap=600)
                        
                        dpg.add_separator()
                        
                        with dpg.collapsing_header(label="Export Data"):
                            dpg.add_button(label="Export Portfolio", callback=self.export_portfolio)
                            dpg.add_text("", tag="export_status")
                
                # NatgasMini RSI Monitor Tab
                with dpg.tab(label="NatgasMini", tag="tab_natgasmini"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("RSI Live Monitor - NATGASMINI", tag="rsi_title")
                        dpg.add_separator()
                        with dpg.group(horizontal=True):
                            dpg.add_combo(label="Future", tag="rsi_contract", items=[], width=400, callback=self.on_contract_change)
                            dpg.add_spacer(width=10)
                            dpg.add_input_text(label="Symbol", tag="rsi_symbol", default_value="NATGASMINI", width=150)
                        dpg.add_combo(label="Interval", tag="rsi_interval", items=["1hour"], default_value="1hour", width=120)
                        # Candle type selection (radio box, default Heikin Ashi)
                        dpg.add_radio_button(items=["Heikin Ashi", "Normal"], tag="rsi_candle_type", default_value="Heikin Ashi", horizontal=True)
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="Launch RSI Monitor", tag="rsi_start_btn", callback=self.launch_rsi_monitor)
                            dpg.add_button(label="Stop Monitor", tag="rsi_stop_btn", callback=self.stop_rsi_monitor, show=False)
                        dpg.add_spacer(height=10)
                        dpg.add_text("Current RSI: --", tag="rsi_current_value", color=(200,200,255))
                        dpg.add_text("Last Alert: --", tag="rsi_last_alert", color=(255,200,100))
                        dpg.add_spacer(height=10)
                        dpg.add_text("Status: Idle", tag="rsi_status", color=(150,150,150))
                        dpg.add_separator()
                        dpg.add_text("Alerts: RSI > 70 (Overbought), RSI < 30 (Oversold)", color=(255,255,255))
                        dpg.add_spacer(height=10)
                        dpg.add_text("Note: RSI matches Zerodha chart (period=14, close)", color=(150,255,150))
                
                # GOLDPETAL Donchian Channel Tab
                with dpg.tab(label="GOLDPETAL", tag="tab_goldpetal"):
                    with dpg.child_window(height=-1):
                        dpg.add_text("Donchian Channel Strategy Monitor", tag="donchian_title")
                        dpg.add_separator()
                        with dpg.group(horizontal=True):
                            dpg.add_combo(label="Future", tag="donchian_contract", items=[], width=400, callback=self.on_donchian_contract_change)
                            dpg.add_spacer(width=10)
                            dpg.add_input_text(label="Symbol", tag="donchian_symbol", default_value="GOLDPETAL", width=150)
                        dpg.add_combo(label="Interval", tag="donchian_interval", items=["1hour"], default_value="1hour", width=120)
                        # Candle type selection for Donchian (radio box, default Heikin Ashi)
                        dpg.add_radio_button(items=["Heikin Ashi", "Normal"], tag="donchian_candle_type", default_value="Heikin Ashi", horizontal=True)
                        with dpg.group(horizontal=True):
                            dpg.add_button(label="Launch Donchian Monitor", tag="donchian_start_btn", callback=self.launch_donchian_monitor)
                            dpg.add_button(label="Stop Monitor", tag="donchian_stop_btn", callback=self.stop_donchian_monitor, show=False)
                        dpg.add_spacer(height=10)
                        dpg.add_text("Current Price: --", tag="donchian_current_price", color=(200,200,255))
                        dpg.add_text("Upper Band: --", tag="donchian_upper_band", color=(255,200,100))
                        dpg.add_text("Lower Band: --", tag="donchian_lower_band", color=(100,200,255))
                        dpg.add_text("Last Alert: --", tag="donchian_last_alert", color=(255,200,100))
                        dpg.add_spacer(height=10)
                        dpg.add_text("Status: Idle", tag="donchian_status", color=(150,150,150))
                        dpg.add_separator()
                        dpg.add_text("Alerts: Price breaks above Upper Band (Bullish) or below Lower Band (Bearish)", color=(255,255,255))
                        dpg.add_spacer(height=10)
                        dpg.add_text("Note: Donchian Channels identify trend reversals and breakouts", color=(150,255,150))
        
        # Don't call show_welcome here - it will be called after viewport is shown
    
    def setup_portfolio_view(self):
        """Setup portfolio view with charts"""
        dpg.add_text("Portfolio Summary", tag="portfolio_title")
        dpg.add_separator()
        
        # Summary metrics in a 3x3 grid
        with dpg.group(tag="portfolio_metrics"):
            # Row 1
            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=120):
                    dpg.add_text("Available Margin", color=(150, 150, 150))
                    dpg.add_text("Rs.0.00", tag="margin_available", color=(100, 200, 100))
                
                dpg.add_spacer(width=20)
                
                with dpg.child_window(width=300, height=120):
                    dpg.add_text("Capital Used", color=(150, 150, 150))
                    dpg.add_text("Rs.0.00", tag="capital_used", color=(255, 200, 100))
                
                dpg.add_spacer(width=20)
                
                with dpg.child_window(width=300, height=120):
                    dpg.add_text("Position P&L", color=(150, 150, 150))
                    dpg.add_text("Rs.0.00", tag="pnl_positions", color=(100, 200, 100))
            
            dpg.add_spacer(height=10)
            
            # Row 2
            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=120):
                    dpg.add_text("Holdings P&L", color=(150, 150, 150))
                    dpg.add_text("Rs.0.00", tag="pnl_holdings", color=(100, 200, 100))
                
                dpg.add_spacer(width=20)
                
                with dpg.child_window(width=300, height=120):
                    dpg.add_text("Total P&L", color=(150, 150, 150))
                    dpg.add_text("Rs.0.00", tag="pnl_total", color=(100, 200, 100))
                
                dpg.add_spacer(width=20)
                
                with dpg.child_window(width=300, height=120):
                    dpg.add_text("", color=(150, 150, 150))
                    dpg.add_text("", color=(100, 200, 100))
        
        dpg.add_separator()
    
    def authenticate(self):
        """Try to authenticate with existing token"""
        try:
            self.update_status("Authenticating...", (255, 200, 0))
            self.trader = KiteTrader()
            self.is_authenticated = True
            self.update_status("Authenticated", (100, 255, 100))
        except Exception as e:
            self.is_authenticated = False
            self.update_status("Not Authenticated", (255, 100, 100))
    
    def update_status(self, text, color=(255, 255, 255)):
        """Update status bar text"""
        if dpg.does_item_exist("status_text"):
            dpg.set_value("status_text", text)
            dpg.configure_item("status_text", color=color)
    
    def show_welcome(self):
        """Show welcome message"""
        welcome_text = """Welcome to the Zerodha Trading Terminal!

This modern interface provides:

Real-time Portfolio Monitoring
   - Live P&L tracking
   - Margin analysis
   - Performance charts

Trading Operations
   - Place market and limit orders
   - Create bracket orders with SL/Target
   - View and manage order history

Market Analysis
   - Real-time market data
   - Multiple symbol quotes
   - Position sizing calculator

Data Management
   - Export portfolio to CSV
   - Track trading history

Select a tab above to get started!
"""
        if dpg.does_item_exist("dashboard_content"):
            dpg.set_value("dashboard_content", welcome_text)
    
    def show_auth_dialog(self):
        """Show authentication dialog"""
        if dpg.does_item_exist("auth_window"):
            dpg.delete_item("auth_window")
        
        with dpg.window(label="Zerodha Authentication", modal=True, 
                       tag="auth_window", width=700, height=500):
            dpg.add_text("Automated Authentication", color=(100, 200, 255))
            dpg.add_separator()
            
            instructions = """
AUTOMATED PROCESS:

1. Click 'Start Authentication' below
   → Starts local callback server
   → Opens Zerodha login in your browser

2. Login with your Zerodha credentials
   → Use your User ID, Password, and 2FA

3. Automatic token capture
   → After login, you'll be redirected back
   → Token is captured automatically
   → Authentication completes in the background

No manual copy-paste needed!
"""
            dpg.add_text(instructions, wrap=650)
            dpg.add_separator()
            
            dpg.add_button(label="Start Authentication", 
                          callback=self.start_auto_auth, width=300)
            dpg.add_text("", tag="auth_status", wrap=650, color=(150, 150, 150))
            
            dpg.add_spacer(height=20)
            dpg.add_separator()
            dpg.add_text("Manual Mode (if auto-mode fails):", color=(150, 150, 150))
            dpg.add_input_text(label="Request Token", tag="auth_token", width=500)
            dpg.add_button(label="Authenticate Manually", callback=self.do_authenticate, width=300)
            
            dpg.add_spacer(height=10)
            dpg.add_text("", tag="auth_result", wrap=650)
            
            dpg.add_separator()
            dpg.add_button(label="Close", callback=lambda: dpg.delete_item("auth_window"))
    
    def start_auto_auth(self):
        """Start automated authentication with callback server"""
        global _request_token_holder
        _request_token_holder['token'] = None
        
        dpg.set_value("auth_status", "Starting local callback server...")
        dpg.configure_item("auth_status", color=(255, 200, 0))
        
        def auth_process():
            try:
                # Start callback server in background
                server_address = ('127.0.0.1', 8888)
                httpd = HTTPServer(server_address, CallbackHandler)
                
                # Start server in a thread
                server_thread = threading.Thread(target=httpd.handle_request, daemon=True)
                server_thread.start()
                
                dpg.set_value("auth_status", "Callback server started on http://127.0.0.1:8888\nOpening login page...")
                
                # Open login page with callback URL
                from kiteconnect import KiteConnect
                from Core_Modules.config import Config
                
                kite = KiteConnect(api_key=Config.API_KEY)
                # Override redirect URL to point to our local server
                login_url = f"https://kite.zerodha.com/connect/login?api_key={Config.API_KEY}&v=3"
                webbrowser.open(login_url)
                
                dpg.set_value("auth_status", "Login page opened in browser.\nWaiting for authentication...\n\nPlease login with your Zerodha credentials.")
                dpg.configure_item("auth_status", color=(100, 200, 255))
                
                # Wait for token (with timeout)
                import time
                timeout = 120  # 2 minutes
                elapsed = 0
                while _request_token_holder['token'] is None and elapsed < timeout:
                    time.sleep(0.5)
                    elapsed += 0.5
                
                if _request_token_holder['token']:
                    # Token received, complete authentication
                    dpg.set_value("auth_status", "Token received! Completing authentication...")
                    dpg.configure_item("auth_status", color=(100, 255, 100))
                    
                    # Set the token in the input field
                    dpg.set_value("auth_token", _request_token_holder['token'])
                    
                    # Authenticate automatically
                    threading.Timer(0.5, self.do_authenticate).start()
                else:
                    dpg.set_value("auth_status", "Timeout waiting for authentication.\nPlease try manual mode or restart.")
                    dpg.configure_item("auth_status", color=(255, 100, 100))
                
            except Exception as e:
                dpg.set_value("auth_status", f"Error: {str(e)}\n\nPlease use manual mode.")
                dpg.configure_item("auth_status", color=(255, 100, 100))
        
        threading.Thread(target=auth_process, daemon=True).start()
    
    def open_login_page(self):
        """Open Zerodha login in browser"""
        try:
            from kiteconnect import KiteConnect
            from Core_Modules.config import Config
            
            kite = KiteConnect(api_key=Config.API_KEY)
            login_url = kite.login_url()
            webbrowser.open(login_url)
            
            dpg.set_value("auth_status", "Login page opened. Complete login and copy request_token.")
            dpg.configure_item("auth_status", color=(100, 255, 100))
        except Exception as e:
            dpg.set_value("auth_status", f"Error: {str(e)}")
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
                
                self.update_status("Authenticated", (100, 255, 100))
                
                result_text = f"""Authentication Successful!

User ID: {data.get('user_id')}
User Name: {data.get('user_name')}

Token saved. You can now start trading!"""
                
                dpg.set_value("auth_result", result_text)
                dpg.configure_item("auth_result", color=(100, 255, 100))
                
            except Exception as e:
                dpg.set_value("auth_result", f"Authentication Failed!\n\n{str(e)}\n\nTry getting a fresh token.")
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
            logger.warning("token_save_failed", error=str(e))
    
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
        
        # Refresh all data
        self.load_portfolio_data()
        self.load_positions_data()
        self.load_holdings_data()
        self.load_orders_data()
    
    def on_tab_change(self, sender, app_data):
        """Callback when tab is changed - auto-refresh data"""
        if not self.is_authenticated:
            return
        
        # Get the current tab label
        current_tab = dpg.get_item_label(app_data)
        
        # Refresh data based on which tab is selected
        if current_tab == "Portfolio":
            self.load_portfolio_data()
        elif current_tab == "Positions":
            self.load_positions_data()
        elif current_tab == "Holdings":
            self.load_holdings_data()
        elif current_tab == "Orders":
            self.load_orders_data()
        elif current_tab == "Margins":
            self.refresh_margins()
    
    def refresh_margins(self):
        """Refresh margin data"""
        if not self.check_auth():
            return
        
        def load_thread():
            try:
                # Get margins for equity and commodity
                equity_margins = self.trader.kite.margins('equity')
                commodity_margins = self.trader.kite.margins('commodity')
                
                # Update equity margins
                if dpg.does_item_exist("equity_available_cash"):
                    dpg.set_value("equity_available_cash", 
                                f"Rs.{equity_margins.get('available', {}).get('cash', 0):,.2f}")
                if dpg.does_item_exist("equity_available"):
                    dpg.set_value("equity_available", 
                                f"Rs.{equity_margins.get('available', {}).get('live_balance', 0):,.2f}")
                if dpg.does_item_exist("equity_used"):
                    dpg.set_value("equity_used", 
                                f"Rs.{equity_margins.get('utilised', {}).get('debits', 0):,.2f}")
                if dpg.does_item_exist("equity_collateral"):
                    dpg.set_value("equity_collateral", 
                                f"Rs.{equity_margins.get('available', {}).get('collateral', 0):,.2f}")
                
                # Update commodity margins
                if dpg.does_item_exist("commodity_available_cash"):
                    dpg.set_value("commodity_available_cash", 
                                f"Rs.{commodity_margins.get('available', {}).get('cash', 0):,.2f}")
                if dpg.does_item_exist("commodity_available"):
                    dpg.set_value("commodity_available", 
                                f"Rs.{commodity_margins.get('available', {}).get('live_balance', 0):,.2f}")
                if dpg.does_item_exist("commodity_used"):
                    dpg.set_value("commodity_used", 
                                f"Rs.{commodity_margins.get('utilised', {}).get('debits', 0):,.2f}")
                if dpg.does_item_exist("commodity_collateral"):
                    dpg.set_value("commodity_collateral", 
                                f"Rs.{commodity_margins.get('available', {}).get('collateral', 0):,.2f}")
                
                # Update timestamp
                if dpg.does_item_exist("margins_last_update"):
                    dpg.set_value("margins_last_update", 
                                f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
                
            except Exception as e:
                logger.error("margins_load_failed", error=str(e), exc_info=True)
                if dpg.does_item_exist("margins_last_update"):
                    dpg.set_value("margins_last_update", f"Error: {str(e)}")
                    dpg.configure_item("margins_last_update", color=(255, 100, 100))
        
        threading.Thread(target=load_thread, daemon=True).start()
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
                dpg.set_value("margin_available", f"Rs.{summary['available_margin']:,.2f}")
                dpg.set_value("pnl_positions", f"Rs.{summary['positions_pnl']:,.2f}")
                dpg.set_value("pnl_holdings", f"Rs.{summary['holdings_pnl']:,.2f}")
                dpg.set_value("pnl_total", f"Rs.{summary['total_pnl']:,.2f}")
                dpg.set_value("capital_used", f"Rs.{summary['capital_used']:,.2f}")
                
                # Set colors based on P&L
                color_positions = (100, 255, 100) if summary['positions_pnl'] >= 0 else (255, 100, 100)
                color_holdings = (100, 255, 100) if summary['holdings_pnl'] >= 0 else (255, 100, 100)
                color_total = (100, 255, 100) if summary['total_pnl'] >= 0 else (255, 100, 100)
                
                dpg.configure_item("pnl_positions", color=color_positions)
                dpg.configure_item("pnl_holdings", color=color_holdings)
                dpg.configure_item("pnl_total", color=color_total)
                
            except Exception as e:
                logger.error("portfolio_load_failed", error=str(e), exc_info=True)
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def load_positions_data(self):
        """Load and display positions"""
        if not self.check_auth():
            return
        
        def fetch():
            try:
                positions = self.trader.get_positions()
                # Get both day and net positions (net includes NRML/carry-forward positions)
                day_pos = [p for p in positions.get('day', []) if p['quantity'] != 0]
                net_pos = [p for p in positions.get('net', []) if p['quantity'] != 0]
                
                # Combine both, but avoid duplicates by using tradingsymbol as key
                all_positions = {}
                for p in day_pos:
                    all_positions[p['tradingsymbol']] = p
                for p in net_pos:
                    # Net positions take precedence as they show the actual position
                    if p['tradingsymbol'] not in all_positions or p['quantity'] != 0:
                        all_positions[p['tradingsymbol']] = p
                
                # Clear existing rows
                if dpg.does_item_exist("positions_table"):
                    children = dpg.get_item_children("positions_table", slot=1)
                    if children:
                        for child in children:
                            dpg.delete_item(child)
                
                # Add position rows
                for symbol, p in all_positions.items():
                    with dpg.table_row(parent="positions_table"):
                        dpg.add_text(p['tradingsymbol'])
                        dpg.add_text(f"{p['quantity']:,}")
                        dpg.add_text(f"Rs.{p['average_price']:.2f}")
                        
                        # Calculate actual margin/capital used for this position
                        # Use order_margins API to get the correct margin requirement
                        try:
                            margin_data = self.trader.kite.order_margins([{
                                'exchange': p['exchange'],
                                'tradingsymbol': p['tradingsymbol'],
                                'transaction_type': 'BUY' if p['quantity'] > 0 else 'SELL',
                                'variety': 'regular',
                                'product': p['product'],
                                'order_type': 'MARKET',
                                'quantity': abs(p['quantity']),
                                'price': 0,
                                'trigger_price': 0
                            }])
                            
                            # Extract total margin required
                            if margin_data and len(margin_data) > 0:
                                invested = margin_data[0].get('total', 0)
                            else:
                                # Fallback to buy_value/sell_value if margin calculation fails
                                invested = p.get('buy_value', 0) if p['quantity'] > 0 else p.get('sell_value', 0)
                        except Exception as e:
                            logger.warning("margin_calculation_failed", 
                                         symbol=p['tradingsymbol'], 
                                         error=str(e))
                            # Fallback to buy_value/sell_value
                            invested = p.get('buy_value', 0) if p['quantity'] > 0 else p.get('sell_value', 0)
                        
                        dpg.add_text(f"Rs.{invested:,.2f}")
                        dpg.add_text(f"Rs.{p['last_price']:.2f}")
                        pnl_color = (100, 255, 100) if p['pnl'] >= 0 else (255, 100, 100)
                        dpg.add_text(f"Rs.{p['pnl']:.2f}", color=pnl_color)
                
            except Exception as e:
                logger.error("positions_load_failed", error=str(e), exc_info=True)
        
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
                        dpg.add_text(f"Rs.{h['average_price']:.2f}")
                        dpg.add_text(f"Rs.{h['last_price']:.2f}")
                        dpg.add_text(f"Rs.{investment:,.2f}")
                        dpg.add_text(f"Rs.{current_value:,.2f}")
                        pnl_color = (100, 255, 100) if h['pnl'] >= 0 else (255, 100, 100)
                        dpg.add_text(f"Rs.{h['pnl']:.2f}", color=pnl_color)
                
            except Exception as e:
                logger.error("holdings_load_failed", error=str(e), exc_info=True)
        
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
                        dpg.add_text(f"Rs.{order.get('price', 0):.2f}")
                        dpg.add_text(order['status'])
                
            except Exception as e:
                logger.error("orders_load_failed", error=str(e), exc_info=True)
        
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
                    output += f"  LTP: Rs.{data['last_price']:.2f}\n"
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
        
        with dpg.window(label="Place Order", modal=True, tag="order_window",
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
            
            dpg.set_value("order_result", f"Order placed successfully!\nOrder ID: {order_id}")
            dpg.configure_item("order_result", color=(100, 255, 100))
            
        except Exception as e:
            dpg.set_value("order_result", f"Error: {str(e)}")
            dpg.configure_item("order_result", color=(255, 100, 100))
    
    def show_bracket_order_dialog(self):
        """Show bracket order dialog"""
        if not self.check_auth():
            return
        
        if dpg.does_item_exist("bracket_window"):
            dpg.delete_item("bracket_window")
        
        with dpg.window(label="Bracket Order", modal=True, tag="bracket_window",
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
            
            dpg.set_value("bracket_result", f"Bracket order placed!\nOrder ID: {order_id}")
            dpg.configure_item("bracket_result", color=(100, 255, 100))
            
        except Exception as e:
            dpg.set_value("bracket_result", f"Error: {str(e)}")
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
Account Size: Rs.{account:,.2f}
Risk per Trade: {risk_pct}%
Risk Amount: Rs.{risk_amount:,.2f}

Entry Price: Rs.{entry:.2f}
Stop Loss: Rs.{sl:.2f}
Risk per Share: Rs.{risk_per_share:.2f}

Recommended Position: {position_size} shares
Capital Required: Rs.{capital_required:,.2f}
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
                         f"Exported:\n{positions_file}\n{holdings_file}")
            dpg.configure_item("export_status", color=(100, 255, 100))
        except Exception as e:
            dpg.set_value("export_status", f"Error: {str(e)}")
            dpg.configure_item("export_status", color=(255, 100, 100))
    
    def on_exchange_change(self):
        """Handle exchange selection change"""
        exchange = dpg.get_value("rsi_exchange")
        
        # Show/hide future dropdown based on exchange
        if exchange == "MCX":
            dpg.configure_item("rsi_contract", show=True)
            dpg.configure_item("rsi_symbol", show=False)
            self.load_mcx_futures()
        elif exchange == "NCDEX":
            dpg.configure_item("rsi_contract", show=True)
            dpg.configure_item("rsi_symbol", show=False)
            self.load_ncdex_futures()
        else:  # NSE
            dpg.configure_item("rsi_contract", show=False)
            dpg.configure_item("rsi_symbol", show=True)
            dpg.set_value("rsi_symbol", "RELIANCE")
    
    def on_contract_change(self):
        """Handle Future contract selection change"""
        contract = dpg.get_value("rsi_contract")
        if contract:
            dpg.set_value("rsi_symbol", contract)
    
    def load_natgasmini_futures(self):
        """Load NATGASMINI futures from MCX API"""
        def fetch_natgasmini():
            try:
                from Core_Modules.config import Config
                from kiteconnect import KiteConnect
                import importlib
                import Core_Modules.config as config_module
                importlib.reload(config_module)
                
                kite = KiteConnect(api_key=Config.API_KEY)
                kite.set_access_token(Config.ACCESS_TOKEN)
                
                instruments = kite.instruments(exchange="MCX")
                # Get NATGASMINI FUT (futures) only, exclude PE/CE (options)
                futures = []
                for inst in instruments:
                    symbol = inst['tradingsymbol']
                    instrument_type = inst.get('instrument_type', '')
                    if 'NATGASMINI' in symbol and instrument_type == 'FUT':
                        futures.append(symbol)
                
                # Sort futures
                futures = sorted(futures)
                dpg.configure_item("rsi_contract", items=futures)
                if futures:
                    # Auto-select first one
                    dpg.set_value("rsi_contract", futures[0])
                    self.on_contract_change()
                logger.info("natgasmini_futures_loaded", count=len(futures))
            except Exception as e:
                logger.error("natgasmini_futures_load_failed", error=str(e), exc_info=True)
                dpg.configure_item("rsi_contract", items=["Error loading futures"])
        
        threading.Thread(target=fetch_natgasmini, daemon=True).start()
    
    def load_mcx_futures(self):
        """Load MCX NATGASMINI futures from API (for backward compatibility)"""
        self.load_natgasmini_futures()
    
    def load_ncdex_futures(self):
        """Load NCDEX futures from API"""
        def fetch_ncdex():
            try:
                from Core_Modules.config import Config
                from kiteconnect import KiteConnect
                import importlib
                import Core_Modules.config as config_module
                importlib.reload(config_module)
                
                kite = KiteConnect(api_key=Config.API_KEY)
                kite.set_access_token(Config.ACCESS_TOKEN)
                
                instruments = kite.instruments(exchange="NCDEX")
                # Get all NCDEX FUT (futures) only, exclude PE/CE (options)
                futures = []
                for inst in instruments:
                    symbol = inst['tradingsymbol']
                    instrument_type = inst.get('instrument_type', '')
                    if instrument_type == 'FUT':
                        futures.append(symbol)
                
                # Sort futures
                futures = sorted(futures)
                dpg.configure_item("rsi_contract", items=futures)
                logger.info("ncdex_futures_loaded", count=len(futures))
            except Exception as e:
                logger.error("ncdex_futures_load_failed", error=str(e), exc_info=True)
                dpg.configure_item("rsi_contract", items=["Error loading futures"])
        
        threading.Thread(target=fetch_ncdex, daemon=True).start()
    
    def load_goldpetal_futures(self):
        """Load GOLDPETAL futures from MCX API"""
        def fetch_goldpetal():
            try:
                from Core_Modules.config import Config
                from kiteconnect import KiteConnect
                import importlib
                import Core_Modules.config as config_module
                importlib.reload(config_module)
                
                kite = KiteConnect(api_key=Config.API_KEY)
                kite.set_access_token(Config.ACCESS_TOKEN)
                
                instruments = kite.instruments(exchange="MCX")
                # Get GOLDPETAL FUT (futures) only, exclude PE/CE (options)
                goldpetal_futures = []
                for inst in instruments:
                    symbol = inst['tradingsymbol']
                    instrument_type = inst.get('instrument_type', '')
                    if 'GOLDPETAL' in symbol and instrument_type == 'FUT':
                        goldpetal_futures.append(symbol)
                
                # Sort futures by expiry
                goldpetal_futures = sorted(goldpetal_futures)
                dpg.configure_item("donchian_contract", items=goldpetal_futures)
                if goldpetal_futures:
                    # Auto-select first one
                    dpg.set_value("donchian_contract", goldpetal_futures[0])
                    self.on_donchian_contract_change()
                logger.info("goldpetal_futures_loaded", count=len(goldpetal_futures))
            except Exception as e:
                logger.error("goldpetal_futures_load_failed", error=str(e), exc_info=True)
                dpg.configure_item("donchian_contract", items=["Error loading futures"])
        
        threading.Thread(target=fetch_goldpetal, daemon=True).start()
    
    def on_donchian_contract_change(self):
        """Handle Donchian future contract selection change"""
        contract = dpg.get_value("donchian_contract")
        if contract and "Error" not in contract:
            dpg.set_value("donchian_symbol", contract)
    
    def launch_rsi_monitor(self):
        """Start live RSI monitoring for NATGASMINI"""
        symbol_input = dpg.get_value("rsi_symbol").strip().upper()
        interval = dpg.get_value("rsi_interval")
        
        # NATGASMINI is always on MCX exchange, use symbol as-is
        symbol = symbol_input
        exchange = "MCX"
        
        if self.rsi_monitor_running:
            dpg.set_value("rsi_status", "Monitor already running. Stop it first.")
            dpg.configure_item("rsi_status", color=(255,200,0))
            return
        
        self.rsi_monitor_running = True
        self.rsi_alerted_candles = set()  # Reset alert tracking for new monitoring session
        dpg.configure_item("rsi_start_btn", show=False)
        dpg.configure_item("rsi_stop_btn", show=True)
        
        dpg.set_value("rsi_status", f"Launching RSI monitor for {symbol} ({interval})...")
        
        # Set tab color to green to indicate running
        dpg.bind_item_theme("tab_natgasmini", "active_monitor_theme")
        
        def rsi_worker():
            import time
            from kiteconnect import KiteConnect
            from Core_Modules.config import Config
            import pandas as pd
            from datetime import datetime, timedelta
            import pytz
            
            logger.info(
                "rsi_monitor_started",
                symbol=symbol,
                interval=interval
            )
            try:
                import importlib
                import Core_Modules.config as config_module
                importlib.reload(config_module)
                api_key = config_module.Config.API_KEY
                access_token = config_module.Config.ACCESS_TOKEN
                kite = KiteConnect(api_key=api_key)
                kite.set_access_token(access_token)
                period = 14
                last_alert = "--"
                first_run = True
                ist = pytz.timezone('Asia/Kolkata')
                # Calculate time to next market hour boundary
                def next_market_hour_boundary(now):
                    # NATGASMINI is on MCX: next check at next whole hour (10:00, 11:00, etc.)
                    if now.minute == 0:
                        # Already at :00, go to next hour
                        next_boundary = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                    else:
                        # Go to next whole hour
                        next_boundary = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                    return next_boundary
                # Immediate analysis on start
                def do_rsi_analysis():
                    # Resolve instrument token
                    instrument_token = self._resolve_instrument_token(symbol)
                    if not instrument_token:
                        error_msg = f"**Symbol:** {symbol}\n**Error:** Instrument token not found\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        logger.error("instrument_token_not_found", symbol=symbol)
                        dpg.set_value("rsi_status", f"Instrument token not found for {symbol}")
                        dpg.configure_item("rsi_status", color=(255,100,100))
                        self._send_discord_alert(error_msg, color=0xFF0000)
                        return False
                    data = kite.historical_data(
                        instrument_token=instrument_token,
                        from_date=(datetime.now()-pd.Timedelta(days=30)).strftime('%Y-%m-%d'),
                        to_date=datetime.now().strftime('%Y-%m-%d'),
                        interval="hour"
                    )
                    df = pd.DataFrame(data)
                    if df.empty or 'close' not in df:
                        error_msg = f"**Symbol:** {symbol}\n**Error:** No data received from API\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        logger.warning("no_data_received_from_api")
                        dpg.set_value("rsi_status", "No data found or API error.")
                        dpg.configure_item("rsi_status", color=(255,100,100))
                        self._send_discord_alert(error_msg, color=0xFFA500)
                        time.sleep(60)
                        return False
                    df['date'] = pd.to_datetime(df['date'])
                    if df['date'].dt.tz is None:
                        df['date'] = df['date'].dt.tz_localize('UTC').dt.tz_convert(ist)
                    else:
                        df['date'] = df['date'].dt.tz_convert(ist)
                    if len(df) < 100:
                        error_msg = f"**Symbol:** {symbol}\n**Error:** Not enough candles ({len(df)}/100)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        logger.warning("not_enough_candles", count=len(df), required=100)
                        dpg.set_value("rsi_status", "Not enough historical candles (need 100+)")
                        dpg.configure_item("rsi_status", color=(255,100,100))
                        self._send_discord_alert(error_msg, color=0xFFA500)
                        return False
                    # Candle type selection
                    candle_type = dpg.get_value("rsi_candle_type")
                    if candle_type == "Heikin Ashi":
                        from Core_Modules.strategies import TradingStrategies
                        ha_df = TradingStrategies.heikin_ashi(df)
                        close = ha_df['ha_close']
                    else:
                        close = df['close']
                    delta = close.diff()
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)
                    avg_gain = gain.rolling(window=period, min_periods=period).mean()
                    avg_loss = loss.rolling(window=period, min_periods=period).mean()
                    for i in range(period, len(gain)):
                        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
                        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    current_rsi = float(rsi.iloc[-1])
                    self.current_rsi_value = current_rsi
                    self.current_rsi_symbol = symbol
                    current_time = datetime.now().strftime('%H:%M:%S')
                    logger.info(
                        "rsi_update",
                        rsi=round(current_rsi, 2),
                        last_candle=df.iloc[-1]['date'].strftime('%Y-%m-%d %H:%M'),
                        close=round(close.iloc[-1], 2)
                    )
                    dpg.set_value("rsi_current_value", f"Current RSI: {current_rsi:.2f}")
                    nonlocal first_run, last_alert
                    
                    if first_run:
                        start_msg = f"**Symbol:** {symbol}\n**Interval:** {interval}\n**RSI:** {current_rsi:.2f}\n**Status:** Monitor Started\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        self._send_discord_alert(start_msg, color=0x3498DB)
                        
                        # LOOKBACK FEATURE: Check last 10 candles for missed RSI signals on startup
                        lookback_count = min(10, len(df) - 1)  # Check last 10 candles or all available
                        logger.info("rsi_lookback_start", lookback_count=lookback_count)
                        
                        for i in range(lookback_count, 0, -1):  # Start from oldest to newest
                            idx = -1 - i  # Index from end of dataframe
                            candle_date = df['date'].iloc[idx]
                            candle_timestamp = candle_date.isoformat()
                            
                            # Skip if already alerted
                            if candle_timestamp in self.rsi_alerted_candles:
                                continue
                            
                            # Calculate RSI for this historical candle
                            if candle_type == "Heikin Ashi":
                                from Core_Modules.strategies import TradingStrategies
                                ha_df_lookback = TradingStrategies.heikin_ashi(df.iloc[:idx+1])
                                close_lookback = ha_df_lookback['ha_close']
                            else:
                                close_lookback = df['close'].iloc[:idx+1]
                            
                            if len(close_lookback) >= period + 1:
                                delta_lb = close_lookback.diff()
                                gain_lb = delta_lb.where(delta_lb > 0, 0)
                                loss_lb = -delta_lb.where(delta_lb < 0, 0)
                                avg_gain_lb = gain_lb.rolling(window=period, min_periods=period).mean()
                                avg_loss_lb = loss_lb.rolling(window=period, min_periods=period).mean()
                                
                                for j in range(period, len(gain_lb)):
                                    avg_gain_lb.iloc[j] = (avg_gain_lb.iloc[j-1] * (period - 1) + gain_lb.iloc[j]) / period
                                    avg_loss_lb.iloc[j] = (avg_loss_lb.iloc[j-1] * (period - 1) + loss_lb.iloc[j]) / period
                                
                                rs_lb = avg_gain_lb / avg_loss_lb
                                rsi_lb = 100 - (100 / (1 + rs_lb))
                                lookback_rsi = float(rsi_lb.iloc[-1])
                                
                                if lookback_rsi > 70:
                                    alert_msg = f"**[MISSED SIGNAL - Lookback]**\n**Symbol:** {symbol}\n**Candle Time:** {candle_date.strftime('%Y-%m-%d %H:%M')}\n**RSI:** {lookback_rsi:.2f}\n**Status:** OVERBOUGHT (> 70)\n**Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                    logger.warning(
                                        "rsi_lookback_overbought",
                                        candle_time=candle_date.strftime('%Y-%m-%d %H:%M'),
                                        rsi=round(lookback_rsi, 2)
                                    )
                                    self._send_discord_alert(alert_msg, color=0xFFD700)  # Gold color for lookback
                                    self.rsi_alerted_candles.add(candle_timestamp)
                                elif lookback_rsi < 30:
                                    alert_msg = f"**[MISSED SIGNAL - Lookback]**\n**Symbol:** {symbol}\n**Candle Time:** {candle_date.strftime('%Y-%m-%d %H:%M')}\n**RSI:** {lookback_rsi:.2f}\n**Status:** OVERSOLD (< 30)\n**Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                    logger.warning(
                                        "rsi_lookback_oversold",
                                        candle_time=candle_date.strftime('%Y-%m-%d %H:%M'),
                                        rsi=round(lookback_rsi, 2)
                                    )
                                    self._send_discord_alert(alert_msg, color=0xFFD700)  # Gold color for lookback
                                    self.rsi_alerted_candles.add(candle_timestamp)
                        
                        first_run = False
                    
                    # Get current candle timestamp for deduplication
                    current_candle_timestamp = df['date'].iloc[-1].isoformat()
                    
                    # Check for RSI alerts with deduplication
                    logger.debug(
                        "rsi_current_check",
                        current_rsi=round(current_rsi, 2),
                        overbought_threshold=70,
                        oversold_threshold=30,
                        already_alerted=current_candle_timestamp in self.rsi_alerted_candles
                    )
                    
                    if current_rsi > 70 and current_candle_timestamp not in self.rsi_alerted_candles:
                        last_alert = f"RSI crossed above 70 at {datetime.now().strftime('%H:%M:%S')}"
                        alert_msg = f"**Symbol:** {symbol}\n**RSI:** {current_rsi:.2f}\n**Status:** OVERBOUGHT (> 70)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        logger.warning(
                            "rsi_alert_overbought",
                            symbol=symbol,
                            rsi=round(current_rsi, 2),
                            threshold=70
                        )
                        dpg.set_value("rsi_last_alert", last_alert)
                        dpg.configure_item("rsi_last_alert", color=(255,100,100))
                        self._send_discord_alert(alert_msg, color=0xFF5733)
                        self._play_alert_sound()
                        self.rsi_alerted_candles.add(current_candle_timestamp)
                    elif current_rsi < 30 and current_candle_timestamp not in self.rsi_alerted_candles:
                        last_alert = f"RSI crossed below 30 at {datetime.now().strftime('%H:%M:%S')}"
                        alert_msg = f"**Symbol:** {symbol}\n**RSI:** {current_rsi:.2f}\n**Status:** OVERSOLD (< 30)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        logger.warning(
                            "rsi_alert_oversold",
                            symbol=symbol,
                            rsi=round(current_rsi, 2),
                            threshold=30
                        )
                        dpg.set_value("rsi_last_alert", last_alert)
                        dpg.configure_item("rsi_last_alert", color=(100,255,100))
                        self._send_discord_alert(alert_msg, color=0x33FF57)
                        self._play_alert_sound()
                        self.rsi_alerted_candles.add(current_candle_timestamp)
                    else:
                        dpg.set_value("rsi_last_alert", last_alert)
                    dpg.set_value("rsi_status", f"Monitoring... Last checked: {datetime.now().strftime('%H:%M:%S')}")
                    dpg.configure_item("rsi_status", color=(150,150,150))
                    return True
                # Immediate analysis
                if self.rsi_monitor_running:
                    do_rsi_analysis()
                # Schedule next checks at :15 mark
                while self.rsi_monitor_running:
                    now = datetime.now(ist)
                    next_boundary = next_market_hour_boundary(now)
                    wait_seconds = (next_boundary - now).total_seconds()
                    if wait_seconds > 0:
                        dpg.set_value("rsi_status", f"Waiting for next market hour boundary: {next_boundary.strftime('%H:%M')}")
                        dpg.configure_item("rsi_status", color=(200,200,100))
                        time.sleep(wait_seconds)
                    if not self.rsi_monitor_running:
                        break
                    do_rsi_analysis()
            except Exception as e:
                error_msg = f"**Symbol:** {symbol}\n**Error:** {str(e)}\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                logger.error("rsi_monitor_exception", error=str(e), exc_info=True)
                dpg.set_value("rsi_status", f"Error: {str(e)}")
                dpg.configure_item("rsi_status", color=(255,100,100))
                self._send_discord_alert(error_msg, color=0xFF0000)
            finally:
                rsi_info = f"\n**RSI:** {self.current_rsi_value:.2f}" if self.current_rsi_value else ""
                stop_msg = f"**Symbol:** {symbol}{rsi_info}\n**Status:** Monitor Stopped (Thread Exit)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                logger.info("rsi_monitor_stopped", symbol=symbol)
                self._send_discord_alert(stop_msg, color=0x808080)
                self.rsi_monitor_running = False
                dpg.configure_item("rsi_start_btn", show=True)
                dpg.configure_item("rsi_stop_btn", show=False)
                # Reset tab color
                dpg.bind_item_theme("tab_natgasmini", 0)  # 0 unbinds the theme
        
        threading.Thread(target=rsi_worker, daemon=True).start()
    
    def stop_rsi_monitor(self):
        """Stop the RSI monitoring"""
        logger.info("rsi_monitor_stop_requested")
        self.rsi_monitor_running = False
        
        # Send Discord alert for manual stop with current RSI
        symbol_info = f"**Symbol:** {self.current_rsi_symbol}\n" if self.current_rsi_symbol else ""
        rsi_info = f"**RSI:** {self.current_rsi_value:.2f}\n" if self.current_rsi_value else ""
        stop_msg = f"{symbol_info}{rsi_info}**Status:** Monitor Stopped (User Request)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self._send_discord_alert(stop_msg, color=0x808080)  # Gray
        
        dpg.set_value("rsi_status", "Monitor stopped")
        dpg.configure_item("rsi_status", color=(255,150,0))
        dpg.configure_item("rsi_start_btn", show=True)
        dpg.configure_item("rsi_stop_btn", show=False)
        # Reset tab color
        dpg.bind_item_theme("tab_natgasmini", 0)  # 0 unbinds the theme
    
    def launch_donchian_monitor(self):
        """Start live Donchian Channel monitoring"""
        symbol_input = dpg.get_value("donchian_symbol").strip().upper()
        upper_period = 20  # Fixed upper band period
        lower_period = 10  # Fixed lower band period
        interval = dpg.get_value("donchian_interval")
        
        # For commodities, symbol is used as-is; for NSE, we'll add the prefix
        symbol = symbol_input
        
        if self.donchian_monitor_running:
            dpg.set_value("donchian_status", "Monitor already running. Stop it first.")
            dpg.configure_item("donchian_status", color=(255,200,0))
            return
        
        self.donchian_monitor_running = True
        self.donchian_alerted_candles = set()  # Reset alert tracking for new monitoring session
        dpg.configure_item("donchian_start_btn", show=False)
        dpg.configure_item("donchian_stop_btn", show=True)
        
        dpg.set_value("donchian_status", f"Launching Donchian monitor for {symbol} ({interval})...")
        
        # Set tab color to green to indicate running
        dpg.bind_item_theme("tab_goldpetal", "active_monitor_theme")
        
        def donchian_worker():
            import time
            from kiteconnect import KiteConnect
            from Core_Modules.config import Config
            import pandas as pd
            from datetime import datetime, timedelta
            import pytz
            
            logger.info(
                "donchian_monitor_started",
                symbol=symbol,
                interval=interval,
                upper_period=upper_period,
                lower_period=lower_period
            )
            
            try:
                import importlib
                import Core_Modules.config as config_module
                importlib.reload(config_module)
                api_key = config_module.Config.API_KEY
                access_token = config_module.Config.ACCESS_TOKEN
                kite = KiteConnect(api_key=api_key)
                kite.set_access_token(access_token)
                
                last_alert = "--"
                first_run = True
                ist = pytz.timezone('Asia/Kolkata')
                
                def next_market_hour_boundary(now):
                    # For commodities: next check at next whole hour
                    if now.minute == 0:
                        next_boundary = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                    else:
                        next_boundary = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                    return next_boundary
                
                def do_donchian_analysis():
                    nonlocal first_run, last_alert
                    
                    # Resolve instrument token
                    instrument_token = self._resolve_instrument_token(symbol)
                    if not instrument_token:
                        error_msg = f"**Symbol:** {symbol}\n**Error:** Instrument token not found\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        logger.error("instrument_token_not_found", symbol=symbol)
                        dpg.set_value("donchian_status", f"Instrument token not found for {symbol}")
                        dpg.configure_item("donchian_status", color=(255,100,100))
                        self._send_discord_alert(error_msg, color=0xFF0000)
                        return False
                    
                    # Fetch historical data
                    data = kite.historical_data(
                        instrument_token=instrument_token,
                        from_date=(datetime.now()-pd.Timedelta(days=30)).strftime('%Y-%m-%d'),
                        to_date=datetime.now().strftime('%Y-%m-%d'),
                        interval="hour"
                    )
                    df = pd.DataFrame(data)
                    
                    if df.empty or 'high' not in df or 'low' not in df or 'close' not in df:
                        error_msg = f"**Symbol:** {symbol}\n**Error:** No data received from API\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        logger.warning("no_data_received_from_api")
                        dpg.set_value("donchian_status", "No data found or API error.")
                        dpg.configure_item("donchian_status", color=(255,100,100))
                        self._send_discord_alert(error_msg, color=0xFFA500)
                        time.sleep(60)
                        return False
                    
                    # Convert dates to IST
                    df['date'] = pd.to_datetime(df['date'])
                    if df['date'].dt.tz is None:
                        df['date'] = df['date'].dt.tz_localize('UTC').dt.tz_convert(ist)
                    else:
                        df['date'] = df['date'].dt.tz_convert(ist)
                    
                    if len(df) < max(upper_period, lower_period):
                        required = max(upper_period, lower_period)
                        error_msg = f"**Symbol:** {symbol}\n**Error:** Not enough candles ({len(df)}/{required})\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        logger.warning("not_enough_candles", count=len(df), required=required)
                        dpg.set_value("donchian_status", f"Not enough historical candles (need {required}+)")
                        dpg.configure_item("donchian_status", color=(255,100,100))
                        self._send_discord_alert(error_msg, color=0xFFA500)
                        return False
                    
                    # Candle type selection for Donchian
                    candle_type = dpg.get_value("donchian_candle_type") if dpg.does_item_exist("donchian_candle_type") else "Normal"
                    if candle_type == "Heikin Ashi":
                        from Core_Modules.strategies import TradingStrategies
                        ha_df = TradingStrategies.heikin_ashi(df)
                        high = ha_df['ha_high']
                        low = ha_df['ha_low']
                        close = ha_df['ha_close']
                    else:
                        high = df['high']
                        low = df['low']
                        close = df['close']
                    # Upper band: highest high over upper_period
                    upper_band = high.rolling(window=upper_period).max().iloc[-1]
                    # Lower band: lowest low over lower_period
                    lower_band = low.rolling(window=lower_period).min().iloc[-1]
                    
                    # Calculate previous candle's bands (excluding the last candle)
                    prev_upper_band = high.iloc[:-1].rolling(window=upper_period).max().iloc[-1]
                    prev_lower_band = low.iloc[:-1].rolling(window=lower_period).min().iloc[-1]
                    prev_close = float(close.iloc[-2]) if len(close) > 1 else None
                    
                    current_price = float(close.iloc[-1])
                    self.current_donchian_price = current_price
                    self.current_donchian_symbol = symbol
                    
                    current_time = datetime.now().strftime('%H:%M:%S')
                    logger.info(
                        "donchian_update",
                        price=round(current_price, 2),
                        upper=round(upper_band, 2),
                        lower=round(lower_band, 2)
                    )
                    
                    dpg.set_value("donchian_current_price", f"Current Price: {current_price:.2f}")
                    dpg.set_value("donchian_upper_band", f"Upper Band: {upper_band:.2f}")
                    dpg.set_value("donchian_lower_band", f"Lower Band: {lower_band:.2f}")
                    
                    if first_run:
                        start_msg = f"**Symbol:** {symbol}\n**Interval:** {interval}\n**Price:** {current_price:.2f}\n**Upper Band:** {upper_band:.2f}\n**Lower Band:** {lower_band:.2f}\n**Status:** Monitor Started\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        self._send_discord_alert(start_msg, color=0x3498DB)
                        
                        # LOOKBACK FEATURE: Check last 10 candles for missed signals on startup
                        lookback_count = min(10, len(df) - 1)  # Check last 10 candles or all available
                        logger.info("donchian_lookback_start", lookback_count=lookback_count)
                        
                        for i in range(lookback_count, 0, -1):  # Start from oldest to newest
                            idx = -1 - i  # Index from end of dataframe
                            candle_date = df['date'].iloc[idx]
                            candle_timestamp = candle_date.isoformat()
                            
                            # Skip if already alerted
                            if candle_timestamp in self.donchian_alerted_candles:
                                continue
                            
                            # Calculate bands excluding candles after this one
                            lookback_high = high.iloc[:idx+1]
                            lookback_low = low.iloc[:idx+1]
                            lookback_close = close.iloc[idx]
                            
                            if len(lookback_high) >= upper_period:
                                lookback_upper = lookback_high.iloc[:-1].rolling(window=upper_period).max().iloc[-1]
                                
                                if lookback_close >= lookback_upper:
                                    alert_msg = f"**[MISSED SIGNAL - Lookback]**\n**Symbol:** {symbol}\n**Candle Time:** {candle_date.strftime('%Y-%m-%d %H:%M')}\n**Close:** {lookback_close:.2f}\n**20-Period High:** {lookback_upper:.2f}\n**Status:** BULLISH SIGNAL (Close > 20-Period High)\n**Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                    logger.warning(
                                        "donchian_lookback_bullish",
                                        candle_time=candle_date.strftime('%Y-%m-%d %H:%M'),
                                        close=round(lookback_close, 2),
                                        upper=round(lookback_upper, 2)
                                    )
                                    self._send_discord_alert(alert_msg, color=0xFFD700)  # Gold color for lookback
                                    self.donchian_alerted_candles.add(candle_timestamp)
                            
                            if len(lookback_low) >= lower_period:
                                lookback_lower = lookback_low.iloc[:-1].rolling(window=lower_period).min().iloc[-1]
                                
                                if lookback_close <= lookback_lower:
                                    alert_msg = f"**[MISSED SIGNAL - Lookback]**\n**Symbol:** {symbol}\n**Candle Time:** {candle_date.strftime('%Y-%m-%d %H:%M')}\n**Close:** {lookback_close:.2f}\n**10-Period Low:** {lookback_lower:.2f}\n**Status:** BEARISH SIGNAL (Close < 10-Period Low)\n**Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                    logger.warning(
                                        "donchian_lookback_bearish",
                                        candle_time=candle_date.strftime('%Y-%m-%d %H:%M'),
                                        close=round(lookback_close, 2),
                                        lower=round(lookback_lower, 2)
                                    )
                                    self._send_discord_alert(alert_msg, color=0xFFD700)  # Gold color for lookback
                                    self.donchian_alerted_candles.add(candle_timestamp)
                        
                        first_run = False
                    
                    # Get previous candle timestamp for deduplication
                    prev_candle_timestamp = df['date'].iloc[-2].isoformat() if len(df) > 1 else None
                    current_candle_timestamp = df['date'].iloc[-1].isoformat()
                    
                    # Check for previous candle close breakouts (earlier signal) with deduplication
                    if prev_close is not None and prev_candle_timestamp:
                        logger.debug(
                            "donchian_prev_candle_check",
                            prev_close=round(prev_close, 2),
                            prev_upper_band=round(prev_upper_band, 2),
                            prev_lower_band=round(prev_lower_band, 2),
                            already_alerted=prev_candle_timestamp in self.donchian_alerted_candles
                        )
                        
                        if prev_close >= prev_upper_band and prev_candle_timestamp not in self.donchian_alerted_candles:
                            last_alert = f"PREV CANDLE CLOSE ABOVE at {datetime.now().strftime('%H:%M:%S')} | Close: {prev_close:.2f}"
                            alert_msg = f"**Symbol:** {symbol}\n**Previous Close:** {prev_close:.2f}\n**20-Period High:** {prev_upper_band:.2f}\n**Status:** BULLISH SIGNAL (Prev Candle Close >= 20-Period High)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            logger.warning(
                                "donchian_alert_prev_candle_bullish",
                                symbol=symbol,
                                prev_close=round(prev_close, 2),
                                prev_upper_band=round(prev_upper_band, 2)
                            )
                            dpg.set_value("donchian_last_alert", last_alert)
                            dpg.configure_item("donchian_last_alert", color=(100,255,100))
                            self._send_discord_alert(alert_msg, color=0x00FF00)
                            self._play_alert_sound()
                            self.donchian_alerted_candles.add(prev_candle_timestamp)
                        elif prev_close <= prev_lower_band and prev_candle_timestamp not in self.donchian_alerted_candles:
                            last_alert = f"PREV CANDLE CLOSE BELOW at {datetime.now().strftime('%H:%M:%S')} | Close: {prev_close:.2f}"
                            alert_msg = f"**Symbol:** {symbol}\n**Previous Close:** {prev_close:.2f}\n**10-Period Low:** {prev_lower_band:.2f}\n**Status:** BEARISH SIGNAL (Prev Candle Close <= 10-Period Low)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            logger.warning(
                                "donchian_alert_prev_candle_bearish",
                                symbol=symbol,
                                prev_close=round(prev_close, 2),
                                prev_lower_band=round(prev_lower_band, 2)
                            )
                            dpg.set_value("donchian_last_alert", last_alert)
                            dpg.configure_item("donchian_last_alert", color=(255,100,100))
                            self._send_discord_alert(alert_msg, color=0xFF0000)
                            self._play_alert_sound()
                            self.donchian_alerted_candles.add(prev_candle_timestamp)
                    
                    # Check for current price breakouts with deduplication
                    logger.debug(
                        "donchian_current_price_check",
                        current_price=round(current_price, 2),
                        upper_band=round(upper_band, 2),
                        lower_band=round(lower_band, 2),
                        already_alerted=current_candle_timestamp in self.donchian_alerted_candles
                    )
                    
                    if current_price >= upper_band and current_candle_timestamp not in self.donchian_alerted_candles:
                        last_alert = f"BREAKOUT ABOVE at {datetime.now().strftime('%H:%M:%S')} | Price: {current_price:.2f}"
                        alert_msg = f"**Symbol:** {symbol}\n**Price:** {current_price:.2f}\n**Upper Band:** {upper_band:.2f}\n**Status:** BULLISH BREAKOUT (Price >= Upper Band)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        logger.warning(
                            "donchian_alert_bullish_breakout",
                            symbol=symbol,
                            price=round(current_price, 2),
                            upper_band=round(upper_band, 2)
                        )
                        dpg.set_value("donchian_last_alert", last_alert)
                        dpg.configure_item("donchian_last_alert", color=(100,255,100))
                        self._send_discord_alert(alert_msg, color=0x33FF57)
                        self._play_alert_sound()
                        self.donchian_alerted_candles.add(current_candle_timestamp)
                    elif current_price <= lower_band and current_candle_timestamp not in self.donchian_alerted_candles:
                        last_alert = f"BREAKDOWN BELOW at {datetime.now().strftime('%H:%M:%S')} | Price: {current_price:.2f}"
                        alert_msg = f"**Symbol:** {symbol}\n**Price:** {current_price:.2f}\n**Lower Band:** {lower_band:.2f}\n**Status:** BEARISH BREAKDOWN (Price <= Lower Band)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        logger.warning(
                            "donchian_alert_bearish_breakout",
                            symbol=symbol,
                            price=round(current_price, 2),
                            lower_band=round(lower_band, 2)
                        )
                        dpg.set_value("donchian_last_alert", last_alert)
                        dpg.configure_item("donchian_last_alert", color=(255,100,100))
                        self._send_discord_alert(alert_msg, color=0xFF5733)
                        self._play_alert_sound()
                        self.donchian_alerted_candles.add(current_candle_timestamp)
                    else:
                        dpg.set_value("donchian_last_alert", last_alert)
                    
                    dpg.set_value("donchian_status", f"Monitoring... Last checked: {datetime.now().strftime('%H:%M:%S')}")
                    dpg.configure_item("donchian_status", color=(150,150,150))
                    return True
                
                # Immediate analysis
                if self.donchian_monitor_running:
                    do_donchian_analysis()
                
                # Schedule next checks at hourly boundaries
                while self.donchian_monitor_running:
                    now = datetime.now(ist)
                    next_boundary = next_market_hour_boundary(now)
                    wait_seconds = (next_boundary - now).total_seconds()
                    if wait_seconds > 0:
                        dpg.set_value("donchian_status", f"Waiting for next market hour boundary: {next_boundary.strftime('%H:%M')}")
                        dpg.configure_item("donchian_status", color=(200,200,100))
                        time.sleep(wait_seconds)
                    if not self.donchian_monitor_running:
                        break
                    do_donchian_analysis()
            
            except Exception as e:
                error_msg = f"**Symbol:** {symbol}\n**Error:** {str(e)}\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                logger.error("donchian_monitor_exception", error=str(e), exc_info=True)
                dpg.set_value("donchian_status", f"Error: {str(e)}")
                dpg.configure_item("donchian_status", color=(255,100,100))
                self._send_discord_alert(error_msg, color=0xFF0000)
            finally:
                price_info = f"**Price:** {self.current_donchian_price:.2f}\n" if self.current_donchian_price else ""
                stop_msg = f"**Symbol:** {symbol}\n{price_info}**Status:** Monitor Stopped (Thread Exit)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                logger.info("donchian_monitor_stopped", symbol=symbol)
                self._send_discord_alert(stop_msg, color=0x808080)
                self.donchian_monitor_running = False
                dpg.configure_item("donchian_start_btn", show=True)
                dpg.configure_item("donchian_stop_btn", show=False)
        
        threading.Thread(target=donchian_worker, daemon=True).start()
    
    def stop_donchian_monitor(self):
        """Stop the Donchian Channel monitoring"""
        logger.info("donchian_monitor_stop_requested")
        self.donchian_monitor_running = False
        
        # Send Discord alert for manual stop
        symbol_info = f"**Symbol:** {self.current_donchian_symbol}\n" if self.current_donchian_symbol else ""
        price_info = f"**Price:** {self.current_donchian_price:.2f}\n" if self.current_donchian_price else ""
        stop_msg = f"{symbol_info}{price_info}**Status:** Monitor Stopped (User Request)\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self._send_discord_alert(stop_msg, color=0x808080)  # Gray
        
        dpg.set_value("donchian_status", "Monitor stopped")
        dpg.configure_item("donchian_status", color=(255,150,0))
        dpg.configure_item("donchian_start_btn", show=True)
        dpg.configure_item("donchian_stop_btn", show=False)
        # Reset tab color
        dpg.bind_item_theme("tab_goldpetal", 0)  # 0 unbinds the theme
    
    def _send_discord_alert(self, message, color=0xFF5733, title="Trading Alert"):
        """Send alert via notification system (email + Discord)"""
        self.notifier.send_alert(
            message=message,
            title=title,
            color=color,
            async_send=True
        )
    
    def _play_alert_sound(self):
        """Play alert sound (cross-platform)"""
        import platform
        if platform.system() == "Darwin":
            os.system('afplay /System/Library/Sounds/Glass.aiff')
        elif platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 500)
        else:
            os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga || aplay /usr/share/sounds/alsa/Front_Center.wav || beep')
    
    def _resolve_instrument_token(self, symbol):
        """Resolve instrument token from symbol using cached instruments list"""
        from kiteconnect import KiteConnect
        from Core_Modules.config import Config
        import time
        
        symbol = symbol.strip().upper()
        
        # Determine exchange from symbol format
        if symbol.startswith("NSE:"):
            exchange = "NSE"
            tradingsymbol = symbol.split(":")[1]
        else:
            # For MCX/NCDEX, determine exchange from symbol patterns
            if 'NATGASMINI' in symbol:
                exchange = "MCX"
            elif any(x in symbol for x in ['WHEAT', 'COTTON', 'SOY', 'SUGAR', 'JEERA']):
                exchange = "NCDEX"
            else:
                exchange = "MCX"  # Default to MCX for commodity symbols
            tradingsymbol = symbol
        
        try:
            # Use cached instruments if available, less than 24 hours old, AND for the same exchange
            if self.instruments_cache is None or self.instruments_cache_time is None or \
               self.instruments_cache_exchange != exchange or \
               (time.time() - self.instruments_cache_time) > 86400:
                # Fetch fresh instruments list for the exchange
                kite = KiteConnect(api_key=Config.API_KEY)
                kite.set_access_token(Config.ACCESS_TOKEN)
                self.instruments_cache = kite.instruments(exchange=exchange)
                self.instruments_cache_time = time.time()
                self.instruments_cache_exchange = exchange
                logger.info("instruments_list_fetched", exchange=exchange, source="api")
            
            # Search in cache
            for inst in self.instruments_cache:
                if inst['tradingsymbol'].upper() == tradingsymbol:
                    return int(inst['instrument_token'])
            
            logger.warning("symbol_not_found_in_instruments", symbol=tradingsymbol, exchange=exchange)
            return None
            
        except Exception as e:
            logger.error("instrument_token_lookup_failed", error=str(e), exc_info=True)
            return None
    
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
