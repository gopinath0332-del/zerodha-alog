"""
Structured Logging Configuration for Trading Bot

This module sets up structured logging using structlog for better
log analysis, debugging, and monitoring.
"""

import sys
import structlog
from pathlib import Path


def setup_logging(log_level="INFO", log_file=None):
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, logs only to console.
    
    Returns:
        Configured structlog logger
    """
    # Custom processor for float formatting, spacing, and value color
    import re
    def format_value(val):
        # Format direct floats and numpy floats
        if isinstance(val, float):
            return f"{val:.2f}"
        # Catch all float-like numpy types
        type_name = type(val).__name__
        if "float" in type_name:
            try:
                return f"{float(val):.2f}"
            except Exception:
                pass
        # Format np.floatXX(...) string representations
        if isinstance(val, str):
            match = re.match(r"np\.float(32|64)\(([-+]?[0-9]*\.?[0-9]+)\)", val)
            if match:
                return f"{float(match.group(2)):.2f}"
        # Recursively format lists, tuples, dicts
        if isinstance(val, list):
            return [format_value(x) for x in val]
        if isinstance(val, tuple):
            return tuple(format_value(x) for x in val)
        if isinstance(val, dict):
            return {k: format_value(v) for k, v in val.items()}
        return val

    def custom_log_formatter(logger, method_name, event_dict):
        formatted = {k: format_value(v) for k, v in event_dict.items()}
        return formatted
    
    import logging
    
    # Determine log level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level_int = level_map.get(log_level.upper(), logging.INFO)
    
    # Configure processors (shared)
    shared_processors = [
        custom_log_formatter,
        # Add log level to event dict
        structlog.stdlib.add_log_level,
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Add filename and line number
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            }
        ),
        # Stack info for exceptions
        structlog.processors.StackInfoRenderer(),
        # Format exceptions
        structlog.processors.format_exc_info,
        # Unicode handling
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            # Use ProcessorFormatter to delegate rendering to stdlib
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_int)
    
    # Colored output for console
    if sys.stderr.isatty():
        # Use ConsoleRenderer with default settings
        # The value color is already white by default in newer structlog versions
        from structlog.dev import ConsoleRenderer
        console_formatter = structlog.stdlib.ProcessorFormatter(
            processor=ConsoleRenderer(colors=True),
            foreign_pre_chain=shared_processors,
        )
    else:
        console_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=shared_processors,
        )
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_int)
    root_logger.addHandler(console_handler)
    
    # If log file specified, add file handler with JSON format
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level_int)
        
        # Console format for file (human-readable, same as terminal)
        from structlog.dev import ConsoleRenderer
        file_formatter = structlog.stdlib.ProcessorFormatter(
            processor=ConsoleRenderer(colors=False),  # No colors in file
            foreign_pre_chain=shared_processors,
        )
        file_handler.setFormatter(file_formatter)
        
        root_logger.addHandler(file_handler)
    
    return structlog.get_logger()


def get_logger(name=None):
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Example usage and best practices
if __name__ == "__main__":
    # Setup logging
    logger = setup_logging(log_level="DEBUG")
    
    # Basic logging
    logger.info("application_started", version="1.0.0")
    
    # Structured logging with context
    logger.info(
        "order_placed",
        order_id="123456",
        symbol="INFY",
        quantity=10,
        price=1500.00,
        order_type="MARKET"
    )
    
    # Warning with context
    logger.warning(
        "api_rate_limit_approaching",
        current_calls=95,
        max_calls=100,
        time_window="1min"
    )
    
    # Error logging
    try:
        result = 1 / 0
    except Exception as e:
        logger.error(
            "calculation_failed",
            error=str(e),
            exc_info=True
        )
    
    # Debug logging
    logger.debug(
        "position_calculated",
        symbol="TCS",
        entry_price=3500,
        stop_loss=3450,
        position_size=20
    )
