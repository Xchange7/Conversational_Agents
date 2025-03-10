"""
Logger class using loguru to log messages to a file.
Implemented as a Singleton to ensure only one instance exists.
"""
import os
from loguru import logger


class Logger:
    _instance = None
    
    def __new__(cls, log_file_path="logs/conversation.log"):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.log_file_path = log_file_path
            cls._instance.setup_logger()
        return cls._instance
    
    def __init__(self, log_file_path="logs/conversation.log"):
        # The initialization is done in __new__, this prevents re-initialization
        # when the instance already exists
        if hasattr(self, 'initialized') and self.log_file_path != log_file_path:
            # Log a warning if someone tries to create a logger with a different path
            logger.warning(f"Logger already initialized with {self.log_file_path}, ignoring new path {log_file_path}")
        self.log_file_path = log_file_path
        self.initialized = True

    def setup_logger(self):
        # Ensure the log directory exists
        log_dir = os.path.dirname(self.log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger.add(self.log_file_path, rotation="500 MB", compression="zip")

    def log(self, message):
        # Use opt(depth=1) to show the correct caller location
        logger.opt(depth=1).info(message)

    def log_error(self, message):
        # Use opt(depth=1) to show the correct caller location
        logger.opt(depth=1).error(message)

    def log_warning(self, message):
        # Use opt(depth=1) to show the correct caller location
        logger.opt(depth=1).warning(message)

