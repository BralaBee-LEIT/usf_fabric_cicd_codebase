"""
Unit tests for circuit breaker
"""

import os
import time
import pytest
from unittest.mock import patch, MagicMock

from ops.scripts.utilities.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
    get_circuit_breaker,
    get_all_circuit_breakers,
    reset_all_circuit_breakers,
)


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment before each test"""
    # Clear all circuit breaker env vars
    env_vars = [
        "FEATURE_USE_CIRCUIT_BREAKER",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


def test_circuit_breaker_disabled_by_default(clean_env):
    """Test that circuit breaker is disabled by default"""
    circuit_breaker = CircuitBreaker(name="test")

    call_count = 0

    @circuit_breaker.protect
    def failing_function():
        nonlocal call_count
        call_count += 1
        raise Exception("Always fails")

    # Should allow all calls through even when failing
    for _ in range(10):
        with pytest.raises(Exception, match="Always fails"):
            failing_function()

    # All calls went through (no circuit breaker protection)
    assert call_count == 10


def test_circuit_breaker_enabled_with_feature_flag(clean_env):
    """Test that circuit breaker works when feature flag is enabled"""
    os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"

    config = CircuitBreakerConfig(failure_threshold=3, timeout_seconds=1)
    circuit_breaker = CircuitBreaker(name="test", config=config)

    call_count = 0

    @circuit_breaker.protect
    def failing_function():
        nonlocal call_count
        call_count += 1
        raise Exception("Service error")

    # First 3 failures should go through
    for _ in range(3):
        with pytest.raises(Exception, match="Service error"):
            failing_function()

    assert circuit_breaker.state == CircuitState.OPEN
    assert call_count == 3

    # Next call should be rejected immediately by circuit breaker
    with pytest.raises(CircuitBreakerOpenError, match="Circuit breaker.*is OPEN"):
        failing_function()

    # Call count should not increase (circuit breaker blocked it)
    assert call_count == 3


def test_circuit_breaker_transitions_to_half_open(clean_env):
    """Test circuit breaker transitions from OPEN to HALF_OPEN after timeout"""
    os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"

    config = CircuitBreakerConfig(
        failure_threshold=2, timeout_seconds=0.5, success_threshold=2
    )
    circuit_breaker = CircuitBreaker(name="test", config=config)

    call_count = 0

    @circuit_breaker.protect
    def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            raise Exception("Initial failures")
        return "success"

    # Trigger circuit to open
    for _ in range(2):
        with pytest.raises(Exception, match="Initial failures"):
            flaky_function()

    assert circuit_breaker.state == CircuitState.OPEN

    # Wait for timeout
    time.sleep(0.6)

    # Next call should transition to HALF_OPEN and succeed
    result = flaky_function()
    assert result == "success"
    assert circuit_breaker.state == CircuitState.HALF_OPEN


def test_circuit_breaker_closes_after_success_threshold(clean_env):
    """Test circuit breaker closes after enough successes in HALF_OPEN"""
    os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"

    config = CircuitBreakerConfig(
        failure_threshold=2, timeout_seconds=0.5, success_threshold=3
    )
    circuit_breaker = CircuitBreaker(name="test", config=config)

    call_count = 0

    @circuit_breaker.protect
    def recovering_function():
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            raise Exception("Initial failures")
        return "success"

    # Open the circuit
    for _ in range(2):
        with pytest.raises(Exception):
            recovering_function()

    assert circuit_breaker.state == CircuitState.OPEN

    # Wait for timeout
    time.sleep(0.6)

    # Make 3 successful calls (success threshold)
    for _ in range(3):
        result = recovering_function()
        assert result == "success"

    # Circuit should be closed now
    assert circuit_breaker.state == CircuitState.CLOSED


def test_circuit_breaker_reopens_on_failure_in_half_open(clean_env):
    """Test circuit breaker reopens if call fails in HALF_OPEN state"""
    os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"

    config = CircuitBreakerConfig(
        failure_threshold=2, timeout_seconds=0.5, success_threshold=2
    )
    circuit_breaker = CircuitBreaker(name="test", config=config)

    call_count = 0

    @circuit_breaker.protect
    def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count != 3:  # Fail except on 3rd call
            raise Exception("Service error")
        return "success"

    # Open the circuit (2 failures)
    for _ in range(2):
        with pytest.raises(Exception):
            flaky_function()

    assert circuit_breaker.state == CircuitState.OPEN

    # Wait for timeout
    time.sleep(0.6)

    # 3rd call will transition to HALF_OPEN and succeed
    result = flaky_function()
    assert result == "success"
    assert circuit_breaker.state == CircuitState.HALF_OPEN

    # 4th call fails in HALF_OPEN - should reopen circuit
    with pytest.raises(Exception):
        flaky_function()

    assert circuit_breaker.state == CircuitState.OPEN


def test_circuit_breaker_half_open_max_calls(clean_env):
    """Test circuit breaker limits concurrent calls in HALF_OPEN state"""
    os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"

    config = CircuitBreakerConfig(
        failure_threshold=2,
        timeout_seconds=0.5,
        success_threshold=2,
        half_open_max_calls=2,
    )
    circuit_breaker = CircuitBreaker(name="test", config=config)

    @circuit_breaker.protect
    def failing_function():
        raise Exception("Fail")

    # Open the circuit
    for _ in range(2):
        with pytest.raises(Exception):
            failing_function()

    assert circuit_breaker.state == CircuitState.OPEN

    # Wait for timeout
    time.sleep(0.6)

    # Manually set state to HALF_OPEN and half_open_calls
    circuit_breaker._state = CircuitState.HALF_OPEN
    circuit_breaker._half_open_calls = 2  # At max capacity

    # Next call should be rejected (max calls reached)
    with pytest.raises(CircuitBreakerOpenError, match="at capacity"):
        failing_function()


def test_circuit_breaker_reset(clean_env):
    """Test manual reset of circuit breaker"""
    os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"

    config = CircuitBreakerConfig(failure_threshold=2)
    circuit_breaker = CircuitBreaker(name="test", config=config)

    @circuit_breaker.protect
    def failing_function():
        raise Exception("Fail")

    # Open the circuit
    for _ in range(2):
        with pytest.raises(Exception):
            failing_function()

    assert circuit_breaker.state == CircuitState.OPEN

    # Reset
    circuit_breaker.reset()

    assert circuit_breaker.state == CircuitState.CLOSED
    stats = circuit_breaker.get_stats()
    assert stats["failure_count"] == 0
    assert stats["success_count"] == 0


def test_circuit_breaker_get_stats(clean_env):
    """Test circuit breaker statistics"""
    os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"

    config = CircuitBreakerConfig(failure_threshold=5, timeout_seconds=60)
    circuit_breaker = CircuitBreaker(name="test_stats", config=config)

    stats = circuit_breaker.get_stats()

    assert stats["name"] == "test_stats"
    assert stats["state"] == "closed"
    assert stats["failure_count"] == 0
    assert stats["config"]["failure_threshold"] == 5
    assert stats["config"]["timeout_seconds"] == 60


def test_get_circuit_breaker_singleton(clean_env):
    """Test get_circuit_breaker returns same instance"""
    cb1 = get_circuit_breaker("test_singleton")
    cb2 = get_circuit_breaker("test_singleton")

    assert cb1 is cb2


def test_get_all_circuit_breakers(clean_env):
    """Test getting all circuit breaker statistics"""
    cb1 = get_circuit_breaker("cb1")
    cb2 = get_circuit_breaker("cb2")

    all_stats = get_all_circuit_breakers()

    assert "cb1" in all_stats
    assert "cb2" in all_stats
    assert all_stats["cb1"]["name"] == "cb1"
    assert all_stats["cb2"]["name"] == "cb2"


def test_reset_all_circuit_breakers(clean_env):
    """Test resetting all circuit breakers"""
    os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"

    config = CircuitBreakerConfig(failure_threshold=1)

    # Use unique names to avoid conflicts with other tests
    cb1 = get_circuit_breaker("reset_test_cb1", config)
    cb2 = get_circuit_breaker("reset_test_cb2", config)

    @cb1.protect
    def fail1():
        raise Exception("Fail")

    @cb2.protect
    def fail2():
        raise Exception("Fail")

    # Open both circuits
    with pytest.raises(Exception):
        fail1()
    with pytest.raises(Exception):
        fail2()

    assert cb1.state == CircuitState.OPEN
    assert cb2.state == CircuitState.OPEN

    # Reset all
    reset_all_circuit_breakers()

    assert cb1.state == CircuitState.CLOSED
    assert cb2.state == CircuitState.CLOSED


def test_circuit_breaker_preserves_function_metadata(clean_env):
    """Test that decorator preserves function metadata"""
    circuit_breaker = CircuitBreaker(name="test")

    @circuit_breaker.protect
    def documented_function():
        """This function has documentation"""
        return "result"

    assert documented_function.__name__ == "documented_function"
    assert "documentation" in documented_function.__doc__


def test_circuit_breaker_with_function_arguments(clean_env):
    """Test circuit breaker preserves function arguments"""
    os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"

    circuit_breaker = CircuitBreaker(name="test")

    @circuit_breaker.protect
    def add_numbers(a: int, b: int, multiply: bool = False) -> int:
        if multiply:
            return a * b
        return a + b

    result1 = add_numbers(2, 3)
    assert result1 == 5

    result2 = add_numbers(2, 3, multiply=True)
    assert result2 == 6

    result3 = add_numbers(a=10, b=5)
    assert result3 == 15
