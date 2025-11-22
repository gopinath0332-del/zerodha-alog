"""
Example: Place a basic market order
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Core_Modules.trader import KiteTrader
import logging

logging.basicConfig(level=logging.INFO)


def main():
    # Initialize trader
    trader = KiteTrader()
    
    # Example 1: Get quote for a stock
    print("\n=== Example 1: Get Quote ===")
    quote = trader.get_quote('NSE:INFY')
    print(f"INFY Quote: {quote}")
    
    # Example 2: Get LTP (Last Traded Price)
    print("\n=== Example 2: Get LTP ===")
    ltp = trader.get_ltp('NSE:TCS', 'NSE:RELIANCE')
    print(f"LTP: {ltp}")
    
    # Example 3: Place a market buy order (COMMENTED FOR SAFETY)
    # UNCOMMENT ONLY WHEN YOU'RE READY TO PLACE ACTUAL ORDERS
    """
    print("\n=== Example 3: Place Market Buy Order ===")
    symbol = 'INFY'
    quantity = 1
    
    try:
        order_id = trader.buy_market(
            symbol=symbol,
            quantity=quantity,
            exchange='NSE',
            product='CNC'  # CNC for delivery
        )
        print(f"Order placed successfully! Order ID: {order_id}")
    except Exception as e:
        print(f"Order failed: {e}")
    """
    
    # Example 4: Get all orders
    print("\n=== Example 4: Get All Orders ===")
    orders = trader.get_orders()
    print(f"Total orders today: {len(orders)}")
    for order in orders[-5:]:  # Show last 5 orders
        print(f"Order: {order['tradingsymbol']} - {order['status']} - {order['order_type']}")
    
    # Example 5: Get positions
    print("\n=== Example 5: Get Positions ===")
    positions = trader.get_positions()
    if positions['day']:
        print(f"Day positions: {len(positions['day'])}")
        for pos in positions['day']:
            print(f"Position: {pos['tradingsymbol']} - Qty: {pos['quantity']} - P&L: {pos['pnl']}")
    else:
        print("No day positions")
    
    # Example 6: Get holdings
    print("\n=== Example 6: Get Holdings ===")
    holdings = trader.get_holdings()
    print(f"Total holdings: {len(holdings)}")
    for holding in holdings[:5]:  # Show first 5 holdings
        print(f"Holding: {holding['tradingsymbol']} - Qty: {holding['quantity']} - P&L: {holding['pnl']}")
    
    # Example 7: Get margins
    print("\n=== Example 7: Get Margins ===")
    margins = trader.get_margins('equity')
    print(f"Available margin: ₹{margins['available']['live_balance']:.2f}")
    print(f"Used margin: ₹{margins['utilised']['debits']:.2f}")


if __name__ == "__main__":
    main()
