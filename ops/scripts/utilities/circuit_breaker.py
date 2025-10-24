"""
Circuit Breaker pattern for Fabric API calls
Prevents cascading failures by tracking error rates
"""

import logging
import time
from enum import Enum
from functools import wraps
from typing import Callable, Optional
from threading import Lock
from datetime import datetime, timedelta

from .feature_flags import _flags as FeatureFlags

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation - requests pass through
    OPEN = "open"  # Too many failures - reject requests immediately
    HALF_OPEN = "half_open"  # Testing if service recovered - allow limited requests


class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: int = 60,
        half_open_max_calls: int = 3,
    ):
        """
        Args:
            failure_threshold: Number of failures before opening circuit
            success_threshold: Number of successes needed to close circuit from half-open
            timeout_seconds: Seconds to wait before transitioning to half-open
            half_open_max_calls: Maximum calls allowed in half-open state
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_max_calls = half_open_max_calls


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures

    States:
        CLOSED: Normal operation, all requests pass through
        OPEN: Too many failures detected, reject requests immediately
        HALF_OPEN: Testing recovery, allow limited requests

    Example:
        circuit_breaker = CircuitBreaker(name="fabric_api")

        @circuit_breaker.protect
        def call_fabric_api():
            response = requests.get("https://api.fabric.microsoft.com/...")
            return response.json()
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls = 0
        self._lock = Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state (thread-safe)"""
        with self._lock:
            return self._state

    def protect(self, func: Callable) -> Callable:
        """
        Decorator to protect a function with circuit breaker

        Usage:
            @circuit_breaker.protect
            def risky_operation():
                return call_external_service()
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if circuit breaker is enabled
            if not FeatureFlags.USE_CIRCUIT_BREAKER:
                # Feature disabled - call function directly
                return func(*args, **kwargs)

            # Check circuit state before executing
            self._check_and_update_state()

            if self.state == CircuitState.OPEN:
                logger.warning(
                    f"Circuit breaker '{self.name}' is OPEN - rejecting request"
                )
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Service is temporarily unavailable. "
                    f"Will retry after {self.config.timeout_seconds} seconds."
                )

            if self.state == CircuitState.HALF_OPEN:
                # In half-open state, limit concurrent calls
                with self._lock:
                    if self._half_open_calls >= self.config.half_open_max_calls:
                        logger.warning(
                            f"Circuit breaker '{self.name}' in HALF_OPEN - "
                            f"max calls reached ({self.config.half_open_max_calls})"
                        )
                        raise CircuitBreakerOpenError(
                            f"Circuit breaker '{self.name}' is HALF_OPEN and at capacity"
                        )
                    self._half_open_calls += 1

            # Execute the function
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise
            finally:
                # Reset half-open call counter if we were in half-open
                if self.state == CircuitState.HALF_OPEN:
                    with self._lock:
                        self._half_open_calls -= 1

        return wrapper

    def _check_and_update_state(self):
        """Check if state should transition based on timeout"""
        with self._lock:
            if self._state == CircuitState.OPEN and self._last_failure_time:
                elapsed = (datetime.now() - self._last_failure_time).total_seconds()
                if elapsed >= self.config.timeout_seconds:
                    logger.info(
                        f"Circuit breaker '{self.name}' transitioning from OPEN to HALF_OPEN "
                        f"after {elapsed:.1f}s timeout"
                    )
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    self._success_count = 0

    def _on_success(self):
        """Handle successful call"""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                logger.debug(
                    f"Circuit breaker '{self.name}' HALF_OPEN success "
                    f"({self._success_count}/{self.config.success_threshold})"
                )

                if self._success_count >= self.config.success_threshold:
                    logger.info(
                        f"Circuit breaker '{self.name}' transitioning to CLOSED "
                        f"after {self._success_count} successes"
                    )
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    self._last_failure_time = None
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success in closed state
                if self._failure_count > 0:
                    logger.debug(
                        f"Circuit breaker '{self.name}' success - "
                        f"resetting failure count from {self._failure_count}"
                    )
                    self._failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.now()

            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open immediately opens circuit
                logger.warning(
                    f"Circuit breaker '{self.name}' failure in HALF_OPEN - "
                    f"transitioning to OPEN"
                )
                self._state = CircuitState.OPEN
                self._success_count = 0
            elif self._state == CircuitState.CLOSED:
                logger.warning(
                    f"Circuit breaker '{self.name}' failure "
                    f"({self._failure_count}/{self.config.failure_threshold})"
                )

                if self._failure_count >= self.config.failure_threshold:
                    logger.error(
                        f"Circuit breaker '{self.name}' threshold reached - "
                        f"transitioning to OPEN"
                    )
                    self._state = CircuitState.OPEN
                    self._success_count = 0

    def reset(self):
        """Manually reset circuit breaker to closed state"""
        with self._lock:
            logger.info(f"Circuit breaker '{self.name}' manually reset to CLOSED")
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._half_open_calls = 0

    def get_stats(self) -> dict:
        """Get circuit breaker statistics"""
        with self._lock:
            stats = {
                "name": self.name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "half_open_calls": self._half_open_calls,
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "success_threshold": self.config.success_threshold,
                    "timeout_seconds": self.config.timeout_seconds,
                    "half_open_max_calls": self.config.half_open_max_calls,
                },
            }

            if self._last_failure_time:
                elapsed = (datetime.now() - self._last_failure_time).total_seconds()
                stats["seconds_since_last_failure"] = round(elapsed, 2)

                if self._state == CircuitState.OPEN:
                    remaining = self.config.timeout_seconds - elapsed
                    stats["seconds_until_half_open"] = max(0, round(remaining, 2))

            return stats


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejects requests"""

    pass


# Global circuit breakers for Fabric API endpoints
_circuit_breakers = {}
_cb_lock = Lock()


def get_circuit_breaker(
    name: str, config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """
    Get or create a circuit breaker by name (singleton pattern)

    Args:
        name: Unique identifier for the circuit breaker
        config: Optional configuration (only used when creating new breaker)

    Returns:
        CircuitBreaker instance
    """
    with _cb_lock:
        if name not in _circuit_breakers:
            _circuit_breakers[name] = CircuitBreaker(name, config)
        return _circuit_breakers[name]


def get_all_circuit_breakers() -> dict:
    """Get statistics for all circuit breakers"""
    with _cb_lock:
        return {name: cb.get_stats() for name, cb in _circuit_breakers.items()}


def reset_all_circuit_breakers():
    """Reset all circuit breakers to closed state"""
    with _cb_lock:
        for cb in _circuit_breakers.values():
            cb.reset()
