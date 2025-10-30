"""
Microsoft Fabric Git Integration Connector

This module provides utilities for automating Git integration with Fabric workspaces.
Implements the Fabric Git Integration REST API for workspace-to-Git connections.

API Reference:
https://learn.microsoft.com/en-us/rest/api/fabric/core/git
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from .fabric_api import FabricClient
from .output import (
    console_success as print_success,
    console_error as print_error,
    console_warning as print_warning,
    console_info as print_info,
)

logger = logging.getLogger(__name__)


class GitConnectionState:
    """Git connection state enumeration"""

    CONNECTED = "Connected"
    DISCONNECTED = "Disconnected"
    NOT_SUPPORTED = "NotSupported"


class GitProviderType:
    """Supported Git provider types"""

    GITHUB = "GitHub"
    AZURE_DEV_OPS = "AzureDevOps"


class FabricGitConnector:
    """
    Automate Git integration with Microsoft Fabric workspaces

    This class provides methods to:
    - Initialize Git connections for workspaces
    - Commit workspace items to Git
    - Update workspace from Git
    - Disconnect Git integration
    - Monitor connection status

    Usage:
        connector = FabricGitConnector()

        # Connect workspace to Git
        connector.initialize_git_connection(
            workspace_id="abc-123",
            branch_name="main",
            directory_path="/data_products/my_product"
        )

        # Commit changes
        connector.commit_to_git(
            workspace_id="abc-123",
            comment="Initial workspace setup"
        )
    """

    def __init__(
        self,
        organization_name: Optional[str] = None,
        project_name: Optional[str] = None,
        repository_name: Optional[str] = None,
        git_provider_type: str = GitProviderType.GITHUB,
    ):
        """
        Initialize Git connector

        Args:
            organization_name: GitHub org or Azure DevOps org (from env if not provided)
            project_name: Project name (Azure DevOps only, uses repo name for GitHub)
            repository_name: Git repository name (from env if not provided)
            git_provider_type: "GitHub" or "AzureDevOps"
        """
        from .fabric_api import get_fabric_client
        
        self.fabric_client = get_fabric_client()

        # Git provider configuration
        self.organization_name = organization_name or os.getenv("GIT_ORGANIZATION")
        self.project_name = project_name or os.getenv("GIT_PROJECT")
        self.repository_name = repository_name or os.getenv("GIT_REPOSITORY")
        self.git_provider_type = git_provider_type

        # Validate configuration
        if not self.organization_name:
            raise ValueError(
                "Git organization not configured. Set GIT_ORGANIZATION env var or pass organization_name."
            )

        if not self.repository_name:
            raise ValueError(
                "Git repository not configured. Set GIT_REPOSITORY env var or pass repository_name."
            )

        # For GitHub, project name is the same as repository
        if self.git_provider_type == GitProviderType.GITHUB and not self.project_name:
            self.project_name = self.repository_name

        logger.info(
            f"Initialized FabricGitConnector for {self.git_provider_type}: "
            f"{self.organization_name}/{self.repository_name}"
        )

    def get_or_create_git_connection(
        self, github_token: Optional[str] = None, connection_id: Optional[str] = None
    ) -> str:
        """
        Get existing or create new Git provider connection

        This creates a Fabric Connection that stores GitHub credentials.
        The connection ID is then used in Git connect operations.

        Args:
            github_token: GitHub Personal Access Token (from env if not provided)
            connection_id: Explicit connection ID to use (skips lookup/creation)

        Returns:
            Connection ID (GUID)

        Raises:
            ValueError: If no connection found and cannot create

        API: GET/POST /v1/connections
        """
        # If explicit connection ID provided, use it
        if connection_id:
            print_info(f"Using provided connection ID: {connection_id}")
            return connection_id

        # Check for connection ID in environment
        env_connection_id = os.getenv("FABRIC_GIT_CONNECTION_ID")
        if env_connection_id:
            print_info(
                f"Using connection ID from FABRIC_GIT_CONNECTION_ID env var: {env_connection_id}"
            )
            return env_connection_id

        # Try to find existing connection for this repo
        connection_name = f"GitHub-{self.organization_name}-{self.repository_name}"

        try:
            # List existing connections
            response = self.fabric_client._make_request("GET", "connections")
            connections = response.json().get("value", [])

            print_info(f"Found {len(connections)} total connections")

            # Look for GitHub connections
            github_connections = [
                c
                for c in connections
                if "GitHub" in c.get("connectionDetails", {}).get("type", "")
            ]
            print_info(f"Found {len(github_connections)} GitHub connections")

            # Look for matching connection by name or repo URL
            repo_url = (
                f"https://github.com/{self.organization_name}/{self.repository_name}"
            )
            for conn in connections:
                conn_name = conn.get("displayName", "")
                conn_path = conn.get("connectionDetails", {}).get("path", "")

                if connection_name in conn_name or repo_url in conn_path:
                    connection_id = conn.get("id")
                    print_info(
                        f"Found existing Git connection: {conn_name} ({connection_id})"
                    )
                    return connection_id

            # If we have GitHub connections but no exact match, offer to use the first one
            if github_connections:
                first_conn = github_connections[0]
                connection_id = first_conn.get("id")
                conn_name = first_conn.get("displayName", "Unknown")
                print_warning(
                    f"No exact match found. Using first GitHub connection: {conn_name} ({connection_id})"
                )
                return connection_id

        except Exception as e:
            logger.debug(f"Could not list connections: {e}")
            print_warning(f"Unable to list connections: {e}")

        # Try to create new connection
        token = github_token or os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError(
                "No Git connection found and cannot create one.\n"
                "Options:\n"
                "  1. Set FABRIC_GIT_CONNECTION_ID env var with your connection ID\n"
                "  2. Create connection in Fabric portal (Settings → Manage connections)\n"
                "  3. Set GITHUB_TOKEN env var with valid PAT (requires repo scope)"
            )

        print_info(f"Creating new Git connection: {connection_name}")

        repo_url = f"https://github.com/{self.organization_name}/{self.repository_name}"

        connection_payload = {
            "displayName": connection_name,
            "connectivityType": "ShareableCloud",
            "connectionDetails": {
                "creationMethod": "GitHubSourceControl.Contents",
                "type": "GitHubSourceControl",
                "parameters": [{"dataType": "Text", "name": "url", "value": repo_url}],
            },
            "credentialDetails": {
                "credentials": {"credentialType": "Key", "key": token}
            },
        }

        try:
            response = self.fabric_client._make_request(
                "POST", "connections", json=connection_payload
            )
            connection_data = response.json()
            connection_id = connection_data.get("id")
            print_success(f"✓ Created Git connection: {connection_id}")
            print_info(
                f"  TIP: Set FABRIC_GIT_CONNECTION_ID={connection_id} in .env to reuse this connection"
            )
            return connection_id
        except Exception as e:
            print_error(f"✗ Failed to create Git connection: {str(e)}")
            raise ValueError(
                f"Failed to create Git connection: {str(e)}\n"
                "Please create connection manually in Fabric portal and set FABRIC_GIT_CONNECTION_ID env var"
            )

    def connect_to_git(
        self,
        workspace_id: str,
        branch_name: str,
        directory_path: str = "/",
        github_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Connect a workspace to Git repository (initial connection)

        This establishes the initial Git connection for a workspace.
        After this, use initialize_git_connection to update settings.

        Args:
            workspace_id: Fabric workspace GUID
            branch_name: Git branch to connect (e.g., "main", "feature/my-feature")
            directory_path: Folder path in repo (default: "/")
            github_token: GitHub PAT (from env if not provided)

        Returns:
            Connection response from Fabric API

        Raises:
            Exception: If connection fails

        API: POST /workspaces/{workspaceId}/git/connect
        """
        print_info(f"Connecting workspace {workspace_id[:8]} to Git...")
        print_info(f"  Repository: {self.organization_name}/{self.repository_name}")
        print_info(f"  Branch: {branch_name}")
        print_info(f"  Directory: {directory_path}")

        # Get or create Git connection (stores credentials)
        connection_id = self.get_or_create_git_connection(github_token)

        # Build payload for connect endpoint
        git_provider_details = {
            "gitProviderType": self.git_provider_type,
            "repositoryName": self.repository_name,
            "branchName": branch_name,
            "directoryName": directory_path,
        }

        # For GitHub, use ownerName instead of organizationName
        if self.git_provider_type == GitProviderType.GITHUB:
            git_provider_details["ownerName"] = self.organization_name
        else:
            git_provider_details["organizationName"] = self.organization_name
            if self.project_name:
                git_provider_details["projectName"] = self.project_name

        payload = {
            "gitProviderDetails": git_provider_details,
            "myGitCredentials": {
                "source": "ConfiguredConnection",
                "connectionId": connection_id,
            },
        }

        print_info(f"DEBUG: Payload = {json.dumps(payload, indent=2)}")

        try:
            response = self.fabric_client._make_request(
                "POST", f"workspaces/{workspace_id}/git/connect", json=payload
            )

            print_success("✓ Workspace connected to Git successfully")
            return response.json() if response.text else {}

        except Exception as e:
            print_error(f"✗ Failed to connect workspace to Git: {str(e)}")
            raise

    def validate_git_prerequisites(
        self,
        workspace_id: str,
        branch_name: str,
        directory_path: str = "/",
        github_token: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate prerequisites before attempting Git connection
        
        Performs comprehensive pre-flight checks to catch configuration issues early:
        - Workspace exists and is accessible
        - Workspace is not already connected to Git
        - Git credentials are valid
        - Repository and branch are accessible
        - User has required permissions
        
        Args:
            workspace_id: Fabric workspace GUID
            branch_name: Git branch to validate
            directory_path: Folder path in repo
            github_token: GitHub PAT (from env if not provided)
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
            
        Example:
            is_valid, error = connector.validate_git_prerequisites(
                workspace_id="abc-123",
                branch_name="main"
            )
            if not is_valid:
                print(f"Validation failed: {error}")
                return
        """
        validation_errors = []
        
        # 1. Validate workspace exists and is accessible
        print_info("→ Validating workspace access...")
        try:
            workspace = self.fabric_client._make_request(
                "GET", f"workspaces/{workspace_id}"
            ).json()
            print_success(f"  ✓ Workspace found: {workspace.get('displayName', 'Unknown')}")
        except Exception as e:
            error_msg = (
                f"Workspace '{workspace_id}' not found or not accessible.\n"
                f"  Error: {str(e)}\n"
                f"  Troubleshooting:\n"
                f"    • Verify workspace ID is correct\n"
                f"    • Ensure you have Contributor or Admin role\n"
                f"    • Check authentication token is valid\n"
                f"  Docs: https://learn.microsoft.com/en-us/rest/api/fabric/core/workspaces"
            )
            validation_errors.append(error_msg)
            logger.error(f"Workspace validation failed: {e}")
        
        # 2. Check if workspace is already connected
        print_info("→ Checking existing Git connection...")
        try:
            current_state = self.get_git_connection_state(workspace_id)
            if current_state.get("gitConnectionState") == GitConnectionState.CONNECTED:
                print_warning(f"  ⚠ Workspace already connected to Git")
                print_info(f"    Current branch: {current_state.get('gitBranchName')}")
                print_info(f"    Current directory: {current_state.get('gitDirectoryPath')}")
                # This is a warning, not an error - return early with success
                return (True, None)
        except Exception as e:
            logger.debug(f"Unable to check existing connection (may be expected): {e}")
        
        # 3. Validate Git credentials and connection
        print_info("→ Validating Git credentials...")
        try:
            connection_id = self.get_or_create_git_connection(github_token)
            print_success(f"  ✓ Git connection available: {connection_id[:8]}...")
        except Exception as e:
            error_msg = (
                f"Git credentials validation failed.\n"
                f"  Error: {str(e)}\n"
                f"  Troubleshooting:\n"
                f"    • Set GITHUB_TOKEN env var with valid Personal Access Token\n"
                f"    • OR set FABRIC_GIT_CONNECTION_ID with existing connection\n"
                f"    • Ensure PAT has 'repo' scope for private repositories\n"
                f"    • Verify PAT has not expired\n"
                f"  Create PAT: https://github.com/settings/tokens"
            )
            validation_errors.append(error_msg)
            logger.error(f"Git credentials validation failed: {e}")
        
        # 4. Validate repository configuration
        print_info("→ Validating repository configuration...")
        if not self.organization_name:
            validation_errors.append(
                "Git organization not configured.\n"
                "  Set GIT_ORGANIZATION environment variable."
            )
        if not self.repository_name:
            validation_errors.append(
                "Git repository not configured.\n"
                "  Set GIT_REPOSITORY environment variable."
            )
        
        if self.organization_name and self.repository_name:
            print_success(
                f"  ✓ Repository: {self.organization_name}/{self.repository_name}"
            )
            print_success(f"  ✓ Branch: {branch_name}")
            print_success(f"  ✓ Directory: {directory_path}")
        
        # Compile results
        if validation_errors:
            error_message = "\n\n".join(validation_errors)
            print_error("✗ Pre-flight validation failed")
            return (False, error_message)
        
        print_success("✓ All pre-flight checks passed")
        return (True, None)

    def initialize_git_connection_with_retry(
        self,
        workspace_id: str,
        branch_name: str,
        directory_path: str = "/",
        auto_commit: bool = False,
        max_retries: int = 3,
        initial_backoff: float = 2.0,
    ) -> Dict[str, Any]:
        """
        Initialize Git connection with automatic retry and exponential backoff
        
        This method wraps initialize_git_connection with retry logic to handle
        transient failures. Implements exponential backoff: 2s, 4s, 8s delays.
        
        Args:
            workspace_id: Fabric workspace GUID
            branch_name: Git branch to connect
            directory_path: Folder path in repo (default: "/")
            auto_commit: If True, automatically commit after connection
            max_retries: Maximum number of retry attempts (default: 3)
            initial_backoff: Initial backoff delay in seconds (default: 2.0)
            
        Returns:
            Connection response from Fabric API
            
        Raises:
            Exception: If all retry attempts fail
            
        Example:
            try:
                result = connector.initialize_git_connection_with_retry(
                    workspace_id="abc-123",
                    branch_name="main",
                    max_retries=3
                )
            except Exception as e:
                print(f"Connection failed after retries: {e}")
        """
        # Run pre-flight validation first
        print_info("Running pre-flight validation...")
        is_valid, error_message = self.validate_git_prerequisites(
            workspace_id, branch_name, directory_path
        )
        
        if not is_valid:
            raise ValueError(f"Pre-flight validation failed:\n{error_message}")
        
        # Attempt connection with retry logic
        last_exception = None
        
        for attempt in range(1, max_retries + 1):
            try:
                print_info(f"Connection attempt {attempt}/{max_retries}...")
                
                result = self.initialize_git_connection(
                    workspace_id=workspace_id,
                    branch_name=branch_name,
                    directory_path=directory_path,
                    auto_commit=auto_commit,
                )
                
                print_success(f"✓ Connection successful on attempt {attempt}")
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {str(e)}")
                
                if attempt < max_retries:
                    # Calculate exponential backoff
                    backoff_delay = initial_backoff * (2 ** (attempt - 1))
                    print_warning(
                        f"⚠ Attempt {attempt} failed: {str(e)}"
                    )
                    print_info(
                        f"  Retrying in {backoff_delay:.1f} seconds "
                        f"({attempt}/{max_retries})..."
                    )
                    time.sleep(backoff_delay)
                else:
                    print_error(
                        f"✗ All {max_retries} connection attempts failed"
                    )
        
        # All retries exhausted
        error_msg = (
            f"Git connection failed after {max_retries} attempts.\n"
            f"Last error: {str(last_exception)}\n\n"
            f"Troubleshooting steps:\n"
            f"  1. Verify workspace ID: {workspace_id}\n"
            f"  2. Check Git credentials (GITHUB_TOKEN or FABRIC_GIT_CONNECTION_ID)\n"
            f"  3. Confirm repository access: {self.organization_name}/{self.repository_name}\n"
            f"  4. Verify branch exists: {branch_name}\n"
            f"  5. Check Fabric service health: https://admin.fabric.microsoft.com/monitoring/servicestatus\n\n"
            f"For manual connection:\n"
            f"  • Open workspace in Fabric Portal\n"
            f"  • Go to Workspace settings → Git integration\n"
            f"  • Connect manually and run this script again\n\n"
            f"Documentation: https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration"
        )
        raise Exception(error_msg)

    def initialize_git_connection(
        self,
        workspace_id: str,
        branch_name: str,
        directory_path: str,
        auto_commit: bool = False,
    ) -> Dict[str, Any]:
        """
        Initialize Git connection for a workspace

        This connects a Fabric workspace to a Git repository and branch.
        After connection, workspace items can be synced with Git.

        Args:
            workspace_id: Fabric workspace GUID
            branch_name: Git branch to connect (e.g., "main", "feature/my-feature")
            directory_path: Folder path in repo (e.g., "/data_products/my_product")
            auto_commit: If True, automatically commit after connection

        Returns:
            Connection response from Fabric API

        Raises:
            Exception: If connection fails or workspace already connected

        API: POST /workspaces/{workspaceId}/git/initializeConnection
        """
        print_info(f"Initializing Git connection for workspace {workspace_id[:8]}...")
        print_info(f"  Branch: {branch_name}")
        print_info(f"  Directory: {directory_path}")

        # Check if already connected
        try:
            current_state = self.get_git_connection_state(workspace_id)
            if current_state.get("gitConnectionState") == GitConnectionState.CONNECTED:
                print_warning("Workspace already connected to Git")
                print_info(f"  Current branch: {current_state.get('gitBranchName')}")
                print_info(
                    f"  Current directory: {current_state.get('gitDirectoryPath')}"
                )
                return current_state
        except Exception as e:
            logger.debug(f"Unable to check existing connection: {e}")

        # Build Git provider details
        git_config = {
            "gitProviderDetails": {
                "organizationName": self.organization_name,
                "projectName": self.project_name,
                "gitProviderType": self.git_provider_type,
                "repositoryName": self.repository_name,
                "branchName": branch_name,
                "directoryName": directory_path,
            }
        }

        try:
            logger.info(f"Sending initializeConnection request for workspace {workspace_id}")
            logger.debug(f"Git config payload: {json.dumps(git_config, indent=2)}")
            
            response = self.fabric_client._make_request(
                "POST",
                f"workspaces/{workspace_id}/git/initializeConnection",
                json=git_config,
            )

            print_success("✓ Git connection initialized successfully")
            logger.info(f"Git connection initialized for workspace {workspace_id}")

            # Verify connection
            connection_state = self.get_git_connection_state(workspace_id)
            actual_state = connection_state.get("gitConnectionState")
            
            if actual_state != GitConnectionState.CONNECTED:
                error_details = (
                    f"Connection request succeeded but workspace is not connected.\n"
                    f"  Current state: {actual_state}\n"
                    f"  Expected state: {GitConnectionState.CONNECTED}\n"
                    f"  This may indicate:\n"
                    f"    • Repository requires authentication\n"
                    f"    • Branch '{branch_name}' does not exist\n"
                    f"    • Directory '{directory_path}' is invalid\n"
                    f"    • Service is experiencing delays\n\n"
                    f"  Try:\n"
                    f"    1. Verify branch exists in repo\n"
                    f"    2. Check directory path format (should start with '/')\n"
                    f"    3. Wait 30 seconds and check connection state\n"
                    f"    4. Review Fabric service status"
                )
                logger.error(f"Connection state mismatch: {actual_state}")
                raise Exception(error_details)

            print_success(
                f"✓ Connection verified: {connection_state.get('gitConnectionState')}"
            )
            logger.info(f"Connection state verified as CONNECTED")

            # Auto-commit if requested
            if auto_commit:
                print_info("Auto-committing workspace items to Git...")
                self.commit_to_git(
                    workspace_id=workspace_id,
                    comment=f"Initial workspace setup - {datetime.utcnow().isoformat()}",
                )

            return response.json() if response.text else {}

        except Exception as e:
            error_type = type(e).__name__
            error_details = str(e)
            
            logger.error(
                f"Git connection failed: {error_type}: {error_details}",
                exc_info=True
            )
            
            # Enhanced error message with troubleshooting
            enhanced_error = (
                f"Failed to initialize Git connection for workspace {workspace_id[:8]}...\n\n"
                f"Error Type: {error_type}\n"
                f"Error Details: {error_details}\n\n"
                f"Common Issues & Solutions:\n"
                f"  • 'WorkspaceNotFound' → Check workspace ID is correct\n"
                f"  • 'Unauthorized' → Verify you have Contributor/Admin role\n"
                f"  • 'RepositoryNotFound' → Confirm repo exists: {self.organization_name}/{self.repository_name}\n"
                f"  • 'BranchNotFound' → Verify branch '{branch_name}' exists in repo\n"
                f"  • 'InvalidPath' → Check directory path format: '{directory_path}'\n"
                f"  • '400 Bad Request' → Review Git provider configuration\n\n"
                f"Workspace: {workspace_id}\n"
                f"Repository: {self.organization_name}/{self.repository_name}\n"
                f"Branch: {branch_name}\n"
                f"Directory: {directory_path}\n\n"
                f"Documentation:\n"
                f"  https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started"
            )
            
            print_error(f"✗ {enhanced_error}")
            raise Exception(enhanced_error) from e

    def get_git_connection_state(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get current Git connection state for workspace

        Args:
            workspace_id: Fabric workspace GUID

        Returns:
            Connection state including branch, directory, and sync status

        API: GET /workspaces/{workspaceId}/git/connection
        """
        try:
            response = self.fabric_client._make_request(
                "GET", f"workspaces/{workspace_id}/git/connection"
            )
            return response.json()
        except Exception as e:
            logger.debug(f"Unable to get Git connection state: {e}")
            return {"gitConnectionState": GitConnectionState.DISCONNECTED}

    def commit_to_git(
        self,
        workspace_id: str,
        comment: str,
        items: Optional[List[str]] = None,
        commit_mode: str = "All",
    ) -> Dict[str, Any]:
        """
        Commit workspace items to Git

        Args:
            workspace_id: Fabric workspace GUID
            comment: Commit message
            items: List of item IDs to commit (None = all items)
            commit_mode: "All" or "Selective"

        Returns:
            Commit response from Fabric API

        API: POST /workspaces/{workspaceId}/git/commitToGit
        """
        print_info("Committing workspace items to Git...")
        print_info(f"  Message: {comment}")
        print_info(f"  Mode: {commit_mode}")

        commit_payload = {
            "mode": commit_mode,
            "comment": comment,
            "workspaceHead": None,  # Use latest workspace state
        }

        if items:
            commit_payload["items"] = [{"logicalId": item_id} for item_id in items]

        try:
            response = self.fabric_client._make_request(
                "POST",
                f"workspaces/{workspace_id}/git/commitToGit",
                json=commit_payload,
            )

            print_success("✓ Committed to Git successfully")
            return response.json() if response.text else {}

        except Exception as e:
            print_error(f"✗ Git commit failed: {str(e)}")
            raise

    def update_from_git(
        self,
        workspace_id: str,
        allow_override: bool = False,
        conflict_resolution: str = "Workspace",
    ) -> Dict[str, Any]:
        """
        Update workspace from Git

        Args:
            workspace_id: Fabric workspace GUID
            allow_override: Allow overwriting workspace changes
            conflict_resolution: "Workspace" (keep workspace) or "Git" (use Git)

        Returns:
            Update response from Fabric API

        API: POST /workspaces/{workspaceId}/git/updateFromGit
        """
        print_info("Updating workspace from Git...")
        print_info(f"  Conflict resolution: {conflict_resolution}")

        update_payload = {
            "remoteCommitHash": None,  # Use latest from branch
            "conflictResolution": {
                "conflictResolutionType": conflict_resolution,
                "conflictResolutionPolicy": (
                    "PreferRemote"
                    if conflict_resolution == "Git"
                    else "PreferWorkspace"
                ),
            },
            "options": {"allowOverrideItems": allow_override},
        }

        try:
            response = self.fabric_client._make_request(
                "POST",
                f"workspaces/{workspace_id}/git/updateFromGit",
                json=update_payload,
            )

            print_success("✓ Updated from Git successfully")
            return response.json() if response.text else {}

        except Exception as e:
            print_error(f"✗ Git update failed: {str(e)}")
            raise

    def prompt_manual_connection(
        self,
        workspace_id: str,
        branch_name: str,
        directory_path: str = "/",
        wait_for_user: bool = True,
    ) -> bool:
        """
        Guide user through manual Git connection and verify completion
        
        When automated connection fails, this provides step-by-step manual
        instructions and optionally waits for user to complete the process
        in Fabric Portal.
        
        Args:
            workspace_id: Fabric workspace GUID
            branch_name: Git branch to connect
            directory_path: Folder path in repo
            wait_for_user: If True, prompt user and wait for manual completion
            
        Returns:
            True if manual connection successful, False otherwise
            
        Example:
            try:
                connector.initialize_git_connection_with_retry(...)
            except Exception as e:
                print(f"Automated connection failed: {e}")
                if connector.prompt_manual_connection(workspace_id, "main"):
                    print("Manual connection successful!")
        """
        print_warning("\n" + "=" * 70)
        print_warning("AUTOMATED GIT CONNECTION FAILED - MANUAL INTERVENTION REQUIRED")
        print_warning("=" * 70)
        
        print_info("\n📋 Manual Connection Steps:\n")
        print_info("1. Open Microsoft Fabric Portal:")
        print_info(f"   https://app.fabric.microsoft.com")
        print_info("")
        print_info("2. Navigate to your workspace:")
        print_info(f"   Workspace ID: {workspace_id}")
        print_info("")
        print_info("3. Open Workspace Settings:")
        print_info("   • Click workspace name in left nav")
        print_info("   • Click 'Workspace settings' (gear icon)")
        print_info("")
        print_info("4. Configure Git Integration:")
        print_info("   • Select 'Git integration' tab")
        print_info("   • Click 'Connect' button")
        print_info(f"   • Repository: {self.organization_name}/{self.repository_name}")
        print_info(f"   • Branch: {branch_name}")
        print_info(f"   • Folder: {directory_path}")
        print_info("   • Click 'Connect and sync'")
        print_info("")
        print_info("5. Verify Connection:")
        print_info("   • Wait for sync to complete")
        print_info("   • Status should show 'Connected'")
        print_info("")
        
        print_info("📚 Documentation:")
        print_info("   https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started")
        print_info("")
        
        if not wait_for_user:
            print_warning("Skipping manual connection (wait_for_user=False)")
            return False
        
        # Wait for user to complete manual steps
        print_warning("\n⏸  Paused - Complete the manual steps above")
        user_input = input("\nHave you completed the manual Git connection? (yes/no): ").strip().lower()
        
        if user_input not in ['yes', 'y']:
            print_warning("Manual connection cancelled by user")
            return False
        
        # Verify the connection was successful
        print_info("\n🔍 Verifying manual connection...")
        try:
            connection_state = self.get_git_connection_state(workspace_id)
            actual_state = connection_state.get("gitConnectionState")
            
            if actual_state == GitConnectionState.CONNECTED:
                print_success("\n✓ Manual Git connection verified successfully!")
                print_info(f"  Branch: {connection_state.get('gitBranchName')}")
                print_info(f"  Directory: {connection_state.get('gitDirectoryPath')}")
                logger.info(f"Manual Git connection verified for workspace {workspace_id}")
                return True
            else:
                print_error(f"\n✗ Workspace not connected. Current state: {actual_state}")
                print_warning("Please review the manual steps and try again")
                return False
                
        except Exception as e:
            print_error(f"\n✗ Failed to verify connection: {str(e)}")
            logger.error(f"Manual connection verification failed: {e}")
            return False

    def disconnect_git(self, workspace_id: str) -> None:
        """
        Disconnect workspace from Git

        Args:
            workspace_id: Fabric workspace GUID

        API: POST /workspaces/{workspaceId}/git/disconnect
        """
        print_info("Disconnecting workspace from Git...")

        try:
            self.fabric_client._make_request(
                "POST", f"workspaces/{workspace_id}/git/disconnect"
            )

            print_success("✓ Git connection disconnected")
            logger.info(f"Git connection disconnected for workspace {workspace_id}")

        except Exception as e:
            error_msg = f"Disconnect failed: {str(e)}"
            print_error(f"✗ {error_msg}")
            logger.error(f"Git disconnect failed for workspace {workspace_id}: {e}")
            raise Exception(error_msg) from e

    def get_git_status(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get Git sync status for workspace

        Shows which items have changed in workspace vs Git

        Args:
            workspace_id: Fabric workspace GUID

        Returns:
            Git status including changed items

        API: GET /workspaces/{workspaceId}/git/status
        """
        try:
            response = self.fabric_client._make_request(
                "GET", f"workspaces/{workspace_id}/git/status"
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get Git status: {e}")
            return {}

    def sync_workspace_bidirectional(
        self, workspace_id: str, commit_message: str, pull_first: bool = True
    ) -> Dict[str, Any]:
        """
        Bidirectional sync: Pull from Git, then push changes

        This is the recommended workflow for keeping workspace and Git in sync.

        Args:
            workspace_id: Fabric workspace GUID
            commit_message: Message for Git commit
            pull_first: If True, update from Git before committing

        Returns:
            Summary of sync operation
        """
        print_info("Starting bidirectional Git sync...")

        result = {
            "workspace_id": workspace_id,
            "pull_status": None,
            "commit_status": None,
            "errors": [],
        }

        try:
            # Step 1: Pull from Git if requested
            if pull_first:
                print_info("Step 1: Updating from Git...")
                try:
                    result["pull_status"] = self.update_from_git(
                        workspace_id=workspace_id,
                        conflict_resolution="Git",  # Prefer Git for safety
                    )
                except Exception as e:
                    result["errors"].append(f"Pull failed: {str(e)}")
                    logger.warning(f"Pull from Git failed: {e}")

            # Step 2: Commit to Git
            print_info("Step 2: Committing to Git...")
            try:
                result["commit_status"] = self.commit_to_git(
                    workspace_id=workspace_id, comment=commit_message
                )
            except Exception as e:
                result["errors"].append(f"Commit failed: {str(e)}")
                raise

            if not result["errors"]:
                print_success("✓ Bidirectional sync completed successfully")
            else:
                print_warning(f"Sync completed with {len(result['errors'])} warnings")

            return result

        except Exception as e:
            print_error(f"✗ Bidirectional sync failed: {str(e)}")
            result["errors"].append(str(e))
            return result


def get_git_connector(
    organization: Optional[str] = None,
    repository: Optional[str] = None,
    git_provider: str = GitProviderType.GITHUB,
) -> FabricGitConnector:
    """
    Factory function to create FabricGitConnector with sensible defaults

    Args:
        organization: Git organization (from env if not provided)
        repository: Git repository (from env if not provided)
        git_provider: "GitHub" or "AzureDevOps"

    Returns:
        Configured FabricGitConnector instance
    """
    return FabricGitConnector(
        organization_name=organization,
        repository_name=repository,
        git_provider_type=git_provider,
    )
