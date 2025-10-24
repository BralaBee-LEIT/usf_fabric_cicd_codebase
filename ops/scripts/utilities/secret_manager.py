"""
Unified secret management with Azure Key Vault and .env fallback
Provides seamless secret access with caching and graceful degradation
"""

import os
import logging
import time
from typing import Optional, Dict
from datetime import datetime, timedelta

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.core.exceptions import AzureError

    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False

from .feature_flags import FeatureFlags

logger = logging.getLogger(__name__)


class SecretManager:
    """
    Unified secret management with Azure Key Vault + .env fallback

    Features:
    - Azure Key Vault integration when enabled
    - In-memory cache with configurable TTL
    - Graceful fallback to environment variables
    - Singleton pattern for efficiency

    Example:
        manager = get_secret_manager()
        api_key = manager.get_secret("fabric-api-key")
    """

    def __init__(self):
        self.use_keyvault = FeatureFlags.USE_KEY_VAULT
        self.kv_client = None
        self._cache: Dict[str, tuple[str, datetime]] = {}
        self._cache_ttl_seconds = int(os.getenv("SECRET_CACHE_TTL", "3600"))  # 1 hour

        if self.use_keyvault:
            self._initialize_keyvault()

    def _initialize_keyvault(self):
        """Initialize Key Vault client"""
        if not AZURE_SDK_AVAILABLE:
            logger.error(
                "Azure SDK not available. Install: pip install azure-keyvault-secrets azure-identity"
            )
            logger.warning("Falling back to .env for secrets")
            self.use_keyvault = False
            return

        vault_url = os.getenv("KEY_VAULT_URL")
        if not vault_url:
            logger.error(
                "KEY_VAULT_URL not set but FEATURE_USE_KEY_VAULT=true. "
                "Please set KEY_VAULT_URL or disable Key Vault feature flag."
            )
            logger.warning("Falling back to .env for secrets")
            self.use_keyvault = False
            return

        try:
            # Try ClientSecretCredential first (explicit service principal)
            tenant_id = os.getenv("AZURE_TENANT_ID")
            client_id = os.getenv("AZURE_CLIENT_ID")
            client_secret = os.getenv("AZURE_CLIENT_SECRET")

            if tenant_id and client_id and client_secret:
                credential = ClientSecretCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret,
                )
                logger.info("Using ClientSecretCredential for Key Vault")
            else:
                # Fallback to DefaultAzureCredential (managed identity, Azure CLI, etc.)
                credential = DefaultAzureCredential()
                logger.info("Using DefaultAzureCredential for Key Vault")

            self.kv_client = SecretClient(vault_url=vault_url, credential=credential)

            # Test connection
            try:
                # Try to list secrets to validate permissions
                next(self.kv_client.list_properties_of_secrets(), None)
                logger.info(f"✓ Key Vault initialized: {vault_url}")
            except StopIteration:
                # Empty vault is okay
                logger.info(f"✓ Key Vault initialized (empty): {vault_url}")
            except AzureError as e:
                logger.warning(
                    f"Key Vault initialized but permission check failed: {e}"
                )
                logger.warning("Secrets may not be accessible")

        except Exception as e:
            logger.error(f"Failed to initialize Key Vault: {e}")
            logger.warning("Falling back to .env for secrets")
            self.use_keyvault = False
            self.kv_client = None

    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from Key Vault with .env fallback

        Args:
            name: Secret name (e.g., "fabric-api-key" or "FABRIC_API_KEY")
            default: Default value if not found

        Returns:
            Secret value or default

        Example:
            api_key = manager.get_secret("fabric-api-key")
            max_retries = manager.get_secret("MAX_RETRIES", default="3")
        """
        if self.use_keyvault and self.kv_client:
            try:
                # Check cache first
                cached_value = self._get_from_cache(name)
                if cached_value is not None:
                    return cached_value

                # Fetch from Key Vault
                # Key Vault uses hyphens, env vars use underscores
                kv_name = name.lower().replace("_", "-")
                secret = self.kv_client.get_secret(kv_name)
                value = secret.value

                # Cache the result
                self._add_to_cache(name, value)

                logger.debug(f"Retrieved secret '{name}' from Key Vault")
                return value

            except AzureError as e:
                logger.warning(
                    f"Failed to get secret '{name}' from Key Vault: {e}. "
                    f"Falling back to environment variable."
                )
                # Fallback to .env
            except Exception as e:
                logger.error(f"Unexpected error getting secret '{name}': {e}")
                # Fallback to .env

        # Fallback to environment variable
        # Try both formats: UPPER_CASE and original
        env_name = name.upper().replace("-", "_")
        value = os.getenv(env_name) or os.getenv(name, default)

        if value:
            logger.debug(f"Retrieved secret '{name}' from environment variable")
        else:
            logger.debug(f"Secret '{name}' not found (using default: {default})")

        return value

    def set_secret(self, name: str, value: str):
        """
        Set secret in Key Vault (production only)

        Args:
            name: Secret name
            value: Secret value

        Raises:
            ValueError: If Key Vault is disabled
            AzureError: If Key Vault operation fails

        Example:
            manager.set_secret("new-api-key", "sk-...")
        """
        if not self.use_keyvault or not self.kv_client:
            raise ValueError(
                "Cannot set secrets when Key Vault is disabled. "
                "Set FEATURE_USE_KEY_VAULT=true and configure KEY_VAULT_URL"
            )

        try:
            kv_name = name.lower().replace("_", "-")
            self.kv_client.set_secret(kv_name, value)

            # Invalidate cache
            self._remove_from_cache(name)

            logger.info(f"✓ Secret '{name}' updated in Key Vault")

        except AzureError as e:
            logger.error(f"Failed to set secret '{name}' in Key Vault: {e}")
            raise

    def refresh_cache(self):
        """
        Clear cache to force reload from Key Vault

        Use this after secret rotation or when troubleshooting

        Example:
            manager.refresh_cache()  # Force reload all secrets
        """
        self._cache.clear()
        logger.info("Secret cache cleared")

    def _get_from_cache(self, name: str) -> Optional[str]:
        """Get secret from cache if not expired"""
        if name not in self._cache:
            return None

        value, cached_at = self._cache[name]
        age = datetime.now() - cached_at

        if age.total_seconds() > self._cache_ttl_seconds:
            # Cache expired
            del self._cache[name]
            return None

        return value

    def _add_to_cache(self, name: str, value: str):
        """Add secret to cache with timestamp"""
        self._cache[name] = (value, datetime.now())

    def _remove_from_cache(self, name: str):
        """Remove secret from cache"""
        if name in self._cache:
            del self._cache[name]

    def get_cache_stats(self) -> Dict[str, any]:
        """
        Get cache statistics for monitoring

        Returns:
            Dictionary with cache size, TTL, and keys
        """
        return {
            "cache_size": len(self._cache),
            "cache_ttl_seconds": self._cache_ttl_seconds,
            "cached_keys": list(self._cache.keys()),
            "use_keyvault": self.use_keyvault,
        }


# Singleton instance
_secret_manager = None


def get_secret_manager() -> SecretManager:
    """
    Get singleton SecretManager instance

    Returns:
        Singleton SecretManager instance

    Example:
        from ops.scripts.utilities.secret_manager import get_secret_manager

        manager = get_secret_manager()
        tenant_id = manager.get_secret("AZURE_TENANT_ID")
    """
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = SecretManager()
    return _secret_manager
