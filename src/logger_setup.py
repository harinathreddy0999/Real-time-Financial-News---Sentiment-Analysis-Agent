import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from src.config_loader import get_config

# Load log level from config
config = get_config()
log_level_str = config.get("log_level", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Define log format
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Console Handler --- #
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)

# --- File Handler --- #
# Create logs directory if it doesn't exist
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(project_root, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, 'financial_agent.log')

# Use RotatingFileHandler for log rotation
# Max 5MB per file, keep 3 backup files
file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=5*1024*1024, # 5 MB
    backupCount=3,
    encoding='utf-8'
)
file_handler.setLevel(log_level)
file_handler.setFormatter(log_format)

# --- Configure Root Logger --- #
def setup_logging():
    """Sets up the root logger with console and file handlers."""
    log_level = logging.INFO
    
    root_logger = logging.getLogger()
    # Avoid adding handlers multiple times if this function is called again
    if not root_logger.handlers:
        root_logger.setLevel(log_level)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.info(f"Logging initialized. Level: {log_level_str}, File: {log_file_path}")
        
        # Add explicit initial log message to confirm visibility
        root_logger.info("====== Financial News Agent Started ======")
    else:
        root_logger.info("Logging already initialized.")

# --- Get Logger for Modules --- #
def get_logger(name):
    """Returns a logger instance for the given name."""
    return logging.getLogger(name)

# Example of how to use it in other modules:
# from src.logger_setup import get_logger
# logger = get_logger(__name__)
# logger.info("This is an info message from my_module.") 