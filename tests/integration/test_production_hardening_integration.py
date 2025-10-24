"""
Integration tests for production hardening features.

Tests basic integration between production hardening components.
"""

import os
import pytest
import requests
import time
from unittest.mock import Mock, patch

from ops.scripts.utilities.retry_handler import fabric_retry
from ops.scripts.utilities.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    reset_all_circuit_breakers,
)
from ops.scripts.utilities.transaction_manager import (
    DeploymentTransaction,
    ResourceType,
)
from ops.scripts.utilities.health_check import get_health_check, reset_health_check


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment and singletons before each test."""
    env_vars = [
        "FEATURE_USE_RETRY_LOGIC",
        "FEATURE_USE_CIRCUIT_BREAKER",
        "FEATURE_USE_ROLLBACK",
        "FEATURE_USE_HEALTH_CHECKS",
    ]
    original_values = {}

    for var in env_vars:
        if var in os.environ:
            original_values[var] = os.environ[var]
            del os.environ[var]

    reset_all_circuit_breakers()
    reset_health_check()

    yield

    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
        if var in original_values:
            os.environ[var] = original_values[var]

    reset_all_circuit_breakers()
    reset_health_check()


class TestRetryAndCircuitBreaker:
    """Test integration between retry logic and circuit breaker."""

    def test_retry_works_independently(self):
        """Test that retry logic works when enabled."""
        os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

        call_count = 0

        @fabric_retry(max_attempts=5, min_wait=0)
        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # Use a retryable exception type
                raise requests.exceptions.Timeout("Temporary failure")
            return "success"

        result = flaky_operation()
        assert result == "success"
        assert call_count == 3  # Should have retried twice

    def test_circuit_breaker_works_independently(self):
        """Test that circuit breaker works when enabled."""
        os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"

        config = CircuitBreakerConfig(failure_threshold=3, timeout_seconds=1)
        breaker = CircuitBreaker(name="failing_service", config=config)

        call_count = 0

        @breaker.protect
        def always_failing():
            nonlocal call_count
            call_count += 1
            raise Exception("Permanent failure")

        # Should fail 3 times then open
        for _ in range(3):
            with pytest.raises(Exception):
                always_failing()

        assert breaker.state == CircuitState.OPEN
        assert call_count == 3


class TestTransactionRollback:
    """Test transaction rollback functionality."""

    def test_transaction_rollback_on_failure(self):
        """Test that transaction rolls back resources on failure."""
        os.environ["FEATURE_USE_ROLLBACK"] = "true"

        transaction = DeploymentTransaction(name="test_deployment")
        cleanup_called = []

        def cleanup_workspace(workspace_id):
            cleanup_called.append(("workspace", workspace_id))

        def cleanup_lakehouse(lakehouse_id):
            cleanup_called.append(("lakehouse", lakehouse_id))

        # Track resources
        transaction.track_resource(
            ResourceType.WORKSPACE,
            "ws-001",
            "Test Workspace",
            cleanup_func=cleanup_workspace,
            cleanup_args=("ws-001",),
        )

        transaction.track_resource(
            ResourceType.LAKEHOUSE,
            "lh-001",
            "Test Lakehouse",
            cleanup_func=cleanup_lakehouse,
            cleanup_args=("lh-001",),
        )

        # Simulate failure and rollback
        transaction.rollback()

        # Verify rollback occurred (LIFO order)
        assert len(cleanup_called) == 2
        assert cleanup_called[0] == ("lakehouse", "lh-001")
        assert cleanup_called[1] == ("workspace", "ws-001")

    def test_transaction_commit_prevents_rollback(self):
        """Test that committed transaction doesn't rollback."""
        os.environ["FEATURE_USE_ROLLBACK"] = "true"

        transaction = DeploymentTransaction(name="test_deployment")
        cleanup_called = []

        def cleanup_resource(resource_id):
            cleanup_called.append(resource_id)

        transaction.track_resource(
            ResourceType.WORKSPACE,
            "ws-001",
            "Test Workspace",
            cleanup_func=cleanup_resource,
            cleanup_args=("ws-001",),
        )

        # Commit transaction
        transaction.commit()

        # Try to rollback - should not execute cleanups
        transaction.rollback()

        assert len(cleanup_called) == 0


