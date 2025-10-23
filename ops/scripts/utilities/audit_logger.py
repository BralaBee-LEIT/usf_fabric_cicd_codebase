"""
Centralized Audit Logger for Fabric CI/CD Operations

Provides comprehensive audit trail for:
- Workspace creation and management
- Item creation and updates
- Git integration operations
- User and permission changes
- Deployment activities

Logs are stored in JSONL format for easy querying and analysis.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import subprocess
import os

logger = logging.getLogger(__name__)


class AuditEventType:
    """Audit event type enumeration"""
    WORKSPACE_CREATED = "workspace_created"
    WORKSPACE_UPDATED = "workspace_updated"
    WORKSPACE_DELETED = "workspace_deleted"
    
    ITEM_CREATED = "item_created"
    ITEM_UPDATED = "item_updated"
    ITEM_DELETED = "item_deleted"
    
    GIT_CONNECTED = "git_connected"
    GIT_DISCONNECTED = "git_disconnected"
    GIT_COMMITTED = "git_committed"
    GIT_UPDATED = "git_updated"
    
    USER_ADDED = "user_added"
    USER_REMOVED = "user_removed"
    USER_ROLE_CHANGED = "user_role_changed"
    
    DEPLOYMENT_STARTED = "deployment_started"
    DEPLOYMENT_COMPLETED = "deployment_completed"
    DEPLOYMENT_FAILED = "deployment_failed"
    
    VALIDATION_FAILED = "validation_failed"
    VALIDATION_PASSED = "validation_passed"
    
    ONBOARDING_STARTED = "onboarding_started"
    ONBOARDING_COMPLETED = "onboarding_completed"
    ONBOARDING_FAILED = "onboarding_failed"


class AuditLogger:
    """
    Centralized audit logging for all Fabric CI/CD operations
    
    Logs events in JSONL format for:
    - Compliance reporting
    - Troubleshooting
    - Change tracking
    - Performance monitoring
    
    Usage:
        audit_logger = AuditLogger()
        
        # Log workspace creation
        audit_logger.log_workspace_creation(
            workspace_id="abc-123",
            workspace_name="My Product [DEV]",
            product_id="my_product",
            environment="dev"
        )
        
        # Log Git connection
        audit_logger.log_git_connection(
            workspace_id="abc-123",
            branch="main",
            directory="/data_products/my_product"
        )
        
        # Generate compliance report
        report = audit_logger.generate_compliance_report(
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
    """
    
    def __init__(
        self,
        audit_file: Optional[Path] = None,
        auto_create_dirs: bool = True
    ):
        """
        Initialize audit logger
        
        Args:
            audit_file: Path to audit log file (JSONL format)
            auto_create_dirs: Automatically create audit directory if missing
        """
        if audit_file is None:
            # Default to audit/audit_trail.jsonl in project root
            project_root = Path(__file__).parent.parent.parent.parent
            self.audit_file = project_root / "audit" / "audit_trail.jsonl"
        else:
            self.audit_file = Path(audit_file)
        
        # Create directory if needed
        if auto_create_dirs:
            self.audit_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Audit logger initialized: {self.audit_file}")
    
    def _get_git_context(self) -> Dict[str, str]:
        """Get current Git context (commit, branch, user)"""
        try:
            git_commit = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            git_commit = "unknown"
        
        try:
            git_branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            git_branch = "unknown"
        
        try:
            git_user = subprocess.check_output(
                ['git', 'config', 'user.email'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            git_user = os.getenv("USER", "unknown")
        
        return {
            "git_commit": git_commit,
            "git_branch": git_branch,
            "git_user": git_user
        }
    
    def _log_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        include_git_context: bool = True
    ) -> None:
        """
        Log an audit event to JSONL file
        
        Args:
            event_type: Type of event (from AuditEventType)
            event_data: Event-specific data
            include_git_context: Include Git commit/branch/user info
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            **event_data
        }
        
        if include_git_context:
            event.update(self._get_git_context())
        
        # Append to JSONL file
        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        logger.debug(f"Audit event logged: {event_type}")
    
    # Workspace operations
    
    def log_workspace_creation(
        self,
        workspace_id: str,
        workspace_name: str,
        product_id: Optional[str] = None,
        environment: Optional[str] = None,
        capacity_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """Log workspace creation event"""
        self._log_event(
            AuditEventType.WORKSPACE_CREATED,
            {
                "workspace_id": workspace_id,
                "workspace_name": workspace_name,
                "product_id": product_id,
                "environment": environment,
                "capacity_id": capacity_id,
                "description": description
            }
        )
    
    def log_workspace_update(
        self,
        workspace_id: str,
        changes: Dict[str, Any]
    ) -> None:
        """Log workspace update event"""
        self._log_event(
            AuditEventType.WORKSPACE_UPDATED,
            {
                "workspace_id": workspace_id,
                "changes": changes
            }
        )
    
    def log_workspace_deletion(
        self,
        workspace_id: str,
        workspace_name: str,
        reason: Optional[str] = None
    ) -> None:
        """Log workspace deletion event"""
        self._log_event(
            AuditEventType.WORKSPACE_DELETED,
            {
                "workspace_id": workspace_id,
                "workspace_name": workspace_name,
                "reason": reason
            }
        )
    
    # Item operations
    
    def log_item_creation(
        self,
        workspace_id: str,
        item_id: str,
        item_name: str,
        item_type: str,
        description: Optional[str] = None,
        validation_passed: bool = True
    ) -> None:
        """Log item creation event"""
        self._log_event(
            AuditEventType.ITEM_CREATED,
            {
                "workspace_id": workspace_id,
                "item_id": item_id,
                "item_name": item_name,
                "item_type": item_type,
                "description": description,
                "validation_passed": validation_passed
            }
        )
    
    def log_item_update(
        self,
        workspace_id: str,
        item_id: str,
        item_name: str,
        changes: Dict[str, Any]
    ) -> None:
        """Log item update event"""
        self._log_event(
            AuditEventType.ITEM_UPDATED,
            {
                "workspace_id": workspace_id,
                "item_id": item_id,
                "item_name": item_name,
                "changes": changes
            }
        )
    
    def log_item_deletion(
        self,
        workspace_id: str,
        item_id: str,
        item_name: str,
        item_type: str
    ) -> None:
        """Log item deletion event"""
        self._log_event(
            AuditEventType.ITEM_DELETED,
            {
                "workspace_id": workspace_id,
                "item_id": item_id,
                "item_name": item_name,
                "item_type": item_type
            }
        )
    
    # Git operations
    
    def log_git_connection(
        self,
        workspace_id: str,
        git_provider: str,
        organization: str,
        repository: str,
        branch: str,
        directory: str
    ) -> None:
        """Log Git connection event"""
        self._log_event(
            AuditEventType.GIT_CONNECTED,
            {
                "workspace_id": workspace_id,
                "git_provider": git_provider,
                "git_organization": organization,
                "git_repository": repository,
                "git_branch": branch,
                "git_directory": directory
            }
        )
    
    def log_git_commit(
        self,
        workspace_id: str,
        commit_message: str,
        items_count: int,
        commit_mode: str = "All"
    ) -> None:
        """Log Git commit event"""
        self._log_event(
            AuditEventType.GIT_COMMITTED,
            {
                "workspace_id": workspace_id,
                "commit_message": commit_message,
                "items_count": items_count,
                "commit_mode": commit_mode
            }
        )
    
    def log_git_update(
        self,
        workspace_id: str,
        conflict_resolution: str,
        items_updated: int
    ) -> None:
        """Log Git update (pull) event"""
        self._log_event(
            AuditEventType.GIT_UPDATED,
            {
                "workspace_id": workspace_id,
                "conflict_resolution": conflict_resolution,
                "items_updated": items_updated
            }
        )
    
    def log_git_disconnection(
        self,
        workspace_id: str,
        reason: Optional[str] = None
    ) -> None:
        """Log Git disconnection event"""
        self._log_event(
            AuditEventType.GIT_DISCONNECTED,
            {
                "workspace_id": workspace_id,
                "reason": reason
            }
        )
    
    # User/permission operations
    
    def log_user_addition(
        self,
        workspace_id: str,
        user_email: str,
        role: str,
        principal_type: str = "User"
    ) -> None:
        """Log user addition event"""
        self._log_event(
            AuditEventType.USER_ADDED,
            {
                "workspace_id": workspace_id,
                "user_email": user_email,
                "role": role,
                "principal_type": principal_type
            }
        )
    
    def log_user_removal(
        self,
        workspace_id: str,
        user_email: str,
        reason: Optional[str] = None
    ) -> None:
        """Log user removal event"""
        self._log_event(
            AuditEventType.USER_REMOVED,
            {
                "workspace_id": workspace_id,
                "user_email": user_email,
                "reason": reason
            }
        )
    
    def log_user_role_change(
        self,
        workspace_id: str,
        user_email: str,
        old_role: str,
        new_role: str
    ) -> None:
        """Log user role change event"""
        self._log_event(
            AuditEventType.USER_ROLE_CHANGED,
            {
                "workspace_id": workspace_id,
                "user_email": user_email,
                "old_role": old_role,
                "new_role": new_role
            }
        )
    
    # Deployment operations
    
    def log_deployment_start(
        self,
        deployment_id: str,
        environment: str,
        product_id: Optional[str] = None,
        triggered_by: Optional[str] = None
    ) -> None:
        """Log deployment start event"""
        self._log_event(
            AuditEventType.DEPLOYMENT_STARTED,
            {
                "deployment_id": deployment_id,
                "environment": environment,
                "product_id": product_id,
                "triggered_by": triggered_by
            }
        )
    
    def log_deployment_completion(
        self,
        deployment_id: str,
        environment: str,
        duration_seconds: Optional[float] = None,
        items_deployed: Optional[int] = None
    ) -> None:
        """Log deployment completion event"""
        self._log_event(
            AuditEventType.DEPLOYMENT_COMPLETED,
            {
                "deployment_id": deployment_id,
                "environment": environment,
                "duration_seconds": duration_seconds,
                "items_deployed": items_deployed
            }
        )
    
    def log_deployment_failure(
        self,
        deployment_id: str,
        environment: str,
        error_message: str,
        duration_seconds: Optional[float] = None
    ) -> None:
        """Log deployment failure event"""
        self._log_event(
            AuditEventType.DEPLOYMENT_FAILED,
            {
                "deployment_id": deployment_id,
                "environment": environment,
                "error_message": error_message,
                "duration_seconds": duration_seconds
            }
        )
    
    # Validation operations
    
    def log_validation_failure(
        self,
        item_name: str,
        item_type: str,
        validation_errors: List[str]
    ) -> None:
        """Log validation failure event"""
        self._log_event(
            AuditEventType.VALIDATION_FAILED,
            {
                "item_name": item_name,
                "item_type": item_type,
                "validation_errors": validation_errors
            }
        )
    
    def log_validation_success(
        self,
        item_name: str,
        item_type: str
    ) -> None:
        """Log validation success event"""
        self._log_event(
            AuditEventType.VALIDATION_PASSED,
            {
                "item_name": item_name,
                "item_type": item_type
            }
        )
    
    # Onboarding operations
    
    def log_onboarding_start(
        self,
        product_id: str,
        product_name: str = None,
        feature_id: Optional[str] = None,
        descriptor_path: Optional[str] = None
    ) -> None:
        """Log onboarding start event"""
        self._log_event(
            AuditEventType.ONBOARDING_STARTED,
            {
                "product_id": product_id,
                "product_name": product_name,
                "feature_id": feature_id,
                "descriptor_path": descriptor_path
            }
        )
    
    # Alias for backward compatibility
    def log_onboarding_started(self, **kwargs):
        """Alias for log_onboarding_start"""
        return self.log_onboarding_start(**kwargs)
    
    def log_onboarding_completion(
        self,
        product_id: str,
        workspace_id: str = None,
        feature_workspace_id: str = None,
        git_branch: str = None,
        items_created: int = None,
        duration_seconds: Optional[float] = None
    ) -> None:
        """Log onboarding completion event"""
        self._log_event(
            AuditEventType.ONBOARDING_COMPLETED,
            {
                "product_id": product_id,
                "workspace_id": workspace_id,
                "feature_workspace_id": feature_workspace_id,
                "git_branch": git_branch,
                "items_created": items_created,
                "duration_seconds": duration_seconds
            }
        )
    
    # Alias for backward compatibility
    def log_onboarding_completed(self, **kwargs):
        """Alias for log_onboarding_completion"""
        return self.log_onboarding_completion(**kwargs)
    
    def log_onboarding_failure(
        self,
        product_id: str,
        error_message: str,
        duration_seconds: Optional[float] = None
    ) -> None:
        """Log onboarding failure event"""
        self._log_event(
            AuditEventType.ONBOARDING_FAILED,
            {
                "product_id": product_id,
                "error_message": error_message,
                "duration_seconds": duration_seconds
            }
        )
    
    # Reporting and analysis
    
    def read_events(
        self,
        event_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Read audit events with optional filtering
        
        Args:
            event_type: Filter by event type
            start_date: Filter events after this date (ISO format)
            end_date: Filter events before this date (ISO format)
            workspace_id: Filter by workspace ID
        
        Returns:
            List of matching audit events
        """
        if not self.audit_file.exists():
            return []
        
        events = []
        
        with open(self.audit_file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    
                    # Apply filters
                    if event_type and event.get('event_type') != event_type:
                        continue
                    
                    if start_date and event.get('timestamp', '') < start_date:
                        continue
                    
                    if end_date and event.get('timestamp', '') > end_date:
                        continue
                    
                    if workspace_id and event.get('workspace_id') != workspace_id:
                        continue
                    
                    events.append(event)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Skipping invalid JSON line in audit log")
                    continue
        
        return events
    
    def generate_compliance_report(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Generate compliance report for date range
        
        Args:
            start_date: Start date (ISO format: YYYY-MM-DD)
            end_date: End date (ISO format: YYYY-MM-DD)
        
        Returns:
            Compliance report with statistics and event summaries
        """
        events = self.read_events(start_date=start_date, end_date=end_date)
        
        # Count events by type
        event_counts = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Count workspaces created
        workspaces_created = sum(
            1 for e in events 
            if e.get('event_type') == AuditEventType.WORKSPACE_CREATED
        )
        
        # Count items created
        items_created = sum(
            1 for e in events 
            if e.get('event_type') == AuditEventType.ITEM_CREATED
        )
        
        # Count Git operations
        git_connections = sum(
            1 for e in events 
            if e.get('event_type') == AuditEventType.GIT_CONNECTED
        )
        
        # Count validation failures
        validation_failures = sum(
            1 for e in events 
            if e.get('event_type') == AuditEventType.VALIDATION_FAILED
        )
        
        return {
            "report_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_events": len(events),
                "workspaces_created": workspaces_created,
                "items_created": items_created,
                "git_connections": git_connections,
                "validation_failures": validation_failures
            },
            "event_counts_by_type": event_counts,
            "events": events[:100]  # Include first 100 events
        }


# Global singleton instance
_global_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create global audit logger instance"""
    global _global_audit_logger
    
    if _global_audit_logger is None:
        _global_audit_logger = AuditLogger()
    
    return _global_audit_logger
