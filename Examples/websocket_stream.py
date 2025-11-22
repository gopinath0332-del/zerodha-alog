"""
Example: Real-time market data streaming using WebSocket
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Core_Modules.websocket_ticker import KiteWebSocket
from Core_Modules.trader import KiteTrader
import logging

logging.basicConfig(level=logging.INFO)


class MarketDataStream:
    """Example market data streaming class"""
    
    def __init__(self):
        self.trader = KiteTrader()
        self.instrument_tokens = []
    
    def get_instrument_token(self, exchange, symbol):
        """
        Get instrument token for a symbol
        
        Args:
            exchange: Exchange name (NSE, BSE, etc.)
            symbol: Trading symbol
            
        Returns:
            int: Instrument token
        """
        instruments = self.trader.get_instruments(exchange)
        
        for instrument in instruments:
            if instrument['tradingsymbol'] == symbol:
                return instrument['instrument_token']
        
        return None
    
    def on_ticks(self, ws, ticks):
        """Handle incoming tick data"""
        for tick in ticks:
            print(f"\n--- {tick.get('tradable', 'Unknown')} ---")
            print(f"Instrument Token: {tick['instrument_token']}")
            print(f"Last Price: ₹{tick['last_price']}")
            print(f"Volume: {tick.get('volume', 0):,}")
            print(f"Change: {tick.get('change', 0):.2f}%")
            
            if 'ohlc' in tick:
                print(f"OHLC: O={tick['ohlc']['open']}, "
                      f"H={tick['ohlc']['high']}, "
                      f"L={tick['ohlc']['low']}, "
                      f"C={tick['ohlc']['close']}")
            
            if 'depth' in tick:
                print("Market Depth:")
                print("  Buy Side:")
                for i, bid in enumerate(tick['depth']['buy'][:3], 1):
                    print(f"    {i}. Price: ₹{bid['price']}, Qty: {bid['quantity']}, Orders: {bid['orders']}")
                print("  Sell Side:")
                for i, ask in enumerate(tick['depth']['sell'][:3], 1):
                    print(f"    {i}. Price: ₹{ask['price']}, Qty: {ask['quantity']}, Orders: {ask['orders']}")
    
    def on_connect(self, ws, response):
        """Handle connection event"""
        print(f"\n✓ WebSocket connected: {response}")
        
        if self.instrument_tokens:
            print(f"Subscribing to {len(self.instrument_tokens)} instruments...")
            ws.subscribe(self.instrument_tokens)
            ws.set_mode(ws.MODE_FULL, self.instrument_tokens)
            print("✓ Subscription successful")
    
    def on_close(self, ws, code, reason):
        """Handle close event"""
        print(f"\n✗ Connection closed: {code} - {reason}")
        ws.stop()
    
    def on_error(self, ws, code, reason):
        """Handle error event"""
        print(f"\n✗ Error: {code} - {reason}")
    
    def start_streaming(self, symbols):
        """
        Start streaming market data for given symbols
        
        Args:
            symbols: List of tuples [(exchange, symbol), ...]
        """
        print("\n=== Fetching Instrument Tokens ===")
        
        for exchange, symbol in symbols:
            token = self.get_instrument_token(exchange, symbol)
            if token:
                self.instrument_tokens.append(token)
                print(f"✓ {exchange}:{symbol} -> Token: {token}")
            else:
                print(f"✗ {exchange}:{symbol} -> Token not found")
        
        if not self.instrument_tokens:
            print("\n✗ No valid instruments to stream")
            return
        
        print(f"\n=== Starting WebSocket Stream ===")
        print("Press Ctrl+C to stop\n")
        
        # Create WebSocket instance
        kws = KiteWebSocket(
            on_ticks_callback=self.on_ticks,
            on_connect_callback=self.on_connect,
            on_close_callback=self.on_close,
            on_error_callback=self.on_error
        )
        
        try:
            kws.connect()
        except KeyboardInterrupt:
            print("\n\nStopping stream...")
            kws.close()
            print("Stream stopped")


def main():
    streamer = MarketDataStream()
    
    # Define symbols to stream
    # Format: [(exchange, symbol), ...]
    symbols = [
        ('NSE', 'INFY'),
        ('NSE', 'TCS'),
        ('NSE', 'RELIANCE'),
        ('NSE', 'HDFCBANK'),
        ('NSE', 'SBIN')
    ]
    
    # Start streaming
    streamer.start_streaming(symbols)


if __name__ == "__main__":
    main()
