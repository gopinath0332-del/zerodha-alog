# Structured Logging Implementation

> **Feature**: Structured Logging with `structlog`  
> **Branch**: `feature/structlog`  
> **Date**: 2025-11-23  
> **Status**: ✅ Implemented

---

## Overview

Implemented structured logging across the trading bot using `structlog` for better log analysis, debugging, and monitoring. This replaces the standard Python logging with a more powerful, context-rich logging system.

## Benefits

✅ **Structured Data**: Logs are key-value pairs, easy to parse and analyze  
✅ **Colored Console Output**: Beautiful, readable logs in the terminal  
✅ **JSON File Logs**: Machine-readable logs for analysis tools  
✅ **Contextual Information**: Automatic inclusion of filename, line number, function name  
✅ **Better Debugging**: Rich context makes debugging much easier  
✅ **Log Aggregation Ready**: JSON format works with ELK, Splunk, Loki, etc.

---

## Implementation Details

### Files Modified

1. **`Core_Modules/logger.py`** (NEW)

   - Centralized logging configuration
   - Colored console output
   - JSON file output
   - Automatic context addition

2. **`Core_Modules/trader.py`**

   - Replaced standard logging with structured logging
   - Added contextual information to log calls
   - Enhanced error logging with exc_info

3. **`Application/main.py`**

   - Updated to use structured logging
   - Logs to both console and file

4. **`Configuration/requirements.txt`**

   - Added `structlog>=25.0.0`
   - Added `colorama>=0.4.6`

5. **`test_logging.py`** (NEW)
   - Comprehensive test script
   - Demonstrates all logging features

---

## Usage

### Basic Setup

```python
from Core_Modules.logger import setup_logging, get_logger

# Setup logging (call once at application start)
setup_logging(log_level="INFO", log_file="logs/app.log")

# Get logger instance
logger = get_logger(__name__)
```

### Logging Examples

#### 1. Basic Info Logging

```python
logger.info("application_started", version="1.0.0")
```

**Output (Console)**:

```
2025-11-23T17:43:19.971016Z [info] application_started [__main__] version=1.0.0
```

**Output (File - JSON)**:

```json
{
  "version": "1.0.0",
  "event": "application_started",
  "level": "info",
  "timestamp": "2025-11-23T17:43:19.971016Z",
  "logger": "__main__",
  "func_name": "<module>",
  "lineno": 20,
  "filename": "test_logging.py"
}
```

#### 2. Order Placement Logging

```python
logger.info(
    "order_placed",
    order_id="ORD123456",
    symbol="INFY",
    exchange="NSE",
    quantity=10,
    price=1500.00,
    order_type="MARKET"
)
```

#### 3. Error Logging with Exception

```python
try:
    result = risky_operation()
except Exception as e:
    logger.error(
        "operation_failed",
        operation="risky_operation",
        error=str(e),
        exc_info=True  # Include stack trace
    )
```

#### 4. Warning with Context

```python
logger.warning(
    "api_rate_limit_approaching",
    current_calls=95,
    max_calls=100,
    time_window="1min"
)
```

#### 5. Debug Logging

```python
logger.debug(
    "position_calculated",
    symbol="TCS",
    entry_price=3500.00,
    stop_loss=3450.00,
    position_size=20
)
```

---

## Log Levels

| Level        | Usage                           | Example                                  |
| ------------ | ------------------------------- | ---------------------------------------- |
| **DEBUG**    | Detailed diagnostic information | Position calculations, API responses     |
| **INFO**     | General informational messages  | Order placed, data fetched               |
| **WARNING**  | Warning messages                | Rate limit approaching, unusual activity |
| **ERROR**    | Error messages                  | Order failed, API error                  |
| **CRITICAL** | Critical errors                 | System failure, data corruption          |

---

## Configuration Options

### Log Level

```python
setup_logging(log_level="DEBUG")  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Log File

```python
# Log to file (JSON format)
setup_logging(log_file="logs/trading.log")

# Console only (no file)
setup_logging()
```

### Combined

```python
setup_logging(
    log_level="INFO",
    log_file="logs/trading.log"
)
```

---

## Automatic Context

Every log entry automatically includes:

- **timestamp**: ISO 8601 format
- **level**: Log level (info, warning, error, etc.)
- **logger**: Logger name (usually module name)
- **filename**: Source file name
- **lineno**: Line number
- **func_name**: Function name
- **event**: Event name (first argument to log call)

---

## Best Practices

### 1. Use Descriptive Event Names

```python
# Good
logger.info("order_placed", order_id="123", symbol="INFY")

# Bad
logger.info("Order placed")
```

### 2. Include Relevant Context

```python
# Good
logger.error(
    "order_placement_failed",
    symbol="INFY",
    quantity=10,
    error=str(e),
    exc_info=True
)

