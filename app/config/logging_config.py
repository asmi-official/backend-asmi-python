import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Setup logging configuration for the application
    - Console handler: display in terminal
    - File handler: save to logs/app.log
    - Error handler: save errors to logs/error.log
    """
    # Create logs directory
    LOG_DIR = "logs"
    os.makedirs(LOG_DIR, exist_ok=True)

    # Log format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)

    # File handler for all logs (rotates when reaches 10MB, keeps 5 backup files)
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'app.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_format)

    # File handler for errors only
    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'error.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


def get_logger(name: str):
    """Get logger instance with specific name"""
    return logging.getLogger(name)
