"""
Unit tests for SecretManager
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


@pytest.fixture
def clean_env():
    """Clean environment before each test"""
    # Save original env
    original_env = os.environ.copy()

    # Clear feature flags and secrets
    for key in [
        "FEATURE_USE_KEY_VAULT",
        "KEY_VAULT_URL",
        "TEST_SECRET",
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
    ]:
        if key in os.environ:
            del os.environ[key]

    yield

    # Restore original env
    os.environ.clear()
    os.environ.update(original_env)


def test_secret_manager_env_fallback(clean_env):
    """Test .env fallback when Key Vault disabled"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "false"
    os.environ["TEST_SECRET"] = "test-value-from-env"

    from ops.scripts.utilities.secret_manager import SecretManager

    manager = SecretManager()

    assert manager.use_keyvault is False
    assert manager.get_secret("TEST_SECRET") == "test-value-from-env"


def test_secret_manager_with_default(clean_env):
    """Test default value when secret not found"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "false"

    from ops.scripts.utilities.secret_manager import SecretManager

    manager = SecretManager()

    result = manager.get_secret("NONEXISTENT_SECRET", default="default-value")
    assert result == "default-value"


def test_secret_manager_env_name_formats(clean_env):
    """Test that SecretManager handles different name formats"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "false"
    os.environ["MY_SECRET_KEY"] = "value1"
    os.environ["my-secret-key"] = "value2"

    from ops.scripts.utilities.secret_manager import SecretManager

    manager = SecretManager()

    # Should handle underscores
    assert manager.get_secret("MY_SECRET_KEY") == "value1"

    # Should convert hyphens to underscores
    result = manager.get_secret("my-secret-key")
    assert result in ["value1", "value2"]  # Could match either format


def test_secret_manager_singleton():
    """Test that get_secret_manager returns singleton"""
    from ops.scripts.utilities.secret_manager import get_secret_manager

    manager1 = get_secret_manager()
    manager2 = get_secret_manager()

    assert manager1 is manager2


def test_secret_manager_cache_ttl(clean_env):
    """Test cache TTL configuration"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "false"
    os.environ["SECRET_CACHE_TTL"] = "1800"  # 30 minutes

    from ops.scripts.utilities.secret_manager import SecretManager

    manager = SecretManager()

    assert manager._cache_ttl_seconds == 1800


def test_secret_manager_refresh_cache(clean_env):
    """Test cache refresh"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "false"

    from ops.scripts.utilities.secret_manager import SecretManager

    manager = SecretManager()

    # Add something to cache manually
    manager._add_to_cache("test-key", "test-value")

    assert len(manager._cache) == 1

    # Refresh cache
    manager.refresh_cache()

    assert len(manager._cache) == 0


def test_secret_manager_get_cache_stats(clean_env):
    """Test get_cache_stats method"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "false"

    from ops.scripts.utilities.secret_manager import SecretManager

    manager = SecretManager()
    manager._add_to_cache("key1", "value1")
    manager._add_to_cache("key2", "value2")

    stats = manager.get_cache_stats()

    assert stats["cache_size"] == 2
    assert "key1" in stats["cached_keys"]
    assert "key2" in stats["cached_keys"]
    assert stats["use_keyvault"] is False


def test_secret_manager_set_secret_requires_keyvault(clean_env):
    """Test that set_secret requires Key Vault to be enabled"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "false"

    from ops.scripts.utilities.secret_manager import SecretManager

    manager = SecretManager()

    with pytest.raises(
        ValueError, match="Cannot set secrets when Key Vault is disabled"
    ):
        manager.set_secret("test-key", "test-value")


