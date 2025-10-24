"""
Unit tests for Application Insights telemetry
"""

import os
import pytest
from unittest.mock import Mock, MagicMock, patch, call

from ops.scripts.utilities.telemetry import (
    TelemetryClient,
    TelemetryEventType,
    get_telemetry_client,
    track_deployment_event,
    track_performance,
    APPINSIGHTS_AVAILABLE,
)


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment before each test"""
    env_vars = ["FEATURE_USE_TELEMETRY", "APPINSIGHTS_INSTRUMENTATION_KEY"]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


def test_telemetry_disabled_by_default(clean_env):
    """Test that telemetry is disabled by default (feature flag off)"""
    client = TelemetryClient()

    assert client.enabled is False

    # Should not raise error, just log
    client.track_event("test_event")
    client.track_metric("test_metric", 42.0)


def test_telemetry_disabled_without_sdk(clean_env, monkeypatch):
    """Test telemetry disabled when SDK not available"""
    os.environ["FEATURE_USE_TELEMETRY"] = "true"
    os.environ["APPINSIGHTS_INSTRUMENTATION_KEY"] = "test-key"

    # Mock SDK as unavailable
    monkeypatch.setattr("ops.scripts.utilities.telemetry.APPINSIGHTS_AVAILABLE", False)

    client = TelemetryClient()

    assert client.enabled is False


def test_telemetry_disabled_without_instrumentation_key(clean_env):
    """Test telemetry disabled when instrumentation key not set"""
    os.environ["FEATURE_USE_TELEMETRY"] = "true"

    client = TelemetryClient()

    # Should be disabled without instrumentation key
    assert client.enabled is False


@pytest.mark.skipif(
    not APPINSIGHTS_AVAILABLE, reason="Application Insights SDK not installed"
)
@patch("ops.scripts.utilities.telemetry.AITelemetryClient")
@patch("ops.scripts.utilities.telemetry.enable_exception_tracking")
def test_telemetry_enabled_with_feature_flag(
    mock_enable_tracking, mock_ai_client, clean_env
):
    """Test telemetry enabled when feature flag and key are set"""
    os.environ["FEATURE_USE_TELEMETRY"] = "true"
    os.environ["APPINSIGHTS_INSTRUMENTATION_KEY"] = "test-key-12345"

    mock_client_instance = MagicMock()
    mock_ai_client.return_value = mock_client_instance

    from ops.scripts.utilities.telemetry import TelemetryClient

    client = TelemetryClient()

    assert client.enabled is True
    mock_ai_client.assert_called_once_with("test-key-12345")
    mock_enable_tracking.assert_called_once_with("test-key-12345")


@pytest.mark.skipif(
    not APPINSIGHTS_AVAILABLE, reason="Application Insights SDK not installed"
)
@patch("ops.scripts.utilities.telemetry.AITelemetryClient")
def test_track_event_with_properties(mock_ai_client, clean_env):
    """Test tracking events with properties"""
    os.environ["FEATURE_USE_TELEMETRY"] = "true"
    os.environ["APPINSIGHTS_INSTRUMENTATION_KEY"] = "test-key"

    mock_client_instance = MagicMock()
    mock_ai_client.return_value = mock_client_instance

    from ops.scripts.utilities.telemetry import TelemetryClient

    client = TelemetryClient()

    properties = {"workspace": "Analytics", "user": "admin"}
    measurements = {"duration": 45.2, "resource_count": 5}

    client.track_event("deployment_completed", properties, measurements)

    # Verify called with correct arguments
    mock_client_instance.track_event.assert_called_once()
    call_args = mock_client_instance.track_event.call_args
    # Check positional args
    assert call_args[0][0] == "deployment_completed"
    # Properties should include standard fields plus custom
    props = call_args[0][1]
    assert "workspace" in props
    assert "timestamp" in props
    assert call_args[0][2] == measurements

    mock_client_instance.flush.assert_called_once()


@pytest.mark.skipif(
    not APPINSIGHTS_AVAILABLE, reason="Application Insights SDK not installed"
)
@patch("ops.scripts.utilities.telemetry.AITelemetryClient")
def test_track_metric(mock_ai_client, clean_env):
    """Test tracking metrics"""
    os.environ["FEATURE_USE_TELEMETRY"] = "true"
    os.environ["APPINSIGHTS_INSTRUMENTATION_KEY"] = "test-key"

    mock_client_instance = MagicMock()
    mock_ai_client.return_value = mock_client_instance

    from ops.scripts.utilities.telemetry import TelemetryClient

    client = TelemetryClient()

    client.track_metric("deployment_duration", 45.2, {"status": "success"})

    mock_client_instance.track_metric.assert_called_once()
    call_args = mock_client_instance.track_metric.call_args
    assert call_args[0][0] == "deployment_duration"
    assert call_args[0][1] == 45.2
    # Check keyword args
    assert "status" in call_args[1]["properties"]
    assert "timestamp" in call_args[1]["properties"]

    mock_client_instance.flush.assert_called_once()


@pytest.mark.skipif(
    not APPINSIGHTS_AVAILABLE, reason="Application Insights SDK not installed"
)
@patch("ops.scripts.utilities.telemetry.AITelemetryClient")
def test_track_exception(mock_ai_client, clean_env):
    """Test tracking exceptions"""
    os.environ["FEATURE_USE_TELEMETRY"] = "true"
    os.environ["APPINSIGHTS_INSTRUMENTATION_KEY"] = "test-key"

    mock_client_instance = MagicMock()
    mock_ai_client.return_value = mock_client_instance

    from ops.scripts.utilities.telemetry import TelemetryClient

    client = TelemetryClient()

    try:
        raise ValueError("Test error")
    except ValueError as e:
        client.track_exception(e, {"operation": "test"})

    mock_client_instance.track_exception.assert_called_once()
    # Verify properties were passed
    call_args = mock_client_instance.track_exception.call_args
    assert "operation" in call_args[1]["properties"]

    mock_client_instance.flush.assert_called_once()


@pytest.mark.skipif(
    not APPINSIGHTS_AVAILABLE, reason="Application Insights SDK not installed"
)
@patch("ops.scripts.utilities.telemetry.AITelemetryClient")
def test_track_dependency(mock_ai_client, clean_env):
    """Test tracking dependency calls"""
    os.environ["FEATURE_USE_TELEMETRY"] = "true"
    os.environ["APPINSIGHTS_INSTRUMENTATION_KEY"] = "test-key"

    mock_client_instance = MagicMock()
    mock_ai_client.return_value = mock_client_instance

    from ops.scripts.utilities.telemetry import TelemetryClient

    client = TelemetryClient()

    client.track_dependency(
        name="Fabric API",
        dependency_type="HTTP",
        data="GET /workspaces",
        duration=0.5,
        success=True,
        properties={"endpoint": "/workspaces"},
    )

    mock_client_instance.track_dependency.assert_called_once()
    call_args = mock_client_instance.track_dependency.call_args
    # Check positional args
    assert call_args[0][0] == "Fabric API"
    assert call_args[0][1] == "GET /workspaces"
    assert call_args[0][2] == "HTTP"

    mock_client_instance.flush.assert_called_once()


@pytest.mark.skipif(
    not APPINSIGHTS_AVAILABLE, reason="Application Insights SDK not installed"
)
@patch("ops.scripts.utilities.telemetry.AITelemetryClient")
def test_track_operation_success(mock_ai_client, clean_env):
    """Test tracking successful operations"""
    os.environ["FEATURE_USE_TELEMETRY"] = "true"
    os.environ["APPINSIGHTS_INSTRUMENTATION_KEY"] = "test-key"

    mock_client_instance = MagicMock()
    mock_ai_client.return_value = mock_client_instance

    from ops.scripts.utilities.telemetry import TelemetryClient

    client = TelemetryClient()

    with client.track_operation("create_workspace"):
        # Simulate work
        pass

    # Should track dependency for operation
    mock_client_instance.track_dependency.assert_called_once()
    call_args = mock_client_instance.track_dependency.call_args

    # Check positional and keyword args
    # track_dependency(name, data, dependency_type, success=..., duration=..., properties=...)
    assert call_args[0][0] == "create_workspace"  # name
    assert call_args[1]["success"] is True


@pytest.mark.skipif(
    not APPINSIGHTS_AVAILABLE, reason="Application Insights SDK not installed"
)
@patch("ops.scripts.utilities.telemetry.AITelemetryClient")
def test_track_operation_failure(mock_ai_client, clean_env):
    """Test tracking failed operations"""
    os.environ["FEATURE_USE_TELEMETRY"] = "true"
    os.environ["APPINSIGHTS_INSTRUMENTATION_KEY"] = "test-key"

    mock_client_instance = MagicMock()
    mock_ai_client.return_value = mock_client_instance

    from ops.scripts.utilities.telemetry import TelemetryClient

    client = TelemetryClient()

    with pytest.raises(ValueError):
        with client.track_operation("failing_operation"):
            raise ValueError("Operation failed")

    # Should track both dependency (failed) and exception
    mock_client_instance.track_dependency.assert_called_once()
    mock_client_instance.track_exception.assert_called_once()

    call_args = mock_client_instance.track_dependency.call_args
    assert call_args[1]["success"] is False


def test_track_performance_decorator(clean_env):
    """Test track_performance decorator"""
    call_count = 0

    @track_performance("test_operation")
    def sample_function(x: int) -> int:
        nonlocal call_count
        call_count += 1
        return x * 2

    result = sample_function(5)

    assert result == 10
    assert call_count == 1


def test_track_performance_decorator_with_exception(clean_env):
    """Test track_performance decorator with exception"""

    @track_performance("failing_operation")
    def failing_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        failing_function()


def test_get_telemetry_client_singleton(clean_env):
    """Test telemetry client is singleton"""
    client1 = get_telemetry_client()
    client2 = get_telemetry_client()

    assert client1 is client2


def test_track_deployment_event(clean_env):
    """Test convenience function for deployment events"""
    # Should not raise error even when disabled
    track_deployment_event(
        TelemetryEventType.DEPLOYMENT_STARTED,
        properties={"workspace": "Analytics"},
        measurements={"resource_count": 5},
    )


def test_telemetry_fallback_to_logging(clean_env, caplog):
    """Test telemetry falls back to logging when disabled"""
    client = TelemetryClient()

    assert client.enabled is False

    with caplog.at_level("INFO"):
        client.track_event("test_event", {"key": "value"})
        client.track_metric("test_metric", 42.0)

    # Should have logged the events
    assert "[TELEMETRY]" in caplog.text
    assert "test_event" in caplog.text
    assert "test_metric" in caplog.text
