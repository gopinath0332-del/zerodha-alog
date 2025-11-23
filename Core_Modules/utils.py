"""
Utility functions for trading operations
"""
from .trader import KiteTrader
import pandas as pd
from datetime import datetime, timedelta
from .logger import get_logger

logger = get_logger(__name__)


def search_instruments(trader, search_term, exchange='NSE'):
    """
    Search for instruments by symbol or name
    
    Args:
        trader: KiteTrader instance
        search_term: Search string
        exchange: Exchange to search in
        
    Returns:
        list: Matching instruments
    """
    try:
        instruments = trader.get_instruments(exchange)
        
        search_term = search_term.upper()
        matches = []
        
        for instrument in instruments:
            if (search_term in instrument['tradingsymbol'].upper() or 
                search_term in instrument['name'].upper()):
                matches.append({
                    'symbol': instrument['tradingsymbol'],
                    'name': instrument['name'],
                    'instrument_token': instrument['instrument_token'],
                    'exchange': instrument['exchange'],
                    'instrument_type': instrument['instrument_type']
                })
        
        return matches
        
    except Exception as e:
        logger.error("instrument_search_failed", error=str(e), exc_info=True)
        return []


def get_top_gainers_losers(trader, symbols, top_n=5):
    """
    Get top gainers and losers from a list of symbols
    
    Args:
        trader: KiteTrader instance
        symbols: List of symbols
        top_n: Number of top gainers/losers to return
        
    Returns:
        dict: {'gainers': [], 'losers': []}
    """
    try:
        instruments = [f'NSE:{s}' if ':' not in s else s for s in symbols]
        quotes = trader.get_quote(*instruments)
        
        changes = []
        
        for instrument, data in quotes.items():
            symbol = instrument.split(':')[1]
            if 'ohlc' in data and 'last_price' in data:
                open_price = data['ohlc']['open']
                current_price = data['last_price']
                
                if open_price > 0:
                    change_pct = ((current_price - open_price) / open_price) * 100
                    changes.append({
                        'symbol': symbol,
                        'price': current_price,
                        'change_pct': round(change_pct, 2),
                        'volume': data.get('volume', 0)
                    })
        
        # Sort by change percentage
        changes.sort(key=lambda x: x['change_pct'], reverse=True)
        
        return {
            'gainers': changes[:top_n],
            'losers': changes[-top_n:][::-1]
        }
        
    except Exception as e:
        logger.error("gainers_losers_fetch_failed", error=str(e), exc_info=True)
        return {'gainers': [], 'losers': []}


def calculate_position_size(trader, symbol, risk_amount, sl_pct):
    """
    Calculate position size based on risk amount and stop loss
    
    Args:
        trader: KiteTrader instance
        symbol: Trading symbol
        risk_amount: Amount willing to risk in INR
        sl_pct: Stop loss percentage
        
    Returns:
        dict: Position size details
    """
    try:
        # Get current price
        ltp_data = trader.get_ltp(f'NSE:{symbol}')
        current_price = ltp_data[f'NSE:{symbol}']['last_price']
        
        # Calculate risk per share
        risk_per_share = current_price * (sl_pct / 100)
        
        # Calculate position size
        quantity = int(risk_amount / risk_per_share)
        
        # Calculate total investment
        total_investment = quantity * current_price
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'quantity': quantity,
            'total_investment': round(total_investment, 2),
            'risk_amount': round(quantity * risk_per_share, 2),
            'sl_price': round(current_price * (1 - sl_pct/100), 2)
        }
        
    except Exception as e:
        logger.error("position_size_calculation_failed", error=str(e), exc_info=True)
        return None


def export_positions_to_csv(trader, filename='positions.csv'):
    """
    Export current positions to CSV file
    
    Args:
        trader: KiteTrader instance
        filename: Output filename
    """
    try:
        positions = trader.get_positions()
        day_positions = [p for p in positions['day'] if p['quantity'] != 0]
        
        if not day_positions:
            logger.info("no_positions_to_export")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(day_positions)
        
        # Select relevant columns
        columns = ['tradingsymbol', 'exchange', 'product', 'quantity', 
                  'average_price', 'last_price', 'pnl', 'day_change']
        
        df = df[columns]
        
        # Save to CSV
        df.to_csv(filename, index=False)
        logger.info("positions_exported", filename=filename, count=len(day_positions))
        
    except Exception as e:
        logger.error("positions_export_failed", error=str(e), exc_info=True)


