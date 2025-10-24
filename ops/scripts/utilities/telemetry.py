"""
Application Insights telemetry for Fabric deployments
Tracks metrics, events, and performance
"""

import logging
import os
import time
from functools import wraps
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from enum import Enum

from .feature_flags import _flags as FeatureFlags

logger = logging.getLogger(__name__)

# Try to import Application Insights
try:
    from applicationinsights import TelemetryClient as AITelemetryClient
    from applicationinsights.channel import TelemetryChannel
    from applicationinsights.exceptions import enable as enable_exception_tracking

    APPINSIGHTS_AVAILABLE = True
except ImportError:
    APPINSIGHTS_AVAILABLE = False
    AITelemetryClient = None
    logger.debug("Application Insights SDK not available")


class TelemetryEventType(Enum):
    """Types of telemetry events"""

    DEPLOYMENT_STARTED = "deployment_started"
    DEPLOYMENT_COMPLETED = "deployment_completed"
    DEPLOYMENT_FAILED = "deployment_failed"
    RESOURCE_CREATED = "resource_created"
    RESOURCE_DELETED = "resource_deleted"
    RETRY_ATTEMPTED = "retry_attempted"
    CIRCUIT_BREAKER_OPENED = "circuit_breaker_opened"
    CIRCUIT_BREAKER_CLOSED = "circuit_breaker_closed"
    TRANSACTION_ROLLED_BACK = "transaction_rolled_back"
    SECRET_ACCESSED = "secret_accessed"
    API_CALL = "api_call"


class TelemetryClient:
    """
    Wrapper for Application Insights telemetry

    Provides simplified interface for tracking metrics, events, and performance.
    Falls back to logging if Application Insights is not available or disabled.

    Example:
        client = get_telemetry_client()

        # Track event
        client.track_event('deployment_started', {'workspace': 'Analytics'})

        # Track metric
        client.track_metric('deployment_duration', 45.2, {'status': 'success'})

        # Track performance
        with client.track_operation('create_workspace'):
            workspace = create_workspace('Analytics')
    """

    def __init__(self, instrumentation_key: Optional[str] = None):
        """
        Initialize telemetry client

        Args:
            instrumentation_key: Application Insights instrumentation key
                                If not provided, reads from APPINSIGHTS_INSTRUMENTATION_KEY env var
        """
        self.enabled = FeatureFlags.USE_TELEMETRY and APPINSIGHTS_AVAILABLE
        self.client = None

        if not self.enabled:
            if not FeatureFlags.USE_TELEMETRY:
                logger.debug("Telemetry disabled by feature flag")
            elif not APPINSIGHTS_AVAILABLE:
                logger.warning(
                    "Application Insights SDK not available. "
                    "Install: pip install applicationinsights"
                )
            return

        # Get instrumentation key
        self.instrumentation_key = instrumentation_key or os.getenv(
            "APPINSIGHTS_INSTRUMENTATION_KEY"
        )

        if not self.instrumentation_key:
            logger.warning(
                "APPINSIGHTS_INSTRUMENTATION_KEY not set - telemetry disabled. "
                "Set environment variable to enable telemetry."
            )
            self.enabled = False
            return

        try:
            self.client = AITelemetryClient(self.instrumentation_key)
            logger.info("Application Insights telemetry initialized")

            # Enable automatic exception tracking
            enable_exception_tracking(self.instrumentation_key)
        except Exception as e:
            logger.error(f"Failed to initialize Application Insights: {e}")
            self.enabled = False

    def track_event(
        self,
        event_name: str,
        properties: Optional[Dict[str, Any]] = None,
        measurements: Optional[Dict[str, float]] = None,
    ):
        """
        Track a custom event

        Args:
            event_name: Name of the event
            properties: Custom properties (strings)
            measurements: Custom measurements (numbers)
        """
        if properties is None:
            properties = {}
        if measurements is None:
            measurements = {}

        # Add standard properties
        properties["timestamp"] = datetime.utcnow().isoformat()
        properties["environment"] = os.getenv("ENVIRONMENT", "development")

        if self.enabled and self.client:
            try:
                self.client.track_event(event_name, properties, measurements)
                self.client.flush()
            except Exception as e:
                logger.error(f"Failed to track event '{event_name}': {e}")
        else:
            # Fallback to logging
            logger.info(
                f"[TELEMETRY] Event: {event_name}, "
                f"Properties: {properties}, Measurements: {measurements}"
            )

    def track_metric(
        self,
        name: str,
        value: float,
        properties: Optional[Dict[str, str]] = None,
    ):
        """
        Track a metric value

        Args:
            name: Metric name
            value: Metric value
            properties: Additional properties
        """
        if properties is None:
            properties = {}

        properties["timestamp"] = datetime.utcnow().isoformat()

        if self.enabled and self.client:
            try:
                self.client.track_metric(name, value, properties=properties)
                self.client.flush()
            except Exception as e:
                logger.error(f"Failed to track metric '{name}': {e}")
        else:
            logger.info(f"[TELEMETRY] Metric: {name}={value}, Properties: {properties}")

    def track_exception(
        self,
        exception: Exception,
        properties: Optional[Dict[str, str]] = None,
        measurements: Optional[Dict[str, float]] = None,
    ):
        """
        Track an exception

        Args:
            exception: The exception that occurred
            properties: Additional properties
            measurements: Additional measurements
        """
        if properties is None:
            properties = {}
        if measurements is None:
            measurements = {}

        properties["timestamp"] = datetime.utcnow().isoformat()

        if self.enabled and self.client:
            try:
                self.client.track_exception(
                    type(exception),
                    exception,
                    exception.__traceback__,
                    properties=properties,
                    measurements=measurements,
                )
                self.client.flush()
            except Exception as e:
                logger.error(f"Failed to track exception: {e}")
        else:
            logger.error(
                f"[TELEMETRY] Exception: {type(exception).__name__}: {exception}, "
                f"Properties: {properties}"
            )

    def track_trace(
        self,
        message: str,
        severity: str = "INFO",
        properties: Optional[Dict[str, str]] = None,
    ):
        """
        Track a trace message

        Args:
            message: Trace message
            severity: Severity level (VERBOSE, INFO, WARNING, ERROR, CRITICAL)
            properties: Additional properties
        """
        if properties is None:
            properties = {}

        properties["timestamp"] = datetime.utcnow().isoformat()

        if self.enabled and self.client:
            try:
                self.client.track_trace(
                    message, severity=severity, properties=properties
                )
                self.client.flush()
            except Exception as e:
                logger.error(f"Failed to track trace: {e}")
        else:
            log_level = getattr(logging, severity, logging.INFO)
            logger.log(log_level, f"[TELEMETRY] {message}, Properties: {properties}")

    def track_dependency(
        self,
        name: str,
        dependency_type: str,
        data: str,
        duration: float,
        success: bool,
        properties: Optional[Dict[str, str]] = None,
    ):
        """
        Track a dependency call (external service, database, etc.)

        Args:
            name: Dependency name
            dependency_type: Type (HTTP, SQL, Azure, etc.)
            data: Command or query executed
            duration: Duration in seconds
            success: Whether the call succeeded
            properties: Additional properties
        """
        if properties is None:
            properties = {}

        properties["timestamp"] = datetime.utcnow().isoformat()

        if self.enabled and self.client:
            try:
                # Convert duration to milliseconds
                duration_ms = duration * 1000
                self.client.track_dependency(
                    name,
                    data,
                    dependency_type,
                    success=success,
                    duration=int(duration_ms),
                    properties=properties,
                )
                self.client.flush()
            except Exception as e:
                logger.error(f"Failed to track dependency '{name}': {e}")
        else:
            logger.info(
                f"[TELEMETRY] Dependency: {name} ({dependency_type}), "
                f"Duration: {duration:.2f}s, Success: {success}"
            )

    def track_operation(
        self, operation_name: str, properties: Optional[Dict[str, str]] = None
    ):
        """
        Context manager to track operation performance

        Args:
            operation_name: Name of the operation
            properties: Additional properties

        Example:
            with telemetry_client.track_operation('create_workspace'):
                workspace = create_workspace('Analytics')
        """
        return OperationTracker(self, operation_name, properties)

    def flush(self):
        """Flush telemetry data immediately"""
        if self.enabled and self.client:
            try:
                self.client.flush()
            except Exception as e:
                logger.error(f"Failed to flush telemetry: {e}")


