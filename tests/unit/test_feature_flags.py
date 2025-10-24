"""
Unit tests for feature flags
"""

import os
import pytest


def test_feature_flags_default_disabled():
    """Test that all feature flags default to disabled"""
    # Clear any env vars that might be set
    for key in [
        "FEATURE_USE_KEY_VAULT",
        "FEATURE_USE_RETRY_LOGIC",
        "FEATURE_USE_CIRCUIT_BREAKER",
        "FEATURE_USE_ROLLBACK",
        "FEATURE_USE_TELEMETRY",
    ]:
        if key in os.environ:
            del os.environ[key]

    # Re-import to get fresh instance
    import importlib
    from ops.scripts.utilities import feature_flags

    importlib.reload(feature_flags)

    # Use singleton instance for property access
    flags = feature_flags._flags
    assert flags.USE_KEY_VAULT is False
    assert flags.USE_RETRY_LOGIC is False
    assert flags.USE_CIRCUIT_BREAKER is False
    assert flags.USE_ROLLBACK is False
    assert flags.USE_TELEMETRY is False


def test_feature_flags_can_be_enabled():
    """Test that feature flags can be enabled via environment variables"""
    # Set env vars
    os.environ["FEATURE_USE_KEY_VAULT"] = "true"
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"

    # Re-import to get fresh instance
    import importlib
    from ops.scripts.utilities import feature_flags

    importlib.reload(feature_flags)

    # Use singleton instance for property access
    flags = feature_flags._flags
    assert flags.USE_KEY_VAULT is True
    assert flags.USE_RETRY_LOGIC is True

    # Clean up
    del os.environ["FEATURE_USE_KEY_VAULT"]
    del os.environ["FEATURE_USE_RETRY_LOGIC"]


def test_feature_flags_case_insensitive():
    """Test that feature flag values are case-insensitive"""
    os.environ["FEATURE_USE_ROLLBACK"] = "TRUE"

    import importlib
    from ops.scripts.utilities import feature_flags

    importlib.reload(feature_flags)

    # Use singleton instance for property access
    flags = feature_flags._flags
    assert flags.USE_ROLLBACK is True

    # Test mixed case
    os.environ["FEATURE_USE_TELEMETRY"] = "True"
    importlib.reload(feature_flags)
    assert flags.USE_TELEMETRY is True

    # Clean up
    del os.environ["FEATURE_USE_ROLLBACK"]
    del os.environ["FEATURE_USE_TELEMETRY"]


def test_is_production_ready():
    """Test is_production_ready method"""
    # All features disabled
    for key in [
        "FEATURE_USE_KEY_VAULT",
        "FEATURE_USE_RETRY_LOGIC",
        "FEATURE_USE_ROLLBACK",
        "FEATURE_USE_TELEMETRY",
    ]:
        if key in os.environ:
            del os.environ[key]

    import importlib
    from ops.scripts.utilities import feature_flags

    importlib.reload(feature_flags)

    # Use singleton instance for method calls
    flags = feature_flags._flags
    assert flags.is_production_ready() is False

    # Enable all required features
    os.environ["FEATURE_USE_KEY_VAULT"] = "true"
    os.environ["FEATURE_USE_RETRY_LOGIC"] = "true"
    os.environ["FEATURE_USE_ROLLBACK"] = "true"
    os.environ["FEATURE_USE_TELEMETRY"] = "true"

    importlib.reload(feature_flags)
    flags = feature_flags._flags

    assert flags.is_production_ready() is True

    # Clean up
    for key in [
        "FEATURE_USE_KEY_VAULT",
        "FEATURE_USE_RETRY_LOGIC",
        "FEATURE_USE_ROLLBACK",
        "FEATURE_USE_TELEMETRY",
    ]:
        if key in os.environ:
            del os.environ[key]


def test_log_status(caplog):
    """Test log_status method"""
    from ops.scripts.utilities.feature_flags import _flags

    with caplog.at_level("INFO"):
        _flags.log_status()

    assert "Feature Flags Status:" in caplog.text
    assert "USE_KEY_VAULT:" in caplog.text
    assert "USE_RETRY_LOGIC:" in caplog.text
