"""
Demo script showing how to use the advanced logging system

This demonstrates:
- Basic logging functionality
- Different log levels with colors
- Error tracing
- Environment configuration
- File rotation
"""

import time
from pathlib import Path

# Import the logging system
from src.libs.logger import (
    get_logger,
    setup_logger,
    LogLevel,
    info,
    debug,
    warning,
    error,
    critical,
    success,
    exception
)


def demonstrate_basic_logging():
    """Demonstrate basic logging functionality"""
    print("\n=== Basic Logging Demonstration ===")
    
    # Get a logger instance
    logger = get_logger("demo_module")
    
    # Test different log levels
    logger.trace("This is a trace message (lowest level)")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.success("This is a success message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")


def demonstrate_convenience_functions():
    """Demonstrate convenience functions"""
    print("\n=== Convenience Functions Demonstration ===")
    
    # Use convenience functions
    debug("Debug message using convenience function")
    info("Info message using convenience function")
    success("Success message using convenience function")
    warning("Warning message using convenience function")
    error("Error message using convenience function")
    critical("Critical message using convenience function")


def demonstrate_error_tracing():
    """Demonstrate error tracing and exception handling"""
    print("\n=== Error Tracing Demonstration ===")
    
    logger = get_logger("error_demo")
    
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"Division by zero error: {e}")
        logger.exception("Exception caught with full traceback")
    
    try:
        # Simulate another error
        data = {"key": "value"}
        missing_key = data["missing_key"]
    except KeyError as e:
        logger.error(f"Key error: {e}")
        exception("KeyError caught with traceback")


def demonstrate_structured_logging():
    """Demonstrate structured logging with extra data"""
    print("\n=== Structured Logging Demonstration ===")
    
    logger = get_logger("structured_demo")
    
    # Log with extra context data
    logger.info(
        "User action performed",
        user_id="12345",
        action="login",
        ip_address="192.168.1.1",
        timestamp=time.time()
    )
    
    logger.warning(
        "Rate limit exceeded",
        user_id="67890",
        endpoint="/api/data",
        rate_limit=100,
        current_requests=150
    )


def demonstrate_function_logging():
    """Demonstrate function entry/exit logging"""
    print("\n=== Function Logging Demonstration ===")
    
    logger = get_logger("function_demo")
    
    def sample_function(param1, param2):
        """Sample function with logging"""
        logger.trace(f"Entering function: sample_function with param1={param1}, param2={param2}")
        
        # Simulate some work
        time.sleep(0.1)
        result = param1 + param2
        
        logger.trace(f"Exiting function: sample_function with result={result}")
        return result
    
    # Call the function
    result = sample_function(10, 20)
    logger.info(f"Function result: {result}")


def demonstrate_log_level_changes():
    """Demonstrate dynamic log level changes"""
    print("\n=== Dynamic Log Level Demonstration ===")
    
    logger_manager = setup_logger()
    logger = get_logger("level_demo")
    
    logger.info("Current log level messages")
    logger.debug("This debug message might not show depending on level")
    
    # Change log level to DEBUG
    print("\nChanging log level to DEBUG...")
    logger_manager.set_log_level(LogLevel.DEBUG)
    
    logger.info("Log level changed to DEBUG")
    logger.debug("This debug message should now be visible")
    
    # Change log level back to INFO
    print("\nChanging log level back to INFO...")
    logger_manager.set_log_level(LogLevel.INFO)
    logger.debug("This debug message should be hidden again")
    logger.info("Log level changed back to INFO")


def demonstrate_file_logging():
    """Demonstrate file logging features"""
    print("\n=== File Logging Demonstration ===")
    
    logger = get_logger("file_demo")
    
    # Log messages that will go to files
    logger.info("This message will be saved to the daily log file")
    logger.error("This error will be saved to both main and error log files")
    
    # Check if log files exist
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.rglob("*.log"))
        if log_files:
            logger.success(f"Log files created: {[f.name for f in log_files]}")
        else:
            logger.warning("No log files found yet")
    else:
        logger.warning("Log directory not found")


def simulate_application_workflow():
    """Simulate a typical application workflow with logging"""
    print("\n=== Application Workflow Simulation ===")
    
    # Setup logger for application
    app_logger = get_logger("multi_agents_app")
    
    # Application startup
    app_logger.info("Multi-Agents application starting up")
    app_logger.debug("Loading configuration...")
    app_logger.success("Configuration loaded successfully")
    
    # Simulate some operations
    app_logger.info("Initializing agents...")
    
    for agent_name in ["appointment_agent", "prescription_agent"]:
        agent_logger = get_logger(f"agent.{agent_name}")
        agent_logger.info(f"Initializing {agent_name}")
        
        # Simulate some work
        time.sleep(0.1)
        
        # Simulate potential issues
        if agent_name == "prescription_agent":
            agent_logger.warning("External API response slow")
            agent_logger.info("Retrying with fallback endpoint")
        
        agent_logger.success(f"{agent_name} initialized successfully")
    
    app_logger.success("All agents initialized")
    app_logger.info("Application ready to serve requests")
    
    # Simulate request processing
    request_logger = get_logger("request_handler")
    request_logger.info("Processing user request", request_id="req_12345")
    request_logger.debug("Validating input parameters")
    request_logger.info("Request processed successfully", response_time="0.5s")


def main():
    """Main demo function"""
    print("🚀 Advanced Logging System Demo")
    print("=" * 50)
    
    # Setup the logging system
    setup_logger()
    
    # Run all demonstrations
    demonstrate_basic_logging()
    demonstrate_convenience_functions()
    demonstrate_error_tracing()
    demonstrate_structured_logging()
    demonstrate_function_logging()
    demonstrate_log_level_changes()
    demonstrate_file_logging()
    simulate_application_workflow()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed! Check the 'logs' directory for log files.")
    print("📁 Log files are organized by date and type.")
    print("🎨 Console output should show different colors for different log levels.")


if __name__ == "__main__":
    main()