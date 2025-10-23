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
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from .fabric_api import FabricClient
from .output import (
    console_success as print_success,
    console_error as print_error,
    console_warning as print_warning,
    console_info as print_info
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
        git_provider_type: str = GitProviderType.GITHUB
    ):
        """
        Initialize Git connector
        
        Args:
            organization_name: GitHub org or Azure DevOps org (from env if not provided)
            project_name: Project name (Azure DevOps only, uses repo name for GitHub)
            repository_name: Git repository name (from env if not provided)
            git_provider_type: "GitHub" or "AzureDevOps"
        """
        self.fabric_client = FabricClient()
        
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
    
    def connect_to_git(
        self,
        workspace_id: str,
        branch_name: str,
        directory_path: str = "/"
    ) -> Dict[str, Any]:
        """
        Connect a workspace to Git repository (initial connection)
        
        This establishes the initial Git connection for a workspace.
        After this, use initialize_git_connection to update settings.
        
        Args:
            workspace_id: Fabric workspace GUID
            branch_name: Git branch to connect (e.g., "main", "feature/my-feature")
            directory_path: Folder path in repo (default: "/")
        
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
        
        # Build payload for connect endpoint
        git_provider_details = {
            "gitProviderType": self.git_provider_type,
            "organizationName": self.organization_name,
            "repositoryName": self.repository_name,
            "branchName": branch_name,
            "directoryName": directory_path
        }
        
        # For GitHub, try ownerName instead of/in addition to organizationName
        if self.git_provider_type == GitProviderType.GITHUB:
            git_provider_details["ownerName"] = self.organization_name
        
        # Add projectName only if provided (required for Azure DevOps)
        if self.project_name:
            git_provider_details["projectName"] = self.project_name
        
        payload = {"gitProviderDetails": git_provider_details}
        
        print_info(f"DEBUG: Payload = {json.dumps(payload, indent=2)}")
        
        try:
            response = self.fabric_client._make_request(
                'POST',
                f'workspaces/{workspace_id}/git/connect',
                json=payload
            )
            
            print_success(f"✓ Workspace connected to Git successfully")
            return response.json() if response.text else {}
            
        except Exception as e:
            print_error(f"✗ Failed to connect workspace to Git: {str(e)}")
            raise

    def initialize_git_connection(
        self,
        workspace_id: str,
        branch_name: str,
        directory_path: str,
        auto_commit: bool = False
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
            if current_state.get('gitConnectionState') == GitConnectionState.CONNECTED:
                print_warning(f"Workspace already connected to Git")
                print_info(f"  Current branch: {current_state.get('gitBranchName')}")
                print_info(f"  Current directory: {current_state.get('gitDirectoryPath')}")
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
                "directoryName": directory_path
            }
        }
        
        try:
            response = self.fabric_client._make_request(
                'POST',
                f'workspaces/{workspace_id}/git/initializeConnection',
                json=git_config
            )
            
            print_success(f"✓ Git connection initialized successfully")
            
            # Verify connection
            connection_state = self.get_git_connection_state(workspace_id)
            if connection_state.get('gitConnectionState') != GitConnectionState.CONNECTED:
                raise Exception(
                    f"Connection initialized but state is: {connection_state.get('gitConnectionState')}"
                )
            
            print_success(f"✓ Connection verified: {connection_state.get('gitConnectionState')}")
            
            # Auto-commit if requested
            if auto_commit:
                print_info("Auto-committing workspace items to Git...")
                self.commit_to_git(
                    workspace_id=workspace_id,
                    comment=f"Initial workspace setup - {datetime.utcnow().isoformat()}"
                )
            
            return response.json() if response.text else {}
            
        except Exception as e:
            print_error(f"✗ Failed to initialize Git connection: {str(e)}")
            raise
    
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
                'GET',
                f'workspaces/{workspace_id}/git/connection'
            )
            return response.json()
        except Exception as e:
            logger.debug(f"Unable to get Git connection state: {e}")
            return {
                'gitConnectionState': GitConnectionState.DISCONNECTED
            }
    
    def commit_to_git(
        self,
        workspace_id: str,
        comment: str,
        items: Optional[List[str]] = None,
        commit_mode: str = "All"
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
        print_info(f"Committing workspace items to Git...")
        print_info(f"  Message: {comment}")
        print_info(f"  Mode: {commit_mode}")
        
        commit_payload = {
            "mode": commit_mode,
            "comment": comment,
            "workspaceHead": None  # Use latest workspace state
        }
        
        if items:
            commit_payload["items"] = [{"logicalId": item_id} for item_id in items]
        
        try:
            response = self.fabric_client._make_request(
                'POST',
                f'workspaces/{workspace_id}/git/commitToGit',
                json=commit_payload
            )
            
            print_success(f"✓ Committed to Git successfully")
            return response.json() if response.text else {}
            
        except Exception as e:
            print_error(f"✗ Git commit failed: {str(e)}")
            raise
    
    def update_from_git(
        self,
        workspace_id: str,
        allow_override: bool = False,
        conflict_resolution: str = "Workspace"
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
        print_info(f"Updating workspace from Git...")
        print_info(f"  Conflict resolution: {conflict_resolution}")
        
        update_payload = {
            "remoteCommitHash": None,  # Use latest from branch
            "conflictResolution": {
                "conflictResolutionType": conflict_resolution,
                "conflictResolutionPolicy": "PreferRemote" if conflict_resolution == "Git" else "PreferWorkspace"
            },
            "options": {
                "allowOverrideItems": allow_override
            }
        }
        
        try:
            response = self.fabric_client._make_request(
                'POST',
                f'workspaces/{workspace_id}/git/updateFromGit',
                json=update_payload
            )
            
            print_success(f"✓ Updated from Git successfully")
            return response.json() if response.text else {}
            
        except Exception as e:
            print_error(f"✗ Git update failed: {str(e)}")
            raise
    
    def disconnect_git(self, workspace_id: str) -> None:
        """
        Disconnect workspace from Git
        
        Args:
            workspace_id: Fabric workspace GUID
        
        API: POST /workspaces/{workspaceId}/git/disconnect
        """
        print_info(f"Disconnecting workspace from Git...")
        
        try:
            self.fabric_client._make_request(
                'POST',
                f'workspaces/{workspace_id}/git/disconnect'
            )
            
            print_success(f"✓ Git connection disconnected")
            
        except Exception as e:
            print_error(f"✗ Disconnect failed: {str(e)}")
            raise
    
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
                'GET',
                f'workspaces/{workspace_id}/git/status'
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get Git status: {e}")
            return {}
    
    def sync_workspace_bidirectional(
        self,
        workspace_id: str,
        commit_message: str,
        pull_first: bool = True
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
            "errors": []
        }
        
        try:
            # Step 1: Pull from Git if requested
            if pull_first:
                print_info("Step 1: Updating from Git...")
                try:
                    result["pull_status"] = self.update_from_git(
                        workspace_id=workspace_id,
                        conflict_resolution="Git"  # Prefer Git for safety
                    )
                except Exception as e:
                    result["errors"].append(f"Pull failed: {str(e)}")
                    logger.warning(f"Pull from Git failed: {e}")
            
            # Step 2: Commit to Git
            print_info("Step 2: Committing to Git...")
            try:
                result["commit_status"] = self.commit_to_git(
                    workspace_id=workspace_id,
                    comment=commit_message
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
    git_provider: str = GitProviderType.GITHUB
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
        git_provider_type=git_provider
    )
