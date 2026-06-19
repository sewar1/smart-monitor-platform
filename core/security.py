# ==============================================================================
# SMART MONITOR PLATFORM - BRUTE FORCE MITIGATION GATEWAY
# ==============================================================================
# In-memory security core designed to block brute-force vectors.
# Throttles and locks authentication attempts dynamically per identity footprint.
# ==============================================================================

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
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration
        
        # Dictionaries for tracking attempts and block time in memory
        self.failed_attempts = {}   # { 'username': count }
        self.lockout_timers = {}    # { 'username': unlock_timestamp }

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
    Automates failure registration and successful access resets via response inspection.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Securely extract the username from the incoming request (JSON payload)
        data = request.get_json() or {}
        username = data.get("username", "").strip()

        if not username:
            return f(*args, **kwargs)

        # 1. Active Security Gate Check: Evaluate if identity footprint is locked
        is_locked, time_left = security_gate.is_locked_out(username)
        if is_locked:
            minutes_left = (time_left // 60) + 1
            return jsonify({
                "error": f"Account temporarily locked. Too many failed attempts. Please retry after {minutes_left} minutes."
            }), 423  # HTTP Status Code 423: Locked

        # Execute the primary authentication route mapping handler
        response_tuple = f(*args, **kwargs)
        
        # Unpack Flask response to inspect performance results safely
        try:
            if isinstance(response_tuple, tuple):
                response_obj, status_code = response_tuple
            else:
                response_obj = response_tuple
                status_code = getattr(response_tuple, "status_code", 200)

            # 2. Reactive Security Tracking: Parse status signals for adaptive filtering
            if status_code == 200:
                # Authentication Success -> Purge failure thresholds immediately
                security_gate.reset_attempts(username)
            elif status_code == 401:
                # Unauthorized Signal -> Register failure trace vector
                security_gate.register_failure(username)
        except Exception as gate_fault:
            log_error(f"[SECURITY ENGINE EXCEPTION] Failed to evaluate auth telemetry metrics: {gate_fault}")

        return response_tuple
    return decorated_function