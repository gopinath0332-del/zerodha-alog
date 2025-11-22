#!/usr/bin/env python3
"""
GUI Application for Zerodha Trading Bot
Provides a graphical interface for all trading operations
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to enable Core_Modules as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime
from Core_Modules.trader import KiteTrader
from Core_Modules.utils import (
    get_portfolio_summary,
    get_top_gainers_losers,
    export_positions_to_csv,
    export_holdings_to_csv,
    calculate_position_size
)

# Helper function for formatting currency
def format_currency(amount):
    """Format amount as Indian Rupee"""
    return f"₹{amount:,.2f}"

class TradingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zerodha Trading Bot")
        self.root.geometry("1200x800")
        
        # Initialize trader
        self.trader = None
        self.is_authenticated = False
        
        # Set up the UI
        self.setup_ui()
        
        # Try to authenticate
        self.authenticate()
    
    def setup_ui(self):
        """Set up the main UI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Status bar at top
        self.status_label = ttk.Label(main_frame, text="Status: Not Authenticated", 
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Left sidebar - Menu buttons
        sidebar = ttk.Frame(main_frame, padding="5")
        sidebar.grid(row=1, column=0, sticky=(tk.W, tk.N, tk.S))
        
        ttk.Label(sidebar, text="Trading Menu", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # Menu buttons
        menu_buttons = [
            ("📊 Portfolio Summary", self.show_portfolio),
            ("📈 Positions", self.show_positions),
            ("💼 Holdings", self.show_holdings),
            ("📋 Orders", self.show_orders),
            ("🎯 Place Order", self.show_place_order),
            ("📉 Market Data", self.show_market_data),
            ("⚡ Bracket Order", self.show_bracket_order),
            ("🏆 Top Gainers/Losers", self.show_gainers_losers),
            ("💰 Position Sizing", self.show_position_sizing),
            ("💾 Export Portfolio", self.export_portfolio),
            ("🔄 Refresh", self.refresh_current_view),
        ]
        
        for text, command in menu_buttons:
            btn = ttk.Button(sidebar, text=text, command=command, width=20)
            btn.pack(pady=2, fill=tk.X)
        
        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(pady=10, fill=tk.X)
        
        ttk.Button(sidebar, text="🔐 Re-authenticate", 
                  command=self.authenticate, width=20).pack(pady=2, fill=tk.X)
        ttk.Button(sidebar, text="❌ Exit", 
                  command=self.root.quit, width=20).pack(pady=2, fill=tk.X)
        
        # Right content area
        content_frame = ttk.Frame(main_frame, padding="5")
        content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Title for content area
        self.content_title = ttk.Label(content_frame, text="Welcome to Trading Bot", 
                                       font=('Arial', 14, 'bold'))
        self.content_title.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Scrolled text area for output
        self.output_area = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, 
                                                     font=('Courier', 10))
        self.output_area.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Current view tracker
        self.current_view = None
        
        self.show_welcome()
    
    def authenticate(self):
        """Authenticate with Zerodha"""
        try:
            self.update_status("Authenticating...")
            self.trader = KiteTrader()
            self.is_authenticated = True
            self.update_status("Status: Authenticated ✓")
            self.output("Authentication successful!\n")
        except Exception as e:
            self.is_authenticated = False
            self.update_status("Status: Authentication Failed ✗")
            messagebox.showerror("Authentication Error", 
                               f"Failed to authenticate:\n{str(e)}\n\nPlease run authenticate.py first.")
    
    def update_status(self, text):
        """Update status bar"""
        self.status_label.config(text=text)
    
    def output(self, text, clear=False):
        """Output text to the display area"""
        if clear:
            self.output_area.delete(1.0, tk.END)
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
    
    def check_auth(self):
        """Check if authenticated"""
        if not self.is_authenticated:
            messagebox.showwarning("Not Authenticated", 
                                 "Please authenticate first!")
            return False
        return True
    
    def show_welcome(self):
        """Show welcome message"""
        self.content_title.config(text="Welcome to Trading Bot")
        welcome_text = """
╔═══════════════════════════════════════════════════════════════╗
║           ZERODHA TRADING BOT - GUI APPLICATION              ║
╚═══════════════════════════════════════════════════════════════╝

Welcome! This application provides a graphical interface for:

📊 Portfolio Management
   • View portfolio summary with P&L
   • Check positions and holdings
   • Monitor margins and balances

📈 Trading Operations
   • Place market and limit orders
   • Create bracket orders with SL/Target
   • View and manage order history

📉 Market Analysis
   • Get real-time market data
   • Find top gainers and losers
   • Calculate position sizes

💾 Data Export
   • Export portfolio to CSV
   • Save trading history

Select an option from the menu to get started!

"""
        self.output(welcome_text, clear=True)
        self.current_view = None
    
    def show_portfolio(self):
        """Display portfolio summary"""
        if not self.check_auth():
            return
        
        self.content_title.config(text="Portfolio Summary")
        self.output("Loading portfolio...\n", clear=True)
        
        def fetch():
            try:
                summary = get_portfolio_summary(self.trader)
                
                output = "\n" + "="*70 + "\n"
                output += "                     PORTFOLIO SUMMARY\n"
                output += "="*70 + "\n\n"
                
                output += f"💰 Available Margin: {format_currency(summary['available_margin'])}\n"
                output += f"💳 Used Margin: {format_currency(summary['used_margin'])}\n\n"
                
                output += f"📊 Day Positions P&L: {format_currency(summary['day_positions_pnl'])}\n"
                output += f"📈 Holdings P&L: {format_currency(summary['holdings_pnl'])}\n"
                output += f"💵 Total P&L: {format_currency(summary['total_pnl'])}\n\n"
                
                output += f"🎯 Holdings Investment: {format_currency(summary['holdings_investment'])}\n"
                output += f"💼 Current Value: {format_currency(summary['holdings_current_value'])}\n"
                
                return_pct = 0
                if summary['holdings_investment'] > 0:
                    return_pct = ((summary['holdings_current_value'] - summary['holdings_investment']) / summary['holdings_investment']) * 100
                output += f"📊 Return: {return_pct:.2f}%\n\n"
                
                output += f"📦 Day Positions: {summary['day_positions_count']}\n"
                output += f"🏢 Holdings Count: {summary['holdings_count']}\n"
                
                output += "\n" + "="*70 + "\n"
                
                self.output(output, clear=True)
                
            except Exception as e:
                self.output(f"Error fetching portfolio: {str(e)}\n", clear=True)
        
        threading.Thread(target=fetch, daemon=True).start()
        self.current_view = 'portfolio'
    
    def show_positions(self):
        """Display current positions"""
        if not self.check_auth():
            return
        
        self.content_title.config(text="Current Positions")
        self.output("Loading positions...\n", clear=True)
        
        def fetch():
            try:
                positions = self.trader.get_positions()
                
                output = "\n" + "="*70 + "\n"
                output += "                     CURRENT POSITIONS\n"
                output += "="*70 + "\n\n"
                
                # Day positions
                day_pos = [p for p in positions['day'] if p['quantity'] != 0]
                if day_pos:
                    output += "📊 DAY POSITIONS:\n"
                    output += "-"*70 + "\n"
                    for p in day_pos:
                        output += f"\n{p['tradingsymbol']}\n"
                        output += f"  Qty: {p['quantity']:,} | Avg: ₹{p['average_price']:.2f} | "
                        output += f"LTP: ₹{p['last_price']:.2f}\n"
                        output += f"  P&L: {format_currency(p['pnl'])} "
                        output += f"({'📈' if p['pnl'] >= 0 else '📉'})\n"
                else:
                    output += "No day positions\n"
                
                output += "\n" + "="*70 + "\n"
                
                self.output(output, clear=True)
                
            except Exception as e:
                self.output(f"Error fetching positions: {str(e)}\n", clear=True)
        
        threading.Thread(target=fetch, daemon=True).start()
        self.current_view = 'positions'
    
    def show_holdings(self):
        """Display holdings"""
        if not self.check_auth():
            return
        
        self.content_title.config(text="Holdings")
        self.output("Loading holdings...\n", clear=True)
        
        def fetch():
            try:
                holdings = self.trader.get_holdings()
                
                output = "\n" + "="*70 + "\n"
                output += "                         HOLDINGS\n"
                output += "="*70 + "\n\n"
                
                if holdings:
                    total_investment = sum(h['average_price'] * h['quantity'] for h in holdings)
                    total_value = sum(h['last_price'] * h['quantity'] for h in holdings)
                    total_pnl = sum(h['pnl'] for h in holdings)
                    
                    for h in holdings:
                        output += f"\n{h['tradingsymbol']}\n"
                        output += f"  Qty: {h['quantity']:,} | Avg: ₹{h['average_price']:.2f} | "
                        output += f"LTP: ₹{h['last_price']:.2f}\n"
                        output += f"  Investment: {format_currency(h['average_price'] * h['quantity'])} | "
                        output += f"Current: {format_currency(h['last_price'] * h['quantity'])}\n"
                        output += f"  P&L: {format_currency(h['pnl'])} "
                        output += f"({'📈' if h['pnl'] >= 0 else '📉'})\n"
                    
                    output += "\n" + "-"*70 + "\n"
                    output += f"Total Investment: {format_currency(total_investment)}\n"
                    output += f"Current Value: {format_currency(total_value)}\n"
                    output += f"Total P&L: {format_currency(total_pnl)}\n"
                else:
                    output += "No holdings\n"
                
                output += "\n" + "="*70 + "\n"
                
                self.output(output, clear=True)
                
            except Exception as e:
                self.output(f"Error fetching holdings: {str(e)}\n", clear=True)
        
        threading.Thread(target=fetch, daemon=True).start()
        self.current_view = 'holdings'
    
    def show_orders(self):
        """Display order history"""
        if not self.check_auth():
            return
        
        self.content_title.config(text="Order History")
        self.output("Loading orders...\n", clear=True)
        
        def fetch():
            try:
                orders = self.trader.get_orders()
                
                output = "\n" + "="*70 + "\n"
                output += "                      ORDER HISTORY\n"
                output += "="*70 + "\n\n"
                
                if orders:
                    for order in orders[-20:]:  # Last 20 orders
                        output += f"\n{order['tradingsymbol']} - {order['transaction_type']}\n"
                        output += f"  Order ID: {order['order_id']}\n"
                        output += f"  Qty: {order['quantity']} | Price: ₹{order.get('price', 0):.2f}\n"
                        output += f"  Status: {order['status']} | Type: {order['order_type']}\n"
                        output += f"  Time: {order['order_timestamp']}\n"
                else:
                    output += "No orders found\n"
                
                output += "\n" + "="*70 + "\n"
                
                self.output(output, clear=True)
                
            except Exception as e:
                self.output(f"Error fetching orders: {str(e)}\n", clear=True)
        
        threading.Thread(target=fetch, daemon=True).start()
        self.current_view = 'orders'
    
    def show_place_order(self):
        """Show order placement form"""
        if not self.check_auth():
            return
        
        # Create new window for order placement
        order_window = tk.Toplevel(self.root)
        order_window.title("Place Order")
        order_window.geometry("500x600")
        
        frame = ttk.Frame(order_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Place New Order", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Form fields
        fields_frame = ttk.Frame(frame)
        fields_frame.pack(fill=tk.X, pady=10)
        
        # Symbol
        ttk.Label(fields_frame, text="Symbol:").grid(row=0, column=0, sticky=tk.W, pady=5)
        symbol_entry = ttk.Entry(fields_frame, width=30)
        symbol_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Exchange
        ttk.Label(fields_frame, text="Exchange:").grid(row=1, column=0, sticky=tk.W, pady=5)
        exchange_var = tk.StringVar(value="NSE")
        exchange_combo = ttk.Combobox(fields_frame, textvariable=exchange_var, 
                                     values=["NSE", "BSE", "NFO", "MCX"], width=27)
        exchange_combo.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Transaction Type
        ttk.Label(fields_frame, text="Transaction:").grid(row=2, column=0, sticky=tk.W, pady=5)
        transaction_var = tk.StringVar(value="BUY")
        transaction_combo = ttk.Combobox(fields_frame, textvariable=transaction_var,
                                        values=["BUY", "SELL"], width=27)
        transaction_combo.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Quantity
        ttk.Label(fields_frame, text="Quantity:").grid(row=3, column=0, sticky=tk.W, pady=5)
        quantity_entry = ttk.Entry(fields_frame, width=30)
        quantity_entry.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Order Type
        ttk.Label(fields_frame, text="Order Type:").grid(row=4, column=0, sticky=tk.W, pady=5)
        order_type_var = tk.StringVar(value="MARKET")
        order_type_combo = ttk.Combobox(fields_frame, textvariable=order_type_var,
                                       values=["MARKET", "LIMIT"], width=27)
        order_type_combo.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Price (for limit orders)
        ttk.Label(fields_frame, text="Price (if LIMIT):").grid(row=5, column=0, sticky=tk.W, pady=5)
        price_entry = ttk.Entry(fields_frame, width=30)
        price_entry.grid(row=5, column=1, pady=5, padx=(10, 0))
        
        # Product Type
        ttk.Label(fields_frame, text="Product:").grid(row=6, column=0, sticky=tk.W, pady=5)
        product_var = tk.StringVar(value="MIS")
        product_combo = ttk.Combobox(fields_frame, textvariable=product_var,
                                    values=["MIS", "CNC", "NRML"], width=27)
        product_combo.grid(row=6, column=1, pady=5, padx=(10, 0))
        
        # Result area
        result_text = scrolledtext.ScrolledText(frame, height=10, width=50)
        result_text.pack(pady=20, fill=tk.BOTH, expand=True)
        
        def place_order():
            try:
                symbol = symbol_entry.get().strip()
                exchange = exchange_var.get()
                transaction = transaction_var.get()
                quantity = int(quantity_entry.get())
                order_type = order_type_var.get()
                product = product_var.get()
                
                if not symbol:
                    messagebox.showerror("Error", "Please enter a symbol")
                    return
                
                price = None
                if order_type == "LIMIT":
                    price = float(price_entry.get())
                
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "Placing order...\n")
                
                order_id = self.trader.place_order(
                    symbol=symbol,
                    exchange=exchange,
                    transaction_type=transaction,
                    quantity=quantity,
                    order_type=order_type,
                    price=price,
                    product=product
                )
                
                result_text.insert(tk.END, f"\n✓ Order placed successfully!\n")
                result_text.insert(tk.END, f"Order ID: {order_id}\n")
                
            except Exception as e:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"✗ Error placing order:\n{str(e)}\n")
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Place Order", command=place_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=order_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_market_data(self):
        """Show market data form"""
        if not self.check_auth():
            return
        
        # Create new window
        data_window = tk.Toplevel(self.root)
        data_window.title("Market Data")
        data_window.geometry("600x500")
        
        frame = ttk.Frame(data_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Get Market Data", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Input frame
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Symbols (comma-separated):").pack(anchor=tk.W)
        symbols_entry = ttk.Entry(input_frame, width=50)
        symbols_entry.pack(fill=tk.X, pady=5)
        symbols_entry.insert(0, "NSE:INFY,NSE:TCS,NSE:RELIANCE")
        
        # Result area
        result_text = scrolledtext.ScrolledText(frame, height=15, width=60)
        result_text.pack(pady=20, fill=tk.BOTH, expand=True)
        
        def fetch_data():
            try:
                symbols = [s.strip() for s in symbols_entry.get().split(',')]
                
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "Fetching market data...\n\n")
                
                quotes = self.trader.get_quote(*symbols)
                
                output = "="*60 + "\n"
                output += "                    MARKET DATA\n"
                output += "="*60 + "\n\n"
                
                for symbol, data in quotes.items():
                    output += f"{symbol}\n"
                    output += f"  LTP: ₹{data['last_price']:.2f}\n"
                    output += f"  Change: {data['net_change']:.2f} ({data.get('change_percent', 0):.2f}%)\n"
                    output += f"  Volume: {data.get('volume', 0):,}\n"
                    output += f"  OHLC: O:{data['ohlc']['open']:.2f} H:{data['ohlc']['high']:.2f} "
                    output += f"L:{data['ohlc']['low']:.2f} C:{data['ohlc']['close']:.2f}\n\n"
                
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, output)
                
            except Exception as e:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"Error fetching data:\n{str(e)}\n")
        
        ttk.Button(frame, text="Fetch Data", command=fetch_data).pack(pady=5)
        ttk.Button(frame, text="Close", command=data_window.destroy).pack(pady=5)
    
    def show_bracket_order(self):
        """Show bracket order form"""
        if not self.check_auth():
            return
        
        # Create new window
        bracket_window = tk.Toplevel(self.root)
        bracket_window.title("Bracket Order")
        bracket_window.geometry("500x650")
        
        frame = ttk.Frame(bracket_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Place Bracket Order", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Form
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        fields = [
            ("Symbol:", "symbol"),
            ("Exchange:", "exchange"),
            ("Transaction (BUY/SELL):", "transaction"),
            ("Quantity:", "quantity"),
            ("Price:", "price"),
            ("Stop Loss (points):", "stoploss"),
            ("Target (points):", "target"),
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, pady=5, padx=(10, 0))
            entries[key] = entry
        
        # Set defaults
        entries['exchange'].insert(0, "NSE")
        entries['transaction'].insert(0, "BUY")
        
        result_text = scrolledtext.ScrolledText(frame, height=8, width=50)
        result_text.pack(pady=20, fill=tk.BOTH, expand=True)
        
        def place_bracket():
            try:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, "Placing bracket order...\n")
                
                order_id = self.trader.place_bracket_order(
                    symbol=entries['symbol'].get(),
                    exchange=entries['exchange'].get(),
                    transaction_type=entries['transaction'].get().upper(),
                    quantity=int(entries['quantity'].get()),
                    price=float(entries['price'].get()),
                    stoploss=float(entries['stoploss'].get()),
                    target=float(entries['target'].get())
                )
                
                result_text.insert(tk.END, f"\n✓ Bracket order placed!\nOrder ID: {order_id}\n")
                
            except Exception as e:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"✗ Error:\n{str(e)}\n")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Place Order", command=place_bracket).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=bracket_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def show_gainers_losers(self):
        """Show top gainers and losers"""
        if not self.check_auth():
            return
        
        self.content_title.config(text="Top Gainers & Losers")
        self.output("Analyzing positions...\n", clear=True)
        
        def fetch():
            try:
                # Get holdings for analysis
                holdings = self.trader.get_holdings()
                
                if not holdings:
                    self.output("No holdings to analyze\n", clear=True)
                    return
                
                # Sort by P&L
                sorted_holdings = sorted(holdings, key=lambda x: x['pnl'], reverse=True)
                
                top_n = min(10, len(sorted_holdings))
                gainers = [h for h in sorted_holdings if h['pnl'] > 0][:top_n]
                losers = [h for h in sorted_holdings if h['pnl'] < 0][-top_n:][::-1]
                
                output = "\n" + "="*70 + "\n"
                output += "                  TOP GAINERS & LOSERS\n"
                output += "="*70 + "\n\n"
                
                if gainers:
                    output += "🏆 TOP GAINERS:\n"
                    output += "-"*70 + "\n"
                    for g in gainers:
                        investment = g['average_price'] * g['quantity']
                        return_pct = (g['pnl'] / investment * 100) if investment > 0 else 0
                        output += f"{g['tradingsymbol']:15} P&L: {format_currency(g['pnl']):>12} "
                        output += f"({return_pct:.2f}%)\n"
                else:
                    output += "No gainers\n"
                
                output += "\n"
                
                if losers:
                    output += "📉 TOP LOSERS:\n"
                    output += "-"*70 + "\n"
                    for l in losers:
                        investment = l['average_price'] * l['quantity']
                        return_pct = (l['pnl'] / investment * 100) if investment > 0 else 0
                        output += f"{l['tradingsymbol']:15} P&L: {format_currency(l['pnl']):>12} "
                        output += f"({return_pct:.2f}%)\n"
                else:
                    output += "No losers\n"
                
                output += "\n" + "="*70 + "\n"
                
                self.output(output, clear=True)
                
            except Exception as e:
                self.output(f"Error: {str(e)}\n", clear=True)
        
        threading.Thread(target=fetch, daemon=True).start()
        self.current_view = 'gainers_losers'
    
    def show_position_sizing(self):
        """Show position sizing calculator"""
        if not self.check_auth():
            return
        
        # Create new window
        calc_window = tk.Toplevel(self.root)
        calc_window.title("Position Sizing Calculator")
        calc_window.geometry("500x400")
        
        frame = ttk.Frame(calc_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Position Sizing Calculator", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Form
        form_frame = ttk.Frame(frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_frame, text="Account Size (₹):").grid(row=0, column=0, sticky=tk.W, pady=5)
        account_entry = ttk.Entry(form_frame, width=30)
        account_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(form_frame, text="Risk % (per trade):").grid(row=1, column=0, sticky=tk.W, pady=5)
        risk_entry = ttk.Entry(form_frame, width=30)
        risk_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        risk_entry.insert(0, "1.0")
        
        ttk.Label(form_frame, text="Entry Price (₹):").grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_price_entry = ttk.Entry(form_frame, width=30)
        entry_price_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        ttk.Label(form_frame, text="Stop Loss (₹):").grid(row=3, column=0, sticky=tk.W, pady=5)
        sl_entry = ttk.Entry(form_frame, width=30)
        sl_entry.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        result_text = scrolledtext.ScrolledText(frame, height=8, width=50)
        result_text.pack(pady=20, fill=tk.BOTH, expand=True)
        
        def calculate():
            try:
                account_size = float(account_entry.get())
                risk_pct = float(risk_entry.get())
                entry_price = float(entry_price_entry.get())
                stop_loss = float(sl_entry.get())
                
                # Calculate risk amount and SL percentage
                risk_amount = account_size * (risk_pct / 100)
                sl_pct = abs((stop_loss - entry_price) / entry_price) * 100
                
                # Get symbol (we'll use a placeholder since we need entry price)
                # The actual function gets current price, but we already have entry_price
                # So we'll calculate manually
                risk_per_share = abs(entry_price - stop_loss)
                position_size = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
                capital_required = position_size * entry_price
                
                result = {
                    'risk_amount': risk_amount,
                    'risk_per_share': risk_per_share,
                    'position_size': position_size,
                    'capital_required': capital_required
                }
                
                output = "\n" + "="*50 + "\n"
                output += "         POSITION SIZING RESULT\n"
                output += "="*50 + "\n\n"
                output += f"Account Size: {format_currency(account_size)}\n"
                output += f"Risk per Trade: {risk_pct}%\n"
                output += f"Risk Amount: {format_currency(result['risk_amount'])}\n\n"
                output += f"Entry Price: ₹{entry_price:.2f}\n"
                output += f"Stop Loss: ₹{stop_loss:.2f}\n"
                output += f"Risk per Share: ₹{result['risk_per_share']:.2f}\n\n"
                output += f"📊 Recommended Position Size: {result['position_size']} shares\n"
                output += f"💰 Capital Required: {format_currency(result['capital_required'])}\n"
                output += "\n" + "="*50 + "\n"
                
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, output)
                
            except Exception as e:
                result_text.delete(1.0, tk.END)
                result_text.insert(tk.END, f"Error: {str(e)}\n")
        
        ttk.Button(frame, text="Calculate", command=calculate).pack(pady=5)
        ttk.Button(frame, text="Close", command=calc_window.destroy).pack(pady=5)
    
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
            
            messagebox.showinfo("Export Successful", 
                              f"Portfolio exported to:\n{positions_file}\n{holdings_file}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error exporting portfolio:\n{str(e)}")
    
    def refresh_current_view(self):
        """Refresh the current view"""
        if self.current_view == 'portfolio':
            self.show_portfolio()
        elif self.current_view == 'positions':
            self.show_positions()
        elif self.current_view == 'holdings':
            self.show_holdings()
        elif self.current_view == 'orders':
            self.show_orders()
        elif self.current_view == 'gainers_losers':
            self.show_gainers_losers()
        else:
            messagebox.showinfo("Refresh", "No active view to refresh")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = TradingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
