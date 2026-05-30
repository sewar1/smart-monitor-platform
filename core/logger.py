# ==========================================
# IMPORTS
# ==========================================

import os
import logging

from logging.handlers import RotatingFileHandler

# ==========================================
# CREATE LOG DIRECTORY
# ==========================================

LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)

# ==========================================
# LOG FORMAT
# ==========================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

FORMATTER = logging.Formatter(LOG_FORMAT)

# ==========================================
# MAIN SYSTEM LOGGER
# ==========================================

system_logger = logging.getLogger("system")

system_logger.setLevel(logging.INFO)

# Prevent duplicate logs
system_logger.propagate = False

# ==========================================
# SYSTEM LOG FILE HANDLER
# ==========================================

system_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "system.log"),
    maxBytes=5 * 1024 * 1024,   # 5 MB
    backupCount=3
)

system_handler.setFormatter(FORMATTER)

system_logger.addHandler(system_handler)

# ==========================================
# ALERT LOGGER
# ==========================================

alert_logger = logging.getLogger("alerts")

alert_logger.setLevel(logging.WARNING)

alert_logger.propagate = False

# ==========================================
# ALERT LOG FILE HANDLER
# ==========================================

alert_handler = RotatingFileHandler(
    filename=os.path.join(LOG_DIR, "alerts.log"),
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)

alert_handler.setFormatter(FORMATTER)

alert_logger.addHandler(alert_handler)

# ==========================================
# CONSOLE LOGGER
# ==========================================

console_handler = logging.StreamHandler()

console_handler.setFormatter(FORMATTER)

system_logger.addHandler(console_handler)

alert_logger.addHandler(console_handler)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def log_info(message):
    """
    Logs informational system events.
    """
    system_logger.info(message)


def log_warning(message):
    """
    Logs warning-level system events.
    """
    system_logger.warning(message)


def log_error(message):
    """
    Logs error-level system events.
    """
    system_logger.error(message)


def log_alert(message):
    """
    Logs monitoring alerts separately.
    """
    alert_logger.warning(message)