def export_holdings_to_csv(trader, filename='holdings.csv'):
    """
    Export holdings to CSV file
    
    Args:
        trader: KiteTrader instance
        filename: Output filename
    """
    try:
        holdings = trader.get_holdings()
        
        if not holdings:
            logger.info("no_holdings_to_export")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(holdings)
        
        # Select relevant columns
        columns = ['tradingsymbol', 'exchange', 'quantity', 'average_price', 
                  'last_price', 'pnl', 't1_quantity', 'isin']
        
        df = df[columns]
        
        # Save to CSV
        df.to_csv(filename, index=False)
        logger.info("holdings_exported", filename=filename, count=len(holdings))
        
    except Exception as e:
        logger.error("holdings_export_failed", error=str(e), exc_info=True)


def get_portfolio_summary(trader):
    """
    Get comprehensive portfolio summary
    
    Args:
        trader: KiteTrader instance
        
    Returns:
        dict: Portfolio summary
    """
    try:
        # Get margins
        margins = trader.get_margins('equity')
        
        # Get positions
        positions = trader.get_positions()
        day_positions = [p for p in positions['day'] if p['quantity'] != 0]
        
        # Get holdings
        holdings = trader.get_holdings()
        
        # Calculate totals
        total_day_pnl = sum(p['pnl'] for p in day_positions)
        total_holdings_pnl = sum(h['pnl'] for h in holdings)
        total_investment = sum(h['average_price'] * h['quantity'] for h in holdings)
        total_current_value = sum(h['last_price'] * h['quantity'] for h in holdings)
        
        summary = {
            'available_margin': margins['available']['live_balance'],
            'used_margin': margins['utilised']['debits'],
            'day_positions_count': len(day_positions),
            'day_positions_pnl': round(total_day_pnl, 2),
            'holdings_count': len(holdings),
            'holdings_investment': round(total_investment, 2),
            'holdings_current_value': round(total_current_value, 2),
            'holdings_pnl': round(total_holdings_pnl, 2),
            'total_pnl': round(total_day_pnl + total_holdings_pnl, 2)
        }
        
        return summary
        
    except Exception as e:
        logger.error("portfolio_summary_failed", error=str(e), exc_info=True)
        return None


def monitor_orders(trader, interval=5, max_checks=12):
    """
    Monitor pending orders and log status
    
    Args:
        trader: KiteTrader instance
        interval: Check interval in seconds
        max_checks: Maximum number of checks
    """
    import time
    
    try:
        for i in range(max_checks):
            orders = trader.get_orders()
            pending = [o for o in orders if o['status'] in ['OPEN', 'TRIGGER PENDING']]
            
            if not pending:
                logger.info("no_pending_orders")
                break
            
            logger.info("pending_orders_check", check=i+1, max_checks=max_checks, count=len(pending))
            
            for order in pending:
                logger.info(
                    "pending_order_status",
                    symbol=order['tradingsymbol'],
                    status=order['status'],
                    transaction=order['transaction_type'],
                    quantity=order['quantity'],
                    price=order.get('price', order.get('trigger_price', 'MARKET'))
                )
            
            if i < max_checks - 1:
                time.sleep(interval)
        
    except Exception as e:
        logger.error("order_monitoring_failed", error=str(e), exc_info=True)


if __name__ == "__main__":
    trader = KiteTrader()
    
    # Example 1: Search instruments
    logger.info("searching_instruments")
    results = search_instruments(trader, 'INFY', 'NSE')
    for result in results[:5]:
        logger.info(
            "instrument_found",
            symbol=result['symbol'],
            name=result['name'],
            type=result['instrument_type']
        )
    
    # Example 2: Get portfolio summary
    logger.info("fetching_portfolio_summary")
    summary = get_portfolio_summary(trader)
    if summary:
        logger.info(
            "portfolio_summary",
            available_margin=summary['available_margin'],
            day_pnl=summary['day_positions_pnl'],
            holdings_pnl=summary['holdings_pnl'],
            total_pnl=summary['total_pnl']
        )
    
    # Example 3: Calculate position size
    logger.info("calculating_position_size")
    pos_size = calculate_position_size(trader, 'INFY', risk_amount=1000, sl_pct=2.0)
    if pos_size:
        logger.info(
            "position_size_calculated",
            symbol=pos_size['symbol'],
            current_price=pos_size['current_price'],
            quantity=pos_size['quantity'],
            investment=pos_size['total_investment'],
            risk=pos_size['risk_amount'],
            stop_loss=pos_size['sl_price']
        )
