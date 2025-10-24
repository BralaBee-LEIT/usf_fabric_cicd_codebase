"""
Unit tests for health check module.

Tests health check endpoints, dependency monitoring, and status determination.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ops.scripts.utilities.health_check import (
    HealthCheck,
    HealthStatus,
    get_health_check,
    get_health_status,
    get_readiness_status,
    reset_health_check,
)


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment and singletons before each test."""
    # Clear environment variables
    env_vars = ["FEATURE_USE_HEALTH_CHECKS", "FEATURE_USE_AZURE_KEYVAULT"]
    original_values = {}

    for var in env_vars:
        if var in os.environ:
            original_values[var] = os.environ[var]
            del os.environ[var]

    # Reset singleton
    reset_health_check()

    yield

    # Restore environment
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
        if var in original_values:
            os.environ[var] = original_values[var]

    # Reset singleton again
    reset_health_check()


def test_health_checks_disabled_by_default():
    """Test that health checks are disabled by default."""
    health_check = HealthCheck()

    # Should return disabled response
    result = health_check.get_health_status()

    assert result["status"] == "healthy"
    assert "Health checks disabled" in result["message"]
    assert "duration_ms" in result


def test_health_checks_enabled_with_feature_flag():
    """Test that health checks can be enabled with feature flag."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    health_check = HealthCheck()
    result = health_check.get_health_status()

    assert result["status"] in ["healthy", "degraded", "unhealthy"]
    assert "checks" in result
    assert "application" in result["checks"]
    assert result["checks"]["application"]["status"] == "healthy"


def test_basic_health_status():
    """Test basic health status check."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    health_check = HealthCheck()
    result = health_check.get_health_status()

    # Should have basic structure
    assert "status" in result
    assert "timestamp" in result
    assert "checks" in result
    assert "duration_ms" in result

    # Should check application
    assert "application" in result["checks"]
    assert result["checks"]["application"]["status"] == "healthy"

    # Should check feature flags
    assert "feature_flags" in result["checks"]


def test_readiness_status_with_all_healthy():
    """Test readiness status when all dependencies are healthy."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    with (
        patch(
            "ops.scripts.utilities.health_check.get_secret_manager"
        ) as mock_secret_mgr,
        patch(
            "ops.scripts.utilities.health_check.get_all_circuit_breakers"
        ) as mock_breakers,
        patch("ops.scripts.utilities.health_check.DefaultAzureCredential") as mock_cred,
    ):

        # Mock secret manager
        mock_secret_mgr.return_value.get_cache_stats.return_value = {"cache_size": 5}

        # Mock circuit breakers (all closed)
        mock_breaker = Mock()
        mock_breaker.state.value = "CLOSED"
        mock_breakers.return_value = {
            "breaker1": mock_breaker,
            "breaker2": mock_breaker,
        }

        # Mock Azure credential
        mock_token = Mock()
        mock_token.token = "test-token"
        mock_cred.return_value.get_token.return_value = mock_token

        health_check = HealthCheck()
        result = health_check.get_readiness_status()

        assert result["status"] == "healthy"
        assert "azure_connectivity" in result["checks"]
        assert "secret_manager" in result["checks"]
        assert "circuit_breakers" in result["checks"]


def test_readiness_status_with_degraded_azure():
    """Test readiness status when Azure connectivity is degraded."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    with (
        patch("ops.scripts.utilities.health_check.AZURE_SDK_AVAILABLE", False),
        patch(
            "ops.scripts.utilities.health_check.get_secret_manager"
        ) as mock_secret_mgr,
        patch(
            "ops.scripts.utilities.health_check.get_all_circuit_breakers"
        ) as mock_breakers,
    ):

        # Mock secret manager
        mock_secret_mgr.return_value.get_cache_stats.return_value = {"cache_size": 5}

        # Mock circuit breakers
        mock_breaker = Mock()
        mock_breaker.state.value = "CLOSED"
        mock_breakers.return_value = {}

        health_check = HealthCheck()
        result = health_check.get_readiness_status()

        # Overall status should be degraded due to Azure SDK unavailable
        assert result["status"] == "degraded"
        assert result["checks"]["azure_connectivity"]["status"] == "degraded"