@pytest.mark.skip(
    reason="Azure SDK not installed - install via 'pip install -r requirements.txt'"
)
@patch("azure.keyvault.secrets.SecretClient")
@patch("azure.identity.ClientSecretCredential")
def test_secret_manager_keyvault_initialization(
    mock_credential, mock_secret_client, clean_env
):
    """Test Key Vault initialization with service principal"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "true"
    os.environ["KEY_VAULT_URL"] = "https://test-vault.vault.azure.net"
    os.environ["AZURE_TENANT_ID"] = "tenant-123"
    os.environ["AZURE_CLIENT_ID"] = "client-456"
    os.environ["AZURE_CLIENT_SECRET"] = "secret-789"

    # Mock the secret client
    mock_client_instance = MagicMock()
    mock_secret_client.return_value = mock_client_instance
    mock_client_instance.list_properties_of_secrets.return_value = iter([])

    # Need to import with mocks in place
    import sys

    if "ops.scripts.utilities.secret_manager" in sys.modules:
        del sys.modules["ops.scripts.utilities.secret_manager"]

    from ops.scripts.utilities.secret_manager import SecretManager

    manager = SecretManager()

    assert manager.use_keyvault is True
    assert manager.kv_client is not None
    mock_credential.assert_called_once_with(
        tenant_id="tenant-123", client_id="client-456", client_secret="secret-789"
    )


@pytest.mark.skip(
    reason="Azure SDK not installed - install via 'pip install -r requirements.txt'"
)
@patch("azure.keyvault.secrets.SecretClient")
def test_secret_manager_keyvault_get_secret(mock_secret_client, clean_env):
    """Test getting secret from Key Vault"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "true"
    os.environ["KEY_VAULT_URL"] = "https://test-vault.vault.azure.net"
    os.environ["AZURE_TENANT_ID"] = "tenant-123"
    os.environ["AZURE_CLIENT_ID"] = "client-456"
    os.environ["AZURE_CLIENT_SECRET"] = "secret-789"

    # Mock the secret client
    mock_client_instance = MagicMock()
    mock_secret_client.return_value = mock_client_instance
    mock_client_instance.list_properties_of_secrets.return_value = iter([])

    # Mock get_secret
    mock_secret = Mock()
    mock_secret.value = "secret-from-keyvault"
    mock_client_instance.get_secret.return_value = mock_secret

    from ops.scripts.utilities.secret_manager import SecretManager

    manager = SecretManager()
    value = manager.get_secret("test-secret")

    assert value == "secret-from-keyvault"
    mock_client_instance.get_secret.assert_called_once_with("test-secret")


@pytest.mark.skip(
    reason="Azure SDK not installed - install via 'pip install -r requirements.txt'"
)
@patch("azure.keyvault.secrets.SecretClient")
def test_secret_manager_keyvault_fallback_on_error(mock_secret_client, clean_env):
    """Test fallback to .env when Key Vault fails"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "true"
    os.environ["KEY_VAULT_URL"] = "https://test-vault.vault.azure.net"
    os.environ["AZURE_TENANT_ID"] = "tenant-123"
    os.environ["AZURE_CLIENT_ID"] = "client-456"
    os.environ["AZURE_CLIENT_SECRET"] = "secret-789"
    os.environ["TEST_SECRET"] = "fallback-value"

    # Mock the secret client to raise exception
    mock_client_instance = MagicMock()
    mock_secret_client.return_value = mock_client_instance
    mock_client_instance.list_properties_of_secrets.return_value = iter([])

    from azure.core.exceptions import AzureError

    mock_client_instance.get_secret.side_effect = AzureError("Permission denied")

    from ops.scripts.utilities.secret_manager import SecretManager

    manager = SecretManager()
    value = manager.get_secret("TEST_SECRET")

    # Should fallback to env var
    assert value == "fallback-value"


def test_secret_manager_cache_expiration(clean_env):
    """Test that cache expires after TTL"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "false"
    os.environ["SECRET_CACHE_TTL"] = "1"  # 1 second

    from ops.scripts.utilities.secret_manager import SecretManager
    import time

    manager = SecretManager()

    # Add to cache
    manager._add_to_cache("test-key", "test-value")

    # Should be in cache
    assert manager._get_from_cache("test-key") == "test-value"

    # Wait for cache to expire
    time.sleep(2)

    # Should be expired
    assert manager._get_from_cache("test-key") is None