# Bad
logger.error(f"Failed: {e}")
```

### 3. Use Appropriate Log Levels

```python
logger.debug("...")   # Diagnostic info
logger.info("...")    # Normal operations
logger.warning("...") # Warnings
logger.error("...")   # Errors
```

### 4. Consistent Naming Convention

```python
# Use snake_case for event names
logger.info("trade_executed", ...)
logger.info("position_updated", ...)
logger.info("market_data_fetched", ...)
```

### 5. Include exc_info for Exceptions

```python
try:
    ...
except Exception as e:
    logger.error(
        "operation_failed",
        error=str(e),
        exc_info=True  # Include full stack trace
    )
```

---

## Log Analysis

### View JSON Logs

```bash
# Pretty print JSON logs
cat logs/trading.log | python -m json.tool

# View specific fields
cat logs/trading.log | jq '.event, .level, .timestamp'

# Filter by log level
cat logs/trading.log | jq 'select(.level == "error")'

# Filter by event
cat logs/trading.log | jq 'select(.event == "order_placed")'
```

### Search Logs

```bash
# Search for specific symbol
grep "INFY" logs/trading.log | jq '.'

# Search for errors
grep '"level": "error"' logs/trading.log | jq '.'

# Count events
cat logs/trading.log | jq -r '.event' | sort | uniq -c
```

---

## Testing

Run the test script to see structured logging in action:

```bash
python3.9 test_logging.py
```

This demonstrates:

- Basic logging
- Structured data
- Warnings
- Error logging with exceptions
- Debug logging
- Multiple context fields

---

## Migration Guide

### Before (Standard Logging)

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Order placed: {order_id}")
logger.error(f"Failed to place order: {e}")
```

### After (Structured Logging)

```python
from Core_Modules.logger import get_logger

logger = get_logger(__name__)

logger.info("order_placed", order_id=order_id, symbol=symbol)
logger.error("order_placement_failed", error=str(e), exc_info=True)
```

---

## Integration with Monitoring Tools

### ELK Stack (Elasticsearch, Logstash, Kibana)

```bash
# Logstash can directly ingest JSON logs
input {
  file {
    path => "/path/to/logs/trading.log"
    codec => "json"
  }
}
```

### Grafana Loki

```yaml
# Promtail config
- job_name: trading-bot
  static_configs:
    - targets:
        - localhost
      labels:
        job: trading-bot
        __path__: /path/to/logs/trading.log
  pipeline_stages:
    - json:
        expressions:
          level: level
          event: event
```

### Splunk

```bash
# Splunk can auto-detect JSON format
[monitor:///path/to/logs/trading.log]
sourcetype = _json
```

---

## Performance Considerations

- ✅ **Minimal Overhead**: structlog is highly optimized
- ✅ **Async Logging**: Can be configured for async if needed
- ✅ **Log Rotation**: Use `logging.handlers.RotatingFileHandler` for large logs
- ✅ **Conditional Logging**: Debug logs only evaluated if level is enabled

---

## Future Enhancements

### Planned Improvements

1. **Log Rotation**

   ```python
   from logging.handlers import RotatingFileHandler
   # Rotate logs at 10MB, keep 5 backups
   ```

2. **Async Logging**

   ```python
   # For high-throughput scenarios
   from structlog.threadlocal import wrap_dict
   ```

3. **Metrics Integration**

   ```python
   # Log metrics for Prometheus
   logger.info("trade_executed", pnl=150.00, metrics=True)
   ```

4. **Alert Integration**
   ```python
   # Trigger alerts on critical errors
   logger.critical("system_failure", alert=True)
   ```

---

## Troubleshooting

### Issue: Logs not appearing in file

**Solution**: Check file path and permissions

```python
import os
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
```

### Issue: Colors not showing in terminal

**Solution**: Ensure terminal supports ANSI colors

```bash
# Check if terminal is TTY
python -c "import sys; print(sys.stderr.isatty())"
```

### Issue: JSON parsing errors

**Solution**: Each line is a separate JSON object

```bash
# Parse line by line
while read line; do echo "$line" | jq '.'; done < logs/trading.log
```

---

## Examples from Codebase

### trader.py - Order Placement

```python
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
```

### trader.py - Position Fetch

```python
logger.info(
    "positions_fetched",
    day_positions=day_count,
    net_positions=net_count,
    total_positions=day_count + net_count
)
```

### trader.py - Error Handling

```python
logger.error(
    "order_placement_failed",
    symbol=symbol,
    exchange=exchange,
    transaction_type=transaction_type,
    quantity=quantity,
    error=str(e),
    exc_info=True
)
```

---

## Summary

Structured logging provides:

- ✅ Better debugging with rich context
- ✅ Easy log analysis with JSON format
- ✅ Beautiful console output
- ✅ Ready for production monitoring tools
- ✅ Consistent logging across the application

This is a foundational improvement that will make development, debugging, and production monitoring significantly easier.

---

**Next Steps**:

1. Update remaining modules to use structured logging
2. Add log rotation for production
3. Integrate with monitoring dashboard
4. Add custom log processors for metrics

---

**References**:

- structlog Documentation: https://www.structlog.org/
- Python Logging: https://docs.python.org/3/library/logging.html
- JSON Logging Best Practices: https://www.structlog.org/en/stable/standard-library.html
