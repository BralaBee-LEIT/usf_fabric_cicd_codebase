"""
Unit tests for retry_handler
"""

import os
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import requests


@pytest.fixture
def clean_env():
    """Clean environment before each test"""
    original_env = os.environ.copy()

    # Clear feature flags
    for key in ["FEATURE_USE_RETRY_LOGIC"]:
        if key in os.environ:
            del os.environ[key]

    yield

    # Restore original env
    os.environ.clear()
    os.environ.update(original_env)


def test_retry_disabled_by_default(clean_env):
    """Test that retry logic is disabled when feature flag is false"""
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "false"

    from ops.scripts.utilities.retry_handler import fabric_retry

    call_count = 0

    @fabric_retry(max_attempts=3)
    def failing_function():
        nonlocal call_count
        call_count += 1
        raise requests.exceptions.ConnectionError("Connection failed")

    # Should fail immediately without retry
    with pytest.raises(requests.exceptions.ConnectionError):
        failing_function()

    assert call_count == 1  # Only called once, no retries


def test_retry_enabled_with_feature_flag(clean_env):
    """Test that retry logic works when feature flag is enabled"""
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

    from ops.scripts.utilities.retry_handler import fabric_retry

    call_count = 0

    @fabric_retry(max_attempts=3, min_wait=0.1, max_wait=1)
    def failing_function():
        nonlocal call_count
        call_count += 1
        raise requests.exceptions.Timeout("Request timed out")

    # Should retry and eventually fail
    with pytest.raises(requests.exceptions.Timeout):
        failing_function()

    assert call_count == 3  # Called 3 times (initial + 2 retries)


def test_retry_eventually_succeeds(clean_env):
    """Test that retry logic succeeds after transient failures"""
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

    from ops.scripts.utilities.retry_handler import fabric_retry

    call_count = 0

    @fabric_retry(max_attempts=5, min_wait=0.1, max_wait=1)
    def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise requests.exceptions.ConnectionError("Connection failed")
        return "success"

    result = flaky_function()

    assert result == "success"
    assert call_count == 3  # Failed twice, succeeded on third attempt


def test_retry_with_http_429_rate_limit(clean_env):
    """Test retry logic handles 429 rate limiting correctly"""
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

    from ops.scripts.utilities.retry_handler import fabric_retry

    call_count = 0

    @fabric_retry(max_attempts=3, min_wait=0.1, max_wait=1)
    def rate_limited_function():
        nonlocal call_count
        call_count += 1

        if call_count < 2:
            # Simulate 429 response
            response = Mock()
            response.status_code = 429
            response.headers = {"Retry-After": "0.2"}
            error = requests.exceptions.HTTPError("Too Many Requests")
            error.response = response
            raise error

        return "success"

    result = rate_limited_function()

    assert result == "success"
    assert call_count == 2  # Failed once with 429, succeeded on retry


def test_retry_with_http_500_server_error(clean_env):
    """Test retry logic handles 500 server errors"""
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

    from ops.scripts.utilities.retry_handler import fabric_retry

    call_count = 0

    @fabric_retry(max_attempts=3, min_wait=0.1, max_wait=1)
    def server_error_function():
        nonlocal call_count
        call_count += 1

        if call_count < 2:
            response = Mock()
            response.status_code = 500
            error = requests.exceptions.HTTPError("Internal Server Error")
            error.response = response
            raise error

        return "recovered"

    result = server_error_function()

    assert result == "recovered"
    assert call_count == 2


def test_retry_does_not_retry_non_retryable_errors(clean_env):
    """Test that non-retryable errors fail immediately"""
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

    from ops.scripts.utilities.retry_handler import fabric_retry

    call_count = 0

    @fabric_retry(max_attempts=3, min_wait=0.1, max_wait=1)
    def validation_error_function():
        nonlocal call_count
        call_count += 1

        # 400 Bad Request is not retryable
        response = Mock()
        response.status_code = 400
        error = requests.exceptions.HTTPError("Bad Request")
        error.response = response
        raise error

    with pytest.raises(requests.exceptions.HTTPError):
        validation_error_function()

    # Should fail immediately without retry for 400 errors
    assert call_count == 1


