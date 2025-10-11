#!/usr/bin/env python3
"""
Microsoft Fabric Git Integration synchronization script
Handles bi-directional sync between Fabric workspaces and Git repositories
"""
import argparse
import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from utilities.fabric_deployment_pipeline import FabricGitIntegration
from utilities.fabric_api import fabric_client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FabricGitSyncManager:
    """Manage Fabric Git Integration synchronization"""
    
    def __init__(self, workspace_name: str):
        self.workspace_name = workspace_name
        self.git_integration = FabricGitIntegration(workspace_name)
        self.sync_stats = {
            'items_synced': 0,
            'errors': 0,
            'warnings': 0
        }

    def sync_to_workspace(self) -> Dict[str, Any]:
        """Sync Git repository changes to Fabric workspace"""
        logger.info(f"Starting Git-to-Workspace sync for {self.workspace_name}")
        
        try:
            # Check current Git status
            git_status = self.git_integration.get_git_status()
            logger.info(f"Current Git status: {git_status.get('gitSyncStatus', 'Unknown')}")
            
            # Perform sync from Git to workspace
            sync_result = self.git_integration.sync_from_git()
            
            # Update stats
            self.sync_stats['items_synced'] = len(sync_result.get('syncedItems', []))
            
            logger.info(f"Successfully synced {self.sync_stats['items_synced']} items to workspace")
            
            return {
                'status': 'success',
                'direction': 'git-to-workspace',
                'workspace': self.workspace_name,
                'stats': self.sync_stats,
                'sync_result': sync_result
            }
            
        except Exception as e:
            logger.error(f"Failed to sync Git to workspace: {e}")
            self.sync_stats['errors'] += 1
            return {
                'status': 'failed',
                'direction': 'git-to-workspace', 
                'workspace': self.workspace_name,
                'error': str(e),
                'stats': self.sync_stats
            }

    def sync_to_git(self, commit_message: str = None) -> Dict[str, Any]:
        """Sync Fabric workspace changes to Git repository"""
        logger.info(f"Starting Workspace-to-Git sync for {self.workspace_name}")
        
        if not commit_message:
            commit_message = f"Automated sync from {self.workspace_name} workspace"
        
        try:
            # Check what items need to be synced
            git_status = self.git_integration.get_git_status()
            
            if git_status.get('gitSyncStatus') == 'Committed':
                logger.info("No changes to sync - workspace is up to date with Git")
                return {
                    'status': 'no_changes',
                    'direction': 'workspace-to-git',
                    'workspace': self.workspace_name,
                    'message': 'No changes detected'
                }
            
            # Perform sync from workspace to Git
            sync_result = self.git_integration.sync_to_git(commit_message)
            
            # Update stats
            self.sync_stats['items_synced'] = len(sync_result.get('syncedItems', []))
            
            logger.info(f"Successfully synced {self.sync_stats['items_synced']} items to Git")
            
            return {
                'status': 'success',
                'direction': 'workspace-to-git',
                'workspace': self.workspace_name,
                'commit_message': commit_message,
                'stats': self.sync_stats,
                'sync_result': sync_result
            }
            
        except Exception as e:
            logger.error(f"Failed to sync workspace to Git: {e}")
            self.sync_stats['errors'] += 1
            return {
                'status': 'failed',
                'direction': 'workspace-to-git',
                'workspace': self.workspace_name, 
                'error': str(e),
                'stats': self.sync_stats
            }

    def initialize_git_connection(self, git_provider: str, organization: str, 
                                repository: str, branch: str, directory: str = "/") -> Dict[str, Any]:
        """Initialize Git integration for the workspace"""
        logger.info(f"Initializing Git connection for workspace {self.workspace_name}")
        
        try:
            result = self.git_integration.connect_to_git(
                git_provider, organization, repository, branch, directory
            )
            
            logger.info(f"Successfully connected workspace to {git_provider}:{organization}/{repository}#{branch}")
            return {
                'status': 'success',
                'workspace': self.workspace_name,
                'git_provider': git_provider,
                'repository': f"{organization}/{repository}",
                'branch': branch,
                'directory': directory,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize Git connection: {e}")
            return {
                'status': 'failed',
                'workspace': self.workspace_name,
                'error': str(e)
            }

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status and configuration"""
        try:
            git_status = self.git_integration.get_git_status()
            
            return {
                'status': 'success',
                'workspace': self.workspace_name,
                'git_status': git_status,
                'is_connected': git_status.get('gitProviderDetails') is not None,
                'last_sync': git_status.get('lastSyncTime'),
                'sync_status': git_status.get('gitSyncStatus')
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync status: {e}")
            return {
                'status': 'failed',
                'workspace': self.workspace_name,
                'error': str(e)
            }

def main():
    parser = argparse.ArgumentParser(
        description="Synchronize Microsoft Fabric workspace with Git repository"
    )
    parser.add_argument("--workspace", required=True, help="Fabric workspace name")
    parser.add_argument("--action", required=True, 
                       choices=["sync-to-workspace", "sync-to-git", "init-git", "status"],
                       help="Synchronization action")
    parser.add_argument("--commit-message", help="Commit message for workspace-to-git sync")
    parser.add_argument("--git-provider", choices=["GitHub", "AzureDevOps"], 
                       help="Git provider (required for init-git)")
    parser.add_argument("--organization", help="Git organization/owner (required for init-git)")
    parser.add_argument("--repository", help="Git repository name (required for init-git)")
    parser.add_argument("--branch", default="main", help="Git branch (default: main)")
    parser.add_argument("--directory", default="/", help="Directory path in repository (default: /)")
    parser.add_argument("--output-format", choices=["json", "text"], default="text",
                       help="Output format")

    args = parser.parse_args()

    # Validate init-git arguments
    if args.action == "init-git":
        if not all([args.git_provider, args.organization, args.repository]):
            parser.error("init-git action requires --git-provider, --organization, and --repository")

    try:
        sync_manager = FabricGitSyncManager(args.workspace)
        
        # Execute the requested action
        if args.action == "sync-to-workspace":
            result = sync_manager.sync_to_workspace()
        elif args.action == "sync-to-git":
            result = sync_manager.sync_to_git(args.commit_message)
        elif args.action == "init-git":
            result = sync_manager.initialize_git_connection(
                args.git_provider, args.organization, args.repository, 
                args.branch, args.directory
            )
        elif args.action == "status":
            result = sync_manager.get_sync_status()
        
        # Output results
        if args.output_format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(f"Action: {args.action}")
            print(f"Workspace: {args.workspace}")
            print(f"Status: {result.get('status', 'unknown')}")
            
            if result.get('status') == 'success':
                if 'stats' in result:
                    print(f"Items synced: {result['stats'].get('items_synced', 0)}")
                if 'commit_message' in result:
                    print(f"Commit message: {result['commit_message']}")
                if 'git_status' in result:
                    git_status = result['git_status']
                    print(f"Git sync status: {git_status.get('gitSyncStatus', 'Unknown')}")
                    if git_status.get('gitProviderDetails'):
                        provider_details = git_status['gitProviderDetails']
                        print(f"Connected to: {provider_details.get('gitProviderType')} - {provider_details.get('repositoryName')}")
                        print(f"Branch: {provider_details.get('branchName')}")
            elif result.get('status') == 'failed':
                print(f"Error: {result.get('error', 'Unknown error')}")
                return 1
            elif result.get('status') == 'no_changes':
                print(f"Message: {result.get('message', 'No changes')}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Sync operation failed: {e}")
        if args.output_format == "json":
            error_result = {
                'status': 'failed',
                'workspace': args.workspace,
                'action': args.action,
                'error': str(e)
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())