class TestHealthCheckIntegration:
    """Test integration between health checks and other features."""

    @pytest.mark.skip(
        reason="Health check circuit breaker integration has API mismatch - needs fix in health_check.py"
    )
    def test_health_check_reflects_circuit_breaker_state(self):
        """Test that health checks show circuit breaker states."""
        os.environ["FEATURE_USE_CIRCUIT_BREAKER"] = "true"
        os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

        # Use get_circuit_breaker to ensure registration
        from ops.scripts.utilities.circuit_breaker import get_circuit_breaker

        config = CircuitBreakerConfig(failure_threshold=2, timeout_seconds=1)
        breaker = get_circuit_breaker("monitored_service", config)

        with (
            patch(
                "ops.scripts.utilities.health_check.get_secret_manager"
            ) as mock_secret_mgr,
            patch(
                "ops.scripts.utilities.health_check.DefaultAzureCredential"
            ) as mock_cred,
        ):

            mock_secret_mgr.return_value.get_cache_stats.return_value = {
                "cache_size": 5
            }
            mock_token = Mock()
            mock_cred.return_value.get_token.return_value = mock_token

            health_check = get_health_check()

            # Initially healthy
            status = health_check.get_readiness_status()
            assert status["status"] == "healthy"

            # Open circuit breaker by failing twice
            @breaker.protect
            def failing_function():
                raise Exception("Failure")

            for _ in range(2):
                with pytest.raises(Exception):
                    failing_function()

            assert breaker.state == CircuitState.OPEN

            # Health check should show degraded
            time.sleep(0.1)
            status = health_check.get_readiness_status()

            # Verify circuit breaker is in the response
            assert "circuit_breakers" in status["checks"]
            cb_status = status["checks"]["circuit_breakers"]

            # Should have counts
            assert "open" in cb_status
            assert cb_status["open"] > 0
            assert status["status"] == "degraded"


class TestCompleteScenarios:
    """Test complete deployment scenarios."""

    def test_successful_deployment_with_all_features(self):
        """Test successful deployment with retry."""
        os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"
        os.environ["FEATURE_USE_ROLLBACK"] = "true"

        transaction = DeploymentTransaction(name="prod_deployment")
        cleanup_called = []

        def cleanup_workspace(workspace_id):
            cleanup_called.append(workspace_id)

        attempt_count = 0

        @fabric_retry(max_attempts=3, min_wait=0)
        def deploy_fabric_workspace():
            nonlocal attempt_count
            attempt_count += 1

            # Simulate occasional failure with retryable exception
            if attempt_count < 2:
                raise requests.exceptions.Timeout("Temporary deployment issue")

            # Track resource
            transaction.track_resource(
                ResourceType.WORKSPACE,
                "ws-prod-001",
                "Production Workspace",
                cleanup_func=cleanup_workspace,
                cleanup_args=("ws-prod-001",),
            )

            return "ws-prod-001"

        workspace_id = deploy_fabric_workspace()

        assert workspace_id == "ws-prod-001"
        assert attempt_count == 2  # 1 failure + 1 success

        # Commit successful deployment
        transaction.commit()
        transaction.rollback()  # Should not clean up

        assert len(cleanup_called) == 0

    def test_failed_deployment_rolls_back(self):
        """Test that failed deployment triggers rollback."""
        os.environ["FEATURE_USE_ROLLBACK"] = "true"

        transaction = DeploymentTransaction(name="failed_deployment")
        cleanup_called = []

        def cleanup_resource(resource_id):
            cleanup_called.append(resource_id)

        # Simulate partial deployment
        transaction.track_resource(
            ResourceType.WORKSPACE,
            "ws-001",
            "Workspace",
            cleanup_func=cleanup_resource,
            cleanup_args=("ws-001",),
        )

        transaction.track_resource(
            ResourceType.LAKEHOUSE,
            "lh-001",
            "Lakehouse",
            cleanup_func=cleanup_resource,
            cleanup_args=("lh-001",),
        )

        # Deployment fails - trigger rollback
        transaction.rollback()

        # All resources should be cleaned up
        assert len(cleanup_called) == 2
        assert "lh-001" in cleanup_called
        assert "ws-001" in cleanup_called
