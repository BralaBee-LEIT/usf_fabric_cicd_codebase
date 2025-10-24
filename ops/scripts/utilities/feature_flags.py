"""
Feature flags for production hardening
All features disabled by default for backward compatibility
"""

import os
import logging

logger = logging.getLogger(__name__)


class FeatureFlags:
    """Control rollout of production hardening features"""

    # Secret Management
    @property
    def USE_KEY_VAULT(self) -> bool:
        return os.getenv("FEATURE_USE_KEY_VAULT", "false").lower() == "true"

    # Reliability
    @property
    def USE_RETRY_LOGIC(self) -> bool:
        return os.getenv("FEATURE_USE_RETRY_LOGIC", "false").lower() == "true"

    @property
    def USE_CIRCUIT_BREAKER(self) -> bool:
        return os.getenv("FEATURE_USE_CIRCUIT_BREAKER", "false").lower() == "true"

    @property
    def USE_ROLLBACK(self) -> bool:
        return os.getenv("FEATURE_USE_ROLLBACK", "false").lower() == "true"

    # Observability
    @property
    def USE_TELEMETRY(self) -> bool:
        return os.getenv("FEATURE_USE_TELEMETRY", "false").lower() == "true"

    def log_status(self):
        """Log current feature flag status"""
        logger.info("Feature Flags Status:")
        logger.info(f"  USE_KEY_VAULT: {self.USE_KEY_VAULT}")
        logger.info(f"  USE_RETRY_LOGIC: {self.USE_RETRY_LOGIC}")
        logger.info(f"  USE_CIRCUIT_BREAKER: {self.USE_CIRCUIT_BREAKER}")
        logger.info(f"  USE_ROLLBACK: {self.USE_ROLLBACK}")
        logger.info(f"  USE_TELEMETRY: {self.USE_TELEMETRY}")

    def is_production_ready(self) -> bool:
        """Check if all production features are enabled"""
        return all(
            [
                self.USE_KEY_VAULT,
                self.USE_RETRY_LOGIC,
                self.USE_ROLLBACK,
                self.USE_TELEMETRY,
            ]
        )


# Singleton instance for easy access
_flags = FeatureFlags()


# Log on import if DEBUG enabled (helps with debugging)
if os.getenv("DEBUG", "false").lower() == "true":
    _flags.log_status()
