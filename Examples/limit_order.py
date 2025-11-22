"""
Example: Place limit orders with stop loss
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Core_Modules.trader import KiteTrader
from kiteconnect import KiteConnect
import logging

logging.basicConfig(level=logging.INFO)


def place_limit_order_with_sl(trader, symbol, quantity, limit_price, sl_price):
    """
    Place a limit buy order with stop loss
    
    Args:
        trader: KiteTrader instance
        symbol: Trading symbol
        quantity: Quantity to buy
        limit_price: Limit price for buy order
        sl_price: Stop loss price
    """
    print(f"\n=== Placing Limit Order for {symbol} ===")
    print(f"Quantity: {quantity}")
    print(f"Limit Price: ₹{limit_price}")
    print(f"Stop Loss: ₹{sl_price}")
    
    # UNCOMMENT WHEN READY TO PLACE ACTUAL ORDERS
    """
    try:
        # Place limit buy order
        buy_order_id = trader.buy_limit(
            symbol=symbol,
            quantity=quantity,
            price=limit_price,
            exchange='NSE',
            product='MIS'  # MIS for intraday
        )
        print(f"✓ Buy order placed! Order ID: {buy_order_id}")
        
        # Wait for order to execute (in real scenario, you'd monitor order status)
        # Then place stop loss order
        
        # Place stop loss order (SL-M type)
        sl_order_id = trader.place_order(
            symbol=symbol,
            exchange='NSE',
            transaction_type=trader.kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            order_type=trader.kite.ORDER_TYPE_SLM,  # Stop Loss Market
            product='MIS',
            trigger_price=sl_price
        )
        print(f"✓ Stop loss order placed! Order ID: {sl_order_id}")
        
        return buy_order_id, sl_order_id
        
    except Exception as e:
        print(f"✗ Order failed: {e}")
        return None, None
    """
    print("(Orders are commented out for safety)")


def main():
    # Initialize trader
    trader = KiteTrader()
    
    # Example: Get current price first
    symbol = 'INFY'
    quote = trader.get_quote(f'NSE:{symbol}')
    current_price = quote[f'NSE:{symbol}']['last_price']
    
    print(f"\n{symbol} Current Price: ₹{current_price}")
    
    # Set limit price slightly below current price (for buy order)
    limit_price = round(current_price * 0.99, 2)  # 1% below current price
    
    # Set stop loss 2% below limit price
    sl_price = round(limit_price * 0.98, 2)
    
    # Place order
    place_limit_order_with_sl(
        trader=trader,
        symbol=symbol,
        quantity=1,
        limit_price=limit_price,
        sl_price=sl_price
    )
    
    # Show pending orders
    print("\n=== Pending Orders ===")
    orders = trader.get_orders()
    pending_orders = [o for o in orders if o['status'] in ['TRIGGER PENDING', 'OPEN']]
    
    for order in pending_orders:
        print(f"Order ID: {order['order_id']}")
        print(f"  Symbol: {order['tradingsymbol']}")
        print(f"  Type: {order['transaction_type']} {order['order_type']}")
        print(f"  Quantity: {order['quantity']}")
        print(f"  Price: ₹{order.get('price', 'N/A')}")
        print(f"  Trigger Price: ₹{order.get('trigger_price', 'N/A')}")
        print(f"  Status: {order['status']}\n")


if __name__ == "__main__":
    main()
