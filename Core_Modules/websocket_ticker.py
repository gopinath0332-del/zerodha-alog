"""
WebSocket ticker module for real-time market data streaming
"""
from kiteconnect import KiteTicker
from .auth import KiteAuth
from .config import Config
from .logger import get_logger

logger = get_logger(__name__)


class KiteWebSocket:
    """WebSocket client for real-time market data"""
    
    def __init__(self, on_ticks_callback=None, on_connect_callback=None, 
                 on_close_callback=None, on_error_callback=None):
        """
        Initialize WebSocket ticker
        
        Args:
            on_ticks_callback: Callback function for tick data
            on_connect_callback: Callback function on connection
            on_close_callback: Callback function on close
            on_error_callback: Callback function on error
        """
        auth = KiteAuth()
        
        if not auth.access_token:
            raise ValueError("Access token not available. Please authenticate first.")
        
        self.kws = KiteTicker(Config.API_KEY, auth.access_token)
        
        # Set callbacks
        self.kws.on_ticks = on_ticks_callback or self.on_ticks
        self.kws.on_connect = on_connect_callback or self.on_connect
        self.kws.on_close = on_close_callback or self.on_close
        self.kws.on_error = on_error_callback or self.on_error
        
        self.subscribed_tokens = []
    
    def on_ticks(self, ws, ticks):
        """
        Default callback to receive ticks
        
        Args:
            ws: WebSocket instance
            ticks: List of tick data
        """
        logger.info("ticks_received", count=len(ticks))
        for tick in ticks:
            logger.debug(
                "tick_received",
                instrument_token=tick.get('instrument_token'),
                last_price=tick.get('last_price'),
                volume=tick.get('volume')
            )
    
    def on_connect(self, ws, response):
        """
        Default callback on successful connect
        
        Args:
            ws: WebSocket instance
            response: Connection response
        """
        logger.info("websocket_connected", response=response)
        
        # Subscribe to tokens if any were set before connection
        if self.subscribed_tokens:
            ws.subscribe(self.subscribed_tokens)
            ws.set_mode(ws.MODE_FULL, self.subscribed_tokens)
            logger.info(
                "subscribed_on_connect",
                count=len(self.subscribed_tokens),
                tokens=self.subscribed_tokens
            )
    
    def on_close(self, ws, code, reason):
        """
        Default callback on connection close
        
        Args:
            ws: WebSocket instance
            code: Close code
            reason: Close reason
        """
        logger.info("connection_closed", code=code, reason=reason)
        ws.stop()
    
    def on_error(self, ws, code, reason):
        """
        Default callback on error
        
        Args:
            ws: WebSocket instance
            code: Error code
            reason: Error reason
        """
        logger.error("websocket_error", code=code, reason=reason)
    
    def subscribe(self, instrument_tokens):
        """
        Subscribe to instrument tokens
        
        Args:
            instrument_tokens (list): List of instrument tokens
        """
        if isinstance(instrument_tokens, int):
            instrument_tokens = [instrument_tokens]
        
        self.subscribed_tokens.extend(instrument_tokens)
        
        if self.kws.is_connected():
            self.kws.subscribe(instrument_tokens)
            logger.info(
                "subscribed",
                count=len(instrument_tokens),
                tokens=instrument_tokens
            )
        else:
            logger.info(
                "tokens_added_offline",
                count=len(instrument_tokens),
                tokens=instrument_tokens
            )
    
    def unsubscribe(self, instrument_tokens):
        """
        Unsubscribe from instrument tokens
        
        Args:
            instrument_tokens (list): List of instrument tokens
        """
        if isinstance(instrument_tokens, int):
            instrument_tokens = [instrument_tokens]
        
        self.kws.unsubscribe(instrument_tokens)
        
        for token in instrument_tokens:
            if token in self.subscribed_tokens:
                self.subscribed_tokens.remove(token)
        
        logger.info(
            "unsubscribed",
            count=len(instrument_tokens),
            tokens=instrument_tokens
        )
    
    def set_mode(self, mode, instrument_tokens):
        """
        Set mode for instruments
        
        Args:
            mode: MODE_LTP, MODE_QUOTE, or MODE_FULL
            instrument_tokens (list): List of instrument tokens
        """
        if isinstance(instrument_tokens, int):
            instrument_tokens = [instrument_tokens]
        
        self.kws.set_mode(mode, instrument_tokens)
        logger.info(
            "mode_set",
            mode=mode,
            count=len(instrument_tokens),
            tokens=instrument_tokens
        )
    
    def connect(self, threaded=False):
        """
        Connect to WebSocket
        
        Args:
            threaded (bool): Run in threaded mode
        """
        logger.info("connecting_websocket", threaded=threaded)
        self.kws.connect(threaded=threaded)
    
    def close(self):
        """Close WebSocket connection"""
        self.kws.close()
        logger.info("websocket_closed")


if __name__ == "__main__":
    # Example usage
    
    def on_ticks(ws, ticks):
        """Custom tick handler"""
        for tick in ticks:
            logger.info(
                "tick_received",
                instrument_token=tick.get('instrument_token'),
                last_price=tick.get('last_price'),
                volume=tick.get('volume', 'N/A')
            )
    
    def on_connect(ws, response):
        """Custom connect handler"""
        logger.info("connected", response=response)
        
        # Example: Subscribe to RELIANCE and TCS
        # You need to replace these with actual instrument tokens
        # Get tokens from kite.instruments() or kite.ltp()
        instrument_tokens = [738561, 2953217]  # Example tokens
        
        ws.subscribe(instrument_tokens)
        ws.set_mode(ws.MODE_FULL, instrument_tokens)
    
    def on_close(ws, code, reason):
        """Custom close handler"""
        logger.info("connection_closed", code=code, reason=reason)
        ws.stop()
    
    # Create WebSocket instance
    kws = KiteWebSocket(
        on_ticks_callback=on_ticks,
        on_connect_callback=on_connect,
        on_close_callback=on_close
    )
    
    # Connect
    logger.info("starting_websocket_connection")
    logger.info("press_ctrl_c_to_stop")
    
    try:
        kws.connect()
    except KeyboardInterrupt:
        logger.info("stopping_websocket")
        kws.close()
