import logging
from logging.handlers import RotatingFileHandler
import os
import time
from threading import Lock

class Logger:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        """Singleton class"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(Logger, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._delete_old_logs()
        self.log_formatter = logging.Formatter('%(message)s')
        # A backup of max. 10+1 files of max. 10 MB
        self.log_handler = RotatingFileHandler("webserver.log", maxBytes=10*1024*1024, backupCount=10)
        self.log_handler.setFormatter(self.log_formatter)
        self.log_handler.setLevel(logging.INFO)
        self.logger = logging.getLogger("webserver")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.log_handler)

        timestamp = self.format_time()
        self.logger.info(f"{timestamp} - INFO - Server started")



    def _delete_old_logs(self):
        for file in os.listdir():
            if file.startswith("webserver.log"):
                os.remove(file)

    def format_time(self):
        return time.strftime("%Y-%m-%d %H:%M:%S GMT", time.gmtime())

    def log_message(self, message: str):
        with self._lock:
            timestamp = self.format_time()
            self.logger.info(f"{timestamp} {message}")

# Exemplu de utilizare
if __name__ == "__main__":
    logger = Logger()
