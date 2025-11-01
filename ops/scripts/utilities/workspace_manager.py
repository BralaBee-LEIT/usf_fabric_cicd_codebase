"""
Microsoft Fabric Workspace Management Module
Supports workspace and user management across dev, test, and prod environments

FRAMEWORK REQUIREMENTS:
- project.config.json: Organization naming standards (MANDATORY)
- .env: Azure credentials (MANDATORY)
- naming_standards.yaml: Naming validation rules (MANDATORY)
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List
from enum import Enum
import requests
from msal import ConfidentialClientApplication

from .constants import (
    FABRIC_API_BASE_URL,
    FABRIC_API_SCOPE,
    get_azure_authority_url,
    ERROR_MISSING_CREDENTIALS,
    ERROR_AUTHENTICATION_FAILED,
    HTTP_DEFAULT_TIMEOUT,
    VALID_ENVIRONMENTS,
)
from .config_manager import get_config_manager
from .framework_validator import FrameworkValidator

# Optional: Import audit logger
try:
    from .audit_logger import get_audit_logger

    AUDIT_LOGGER_AVAILABLE = True
except ImportError:
    AUDIT_LOGGER_AVAILABLE = False

# Optional: Import folder manager
try:
    from .fabric_folder_manager import FabricFolderManager, FolderOperationError

    FOLDER_MANAGER_AVAILABLE = True
except ImportError:
    FOLDER_MANAGER_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkspaceRole(str, Enum):
    """Fabric workspace role definitions"""

    ADMIN = "Admin"
    MEMBER = "Member"
    CONTRIBUTOR = "Contributor"
    VIEWER = "Viewer"


class CapacityType(str, Enum):
    """Fabric capacity types"""

    TRIAL = "Trial"
    PREMIUM_P1 = "Premium_P1"
    PREMIUM_P2 = "Premium_P2"
    PREMIUM_P3 = "Premium_P3"
    FABRIC_F2 = "Fabric_F2"
    FABRIC_F4 = "Fabric_F4"
    FABRIC_F8 = "Fabric_F8"
    FABRIC_F16 = "Fabric_F16"
    FABRIC_F32 = "Fabric_F32"
    FABRIC_F64 = "Fabric_F64"


class WorkspaceManager:
    """
    Comprehensive workspace management for Microsoft Fabric
    Supports multi-environment operations (dev, test, prod)
    """

    def __init__(
        self, environment: Optional[str] = None, enable_audit_logging: bool = True,
        skip_framework_validation: bool = False
    ):
        """
        Initialize workspace manager

        Args:
            environment: Target environment (dev, test, prod). If None, no environment suffix is applied.
            enable_audit_logging: Whether to enable audit logging (default: True)
            skip_framework_validation: Skip framework prerequisites validation (NOT RECOMMENDED)
        """
        # ENFORCE FRAMEWORK PREREQUISITES
        if not skip_framework_validation:
            validator = FrameworkValidator(strict_mode=True)
            validator.validate_or_exit("workspace operations")
        
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.base_url = FABRIC_API_BASE_URL
        self.token = None
        self.environment = environment.lower() if environment else None
        self.max_retries = int(os.getenv("FABRIC_API_MAX_RETRIES", "3"))

        # Initialize audit logger if available and enabled
        self.audit_logger = None
        if enable_audit_logging and AUDIT_LOGGER_AVAILABLE:
            self.audit_logger = get_audit_logger()

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError(ERROR_MISSING_CREDENTIALS)

        # Validate environment if provided
        if self.environment and self.environment not in VALID_ENVIRONMENTS:
            raise ValueError(
                f"Invalid environment '{self.environment}'. "
                f"Valid environments: {', '.join(VALID_ENVIRONMENTS)}"
            )

        # Load config manager for environment-aware naming
        self.config_manager = get_config_manager()

        # Initialize folder manager if available
        self.folder_manager = None
        if FOLDER_MANAGER_AVAILABLE:
            self.folder_manager = FabricFolderManager()

        logger.info(
            f"WorkspaceManager initialized for environment: {self.environment or 'all'}"
        )

    def _get_access_token(self) -> str:
        """Get Azure AD access token for Fabric API"""
        if self.token:
            return self.token

        app = ConfidentialClientApplication(
            self.client_id,
            authority=get_azure_authority_url(self.tenant_id),
            client_credential=self.client_secret,
        )

        result = app.acquire_token_for_client(scopes=[FABRIC_API_SCOPE])

        if "access_token" in result:
            self.token = result["access_token"]
            logger.debug("Successfully acquired access token")
            return self.token
        else:
            error_desc = result.get("error_description", "Unknown error")
            raise Exception(ERROR_AUTHENTICATION_FAILED.format(error_desc))

    def _make_request(
        self, method: str, endpoint: str, retry_count: int = None, **kwargs
    ) -> requests.Response:
        """
        Make authenticated request to Fabric API with retry logic

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint
            retry_count: Number of retries for transient failures (defaults to FABRIC_API_MAX_RETRIES env var or 3)
            **kwargs: Additional request parameters

        Returns:
            Response object
        """
        if retry_count is None:
            retry_count = self.max_retries

        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self._get_access_token()}"
        headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers

        # Add default timeout if not specified
        if "timeout" not in kwargs:
            kwargs["timeout"] = HTTP_DEFAULT_TIMEOUT

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(retry_count):
            try:
                response = requests.request(method, url, **kwargs)

                # Handle rate limiting (429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(
                        f"Rate limited. Retrying after {retry_after} seconds..."
                    )
                    time.sleep(retry_after)
                    continue

                # Handle transient errors (500-503)
                if (
                    response.status_code in [500, 502, 503]
                    and attempt < retry_count - 1
                ):
                    wait_time = 2**attempt  # Exponential backoff
                    logger.warning(
                        f"Transient error {response.status_code}. Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue

                if not response.ok:
                    logger.error(
                        f"Fabric API error: {response.status_code} - {response.text}"
                    )
                    response.raise_for_status()

                return response

            except requests.exceptions.RequestException as e:
                if attempt < retry_count - 1:
                    wait_time = 2**attempt
                    logger.warning(f"Request failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

        raise Exception(f"Failed to complete request after {retry_count} attempts")

    def _generate_workspace_name(self, base_name: str) -> str:
        """
        Generate environment-aware workspace name

        Args:
            base_name: Base workspace name

        Returns:
            Environment-specific workspace name
        
        Note:
            If base_name already contains the prefix or environment suffix,
            it will be returned as-is to avoid double-prefixing like:
            "usf2-fabric-usf2-fabric-Sales-dev-dev"
        """
        if not self.environment:
            return base_name

        # Check if name already follows the naming pattern (has prefix and/or environment)
        # to avoid double-prefixing
        if self.config_manager:
            prefix = self.config_manager.config.get("project", {}).get("prefix", "")
            
            # If name already starts with prefix AND ends with environment, return as-is
            if prefix and base_name.startswith(prefix) and base_name.endswith(f"-{self.environment}"):
                logger.info(f"Name '{base_name}' already formatted - using as-is")
                return base_name
            
            # If name already starts with prefix, only add environment suffix
            if prefix and base_name.startswith(prefix):
                # Check if it already ends with the environment
                if base_name.endswith(f"-{self.environment}"):
                    return base_name
                return f"{base_name}-{self.environment}"
            
            # Generate full name from pattern
            return self.config_manager.generate_name(
                "workspace", self.environment, name=base_name
            )

        # Fallback: check for duplicate environment suffix
        if base_name.endswith(f"-{self.environment}"):
            return base_name
        
        return f"{base_name}-{self.environment}"

    # ==================== WORKSPACE OPERATIONS ====================

    def create_workspace(
        self,
        name: str,
        description: Optional[str] = None,
        capacity_id: Optional[str] = None,
        capacity_type: CapacityType = CapacityType.TRIAL,
    ) -> Dict[str, Any]:
        """
        Create a new Fabric workspace

        Args:
            name: Workspace name (will be suffixed with environment if configured)
            description: Workspace description
            capacity_id: Optional capacity ID (for Premium/Fabric capacities)
            capacity_type: Capacity type (default: Trial)

        Returns:
            Created workspace details
        """
        workspace_name = self._generate_workspace_name(name)

        payload = {
            "displayName": workspace_name,
            "description": description
            or f"Workspace for {self.environment or 'general'} environment",
        }

        # Add capacity if specified
        if capacity_id:
            payload["capacityId"] = capacity_id
        elif capacity_type != CapacityType.TRIAL:
            logger.warning(
                f"Capacity type {capacity_type} specified but no capacity_id provided. "
                "Workspace will use Trial capacity."
            )

        try:
            response = self._make_request("POST", "workspaces", json=payload)
            workspace = response.json()
            logger.info(
                f"✓ Created workspace: {workspace_name} (ID: {workspace.get('id')})"
            )

            # Log workspace creation to audit trail
            if self.audit_logger:
                self.audit_logger.log_workspace_creation(
                    workspace_id=workspace.get("id"),
                    workspace_name=workspace_name,
                    capacity_id=capacity_id,
                    description=description
                    or f"Workspace for {self.environment or 'general'} environment",
                )

            return workspace

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                logger.error(f"✗ Workspace '{workspace_name}' already exists")
                raise ValueError(f"Workspace '{workspace_name}' already exists")
            raise

    def create_workspace_with_structure(
        self,
        name: str,
        folder_structure: Optional[Dict[str, Any]] = None,
        use_medallion_architecture: bool = False,
        description: Optional[str] = None,
        capacity_id: Optional[str] = None,
        capacity_type: CapacityType = CapacityType.TRIAL,
    ) -> Dict[str, Any]:
        """
        Create a new Fabric workspace with folder structure

        Args:
            name: Workspace name (will be suffixed with environment if configured)
            folder_structure: Custom folder structure (dict with folder names and subfolders)
            use_medallion_architecture: Use Bronze/Silver/Gold medallion architecture (default: False)
            description: Workspace description
            capacity_id: Optional capacity ID (for Premium/Fabric capacities)
            capacity_type: Capacity type (default: Trial)

        Returns:
            Dict containing workspace details and folder IDs

        Example:
            # Create with medallion architecture
            result = manager.create_workspace_with_structure(
                name="Data Platform",
                use_medallion_architecture=True
            )

            # Create with custom structure
            result = manager.create_workspace_with_structure(
                name="Analytics",
                folder_structure={
                    "Reports": {"subfolders": ["Sales", "Finance"]},
                    "Dashboards": {},
                    "Data": {"subfolders": ["Raw", "Processed"]}
                }
            )
        """
        if not self.folder_manager:
            raise RuntimeError(
                "Folder manager not available. Install fabric_folder_manager module."
            )

        # Create workspace first
        workspace = self.create_workspace(
            name=name,
            description=description,
            capacity_id=capacity_id,
            capacity_type=capacity_type,
        )

        workspace_id = workspace.get("id")
        workspace_name = workspace.get("displayName")

        # Determine folder structure to create
        structure = None
        if use_medallion_architecture:
            logger.info(f"Creating medallion architecture folders in {workspace_name}...")
            structure = {
                "Bronze Layer": {
                    "subfolders": ["Raw Data", "Archive", "External Sources"]
                },
                "Silver Layer": {
                    "subfolders": ["Cleaned", "Transformed", "Validated"]
                },
                "Gold Layer": {
                    "subfolders": ["Analytics", "Reports", "Business Metrics"]
                },
            }
        elif folder_structure:
            logger.info(f"Creating custom folder structure in {workspace_name}...")
            structure = folder_structure

        # Create folders if structure specified
        folder_ids = {}
        if structure:
            try:
                folder_ids = self.folder_manager.create_folder_structure(
                    workspace_id, structure
                )
                logger.info(
                    f"✓ Created {len(folder_ids)} folder(s) in workspace {workspace_name}"
                )

                # Show folder tree
                logger.info(f"\nFolder structure for {workspace_name}:")
                self.folder_manager.print_folder_tree(workspace_id)

            except FolderOperationError as e:
                logger.warning(
                    f"⚠ Workspace created but folder creation failed: {e}"
                )
                # Don't fail the whole operation if folders fail
                # Workspace is still created

        return {
            "workspace": workspace,
            "folder_ids": folder_ids,
            "workspace_id": workspace_id,
            "workspace_name": workspace_name,
        }

    def add_folder_structure(
        self,
        workspace_id: str,
        folder_structure: Optional[Dict[str, Any]] = None,
        use_medallion_architecture: bool = False,
    ) -> Dict[str, str]:
        """
        Add folder structure to an existing workspace

        Args:
            workspace_id: Target workspace ID
            folder_structure: Custom folder structure
            use_medallion_architecture: Use Bronze/Silver/Gold medallion architecture

        Returns:
            Dict mapping folder names to folder IDs

        Example:
            # Add medallion architecture to existing workspace
            folder_ids = manager.add_folder_structure(
                workspace_id="abc123",
                use_medallion_architecture=True
            )
        """
        if not self.folder_manager:
            raise RuntimeError(
                "Folder manager not available. Install fabric_folder_manager module."
            )

        workspace = self.get_workspace_details(workspace_id)
        workspace_name = workspace.get("displayName", workspace_id)

        # Determine folder structure
        structure = None
        if use_medallion_architecture:
            logger.info(f"Adding medallion architecture to {workspace_name}...")
            structure = {
                "Bronze Layer": {
                    "subfolders": ["Raw Data", "Archive", "External Sources"]
                },
                "Silver Layer": {
                    "subfolders": ["Cleaned", "Transformed", "Validated"]
                },
                "Gold Layer": {
                    "subfolders": ["Analytics", "Reports", "Business Metrics"]
                },
            }
        elif folder_structure:
            logger.info(f"Adding custom folders to {workspace_name}...")
            structure = folder_structure
        else:
            raise ValueError("Must specify either folder_structure or use_medallion_architecture=True")

        # Create folders
        folder_ids = self.folder_manager.create_folder_structure(workspace_id, structure)
        logger.info(f"✓ Created {len(folder_ids)} folder(s) in {workspace_name}")

        # Show folder tree
        logger.info(f"\nFolder structure for {workspace_name}:")
        self.folder_manager.print_folder_tree(workspace_id)

        return folder_ids

    def delete_workspace(self, workspace_id: str, force: bool = False) -> bool:
        """
        Delete a Fabric workspace

        Args:
            workspace_id: Workspace ID to delete
            force: Force deletion even if workspace contains items

        Returns:
            True if successful
        """
        # Get workspace details first
        workspace = self.get_workspace_details(workspace_id)
        workspace_name = workspace.get("displayName", workspace_id)

        # Check if workspace has items (unless force=True)
        if not force:
            items = self.list_workspace_items(workspace_id)
            if items:
                raise ValueError(
                    f"Workspace '{workspace_name}' contains {len(items)} items. "
                    "Use force=True to delete anyway."
                )

        try:
            self._make_request("DELETE", f"workspaces/{workspace_id}")
            logger.info(f"✓ Deleted workspace: {workspace_name} (ID: {workspace_id})")

            # Log workspace deletion to audit trail
            if self.audit_logger:
                self.audit_logger.log_workspace_deleted(
                    workspace_id=workspace_id, workspace_name=workspace_name
                )

            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Workspace {workspace_id} not found")
                return False
            raise

    def list_workspaces(
        self, filter_by_environment: bool = True, include_details: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List all accessible workspaces

        Args:
            filter_by_environment: Only show workspaces for current environment
            include_details: Include detailed information for each workspace

        Returns:
            List of workspace objects
        """
        response = self._make_request("GET", "workspaces")
        workspaces = response.json().get("value", [])

        # Filter by environment if configured
        if filter_by_environment and self.environment:
            env_suffix = f"-{self.environment}"
            workspaces = [
                ws
                for ws in workspaces
                if ws.get("displayName", "").endswith(env_suffix)
            ]

        # Add detailed info if requested
        if include_details:
            for workspace in workspaces:
                try:
                    details = self.get_workspace_details(workspace["id"])
                    workspace.update(details)
                except Exception as e:
                    logger.warning(
                        f"Could not fetch details for workspace {workspace['id']}: {e}"
                    )

        logger.info(f"Found {len(workspaces)} workspaces")
        return workspaces

    def get_workspace_details(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace details
        """
        response = self._make_request("GET", f"workspaces/{workspace_id}")
        return response.json()

    def get_workspace_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find workspace by name

        Args:
            name: Workspace name (without environment suffix)

        Returns:
            Workspace details or None if not found
        """
        workspace_name = self._generate_workspace_name(name)
        workspaces = self.list_workspaces(filter_by_environment=False)

        for workspace in workspaces:
            if workspace.get("displayName") == workspace_name:
                return workspace

        return None

    def update_workspace(
        self,
        workspace_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update workspace properties

        Args:
            workspace_id: Workspace ID
            name: New workspace name (optional)
            description: New description (optional)

        Returns:
            Updated workspace details
        """
        payload = {}

        if name:
            payload["displayName"] = self._generate_workspace_name(name)

        if description:
            payload["description"] = description

        if not payload:
            raise ValueError(
                "At least one property (name or description) must be provided"
            )

        response = self._make_request(
            "PATCH", f"workspaces/{workspace_id}", json=payload
        )
        logger.info(f"✓ Updated workspace {workspace_id}")
        return response.json()

    def assign_capacity(self, workspace_id: str, capacity_id: str) -> Dict[str, Any]:
        """
        Assign a Fabric capacity to an existing workspace

        Args:
            workspace_id: Workspace ID
            capacity_id: Capacity ID (GUID) to assign to the workspace

        Returns:
            Updated workspace details

        Example:
            >>> manager = WorkspaceManager()
            >>> manager.assign_capacity(
            ...     workspace_id="06ca81b0-8135-4c89-90b4-b6a9a3bd1879",
            ...     capacity_id="your-capacity-guid"
            ... )
        """
        # First verify the workspace exists
        workspace = self.get_workspace_details(workspace_id)
        workspace_name = workspace.get("displayName", workspace_id)

        # Assign capacity using PATCH with capacityId
        payload = {"capacityId": capacity_id}

        try:
            response = self._make_request(
                "PATCH", f"workspaces/{workspace_id}", json=payload
            )
            logger.info(
                f"✓ Assigned capacity {capacity_id} to workspace '{workspace_name}' ({workspace_id})"
            )
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = f"Failed to assign capacity to workspace '{workspace_name}': {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def unassign_capacity(self, workspace_id: str) -> Dict[str, Any]:
        """
        Remove capacity assignment from a workspace (revert to Trial/Shared)

        Args:
            workspace_id: Workspace ID

        Returns:
            Updated workspace details
        """
        workspace = self.get_workspace_details(workspace_id)
        workspace_name = workspace.get("displayName", workspace_id)

        # Unassign by setting capacityId to None/empty
        payload = {"capacityId": None}

        try:
            response = self._make_request(
                "PATCH", f"workspaces/{workspace_id}", json=payload
            )
            logger.info(
                f"✓ Removed capacity assignment from workspace '{workspace_name}' ({workspace_id})"
            )
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = f"Failed to unassign capacity from workspace '{workspace_name}': {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def list_workspace_items(
        self, workspace_id: str, item_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List items in a workspace

        Args:
            workspace_id: Workspace ID
            item_type: Filter by item type (Notebook, Pipeline, Lakehouse, etc.)

        Returns:
            List of workspace items
        """
        endpoint = f"workspaces/{workspace_id}/items"
        if item_type:
            endpoint += f"?type={item_type}"

        response = self._make_request("GET", endpoint)
        items = response.json().get("value", [])
        logger.debug(f"Found {len(items)} items in workspace {workspace_id}")
        return items

    # ==================== USER MANAGEMENT OPERATIONS ====================

    def add_user(
        self,
        workspace_id: str,
        principal_id: str,
        principal_type: str = "User",
        role: WorkspaceRole = WorkspaceRole.VIEWER,
    ) -> Dict[str, Any]:
        """
        Add a user or service principal to a workspace

        Args:
            workspace_id: Workspace ID
            principal_id: User email or service principal ID
            principal_type: "User", "Group", or "ServicePrincipal"
            role: Workspace role (Admin, Member, Contributor, Viewer)

        Returns:
            Added user details
        """
        payload = {
            "principal": {"id": principal_id, "type": principal_type},
            "role": role.value,
        }

        try:
            response = self._make_request(
                "POST", f"workspaces/{workspace_id}/roleAssignments", json=payload
            )
            logger.info(
                f"✓ Added {principal_type} '{principal_id}' to workspace {workspace_id} "
                f"with role '{role.value}'"
            )

            # Log user addition to audit trail
            if self.audit_logger:
                self.audit_logger.log_user_addition(
                    workspace_id=workspace_id,
                    user_email=principal_id if principal_type == "User" else None,
                    user_id=principal_id if principal_type != "User" else None,
                    role=role.value,
                    principal_type=principal_type,
                )

            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 409:
                logger.warning(f"User '{principal_id}' already has access to workspace")
                raise ValueError(
                    f"User '{principal_id}' already has access to workspace"
                )
            raise

    def remove_user(self, workspace_id: str, principal_id: str) -> bool:
        """
        Remove a user from a workspace

        Args:
            workspace_id: Workspace ID
            principal_id: User email or service principal ID

        Returns:
            True if successful
        """
        try:
            self._make_request(
                "DELETE", f"workspaces/{workspace_id}/roleAssignments/{principal_id}"
            )
            logger.info(
                f"✓ Removed user '{principal_id}' from workspace {workspace_id}"
            )

            # Log user removal to audit trail
            if self.audit_logger:
                self.audit_logger.log_user_removal(
                    workspace_id=workspace_id, user_email=principal_id
                )

            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(
                    f"User '{principal_id}' not found in workspace {workspace_id}"
                )
                return False
            raise

    def list_users(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        List all users in a workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            List of users with their roles
        """
        response = self._make_request(
            "GET", f"workspaces/{workspace_id}/roleAssignments"
        )
        users = response.json().get("value", [])
        logger.info(f"Found {len(users)} users in workspace {workspace_id}")
        return users

    def update_user_role(
        self, workspace_id: str, principal_id: str, new_role: WorkspaceRole
    ) -> Dict[str, Any]:
        """
        Update a user's role in a workspace

        Args:
            workspace_id: Workspace ID
            principal_id: User email or service principal ID
            new_role: New workspace role

        Returns:
            Updated user details
        """
        payload = {"workspaceRole": new_role.value}

        response = self._make_request(
            "PATCH",
            f"workspaces/{workspace_id}/roleAssignments/{principal_id}",
            json=payload,
        )
        logger.info(
            f"✓ Updated user '{principal_id}' role to '{new_role.value}' "
            f"in workspace {workspace_id}"
        )
        return response.json()

    # ==================== BULK OPERATIONS ====================

    def create_workspace_set(
        self,
        base_name: str,
        environments: List[str] = None,
        description_template: str = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Create workspaces for multiple environments (dev, test, prod)

        Args:
            base_name: Base workspace name
            environments: List of environments (default: ['dev', 'test', 'prod'])
            description_template: Description template (can use {env} placeholder)

        Returns:
            Dictionary mapping environment to workspace details
        """
        if environments is None:
            environments = ["dev", "test", "prod"]

        if description_template is None:
            description_template = f"{base_name} - {{env}} environment"

        results = {}

        for env in environments:
            # Temporarily set environment
            original_env = self.environment
            self.environment = env

            try:
                description = description_template.format(env=env.upper())
                workspace = self.create_workspace(base_name, description=description)
                results[env] = workspace
                logger.info(
                    f"✓ Created {env} workspace: {workspace.get('displayName')}"
                )

            except Exception as e:
                logger.error(f"✗ Failed to create {env} workspace: {e}")
                results[env] = {"error": str(e)}

            finally:
                # Restore original environment
                self.environment = original_env

        return results

    def copy_users_between_workspaces(
        self,
        source_workspace_id: str,
        target_workspace_id: str,
        role_mapping: Optional[Dict[str, WorkspaceRole]] = None,
    ) -> Dict[str, Any]:
        """
        Copy users from one workspace to another

        Args:
            source_workspace_id: Source workspace ID
            target_workspace_id: Target workspace ID
            role_mapping: Optional role mapping (e.g., downgrade roles in test)

        Returns:
            Summary of copied users
        """
        source_users = self.list_users(source_workspace_id)

        results = {"success": [], "failed": [], "skipped": []}

        for user in source_users:
            principal_id = user.get("identifier")
            principal_type = user.get("principalType")
            current_role = WorkspaceRole(user.get("workspaceRole"))

            # Apply role mapping if provided
            target_role = (
                role_mapping.get(principal_id, current_role)
                if role_mapping
                else current_role
            )

            try:
                self.add_user(
                    target_workspace_id, principal_id, principal_type, target_role
                )
                results["success"].append(
                    {"principal_id": principal_id, "role": target_role.value}
                )

            except ValueError as e:
                # User already exists
                results["skipped"].append(
                    {"principal_id": principal_id, "reason": str(e)}
                )

            except Exception as e:
                results["failed"].append(
                    {"principal_id": principal_id, "error": str(e)}
                )

        logger.info(
            f"User copy complete: {len(results['success'])} succeeded, "
            f"{len(results['skipped'])} skipped, {len(results['failed'])} failed"
        )

        return results


# Convenience functions for common operations
def create_workspace_for_environment(
    workspace_name: str, environment: str, description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to create an environment-specific workspace

    Args:
        workspace_name: Base workspace name
        environment: Environment (dev, test, prod)
        description: Optional description

    Returns:
        Created workspace details
    """
    manager = WorkspaceManager(environment=environment)
    return manager.create_workspace(workspace_name, description=description)


def setup_complete_environment(
    project_name: str,
    admin_emails: List[str],
    member_emails: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Set up complete workspace environment (dev, test, prod) with users

    Args:
        project_name: Project name
        admin_emails: List of admin user emails
        member_emails: Optional list of member user emails

    Returns:
        Summary of created workspaces and assigned users
    """
    manager = WorkspaceManager()

    # Create workspaces for all environments
    workspaces = manager.create_workspace_set(project_name)

    # Add users to each workspace
    for env, workspace in workspaces.items():
        if "error" in workspace:
            continue

        workspace_id = workspace["id"]

        # Add admins
        for email in admin_emails:
            try:
                manager.add_user(workspace_id, email, role=WorkspaceRole.ADMIN)
            except Exception as e:
                logger.warning(f"Failed to add admin {email} to {env}: {e}")

        # Add members
        if member_emails:
            for email in member_emails:
                try:
                    manager.add_user(workspace_id, email, role=WorkspaceRole.MEMBER)
                except Exception as e:
                    logger.warning(f"Failed to add member {email} to {env}: {e}")

    return workspaces