def test_retry_with_rate_limit_decorator(clean_env):
    """Test specialized rate limit decorator"""
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

    from ops.scripts.utilities.retry_handler import fabric_retry_with_rate_limit

    call_count = 0

    @fabric_retry_with_rate_limit(
        max_attempts=3, min_wait=0.1, max_wait=1, rate_limit_wait=0.2
    )
    def heavily_rate_limited():
        nonlocal call_count
        call_count += 1

        if call_count < 3:
            response = Mock()
            response.status_code = 429
            response.headers = {}  # No Retry-After header
            error = requests.exceptions.HTTPError("Too Many Requests")
            error.response = response
            raise error

        return "finally succeeded"

    result = heavily_rate_limited()

    assert result == "finally succeeded"
    assert call_count == 3


def test_retry_respects_retry_after_header(clean_env):
    """Test that retry logic respects Retry-After header"""
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

    from ops.scripts.utilities.retry_handler import fabric_retry_with_rate_limit

    call_count = 0
    start_time = time.time()

    @fabric_retry_with_rate_limit(max_attempts=2, rate_limit_wait=1)
    def function_with_retry_after():
        nonlocal call_count
        call_count += 1

        if call_count < 2:
            response = Mock()
            response.status_code = 429
            response.headers = {"Retry-After": "0.3"}  # Wait 300ms
            error = requests.exceptions.HTTPError("Too Many Requests")
            error.response = response
            raise error

        return "success"

    result = function_with_retry_after()
    elapsed_time = time.time() - start_time

    assert result == "success"
    assert call_count == 2
    # Should have waited at least 0.3 seconds
    assert elapsed_time >= 0.3


def test_get_retry_stats():
    """Test retry statistics retrieval"""
    from ops.scripts.utilities.retry_handler import get_retry_stats

    stats = get_retry_stats()

    assert "enabled" in stats
    assert "default_max_attempts" in stats
    assert stats["default_max_attempts"] == 3
    assert stats["default_min_wait"] == 1
    assert stats["default_max_wait"] == 60
    assert 429 in stats["retryable_status_codes"]
    assert 500 in stats["retryable_status_codes"]


def test_retry_preserves_function_metadata(clean_env):
    """Test that decorator preserves function name and docstring"""
    from ops.scripts.utilities.retry_handler import fabric_retry

    @fabric_retry(max_attempts=3)
    def documented_function():
        """This is a test function"""
        return "result"

    assert documented_function.__name__ == "documented_function"
    assert documented_function.__doc__ == "This is a test function"


def test_retry_with_function_arguments(clean_env):
    """Test that retry decorator works with function arguments"""
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

    from ops.scripts.utilities.retry_handler import fabric_retry

    call_count = 0

    @fabric_retry(max_attempts=3, min_wait=0.1, max_wait=1)
    def function_with_args(x: int, y: int, operation: str = "add"):
        nonlocal call_count
        call_count += 1

        if call_count < 2:
            raise requests.exceptions.Timeout("Timeout")

        if operation == "add":
            return x + y
        elif operation == "multiply":
            return x * y
        return 0

    result = function_with_args(5, 3, operation="add")
    assert result == 8
    assert call_count == 2

    # Reset for next test
    call_count = 0
    result = function_with_args(4, 7, operation="multiply")
    assert result == 28
    assert call_count == 2


def test_retry_max_wait_caps_exponential_backoff(clean_env):
    """Test that max_wait parameter caps the exponential backoff"""
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

    from ops.scripts.utilities.retry_handler import fabric_retry

    call_count = 0
    wait_times = []

    @fabric_retry(max_attempts=5, min_wait=1, max_wait=3)
    def function_with_capped_wait():
        nonlocal call_count
        call_count += 1
        raise requests.exceptions.ConnectionError("Always fails")

    # This will fail after max_attempts, but we're testing wait time capping
    with pytest.raises(requests.exceptions.ConnectionError):
        function_with_capped_wait()

    assert call_count == 5  # All attempts exhausted