class OperationTracker:
    """Context manager for tracking operation performance"""

    def __init__(
        self,
        telemetry_client: TelemetryClient,
        operation_name: str,
        properties: Optional[Dict[str, str]] = None,
    ):
        self.telemetry_client = telemetry_client
        self.operation_name = operation_name
        self.properties = properties or {}
        self.start_time = None
        self.success = True

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.success = exc_type is None

        # Track as dependency
        self.telemetry_client.track_dependency(
            name=self.operation_name,
            dependency_type="Operation",
            data=self.operation_name,
            duration=duration,
            success=self.success,
            properties=self.properties,
        )

        # If failed, track exception
        if not self.success:
            self.telemetry_client.track_exception(
                exc_val, properties={"operation": self.operation_name}
            )

        return False  # Don't suppress exceptions


def track_performance(operation_name: Optional[str] = None):
    """
    Decorator to track function performance

    Args:
        operation_name: Name for the operation (defaults to function name)

    Example:
        @track_performance("create_workspace")
        def create_workspace(name: str) -> dict:
            # ... implementation
            return workspace
    """

    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            telemetry_client = get_telemetry_client()

            with telemetry_client.track_operation(op_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Global telemetry client singleton
_telemetry_client: Optional[TelemetryClient] = None


def get_telemetry_client() -> TelemetryClient:
    """
    Get or create the global telemetry client

    Returns:
        TelemetryClient instance (singleton)
    """
    global _telemetry_client

    if _telemetry_client is None:
        _telemetry_client = TelemetryClient()

    return _telemetry_client


def track_deployment_event(
    event_type: TelemetryEventType,
    properties: Optional[Dict[str, Any]] = None,
    measurements: Optional[Dict[str, float]] = None,
):
    """
    Convenience function to track deployment events

    Args:
        event_type: Type of deployment event
        properties: Event properties
        measurements: Event measurements
    """
    client = get_telemetry_client()
    client.track_event(event_type.value, properties, measurements)
