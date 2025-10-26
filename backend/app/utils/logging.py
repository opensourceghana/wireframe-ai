"""
Logging configuration and utilities
"""

import logging
import sys
from ..core.config import settings


def setup_logging():
    """Configure application logging"""
    
    # Create formatter
    formatter = logging.Formatter(settings.log_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from external libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    if not settings.debug:
        logging.getLogger("diffusers").setLevel(logging.WARNING)
        logging.getLogger("transformers").setLevel(logging.WARNING)
    
    logging.info(f"Logging configured: level={settings.log_level}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
