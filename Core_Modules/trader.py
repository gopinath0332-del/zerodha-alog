"""
Trading module for executing trades on Zerodha Kite Connect
"""
from kiteconnect import KiteConnect
from .auth import KiteAuth
from .config import Config
from .logger import get_logger
import pandas as pd

logger = get_logger(__name__)


class KiteTrader:
    """Main trading class for Zerodha Kite Connect"""
    
    def __init__(self):
        """Initialize trader with authenticated KiteConnect instance"""
        auth = KiteAuth()
        self.kite = auth.get_kite_instance()
    
    # ==================== Market Data Methods ====================
    
    def get_instruments(self, exchange=None):
        """
        Get list of all instruments
        
        Args:
            exchange (str, optional): Exchange name (NSE, BSE, NFO, etc.)
            
        Returns:
            list: List of instruments
        """
        try:
            instruments = self.kite.instruments(exchange)
            logger.info(
                "instruments_fetched",
                exchange=exchange,
                count=len(instruments)
            )
            return instruments
        except Exception as e:
            logger.error(
                "instruments_fetch_failed",
                exchange=exchange,
                error=str(e),
                exc_info=True
            )
            raise
    
    def get_quote(self, *instruments):
        """
        Get quote for instruments
        
        Args:
            *instruments: Instrument codes (e.g., 'NSE:INFY', 'BSE:SENSEX')
            
        Returns:
            dict: Quote data
        """
        try:
            quote = self.kite.quote(*instruments)
            logger.debug(
                "quote_fetched",
                instruments=list(instruments),
                count=len(instruments)
            )
            return quote
        except Exception as e:
            logger.error(
                "quote_fetch_failed",
                instruments=list(instruments),
                error=str(e),
                exc_info=True
            )
            raise
    
    def get_ltp(self, *instruments):
        """
        Get last traded price for instruments
        
        Args:
            *instruments: Instrument codes (e.g., 'NSE:INFY')
            
        Returns:
            dict: LTP data
        """
        try:
            ltp = self.kite.ltp(*instruments)
            return ltp
        except Exception as e:
            logger.error(f"Failed to fetch LTP: {e}")
            raise
    
    def get_ohlc(self, *instruments):
        """
        Get OHLC and market depth for instruments
        
        Args:
            *instruments: Instrument codes
            
        Returns:
            dict: OHLC data
        """
        try:
            ohlc = self.kite.ohlc(*instruments)
            return ohlc
        except Exception as e:
            logger.error(f"Failed to fetch OHLC: {e}")
            raise
    
    def get_historical_data(self, instrument_token, from_date, to_date, interval):
        """
        Get historical candle data
        
        Args:
            instrument_token (str): Instrument token
            from_date (datetime/str): From date
            to_date (datetime/str): To date
            interval (str): Candle interval (minute, day, 3minute, 5minute, etc.)
            
        Returns:
            list: Historical data
        """
        try:
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            logger.info(f"Fetched {len(data)} candles")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            raise
    
    # ==================== Order Management Methods ====================
    
    def place_order(self, symbol, exchange, transaction_type, quantity, 
                   order_type='MARKET', product='CNC', price=None, 
                   trigger_price=None, validity='DAY', variety='regular'):
        """
        Place an order
        
        Args:
            symbol (str): Trading symbol (e.g., 'INFY')
            exchange (str): Exchange (NSE, BSE, etc.)
            transaction_type (str): BUY or SELL
            quantity (int): Quantity to trade
            order_type (str): MARKET, LIMIT, SL, SL-M
            product (str): CNC, MIS, NRML
            price (float, optional): Price for limit orders
            trigger_price (float, optional): Trigger price for SL orders
            validity (str): DAY or IOC
            variety (str): regular, amo, co, iceberg
            
        Returns:
            str: Order ID
        """
        try:
            order_id = self.kite.place_order(
                variety=variety,
                exchange=exchange,
                tradingsymbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                product=product,
                order_type=order_type,
                price=price,
                validity=validity,
                trigger_price=trigger_price
            )
            logger.info(
                "order_placed",
                order_id=order_id,
                symbol=symbol,
                exchange=exchange,
                transaction_type=transaction_type,
                quantity=quantity,
                order_type=order_type,
                product=product,
                price=price
            )
            return order_id
        except Exception as e:
            logger.error(
                "order_placement_failed",
                symbol=symbol,
                exchange=exchange,
                transaction_type=transaction_type,
                quantity=quantity,
                error=str(e),
                exc_info=True
            )
            raise
    
    def modify_order(self, order_id, variety='regular', quantity=None, 
                    price=None, order_type=None, trigger_price=None, validity=None):
        """
        Modify an existing order
        
        Args:
            order_id (str): Order ID to modify
            variety (str): Order variety
            quantity (int, optional): New quantity
            price (float, optional): New price
            order_type (str, optional): New order type
            trigger_price (float, optional): New trigger price
            validity (str, optional): New validity
            
        Returns:
            str: Order ID
        """
        try:
            order_id = self.kite.modify_order(
                variety=variety,
                order_id=order_id,
                quantity=quantity,
                price=price,
                order_type=order_type,
                trigger_price=trigger_price,
                validity=validity
            )
            logger.info(f"Order modified successfully. Order ID: {order_id}")
            return order_id
        except Exception as e:
            logger.error(f"Order modification failed: {e}")
            raise
    
    def cancel_order(self, order_id, variety='regular'):
        """
        Cancel an order
        
        Args:
            order_id (str): Order ID to cancel
            variety (str): Order variety
            
        Returns:
            str: Order ID
        """
        try:
            order_id = self.kite.cancel_order(variety=variety, order_id=order_id)
            logger.info(f"Order cancelled successfully. Order ID: {order_id}")
            return order_id
        except Exception as e:
            logger.error(f"Order cancellation failed: {e}")
            raise
    
    def get_orders(self):
        """
        Get all orders for the day
        
        Returns:
            list: List of orders
        """
        try:
            orders = self.kite.orders()
            logger.info(f"Fetched {len(orders)} orders")
            return orders
        except Exception as e:
            logger.error(f"Failed to fetch orders: {e}")
            raise
    
    def get_order_history(self, order_id):
        """
        Get history of a particular order
        
        Args:
            order_id (str): Order ID
            
        Returns:
            list: Order history
        """
        try:
            history = self.kite.order_history(order_id=order_id)
            return history
        except Exception as e:
            logger.error(f"Failed to fetch order history: {e}")
            raise
    
    # ==================== Portfolio Methods ====================
    
    def get_positions(self):
        """
        Get current positions
        
        Returns:
            dict: Positions (day and net)
        """
        try:
            positions = self.kite.positions()
            day_count = len([p for p in positions.get('day', []) if p['quantity'] != 0])
            net_count = len([p for p in positions.get('net', []) if p['quantity'] != 0])
            logger.info(
                "positions_fetched",
                day_positions=day_count,
                net_positions=net_count,
                total_positions=day_count + net_count
            )
            return positions
        except Exception as e:
            logger.error(
                "positions_fetch_failed",
                error=str(e),
                exc_info=True
            )
            raise
    
    def get_holdings(self):
        """
        Get holdings (long term positions)
        
        Returns:
            list: Holdings
        """
        try:
            holdings = self.kite.holdings()
            logger.info(f"Fetched {len(holdings)} holdings")
            return holdings
        except Exception as e:
            logger.error(f"Failed to fetch holdings: {e}")
            raise
    
    def get_margins(self, segment=None):
        """
        Get account margins
        
        Args:
            segment (str, optional): equity or commodity
            
        Returns:
            dict: Margin data
        """
        try:
            margins = self.kite.margins(segment)
            return margins
        except Exception as e:
            logger.error(f"Failed to fetch margins: {e}")
            raise
    
    # ==================== Helper Methods ====================
    
    def buy_market(self, symbol, quantity, exchange='NSE', product='CNC'):
        """
        Place a market buy order
        
        Args:
            symbol (str): Trading symbol
            quantity (int): Quantity to buy
            exchange (str): Exchange
            product (str): Product type
            
        Returns:
            str: Order ID
        """
        return self.place_order(
            symbol=symbol,
            exchange=exchange,
            transaction_type=self.kite.TRANSACTION_TYPE_BUY,
            quantity=quantity,
            order_type=self.kite.ORDER_TYPE_MARKET,
            product=product
        )
    
    def sell_market(self, symbol, quantity, exchange='NSE', product='CNC'):
        """
        Place a market sell order
        
        Args:
            symbol (str): Trading symbol
            quantity (int): Quantity to sell
            exchange (str): Exchange
            product (str): Product type
            
        Returns:
            str: Order ID
        """
        return self.place_order(
            symbol=symbol,
            exchange=exchange,
            transaction_type=self.kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            order_type=self.kite.ORDER_TYPE_MARKET,
            product=product
        )
    
    def buy_limit(self, symbol, quantity, price, exchange='NSE', product='CNC'):
        """
        Place a limit buy order
        
        Args:
            symbol (str): Trading symbol
            quantity (int): Quantity to buy
            price (float): Limit price
            exchange (str): Exchange
            product (str): Product type
            
        Returns:
            str: Order ID
        """
        return self.place_order(
            symbol=symbol,
            exchange=exchange,
            transaction_type=self.kite.TRANSACTION_TYPE_BUY,
            quantity=quantity,
            order_type=self.kite.ORDER_TYPE_LIMIT,
            product=product,
            price=price
        )
    
    def sell_limit(self, symbol, quantity, price, exchange='NSE', product='CNC'):
        """
        Place a limit sell order
        
        Args:
            symbol (str): Trading symbol
            quantity (int): Quantity to sell
            price (float): Limit price
            exchange (str): Exchange
            product (str): Product type
            
        Returns:
            str: Order ID
        """
        return self.place_order(
            symbol=symbol,
            exchange=exchange,
            transaction_type=self.kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            order_type=self.kite.ORDER_TYPE_LIMIT,
            product=product,
            price=price
        )


if __name__ == "__main__":
    # Example usage
    trader = KiteTrader()
    
    # Get quote
    quote = trader.get_quote('NSE:INFY', 'NSE:TCS')
    logger.info("quote_fetched", quote=quote)
    
    # Get positions
    positions = trader.get_positions()
    logger.info("positions_fetched", positions=positions)
    
    # Get holdings
    holdings = trader.get_holdings()
    logger.info("holdings_fetched", holdings=holdings)
