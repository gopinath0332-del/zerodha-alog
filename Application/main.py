"""
Main entry point for the trading application
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Core_Modules.trader import KiteTrader
from Core_Modules.config import Config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def display_menu():
    """Display main menu"""
    print("\n" + "="*50)
    print("  ZERODHA KITE TRADING BOT")
    print("="*50)
    print("\n1. View Market Data")
    print("2. View Portfolio")
    print("3. Place Order")
    print("4. View Orders")
    print("5. View Positions")
    print("6. View Holdings")
    print("7. View Margins")
    print("8. Start WebSocket Stream")
    print("9. Exit")
    print("\n" + "="*50)


def view_market_data(trader):
    """View market data for symbols"""
    print("\n=== Market Data ===")
    symbols_input = input("Enter symbols (e.g., NSE:INFY, NSE:TCS): ").strip()
    
    if not symbols_input:
        print("No symbols entered")
        return
    
    symbols = [s.strip() for s in symbols_input.split(',')]
    
    try:
        # Get quote
        quote = trader.get_quote(*symbols)
        
        for symbol in symbols:
            if symbol in quote:
                data = quote[symbol]
                print(f"\n{symbol}:")
                print(f"  Last Price: ₹{data['last_price']}")
                print(f"  Open: ₹{data['ohlc']['open']}")
                print(f"  High: ₹{data['ohlc']['high']}")
                print(f"  Low: ₹{data['ohlc']['low']}")
                print(f"  Close: ₹{data['ohlc']['close']}")
                print(f"  Volume: {data.get('volume', 'N/A'):,}")
                print(f"  Change: {data.get('net_change', 0):.2f}%")
    except Exception as e:
        logger.error(f"Failed to fetch market data: {e}")


def view_portfolio(trader):
    """View complete portfolio"""
    print("\n=== Portfolio Summary ===")
    
    try:
        # Get margins
        margins = trader.get_margins('equity')
        print(f"\nAvailable Margin: ₹{margins['available']['live_balance']:,.2f}")
        print(f"Used Margin: ₹{margins['utilised']['debits']:,.2f}")
        
        # Get positions
        positions = trader.get_positions()
        day_positions = positions['day']
        net_positions = positions['net']
        
        print(f"\nDay Positions: {len([p for p in day_positions if p['quantity'] != 0])}")
        print(f"Net Positions: {len([p for p in net_positions if p['quantity'] != 0])}")
        
        # Get holdings
        holdings = trader.get_holdings()
        print(f"Holdings: {len(holdings)}")
        
        total_investment = sum(h['average_price'] * h['quantity'] for h in holdings)
        total_current_value = sum(h['last_price'] * h['quantity'] for h in holdings)
        total_pnl = total_current_value - total_investment
        
        print(f"\nHoldings Value: ₹{total_current_value:,.2f}")
        print(f"Total P&L: ₹{total_pnl:,.2f} ({(total_pnl/total_investment*100) if total_investment > 0 else 0:.2f}%)")
        
    except Exception as e:
        logger.error(f"Failed to fetch portfolio: {e}")


def place_order_interactive(trader):
    """Interactive order placement"""
    print("\n=== Place Order ===")
    print("⚠️  WARNING: This will place a REAL order!")
    
    confirm = input("Do you want to continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Order cancelled")
        return
    
    try:
        # Get order details
        symbol = input("Symbol (e.g., INFY): ").strip().upper()
        exchange = input("Exchange (NSE/BSE) [NSE]: ").strip().upper() or 'NSE'
        transaction = input("Transaction (BUY/SELL): ").strip().upper()
        quantity = int(input("Quantity: ").strip())
        order_type = input("Order Type (MARKET/LIMIT) [MARKET]: ").strip().upper() or 'MARKET'
        product = input("Product (CNC/MIS/NRML) [CNC]: ").strip().upper() or 'CNC'
        
        price = None
        if order_type == 'LIMIT':
            price = float(input("Price: ").strip())
        
        # Confirm order
        print(f"\n--- Order Summary ---")
        print(f"Symbol: {symbol}")
        print(f"Exchange: {exchange}")
        print(f"Transaction: {transaction}")
        print(f"Quantity: {quantity}")
        print(f"Type: {order_type}")
        print(f"Product: {product}")
        if price:
            print(f"Price: ₹{price}")
        print("--------------------")
        
        final_confirm = input("\nConfirm order? (yes/no): ").strip().lower()
        if final_confirm != 'yes':
            print("Order cancelled")
            return
        
        # Place order
        order_id = trader.place_order(
            symbol=symbol,
            exchange=exchange,
            transaction_type=transaction,
            quantity=quantity,
            order_type=order_type,
            product=product,
            price=price
        )
        
        print(f"\n✓ Order placed successfully!")
        print(f"Order ID: {order_id}")
        
    except Exception as e:
        logger.error(f"Order placement failed: {e}")


def view_orders(trader):
    """View all orders"""
    print("\n=== Orders ===")
    
    try:
        orders = trader.get_orders()
        
        if not orders:
            print("No orders found")
            return
        
        print(f"\nTotal orders: {len(orders)}\n")
        
        for i, order in enumerate(orders[-10:], 1):  # Show last 10 orders
            print(f"{i}. Order ID: {order['order_id']}")
            print(f"   Symbol: {order['tradingsymbol']}")
            print(f"   Type: {order['transaction_type']} {order['order_type']}")
            print(f"   Quantity: {order['quantity']}")
            print(f"   Price: ₹{order.get('price', 'N/A')}")
            print(f"   Status: {order['status']}")
            print(f"   Time: {order['order_timestamp']}\n")
            
    except Exception as e:
        logger.error(f"Failed to fetch orders: {e}")


def view_positions(trader):
    """View current positions"""
    print("\n=== Positions ===")
    
    try:
        positions = trader.get_positions()
        
        day_positions = [p for p in positions['day'] if p['quantity'] != 0]
        
        if not day_positions:
            print("No positions found")
            return
        
        print(f"\nTotal positions: {len(day_positions)}\n")
        
        total_pnl = 0
        for i, pos in enumerate(day_positions, 1):
            print(f"{i}. {pos['tradingsymbol']}")
            print(f"   Quantity: {pos['quantity']}")
            print(f"   Average Price: ₹{pos['average_price']}")
            print(f"   Last Price: ₹{pos['last_price']}")
            print(f"   P&L: ₹{pos['pnl']:.2f}")
            print(f"   Day Change: {pos['day_change']:.2f}%\n")
            total_pnl += pos['pnl']
        
        print(f"Total P&L: ₹{total_pnl:.2f}")
        
    except Exception as e:
        logger.error(f"Failed to fetch positions: {e}")


def view_holdings(trader):
    """View holdings"""
    print("\n=== Holdings ===")
    
    try:
        holdings = trader.get_holdings()
        
        if not holdings:
            print("No holdings found")
            return
        
        print(f"\nTotal holdings: {len(holdings)}\n")
        
        total_investment = 0
        total_current = 0
        
        for i, holding in enumerate(holdings, 1):
            investment = holding['average_price'] * holding['quantity']
            current_value = holding['last_price'] * holding['quantity']
            
            print(f"{i}. {holding['tradingsymbol']}")
            print(f"   Quantity: {holding['quantity']}")
            print(f"   Avg Price: ₹{holding['average_price']:.2f}")
            print(f"   LTP: ₹{holding['last_price']:.2f}")
            print(f"   Investment: ₹{investment:,.2f}")
            print(f"   Current Value: ₹{current_value:,.2f}")
            print(f"   P&L: ₹{holding['pnl']:.2f} ({holding['pnl']/investment*100:.2f}%)\n")
            
            total_investment += investment
            total_current += current_value
        
        total_pnl = total_current - total_investment
        print(f"Total Investment: ₹{total_investment:,.2f}")
        print(f"Total Current Value: ₹{total_current:,.2f}")
        print(f"Total P&L: ₹{total_pnl:,.2f} ({total_pnl/total_investment*100:.2f}%)")
        
    except Exception as e:
        logger.error(f"Failed to fetch holdings: {e}")


def view_margins(trader):
    """View margin details"""
    print("\n=== Margins ===")
    
    try:
        margins = trader.get_margins()
        
        for segment, data in margins.items():
            print(f"\n{segment.upper()}:")
            print(f"  Available Cash: ₹{data['available']['cash']:,.2f}")
            print(f"  Available Margin: ₹{data['available']['live_balance']:,.2f}")
            print(f"  Used Margin: ₹{data['utilised']['debits']:,.2f}")
            
    except Exception as e:
        logger.error(f"Failed to fetch margins: {e}")


def main():
    """Main application loop"""
    try:
        # Initialize trader
        logger.info("Initializing trader...")
        trader = KiteTrader()
        logger.info("✓ Trader initialized successfully")
        
        while True:
            display_menu()
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == '1':
                view_market_data(trader)
            elif choice == '2':
                view_portfolio(trader)
            elif choice == '3':
                place_order_interactive(trader)
            elif choice == '4':
                view_orders(trader)
            elif choice == '5':
                view_positions(trader)
            elif choice == '6':
                view_holdings(trader)
            elif choice == '7':
                view_margins(trader)
            elif choice == '8':
                print("\nWebSocket streaming is available in examples/websocket_stream.py")
                print("Run: python examples/websocket_stream.py")
            elif choice == '9':
                print("\nGoodbye!")
                break
            else:
                print("\n✗ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        logger.error(f"Application error: {e}")


if __name__ == "__main__":
    main()
