"""
Common trading strategies and helper functions
"""
from .trader import KiteTrader
from datetime import datetime, timedelta
from .logger import get_logger

logger = get_logger(__name__)


class TradingStrategies:
    """Collection of common trading strategies"""
    
    def __init__(self):
        self.trader = KiteTrader()
    
    def place_bracket_order(self, symbol, quantity, target_pct=3.0, sl_pct=1.5):
        """
        Place a bracket order (buy with target and stop loss)
        
        Args:
            symbol: Trading symbol
            quantity: Quantity to trade
            target_pct: Target profit percentage
            sl_pct: Stop loss percentage
            
        Returns:
            dict: Order details
        """
        try:
            # Get current price
            ltp_data = self.trader.get_ltp(f'NSE:{symbol}')
            current_price = ltp_data[f'NSE:{symbol}']['last_price']
            
            # Calculate target and SL prices
            target_price = round(current_price * (1 + target_pct/100), 2)
            sl_price = round(current_price * (1 - sl_pct/100), 2)
            
            logger.info(
                "calculating_bracket_order",
                symbol=symbol,
                entry_price=current_price,
                target_price=target_price,
                target_pct=target_pct,
                sl_price=sl_price,
                sl_pct=sl_pct
            )
            
            # This is just a simulation - actual bracket orders need to be placed carefully
            # UNCOMMENT TO PLACE REAL ORDERS
            """
            # Place buy order
            buy_order_id = self.trader.buy_market(
                symbol=symbol,
                quantity=quantity,
                exchange='NSE',
                product='MIS'
            )
            
            logger.info(f"Buy order placed: {buy_order_id}")
            
            # Place target order (limit sell)
            target_order_id = self.trader.sell_limit(
                symbol=symbol,
                quantity=quantity,
                price=target_price,
                exchange='NSE',
                product='MIS'
            )
            
            logger.info(f"Target order placed: {target_order_id}")
            
            # Place stop loss order (SL-M)
            sl_order_id = self.trader.place_order(
                symbol=symbol,
                exchange='NSE',
                transaction_type=self.trader.kite.TRANSACTION_TYPE_SELL,
                quantity=quantity,
                order_type=self.trader.kite.ORDER_TYPE_SLM,
                product='MIS',
                trigger_price=sl_price
            )
            
            logger.info(f"Stop loss order placed: {sl_order_id}")
            
            return {
                'buy_order_id': buy_order_id,
                'target_order_id': target_order_id,
                'sl_order_id': sl_order_id,
                'entry_price': current_price,
                'target_price': target_price,
                'sl_price': sl_price
            }
            """
            
            return {
                'entry_price': current_price,
                'target_price': target_price,
                'sl_price': sl_price,
                'status': 'simulation'
            }
            
        except Exception as e:
            logger.error("bracket_order_failed", error=str(e), exc_info=True)
            raise
    
    def momentum_strategy(self, symbols, threshold=2.0):
        """
        Simple momentum strategy - identify stocks with strong price movement
        
        Args:
            symbols: List of symbols to analyze
            threshold: Minimum % change to consider
            
        Returns:
            list: Stocks meeting momentum criteria
        """
        try:
            # Add NSE prefix if not present
            instruments = [f'NSE:{s}' if ':' not in s else s for s in symbols]
            
            # Get quotes
            quotes = self.trader.get_quote(*instruments)
            
            momentum_stocks = []
            
            for instrument, data in quotes.items():
                symbol = instrument.split(':')[1]
                
                if 'ohlc' in data and 'last_price' in data:
                    open_price = data['ohlc']['open']
                    current_price = data['last_price']
                    
                    if open_price > 0:
                        change_pct = ((current_price - open_price) / open_price) * 100
                        
                        if abs(change_pct) >= threshold:
                            momentum_stocks.append({
                                'symbol': symbol,
                                'current_price': current_price,
                                'open_price': open_price,
                                'change_pct': round(change_pct, 2),
                                'volume': data.get('volume', 0),
                                'high': data['ohlc']['high'],
                                'low': data['ohlc']['low']
                            })
            
            # Sort by absolute change percentage
            momentum_stocks.sort(key=lambda x: abs(x['change_pct']), reverse=True)
            
            return momentum_stocks
            
        except Exception as e:
            logger.error("momentum_strategy_failed", error=str(e), exc_info=True)
            raise
    
    def trailing_stop_loss(self, symbol, quantity, initial_sl_pct=2.0, trail_pct=0.5):
        """
        Implement trailing stop loss logic
        
        Args:
            symbol: Trading symbol
            quantity: Quantity held
            initial_sl_pct: Initial stop loss percentage
            trail_pct: Trailing percentage
            
        Returns:
            dict: Trailing SL details
        """
        try:
            # Get current price
            ltp_data = self.trader.get_ltp(f'NSE:{symbol}')
            current_price = ltp_data[f'NSE:{symbol}']['last_price']
            
            # Get positions to find entry price
            positions = self.trader.get_positions()
            entry_price = None
            
            for pos in positions['day']:
                if pos['tradingsymbol'] == symbol and pos['quantity'] == quantity:
                    entry_price = pos['average_price']
                    break
            
            if not entry_price:
                logger.warning("no_position_found_for_trailing_sl", symbol=symbol)
                return None
            
            # Calculate profit percentage
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Calculate trailing SL
            if profit_pct > initial_sl_pct:
                # Trail stop loss
                trail_sl = round(current_price * (1 - trail_pct/100), 2)
            else:
                # Keep initial stop loss
                trail_sl = round(entry_price * (1 - initial_sl_pct/100), 2)
            
            logger.info(
                "trailing_sl_calculated",
                symbol=symbol,
                entry_price=entry_price,
                current_price=current_price,
                profit_pct=round(profit_pct, 2),
                trail_sl=trail_sl
            )
            
            return {
                'symbol': symbol,
                'entry_price': entry_price,
                'current_price': current_price,
                'profit_pct': round(profit_pct, 2),
                'trail_sl': trail_sl
            }
            
        except Exception as e:
            logger.error("trailing_sl_calculation_failed", error=str(e), exc_info=True)
            raise
    
    def square_off_all_positions(self):
        """
        Square off all open positions (use with caution!)
        """
        try:
            positions = self.trader.get_positions()
            day_positions = [p for p in positions['day'] if p['quantity'] != 0]
            
            if not day_positions:
                logger.info("no_positions_to_square_off")
                return
            
            logger.warning("squaring_off_positions", count=len(day_positions))
            
            # UNCOMMENT TO ACTUALLY SQUARE OFF
            """
            for pos in day_positions:
                symbol = pos['tradingsymbol']
                quantity = abs(pos['quantity'])
                
                # Determine transaction type (opposite of current position)
                if pos['quantity'] > 0:
                    # Long position - sell to square off
                    transaction_type = self.trader.kite.TRANSACTION_TYPE_SELL
                else:
                    # Short position - buy to square off
                    transaction_type = self.trader.kite.TRANSACTION_TYPE_BUY
                
                try:
                    order_id = self.trader.place_order(
                        symbol=symbol,
                        exchange=pos['exchange'],
                        transaction_type=transaction_type,
                        quantity=quantity,
                        order_type=self.trader.kite.ORDER_TYPE_MARKET,
                        product=pos['product']
                    )
                    logger.info(f"Squared off {symbol}: Order ID {order_id}")
                except Exception as e:
                    logger.error(f"Failed to square off {symbol}: {e}")
            """
            
            for pos in day_positions:
                logger.info(
                    "would_square_off",
                    symbol=pos['tradingsymbol'],
                    quantity=pos['quantity']
                )
            
        except Exception as e:
            logger.error("square_off_failed", error=str(e), exc_info=True)
            raise


if __name__ == "__main__":
    strategy = TradingStrategies()
    
    # Example 1: Momentum strategy
    logger.info("running_momentum_strategy")
    stocks = ['INFY', 'TCS', 'RELIANCE', 'HDFCBANK', 'SBIN', 'WIPRO', 'LT', 'ITC']
    momentum = strategy.momentum_strategy(stocks, threshold=1.5)
    
    logger.info("momentum_stocks_found", count=len(momentum))
    for stock in momentum:
        logger.info(
            "momentum_stock",
            symbol=stock['symbol'],
            change_pct=stock['change_pct'],
            current_price=stock['current_price'],
            volume=stock['volume']
        )
    
    # Example 2: Bracket order simulation
    logger.info("running_bracket_order_simulation")
    bracket = strategy.place_bracket_order('INFY', quantity=1, target_pct=3.0, sl_pct=1.5)
    logger.info(
        "bracket_order_result",
        entry_price=bracket['entry_price'],
        target_price=bracket['target_price'],
        sl_price=bracket['sl_price']
    )
