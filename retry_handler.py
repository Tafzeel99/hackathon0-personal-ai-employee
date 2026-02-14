# Gold Tier – Hackathon 0 – Personal AI Employee
# Generated following spec.constitution.md
"""Shared retry utility with exponential backoff for transient API errors."""
import time
from log_utils import log_event

# HTTP status codes considered transient (safe to retry)
TRANSIENT_CODES = {429, 500, 502, 503, 504}

# Default backoff schedule: 1s, 2s, 4s (doubles each time, capped at max_delay)
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1
DEFAULT_MAX_DELAY = 60


class RetryExhausted(Exception):
    """Raised when all retry attempts have been exhausted."""
    def __init__(self, last_error, attempts):
        self.last_error = last_error
        self.attempts = attempts
        super().__init__(f"Exhausted {attempts} retries. Last error: {last_error}")


def is_transient(exc):
    """Check if an exception represents a transient/retryable error."""
    msg = str(exc).lower()
    # Check for HTTP status codes in exception message
    for code in TRANSIENT_CODES:
        if str(code) in str(exc):
            return True
    # Check for common transient error patterns
    transient_patterns = ["timeout", "connection", "temporary", "unavailable",
                          "rate limit", "too many requests", "server error"]
    return any(p in msg for p in transient_patterns)


def retry_call(func, args=None, kwargs=None, source="retry_handler",
               task_ref=None, max_retries=DEFAULT_MAX_RETRIES,
               base_delay=DEFAULT_BASE_DELAY, max_delay=DEFAULT_MAX_DELAY):
    """Call func with retry on transient errors using exponential backoff.

    Args:
        func: Callable to execute.
        args: Positional arguments for func.
        kwargs: Keyword arguments for func.
        source: Log source identifier.
        task_ref: Optional task reference for logging.
        max_retries: Maximum number of retry attempts (default 3).
        base_delay: Initial delay in seconds (default 1).
        max_delay: Maximum delay cap in seconds (default 60).

    Returns:
        Result of func(*args, **kwargs) on success.

    Raises:
        RetryExhausted: If all retries fail with transient errors.
        Exception: If a non-transient error occurs (raised immediately).
    """
    args = args or ()
    kwargs = kwargs or {}
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            if not is_transient(e) or attempt == max_retries:
                if attempt == max_retries and is_transient(e):
                    log_event("retry_exhausted", source, "failure", task_ref,
                              {"retry_count": attempt, "error": str(e)[:200]})
                    raise RetryExhausted(e, attempt)
                raise
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            log_event("retry_attempt", source, "failure", task_ref,
                      {"retry_count": attempt, "delay_s": delay,
                       "error": str(e)[:200]})
            time.sleep(delay)

    raise RetryExhausted(last_error, max_retries)
