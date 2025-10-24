"""
Retry logic with exponential backoff for Fabric API calls
Handles transient failures, rate limiting, and network issues
"""

import logging
import time
from functools import wraps
from typing import Callable, Optional, Tuple, Type
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
)
import requests

from .feature_flags import _flags as FeatureFlags

logger = logging.getLogger(__name__)


# Exceptions that should trigger retry (excluding HTTPError - handled separately)
RETRYABLE_EXCEPTIONS = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
)


def is_retryable_http_error(exception: Exception) -> bool:
    """
    Check if HTTP error should trigger a retry

    Retryable status codes:
    - 408: Request Timeout
    - 429: Too Many Requests (rate limiting)
    - 500: Internal Server Error
    - 502: Bad Gateway
    - 503: Service Unavailable
    - 504: Gateway Timeout
    """
    if isinstance(exception, requests.exceptions.HTTPError):
        if hasattr(exception, "response") and exception.response is not None:
            return exception.response.status_code in [408, 429, 500, 502, 503, 504]
    return False


def retry_if_retryable_http_error(exception: Exception) -> bool:
    """Retry condition for tenacity: returns True if exception should be retried"""
    return is_retryable_http_error(exception)


def fabric_retry(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 60,
    exponential_base: int = 2,
    logger_name: Optional[str] = None,
) -> Callable:
    """
    Decorator for retrying Fabric API calls with exponential backoff

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        min_wait: Minimum wait time in seconds between retries (default: 1)
        max_wait: Maximum wait time in seconds between retries (default: 60)
        exponential_base: Base for exponential backoff calculation (default: 2)
        logger_name: Optional logger name for custom logging

    Example:
        @fabric_retry(max_attempts=5, min_wait=2, max_wait=120)
        def create_workspace(self, name: str) -> dict:
            response = self._make_request("POST", "workspaces", json={"name": name})
            return response.json()

    Retry behavior:
        - Attempt 1: Immediate
        - Attempt 2: Wait 1s (2^0 * 1s)
        - Attempt 3: Wait 2s (2^1 * 1s)
        - Attempt 4: Wait 4s (2^2 * 1s)
        - Attempt 5: Wait 8s (2^3 * 1s)
        - Max wait capped at max_wait seconds
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if retry logic is enabled
            if not FeatureFlags.USE_RETRY_LOGIC:
                # Feature disabled - call function directly without retry
                return func(*args, **kwargs)

            # Use custom logger if provided, otherwise use function's module logger
            retry_logger = logging.getLogger(logger_name) if logger_name else logger

            # Define retry strategy
            from tenacity import retry_if_exception

            retry_decorator = retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(
                    multiplier=min_wait,
                    min=min_wait,
                    max=max_wait,
                    exp_base=exponential_base,
                ),
                retry=(
                    retry_if_exception_type(RETRYABLE_EXCEPTIONS)
                    | retry_if_exception(retry_if_retryable_http_error)
                ),
                before_sleep=before_sleep_log(retry_logger, logging.WARNING),
                after=after_log(retry_logger, logging.INFO),
                reraise=True,
            )

            # Apply retry logic
            retryable_func = retry_decorator(func)
            return retryable_func(*args, **kwargs)

        return wrapper

    return decorator


def fabric_retry_with_rate_limit(
    max_attempts: int = 5,
    min_wait: int = 2,
    max_wait: int = 120,
    rate_limit_wait: int = 60,
) -> Callable:
    """
    Specialized retry decorator for API calls with aggressive rate limiting

    This decorator is optimized for endpoints that frequently return 429 (Too Many Requests).
    It uses longer wait times and more attempts than the standard retry decorator.

    Args:
        max_attempts: Maximum number of retry attempts (default: 5)
        min_wait: Minimum wait time in seconds (default: 2)
        max_wait: Maximum wait time in seconds (default: 120)
        rate_limit_wait: Fixed wait time for 429 errors (default: 60)

    Example:
        @fabric_retry_with_rate_limit(max_attempts=10, rate_limit_wait=90)
        def list_all_workspaces(self) -> List[dict]:
            # This endpoint is heavily rate-limited
            response = self._make_request("GET", "workspaces")
            return response.json()
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not FeatureFlags.USE_RETRY_LOGIC:
                return func(*args, **kwargs)

            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    attempt += 1

                    # Check for rate limiting (429)
                    if hasattr(e, "response") and e.response is not None:
                        if e.response.status_code == 429:
                            if attempt < max_attempts:
                                # Check for Retry-After header
                                retry_after = e.response.headers.get("Retry-After")
                                if retry_after:
                                    try:
                                        wait_time = int(retry_after)
                                    except ValueError:
                                        wait_time = rate_limit_wait
                                else:
                                    wait_time = rate_limit_wait

                                logger.warning(
                                    f"Rate limited (429). Waiting {wait_time}s before retry {attempt}/{max_attempts}"
                                )
                                time.sleep(wait_time)
                                continue

                    # For other retryable errors, use exponential backoff
                    if is_retryable_http_error(e) and attempt < max_attempts:
                        wait_time = min(min_wait * (2 ** (attempt - 1)), max_wait)
                        logger.warning(
                            f"Retryable error {e.response.status_code}. "
                            f"Waiting {wait_time}s before retry {attempt}/{max_attempts}"
                        )
                        time.sleep(wait_time)
                        continue

                    # Non-retryable error or max attempts reached
                    raise

                except RETRYABLE_EXCEPTIONS as e:
                    attempt += 1
                    if attempt < max_attempts:
                        wait_time = min(min_wait * (2 ** (attempt - 1)), max_wait)
                        logger.warning(
                            f"Connection error: {type(e).__name__}. "
                            f"Waiting {wait_time}s before retry {attempt}/{max_attempts}"
                        )
                        time.sleep(wait_time)
                        continue
                    raise

            # Should not reach here, but just in case
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_retry_stats() -> dict:
    """
    Get retry statistics for monitoring and debugging

    Returns:
        dict: Retry statistics including enabled status, default config
    """
    return {
        "enabled": FeatureFlags.USE_RETRY_LOGIC,
        "default_max_attempts": 3,
        "default_min_wait": 1,
        "default_max_wait": 60,
        "rate_limit_max_attempts": 5,
        "rate_limit_wait": 60,
        "retryable_status_codes": [408, 429, 500, 502, 503, 504],
    }
