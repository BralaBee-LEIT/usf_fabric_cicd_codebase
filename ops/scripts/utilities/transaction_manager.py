"""
Transaction rollback system for Fabric deployments
Tracks resources and enables cleanup on failure
"""

import logging
from typing import Optional, Dict, List, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

from .feature_flags import _flags as FeatureFlags

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of Fabric resources that can be tracked"""

    WORKSPACE = "workspace"
    LAKEHOUSE = "lakehouse"
    NOTEBOOK = "notebook"
    SEMANTIC_MODEL = "semantic_model"
    REPORT = "report"
    PIPELINE = "pipeline"
    DATAFLOW = "dataflow"
    WAREHOUSE = "warehouse"
    SPARK_JOB_DEFINITION = "spark_job_definition"


@dataclass
class TrackedResource:
    """Represents a resource that can be rolled back"""

    resource_type: ResourceType
    resource_id: str
    resource_name: str
    workspace_id: Optional[str] = None
    cleanup_func: Optional[Callable] = None
    cleanup_args: tuple = field(default_factory=tuple)
    cleanup_kwargs: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for logging"""
        return {
            "resource_type": self.resource_type.value,
            "resource_id": self.resource_id,
            "resource_name": self.resource_name,
            "workspace_id": self.workspace_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }


class TransactionStatus(Enum):
    """Transaction lifecycle states"""

    ACTIVE = "active"  # Transaction in progress
    COMMITTED = "committed"  # Successfully completed
    ROLLED_BACK = "rolled_back"  # Failed and cleaned up
    FAILED = "failed"  # Failed but cleanup disabled


