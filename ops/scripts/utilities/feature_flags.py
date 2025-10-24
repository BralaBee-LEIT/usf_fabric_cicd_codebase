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
    USE_KEY_VAULT = os.getenv("FEATURE_USE_KEY_VAULT", "false").lower() == "true"

    # Reliability
    USE_RETRY_LOGIC = os.getenv("FEATURE_USE_RETRY_LOGIC", "false").lower() == "true"
    USE_CIRCUIT_BREAKER = (
        os.getenv("FEATURE_USE_CIRCUIT_BREAKER", "false").lower() == "true"
    )
    USE_ROLLBACK = os.getenv("FEATURE_USE_ROLLBACK", "false").lower() == "true"

    # Observability
    USE_TELEMETRY = os.getenv("FEATURE_USE_TELEMETRY", "false").lower() == "true"

    @classmethod
    def log_status(cls):
        """Log current feature flag status"""
        logger.info("Feature Flags Status:")
        logger.info(f"  USE_KEY_VAULT: {cls.USE_KEY_VAULT}")
        logger.info(f"  USE_RETRY_LOGIC: {cls.USE_RETRY_LOGIC}")
        logger.info(f"  USE_CIRCUIT_BREAKER: {cls.USE_CIRCUIT_BREAKER}")
        logger.info(f"  USE_ROLLBACK: {cls.USE_ROLLBACK}")
        logger.info(f"  USE_TELEMETRY: {cls.USE_TELEMETRY}")

    @classmethod
    def is_production_ready(cls) -> bool:
        """Check if all production features are enabled"""
        return all(
            [
                cls.USE_KEY_VAULT,
                cls.USE_RETRY_LOGIC,
                cls.USE_ROLLBACK,
                cls.USE_TELEMETRY,
            ]
        )


# Log on import if DEBUG enabled (helps with debugging)
if os.getenv("DEBUG", "false").lower() == "true":
    FeatureFlags.log_status()
