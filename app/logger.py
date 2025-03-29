"""Module for logging server's activity"""

import logging
from logging.handlers import RotatingFileHandler
import os
import time
from threading import Lock
from app.job_type import JobType

class Logger:
    """
    This class is used to log server's activity
    by providing the 'log_message()' function
    which writes meaningful messages in .log files on the disk.
    """
    _lock = Lock()

    def __init__(self):
        self._delete_old_logs()
        self.log_formatter = logging.Formatter('%(message)s')
        # A backup of max. 10+1 files of max. 11 MB
        self.log_handler = RotatingFileHandler(
            "webserver.log",
            maxBytes=10*1024*1024, backupCount=10
        )
        self.log_handler.setFormatter(self.log_formatter)
        self.log_handler.setLevel(logging.INFO)
        self.logger = logging.getLogger("webserver")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.log_handler)


    def _delete_old_logs(self):
        """
        It resets the logging activity by
        deleting the previously created .log files
        """
        for file in os.listdir():
            if file.startswith("webserver.log"):
                os.remove(file)

    def format_time(self):
        """
        Formats the current time using GMT standard
        The returned string will look like '2025-03-28 14:03:04 GMT'
        """
        return time.strftime("%Y-%m-%d %H:%M:%S GMT", time.gmtime())

    def log_message(self, message: str):
        """
        Receives a message and writes in the .log file
        the current GMT timestamp and then the message
        """
        with self._lock:
            timestamp = self.format_time()
            self.logger.info("%s %s", timestamp, message)