def test_readiness_status_with_unhealthy_secret_manager():
    """Test readiness status when secret manager is unhealthy."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    with (
        patch(
            "ops.scripts.utilities.health_check.get_secret_manager"
        ) as mock_secret_mgr,
        patch(
            "ops.scripts.utilities.health_check.get_all_circuit_breakers"
        ) as mock_breakers,
        patch("ops.scripts.utilities.health_check.DefaultAzureCredential") as mock_cred,
    ):

        # Mock secret manager error
        mock_secret_mgr.side_effect = Exception("Secret manager unavailable")

        # Mock circuit breakers
        mock_breaker = Mock()
        mock_breaker.state.value = "CLOSED"
        mock_breakers.return_value = {}

        # Mock Azure credential
        mock_token = Mock()
        mock_cred.return_value.get_token.return_value = mock_token

        health_check = HealthCheck()
        result = health_check.get_readiness_status()

        # Overall status should be unhealthy
        assert result["status"] == "unhealthy"
        assert result["checks"]["secret_manager"]["status"] == "unhealthy"
        assert (
            "Secret manager unavailable"
            in result["checks"]["secret_manager"]["message"]
        )


def test_readiness_status_with_open_circuit_breakers():
    """Test readiness status when circuit breakers are open."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    with (
        patch(
            "ops.scripts.utilities.health_check.get_secret_manager"
        ) as mock_secret_mgr,
        patch(
            "ops.scripts.utilities.health_check.get_all_circuit_breakers"
        ) as mock_breakers,
        patch("ops.scripts.utilities.health_check.DefaultAzureCredential") as mock_cred,
    ):

        # Mock secret manager
        mock_secret_mgr.return_value.get_cache_stats.return_value = {"cache_size": 5}

        # Mock circuit breakers (one open, one closed)
        mock_open_breaker = Mock()
        mock_open_breaker.state.value = "OPEN"
        mock_closed_breaker = Mock()
        mock_closed_breaker.state.value = "CLOSED"
        mock_breakers.return_value = {
            "breaker1": mock_open_breaker,
            "breaker2": mock_closed_breaker,
        }

        # Mock Azure credential
        mock_token = Mock()
        mock_cred.return_value.get_token.return_value = mock_token

        health_check = HealthCheck()
        result = health_check.get_readiness_status()

        # Overall status should be degraded due to open breaker
        assert result["status"] == "degraded"
        assert result["checks"]["circuit_breakers"]["status"] == "degraded"
        assert result["checks"]["circuit_breakers"]["open"] == 1
        assert result["checks"]["circuit_breakers"]["closed"] == 1


def test_readiness_status_with_half_open_circuit_breakers():
    """Test readiness status when circuit breakers are half-open."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    with (
        patch(
            "ops.scripts.utilities.health_check.get_secret_manager"
        ) as mock_secret_mgr,
        patch(
            "ops.scripts.utilities.health_check.get_all_circuit_breakers"
        ) as mock_breakers,
        patch("ops.scripts.utilities.health_check.DefaultAzureCredential") as mock_cred,
    ):

        # Mock secret manager
        mock_secret_mgr.return_value.get_cache_stats.return_value = {"cache_size": 5}

        # Mock circuit breakers (half-open)
        mock_half_open_breaker = Mock()
        mock_half_open_breaker.state.value = "HALF_OPEN"
        mock_breakers.return_value = {"breaker1": mock_half_open_breaker}

        # Mock Azure credential
        mock_token = Mock()
        mock_cred.return_value.get_token.return_value = mock_token

        health_check = HealthCheck()
        result = health_check.get_readiness_status()

        # Overall status should be degraded due to half-open breaker
        assert result["status"] == "degraded"
        assert result["checks"]["circuit_breakers"]["status"] == "degraded"
        assert result["checks"]["circuit_breakers"]["half_open"] == 1


def test_azure_connectivity_with_keyvault_disabled():
    """Test Azure connectivity check when Key Vault is disabled."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"
    os.environ["FEATURE_USE_AZURE_KEYVAULT"] = "false"

    health_check = HealthCheck()
    result = health_check._check_azure_connectivity()

    assert result["status"] == "healthy"
    assert "not in use" in result["message"]