class DeploymentTransaction:
    """
    Manages transactional deployment of Fabric resources

    Tracks all created resources and provides rollback capability on failure.
    Ensures consistent state by cleaning up partially deployed resources.

    Example:
        transaction = DeploymentTransaction(name="Deploy Analytics Workspace")

        try:
            # Create resources
            workspace_id = create_workspace("Analytics")
            transaction.track_resource(
                ResourceType.WORKSPACE,
                workspace_id,
                "Analytics",
                cleanup_func=delete_workspace,
                cleanup_args=(workspace_id,)
            )

            lakehouse_id = create_lakehouse(workspace_id, "Data")
            transaction.track_resource(
                ResourceType.LAKEHOUSE,
                lakehouse_id,
                "Data",
                workspace_id=workspace_id,
                cleanup_func=delete_lakehouse,
                cleanup_args=(workspace_id, lakehouse_id)
            )

            # Commit on success
            transaction.commit()

        except Exception as e:
            # Automatic rollback on failure
            transaction.rollback()
            raise
    """

    def __init__(
        self,
        name: str,
        enable_rollback: bool = True,
        dry_run: bool = False,
    ):
        """
        Initialize deployment transaction

        Args:
            name: Descriptive name for this transaction
            enable_rollback: Whether to perform rollback on failure (default: True)
            dry_run: If True, log actions but don't execute cleanup (default: False)
        """
        self.name = name
        self.enable_rollback = enable_rollback and FeatureFlags.USE_ROLLBACK
        self.dry_run = dry_run
        self.status = TransactionStatus.ACTIVE
        self.resources: List[TrackedResource] = []
        self.started_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.rollback_errors: List[str] = []

        logger.info(
            f"Transaction '{name}' started (rollback={'enabled' if self.enable_rollback else 'disabled'})"
        )

    def track_resource(
        self,
        resource_type: ResourceType,
        resource_id: str,
        resource_name: str,
        workspace_id: Optional[str] = None,
        cleanup_func: Optional[Callable] = None,
        cleanup_args: tuple = (),
        cleanup_kwargs: dict = None,
        metadata: dict = None,
    ):
        """
        Track a resource for potential rollback

        Args:
            resource_type: Type of resource (workspace, lakehouse, etc.)
            resource_id: Unique identifier for the resource
            resource_name: Human-readable name
            workspace_id: Parent workspace ID (if applicable)
            cleanup_func: Function to call for cleanup/deletion
            cleanup_args: Positional arguments for cleanup function
            cleanup_kwargs: Keyword arguments for cleanup function
            metadata: Additional metadata to store with resource
        """
        if cleanup_kwargs is None:
            cleanup_kwargs = {}
        if metadata is None:
            metadata = {}

        resource = TrackedResource(
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            workspace_id=workspace_id,
            cleanup_func=cleanup_func,
            cleanup_args=cleanup_args,
            cleanup_kwargs=cleanup_kwargs,
            metadata=metadata,
        )

        self.resources.append(resource)

        logger.info(
            f"Transaction '{self.name}': Tracking {resource_type.value} "
            f"'{resource_name}' (ID: {resource_id})"
        )

    def commit(self):
        """
        Commit transaction - marks deployment as successful
        Resources will not be rolled back after commit
        """
        if self.status != TransactionStatus.ACTIVE:
            logger.warning(
                f"Transaction '{self.name}' already {self.status.value} - cannot commit"
            )
            return

        self.status = TransactionStatus.COMMITTED
        self.completed_at = datetime.now()
        duration = (self.completed_at - self.started_at).total_seconds()

        logger.info(
            f"Transaction '{self.name}' COMMITTED successfully "
            f"({len(self.resources)} resources, {duration:.2f}s)"
        )

    def rollback(self, reason: Optional[str] = None):
        """
        Rollback transaction - delete all tracked resources in reverse order

        Args:
            reason: Optional reason for rollback (logged)
        """
        if self.status != TransactionStatus.ACTIVE:
            logger.warning(
                f"Transaction '{self.name}' already {self.status.value} - cannot rollback"
            )
            return

        if not self.enable_rollback:
            logger.warning(
                f"Transaction '{self.name}' rollback disabled - "
                f"resources will NOT be cleaned up"
            )
            self.status = TransactionStatus.FAILED
            self.completed_at = datetime.now()
            return

        logger.warning(
            f"Transaction '{self.name}' ROLLING BACK "
            f"({len(self.resources)} resources)"
        )
        if reason:
            logger.warning(f"Rollback reason: {reason}")

        # Rollback in reverse order (LIFO - last in, first out)
        cleanup_count = 0
        for resource in reversed(self.resources):
            try:
                self._cleanup_resource(resource)
                cleanup_count += 1
            except Exception as e:
                error_msg = (
                    f"Failed to cleanup {resource.resource_type.value} "
                    f"'{resource.resource_name}': {str(e)}"
                )
                logger.error(error_msg)
                self.rollback_errors.append(error_msg)

        self.status = TransactionStatus.ROLLED_BACK
        self.completed_at = datetime.now()

        if self.rollback_errors:
            logger.error(
                f"Transaction '{self.name}' rollback completed with "
                f"{len(self.rollback_errors)} errors (cleaned up {cleanup_count}/{len(self.resources)})"
            )
        else:
            logger.info(
                f"Transaction '{self.name}' rollback successful "
                f"(cleaned up {cleanup_count} resources)"
            )

    def _cleanup_resource(self, resource: TrackedResource):
        """Execute cleanup for a single resource"""
        if resource.cleanup_func is None:
            logger.warning(
                f"No cleanup function for {resource.resource_type.value} "
                f"'{resource.resource_name}' - skipping"
            )
            return

        if self.dry_run:
            logger.info(
                f"[DRY RUN] Would cleanup {resource.resource_type.value} "
                f"'{resource.resource_name}' (ID: {resource.resource_id})"
            )
            return

        logger.info(
            f"Cleaning up {resource.resource_type.value} "
            f"'{resource.resource_name}' (ID: {resource.resource_id})"
        )

        try:
            resource.cleanup_func(*resource.cleanup_args, **resource.cleanup_kwargs)
            logger.debug(f"Successfully cleaned up '{resource.resource_name}'")
        except Exception as e:
            logger.error(f"Cleanup failed for '{resource.resource_name}': {str(e)}")
            raise

    def get_stats(self) -> dict:
        """Get transaction statistics and resource summary"""
        duration = None
        if self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()

        return {
            "name": self.name,
            "status": self.status.value,
            "enable_rollback": self.enable_rollback,
            "dry_run": self.dry_run,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "duration_seconds": round(duration, 2) if duration else None,
            "resource_count": len(self.resources),
            "resources": [r.to_dict() for r in self.resources],
            "rollback_errors": self.rollback_errors,
        }

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - auto rollback on exception"""
        if exc_type is not None:
            # Exception occurred - rollback
            self.rollback(reason=f"{exc_type.__name__}: {exc_val}")
            # Re-raise exception
            return False
        else:
            # Success - commit
            self.commit()
            return True


# Transaction registry for monitoring
_active_transactions: Dict[str, DeploymentTransaction] = {}


def register_transaction(transaction: DeploymentTransaction):
    """Register transaction for monitoring"""
    _active_transactions[transaction.name] = transaction


def unregister_transaction(transaction_name: str):
    """Remove transaction from registry"""
    if transaction_name in _active_transactions:
        del _active_transactions[transaction_name]


def get_active_transactions() -> List[dict]:
    """Get statistics for all active transactions"""
    return [t.get_stats() for t in _active_transactions.values()]
