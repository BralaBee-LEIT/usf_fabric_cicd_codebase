"""
Health check endpoints for monitoring application and dependency status.

This module provides health check functionality to monitor:
- Basic application health (/health endpoint)
- Dependency readiness (/ready endpoint)
- Azure service connectivity
- Secret Manager availability
- Circuit breaker states

Health checks are feature-flag gated and return JSON responses with:
- Overall status (healthy/degraded/unhealthy)
- Individual check results
- Timestamps and response times
- Detailed error messages when applicable

Usage:
    from ops.scripts.utilities.health_check import get_health_status, get_readiness_status
    
    # Basic health check
    health = get_health_status()
    print(f"Status: {health['status']}")
    
    # Dependency readiness check
    ready = get_readiness_status()
    if ready['status'] == 'healthy':
        print("All dependencies available")
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

from ops.scripts.utilities.feature_flags import FeatureFlags
from ops.scripts.utilities.secret_manager import get_secret_manager
from ops.scripts.utilities.circuit_breaker import get_all_circuit_breakers

# Try importing Azure SDK for connectivity checks
try:
    from azure.identity import DefaultAzureCredential
    from azure.core.exceptions import AzureError

    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """
    Health check manager for monitoring application and dependencies.

    Provides endpoints for:
    - Basic health: Application is running and responsive
    - Readiness: All dependencies are available and healthy

    Feature flag controlled: FEATURE_USE_HEALTH_CHECKS
    """

    def __init__(self):
        """Initialize health check manager."""
        self.feature_flags = FeatureFlags()
        self._checks_enabled = self.feature_flags.USE_HEALTH_CHECKS

        if not self._checks_enabled:
            logger.info("Health checks disabled by feature flag")

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get basic health status of the application.

        This is a lightweight check that returns quickly.
        Checks:
        - Application is running
        - Basic configuration is valid

        Returns:
            dict: Health status with format:
                {
                    'status': 'healthy|degraded|unhealthy',
                    'timestamp': ISO timestamp,
                    'checks': {
                        'application': {'status': '...', 'message': '...'},
                        ...
                    },
                    'duration_ms': response time in milliseconds
                }
        """
        start_time = time.time()

        if not self._checks_enabled:
            return self._disabled_response(start_time)

        checks = {}

        # Check 1: Application running
        checks["application"] = {
            "status": HealthStatus.HEALTHY.value,
            "message": "Application is running",
        }

        # Check 2: Feature flags accessible
        try:
            self.feature_flags.is_production_ready()
            checks["feature_flags"] = {
                "status": HealthStatus.HEALTHY.value,
                "message": "Feature flags accessible",
            }
        except Exception as e:
            checks["feature_flags"] = {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Feature flags error: {str(e)}",
            }

        # Determine overall status
        overall_status = self._determine_overall_status(checks)

        duration_ms = (time.time() - start_time) * 1000

        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
            "duration_ms": round(duration_ms, 2),
        }

    def get_readiness_status(self) -> Dict[str, Any]:
        """
        Get readiness status including all dependencies.

        This is a more thorough check that may take longer.
        Checks:
        - Azure connectivity
        - Secret Manager availability
        - Circuit breaker states

        Returns:
            dict: Readiness status with same format as health status
        """
        start_time = time.time()

        if not self._checks_enabled:
            return self._disabled_response(start_time)

        checks = {}

        # Check 1: Azure connectivity
        checks["azure_connectivity"] = self._check_azure_connectivity()

        # Check 2: Secret Manager
        checks["secret_manager"] = self._check_secret_manager()

        # Check 3: Circuit breakers
        checks["circuit_breakers"] = self._check_circuit_breakers()

        # Determine overall status
        overall_status = self._determine_overall_status(checks)

        duration_ms = (time.time() - start_time) * 1000

        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
            "duration_ms": round(duration_ms, 2),
        }

    def _check_azure_connectivity(self) -> Dict[str, Any]:
        """
        Check Azure connectivity by attempting authentication.

        Returns:
            dict: Check result with status and message
        """
        if not AZURE_SDK_AVAILABLE:
            return {
                "status": HealthStatus.DEGRADED.value,
                "message": "Azure SDK not available (optional dependency)",
            }

        if not self.feature_flags.USE_AZURE_KEYVAULT:
            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Azure Key Vault not in use",
            }

        try:
            # Attempt to get a credential token
            credential = DefaultAzureCredential()
            # Try to get a token (lightweight check)
            token = credential.get_token("https://vault.azure.net/.default")

            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Azure authentication successful",
            }
        except Exception as e:
            logger.warning(f"Azure connectivity check failed: {e}")
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Azure authentication failed: {str(e)}",
            }

    def _check_secret_manager(self) -> Dict[str, Any]:
        """
        Check Secret Manager availability.

        Returns:
            dict: Check result with status and message
        """
        try:
            secret_manager = get_secret_manager()

            # Get cache stats as a lightweight check
            stats = secret_manager.get_cache_stats()

            return {
                "status": HealthStatus.HEALTHY.value,
                "message": "Secret Manager available",
                "cache_size": stats["cache_size"],
            }
        except Exception as e:
            logger.warning(f"Secret Manager check failed: {e}")
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Secret Manager error: {str(e)}",
            }

    def _check_circuit_breakers(self) -> Dict[str, Any]:
        """
        Check circuit breaker states.

        Returns:
            dict: Check result with status and circuit breaker summary
        """
        try:
            breakers = get_all_circuit_breakers()

            if not breakers:
                return {
                    "status": HealthStatus.HEALTHY.value,
                    "message": "No circuit breakers registered",
                }

            # Count states
            open_count = sum(1 for b in breakers.values() if b.state.value == "OPEN")
            half_open_count = sum(
                1 for b in breakers.values() if b.state.value == "HALF_OPEN"
            )
            closed_count = sum(
                1 for b in breakers.values() if b.state.value == "CLOSED"
            )

            # Determine status based on open breakers
            if open_count > 0:
                status = HealthStatus.DEGRADED
                message = f"{open_count} circuit breaker(s) OPEN"
            elif half_open_count > 0:
                status = HealthStatus.DEGRADED
                message = f"{half_open_count} circuit breaker(s) HALF_OPEN"
            else:
                status = HealthStatus.HEALTHY
                message = "All circuit breakers CLOSED"

            return {
                "status": status.value,
                "message": message,
                "total": len(breakers),
                "open": open_count,
                "half_open": half_open_count,
                "closed": closed_count,
            }
        except Exception as e:
            logger.warning(f"Circuit breaker check failed: {e}")
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"Circuit breaker check error: {str(e)}",
            }

    def _determine_overall_status(
        self, checks: Dict[str, Dict[str, Any]]
    ) -> HealthStatus:
        """
        Determine overall status from individual checks.

        Rules:
        - If any check is UNHEALTHY, overall is UNHEALTHY
        - If any check is DEGRADED, overall is DEGRADED
        - Otherwise, overall is HEALTHY

        Args:
            checks: Dictionary of check results

        Returns:
            HealthStatus: Overall status
        """
        statuses = [check.get("status") for check in checks.values()]

        if HealthStatus.UNHEALTHY.value in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED.value in statuses:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

    def _disabled_response(self, start_time: float) -> Dict[str, Any]:
        """
        Return response when health checks are disabled.

        Args:
            start_time: Start time for duration calculation

        Returns:
            dict: Disabled response
        """
        duration_ms = (time.time() - start_time) * 1000

        return {
            "status": HealthStatus.HEALTHY.value,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Health checks disabled by feature flag",
            "duration_ms": round(duration_ms, 2),
        }


# Singleton instance
_health_check_instance: Optional[HealthCheck] = None


def get_health_check() -> HealthCheck:
    """
    Get or create singleton HealthCheck instance.

    Returns:
        HealthCheck: Singleton health check instance
    """
    global _health_check_instance

    if _health_check_instance is None:
        _health_check_instance = HealthCheck()

    return _health_check_instance


def get_health_status() -> Dict[str, Any]:
    """
    Convenience function to get health status.

    Returns:
        dict: Health status
    """
    return get_health_check().get_health_status()


def get_readiness_status() -> Dict[str, Any]:
    """
    Convenience function to get readiness status.

    Returns:
        dict: Readiness status
    """
    return get_health_check().get_readiness_status()


def reset_health_check():
    """Reset the singleton instance (mainly for testing)."""
    global _health_check_instance
    _health_check_instance = None
