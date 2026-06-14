import time
from functools import wraps
from flask import jsonify, request
from core.logger import log_info, log_error

class BruteForceMitigator:
    """
    In-memory security core designed to block brute-force vectors.
    Throttles and locks authentication attempts per username.
    """
    def __init__(self, max_attempts: int = 5, lockout_duration: int = 900):
        # max_attempts: Maximum 5 failed attempts
        # lockout_duration: The duration of the ban in seconds (900 seconds = 15 minutes)
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        
        # Dictionaries for tracking attempts and block time in memory
        self.failed_attempts = {}  # { 'username': count }
        self.lockout_timers = {}   # { 'username': unlock_timestamp }

    def is_locked_out(self, username: str) -> tuple[bool, int]:
        """Checks if a specific identity sequence is currently blocked."""
        if username in self.lockout_timers:
            remaining_time = int(self.lockout_timers[username] - time.time())
            if remaining_time > 0:
                return True, remaining_time
            else:
                # The lockdown period has ended; we are automatically resetting the counters
                self.reset_attempts(username)
        return False, 0

    def register_failure(self, username: str) -> int:
        """Increments the failure counter and triggers dynamic lockout if boundary is breached."""
        self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
        
        if self.failed_attempts[username] >= self.max_attempts:
            self.lockout_timers[username] = time.time() + self.lockout_duration
            log_error(f"[SECURITY ALERT] Identity [{username}] has been LOCKED OUT for 15 minutes due to excessive authentication failures.")
            return self.lockout_duration
            
        return 0

    def reset_attempts(self, username: str):
        """Clears all anomaly tracking data for a cleared/authenticated identity."""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        if username in self.lockout_timers:
            del self.lockout_timers[username]


# Export a ready-to-use version for direct connection to the Flask server.
security_gate = BruteForceMitigator(max_attempts=5, lockout_duration=900)


def limit_login_attempts(f):
    """
    Flask Decorator Middleware to wrap the login route.
    Intercepts and blocks brute-force requests before hitting database processing.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Securely extract the username from the incoming request (JSON payload)
        data = request.get_json() or {}
        username = data.get("username", "").strip()

        if not username:
            return f(*args, **kwargs)

# 1. Check if the user is currently blocked
        is_locked, time_left = security_gate.is_locked_out(username)
        if is_locked:
            minutes_left = (time_left // 60) + 1
            return jsonify({
                "error": f"Account temporarily locked. Too many failed attempts. Please retry after {minutes_left} minutes."
            }), 423  # HTTP Status Code 423: Locked

        return f(*args, **kwargs)
    return decorated_function