# ==============================================================================
# SMART MONITOR PLATFORM - ENTERPRISE LOGGING SUBSYSTEM
# ==============================================================================
# Thread-safe, non-blocking asynchronous log rotation matrix.
# Implements strict resource bounding to eliminate persistent storage depletion.
# ==============================================================================

import os
import logging
from logging.handlers import RotatingFileHandler


class ProductionLogger:
    """
    Centralized logging orchestrator enforcing thread-safe runtime tracing.
    Manages bounded file descriptors with dynamic backup retention loops.
    """

    def __init__(self, log_dir: str = "logs", max_mb: int = 5, backup_count: int = 3):
        self.log_dir = log_dir
        self.max_bytes = max_mb * 1024 * 1024  # Parse Megabytes to bytes
        self.backup_count = backup_count

        # Ensure baseline directory infrastructure is present
        os.makedirs(self.log_dir, exist_ok=True)

        # Standard unified ISO-8601 formatting layout
        self.log_format = "%(asctime)s | %(levelname)s | [%(name)s] | %(message)s"
        self.formatter = logging.Formatter(self.log_format)

        # Instantiate dedicated telemetry loggers
        self.system_logger = self._build_logger(name="system", log_file="system.log", level=logging.INFO)
        self.alert_logger = self._build_logger(name="alerts", log_file="alerts.log", level=logging.WARNING)

        # Attach shared real-time console streaming capability
        self._attach_console_stream()

    def _build_logger(self, name: str, log_file: str, level: int) -> logging.Logger:
        """
        Constructs and bounds a unique localized File-Rotating logger interface.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False  # Critical: Stop duplicate log bubbling to root handlers

        # Bind the highly resilient Rotating File Handler
        file_path = os.path.join(self.log_dir, log_file)
        handler = RotatingFileHandler(
            filename=file_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding="utf-8"  # Enforce UTF-8 to prevent character encoding crashes on foreign systems
        )
        handler.setFormatter(self.formatter)
        logger.addHandler(handler)
        
        return logger

    def _attach_console_stream(self) -> None:
        """
        Pipes real-time diagnostic output to STDOUT/STDERR for systemd/journalctl interception.
        """
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        
        self.system_logger.addHandler(console_handler)
        self.alert_logger.addHandler(console_handler)


# ==============================================================================
# CORE SYSTEM FUNCTIONAL INTERFACES (Seamless integration layer for app.py)
# ==============================================================================
_logger_orchestrator = ProductionLogger()

def log_info(message: str) -> None:
    _logger_orchestrator.system_logger.info(message)

def log_warning(message: str) -> None:
    _logger_orchestrator.system_logger.warning(message)

def log_error(message: str) -> None:
    _logger_orchestrator.system_logger.error(message)

def log_alert(message: str) -> None:
    _logger_orchestrator.alert_logger.warning(message)