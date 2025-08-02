# Advanced Logging System

A comprehensive logging solution using Loguru with Pydantic configuration management.

## Features

- 🗓️ **Daily File Rotation**: Automatic daily log file creation
- 🔄 **Smart File Rotation**: Size-based and time-based rotation
- 🎨 **Color-Coded Console Output**: Different colors for different log levels
- 🔍 **Error Tracing**: Detailed stack traces for errors and exceptions
- ⚙️ **Environment Configuration**: Configurable via environment variables
- 📁 **Multiple Log Files**: Main, error-specific, and daily log files
- 🏗️ **System Design Principles**: Singleton pattern, facade pattern, and SOLID principles
- 🔒 **Thread-Safe**: Safe for concurrent usage

## Quick Start

```python
from lib.logger import get_logger, setup_logger

# Setup logger (call once at application startup)
logger_manager = setup_logger()

# Get logger instance
logger = get_logger("my_module")

# Use logger
logger.info("Application started")
logger.error("Something went wrong")
logger.success("Operation completed successfully")
```

## Environment Configuration

Create a `.env` file in your project root with the following variables:

```bash
# Log Level Configuration
LOG_LEVEL=INFO                    # TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL

# File Logging Configuration  
ENABLE_FILE_LOGGING=true
LOG_DIRECTORY=logs

# File Rotation Configuration
LOG_ROTATION_TIME=00:00          # HH:MM format (24-hour)
LOG_RETENTION_DAYS=30
LOG_MAX_FILE_SIZE=100 MB

# Console Logging Configuration
ENABLE_CONSOLE_LOGGING=true
COLORIZE_CONSOLE=true

# Application Configuration
APP_NAME=multi-agents
ENVIRONMENT=development
```

## Usage Examples

### Basic Logging

```python
from lib.logger import get_logger

logger = get_logger("my_module")

logger.trace("Detailed trace information")
logger.debug("Debug information")
logger.info("General information")
logger.success("Success message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error message")
```

### Convenience Functions

```python
from lib.logger import info, error, debug, warning, success

info("This is an info message")
error("This is an error message")
debug("This is a debug message")
warning("This is a warning message")
success("This is a success message")
```

### Structured Logging

```python
from lib.logger import get_logger

logger = get_logger("api")

logger.info(
    "User action performed",
    user_id="12345",
    action="login",
    ip_address="192.168.1.1",
    endpoint="/api/auth/login"
)
```

### Exception Handling with Tracing

```python
from lib.logger import get_logger

logger = get_logger("error_handler")

try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    logger.exception("Full traceback of the error")
```

### Dynamic Log Level Changes

```python
from lib.logger import setup_logger, LogLevel

logger_manager = setup_logger()

# Change log level at runtime
logger_manager.set_log_level(LogLevel.DEBUG)
```

### Function Entry/Exit Logging

```python
from lib.logger import get_logger

logger = get_logger("function_tracer")

def my_function(param1, param2):
    logger.log_function_entry("my_function", param1=param1, param2=param2)
    
    # Your function logic here
    result = param1 + param2
    
    logger.log_function_exit("my_function", result=result)
    return result
```

## Log File Structure

The logger creates the following log files in the configured directory:

```
logs/
├── multi-agents.log              # Main application log (rotated daily)
├── multi-agents_errors.log       # Error-only log (rotated by size)
└── YYYY-MM-DD/
    └── multi-agents_YYYY-MM-DD.log  # Daily log files
```

## Log Levels and Colors

| Level    | Color   | Description                           |
|----------|---------|---------------------------------------|
| TRACE    | Cyan    | Detailed trace information            |
| DEBUG    | Blue    | Debug information                     |
| INFO     | Green   | General information                   |
| SUCCESS  | Green   | Success messages                      |
| WARNING  | Yellow  | Warning messages                      |
| ERROR    | Red     | Error messages                        |
| CRITICAL | Red     | Critical error messages               |

## Advanced Configuration

### Custom Log Format

```python
from lib.logger.logger import LoggerConfig

# Override default configuration
config = LoggerConfig(
    log_format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
    log_level="DEBUG",
    rotation_time="02:00",  # Rotate at 2 AM
    retention_days=60
)
```

### Environment-Specific Configurations

#### Development
```bash
LOG_LEVEL=DEBUG
COLORIZE_CONSOLE=true
ENABLE_CONSOLE_LOGGING=true
```

#### Production
```bash
LOG_LEVEL=INFO
COLORIZE_CONSOLE=false
LOG_RETENTION_DAYS=90
LOG_MAX_FILE_SIZE=500 MB
```

#### Testing
```bash
LOG_LEVEL=WARNING
ENABLE_FILE_LOGGING=false
ENABLE_CONSOLE_LOGGING=true
```

## System Design

The logging system follows several design patterns:

- **Singleton Pattern**: Ensures only one logger configuration exists
- **Facade Pattern**: Provides a simple interface to the complex loguru system
- **Factory Pattern**: `get_logger()` function creates appropriately configured loggers
- **Strategy Pattern**: Different logging strategies for console vs file output

## Thread Safety

The logger is thread-safe and can be used in multi-threaded applications:

```python
import threading
from lib.logger import get_logger

def worker_function(worker_id):
    logger = get_logger(f"worker_{worker_id}")
    logger.info(f"Worker {worker_id} started")
    # Your work here
    logger.info(f"Worker {worker_id} completed")

# Create multiple threads
threads = []
for i in range(5):
    thread = threading.Thread(target=worker_function, args=(i,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
```

## Performance Considerations

- **Enqueued Logging**: File logging is enqueued for better performance
- **Compression**: Old log files are compressed to save space
- **Lazy Initialization**: Logger is initialized only when first used
- **Efficient Rotation**: Rotation is handled efficiently by loguru

## Troubleshooting

### No log files created
- Check if `ENABLE_FILE_LOGGING=true`
- Verify the log directory has write permissions
- Check if the `LOG_DIRECTORY` path exists and is writable

### Console colors not showing
- Set `COLORIZE_CONSOLE=true`
- Ensure your terminal supports ANSI color codes

### Log level not filtering correctly
- Verify the `LOG_LEVEL` environment variable is set correctly
- Check that the level is one of: TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL

## Demo Script

Run the demo script to see all features in action:

```bash
cd lib/logger
python demo.py
```

This will demonstrate all logging features and create sample log files.

## Integration with LangGraph

For LangGraph applications, initialize the logger early in your application:

```python
# main.py
from lib.logger import setup_logger, get_logger

def main():
    # Setup logging first
    logger_manager = setup_logger()
    logger = get_logger("main")
    
    logger.info("LangGraph application starting")
    
    # Your LangGraph code here
    
if __name__ == "__main__":
    main()
```