def test_azure_connectivity_with_authentication_failure():
    """Test Azure connectivity check when authentication fails."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"
    os.environ["FEATURE_USE_AZURE_KEYVAULT"] = "true"

    with patch(
        "ops.scripts.utilities.health_check.DefaultAzureCredential"
    ) as mock_cred:
        mock_cred.return_value.get_token.side_effect = Exception("Auth failed")

        health_check = HealthCheck()
        result = health_check._check_azure_connectivity()

        assert result["status"] == "unhealthy"
        assert "Auth failed" in result["message"]


def test_get_health_check_singleton():
    """Test that get_health_check returns singleton instance."""
    instance1 = get_health_check()
    instance2 = get_health_check()

    assert instance1 is instance2


def test_get_health_status_convenience_function():
    """Test convenience function for getting health status."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    result = get_health_status()

    assert "status" in result
    assert "timestamp" in result


def test_get_readiness_status_convenience_function():
    """Test convenience function for getting readiness status."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    with (
        patch(
            "ops.scripts.utilities.health_check.get_secret_manager"
        ) as mock_secret_mgr,
        patch(
            "ops.scripts.utilities.health_check.get_all_circuit_breakers"
        ) as mock_breakers,
        patch("ops.scripts.utilities.health_check.DefaultAzureCredential") as mock_cred,
    ):

        mock_secret_mgr.return_value.get_cache_stats.return_value = {"cache_size": 5}
        mock_breakers.return_value = {}
        mock_token = Mock()
        mock_cred.return_value.get_token.return_value = mock_token

        result = get_readiness_status()

        assert "status" in result
        assert "checks" in result


def test_health_status_includes_duration():
    """Test that health status includes response duration."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    result = get_health_status()

    assert "duration_ms" in result
    assert result["duration_ms"] >= 0


def test_readiness_status_includes_duration():
    """Test that readiness status includes response duration."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    with (
        patch(
            "ops.scripts.utilities.health_check.get_secret_manager"
        ) as mock_secret_mgr,
        patch(
            "ops.scripts.utilities.health_check.get_all_circuit_breakers"
        ) as mock_breakers,
        patch("ops.scripts.utilities.health_check.DefaultAzureCredential") as mock_cred,
    ):

        mock_secret_mgr.return_value.get_cache_stats.return_value = {"cache_size": 5}
        mock_breakers.return_value = {}
        mock_token = Mock()
        mock_cred.return_value.get_token.return_value = mock_token

        result = get_readiness_status()

        assert "duration_ms" in result
        assert result["duration_ms"] >= 0


def test_circuit_breakers_check_with_no_breakers():
    """Test circuit breaker check when no breakers are registered."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    with patch(
        "ops.scripts.utilities.health_check.get_all_circuit_breakers"
    ) as mock_breakers:
        mock_breakers.return_value = {}

        health_check = HealthCheck()
        result = health_check._check_circuit_breakers()

        assert result["status"] == "healthy"
        assert "No circuit breakers" in result["message"]


def test_circuit_breakers_check_with_error():
    """Test circuit breaker check when an error occurs."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    with patch(
        "ops.scripts.utilities.health_check.get_all_circuit_breakers"
    ) as mock_breakers:
        mock_breakers.side_effect = Exception("Breaker check failed")

        health_check = HealthCheck()
        result = health_check._check_circuit_breakers()

        assert result["status"] == "unhealthy"
        assert "Breaker check failed" in result["message"]


def test_timestamp_format():
    """Test that timestamps are in ISO format."""
    os.environ["FEATURE_USE_HEALTH_CHECKS"] = "true"

    result = get_health_status()

    # Should be parseable as datetime
    timestamp = datetime.fromisoformat(result["timestamp"])
    assert isinstance(timestamp, datetime)
