"""
Microsoft Fabric Deployment Pipeline Management
Handles promotion between Dev/Test/Production stages using Fabric Deployment Pipelines API
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional
from .fabric_api import fabric_client

from .constants import (
    DEFAULT_POLLING_INTERVAL_SECONDS,
    MAX_POLLING_ATTEMPTS,
    DEPLOYMENT_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


class FabricDeploymentManager:
    """Manage Fabric Deployment Pipelines for stage promotions"""

    def __init__(self):
        self.fabric_client = fabric_client

    def list_deployment_pipelines(self) -> List[Dict[str, Any]]:
        """List all deployment pipelines"""
        response = self.fabric_client._make_request("GET", "pipelines")
        return response.json().get("value", [])

    def get_deployment_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """Get deployment pipeline details"""
        response = self.fabric_client._make_request("GET", f"pipelines/{pipeline_id}")
        return response.json()

    def list_pipeline_stages(self, pipeline_id: str) -> List[Dict[str, Any]]:
        """List stages in deployment pipeline"""
        response = self.fabric_client._make_request(
            "GET", f"pipelines/{pipeline_id}/stages"
        )
        return response.json().get("value", [])

    def get_stage_artifacts(
        self, pipeline_id: str, stage_id: str
    ) -> List[Dict[str, Any]]:
        """Get artifacts in a specific pipeline stage"""
        response = self.fabric_client._make_request(
            "GET", f"pipelines/{pipeline_id}/stages/{stage_id}/artifacts"
        )
        return response.json().get("value", [])

    def promote_to_next_stage(
        self,
        pipeline_id: str,
        source_stage_order: int,
        target_stage_order: int,
        items: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Promote items between pipeline stages"""

        default_options = {
            "allowCreateArtifact": True,
            "allowOverwriteArtifact": True,
            "allowPurviewScan": True,
        }

        if options:
            default_options.update(options)

        payload = {
            "sourceStageOrder": source_stage_order,
            "targetStageOrder": target_stage_order,
            "options": default_options,
        }

        # If specific items are provided, include them
        if items:
            payload["artifacts"] = [{"sourceArtifactId": item_id} for item_id in items]

        logger.info(
            f"Promoting from stage {source_stage_order} to stage {target_stage_order}"
        )
        logger.debug(f"Promotion payload: {json.dumps(payload, indent=2)}")

        response = self.fabric_client._make_request(
            "POST", f"pipelines/{pipeline_id}/deployments", json=payload
        )
        deployment_result = response.json()

        # Wait for deployment to complete and get status
        if "id" in deployment_result:
            deployment_id = deployment_result["id"]
            final_status = self._wait_for_deployment_completion(
                pipeline_id, deployment_id
            )
            deployment_result["final_status"] = final_status

        return deployment_result

    def _wait_for_deployment_completion(
        self, pipeline_id: str, deployment_id: str, timeout_minutes: int = 30
    ) -> Dict[str, Any]:
        """Wait for deployment to complete and return final status"""
        timeout_seconds = timeout_minutes * 60
        start_time = time.time()

        while time.time() - start_time < timeout_seconds:
            try:
                response = self.fabric_client._make_request(
                    "GET", f"pipelines/{pipeline_id}/deployments/{deployment_id}"
                )
                status = response.json()

                deployment_status = status.get("status", "").upper()

                if deployment_status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
                    logger.info(
                        f"Deployment {deployment_id} completed with status: {deployment_status}"
                    )
                    return status

                logger.info(
                    f"Deployment {deployment_id} status: {deployment_status}, waiting {DEFAULT_POLLING_INTERVAL_SECONDS}s..."
                )
                time.sleep(DEFAULT_POLLING_INTERVAL_SECONDS)

            except Exception as e:
                logger.warning(f"Error checking deployment status: {e}")
                time.sleep(DEFAULT_POLLING_INTERVAL_SECONDS)

        logger.error(
            f"Deployment {deployment_id} timed out after {timeout_minutes} minutes"
        )
        return {
            "status": "TIMEOUT",
            "message": f"Deployment timed out after {timeout_minutes} minutes",
        }

    def get_deployment_history(
        self, pipeline_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent deployment history"""
        response = self.fabric_client._make_request(
            "GET", f"pipelines/{pipeline_id}/deployments?$top={limit}"
        )
        return response.json().get("value", [])

    def create_deployment_pipeline(
        self, display_name: str, description: str = ""
    ) -> Dict[str, Any]:
        """Create a new deployment pipeline"""
        payload = {"displayName": display_name, "description": description}

        response = self.fabric_client._make_request("POST", "pipelines", json=payload)
        logger.info(f"Created deployment pipeline: {display_name}")
        return response.json()

    def add_workspace_to_stage(
        self, pipeline_id: str, stage_order: int, workspace_id: str
    ) -> Dict[str, Any]:
        """Assign workspace to deployment pipeline stage"""
        payload = {"workspaceId": workspace_id}

        response = self.fabric_client._make_request(
            "POST",
            f"pipelines/{pipeline_id}/stages/{stage_order}/assignWorkspace",
            json=payload,
        )
        logger.info(f"Assigned workspace {workspace_id} to stage {stage_order}")
        return response.json()

    def validate_deployment_readiness(
        self, pipeline_id: str, source_stage_order: int, target_stage_order: int
    ) -> Dict[str, Any]:
        """Validate if deployment between stages is ready"""

        # Get source and target stage details
        stages = self.list_pipeline_stages(pipeline_id)
        source_stage = next(
            (s for s in stages if s["order"] == source_stage_order), None
        )
        target_stage = next(
            (s for s in stages if s["order"] == target_stage_order), None
        )

        if not source_stage or not target_stage:
            return {
                "ready": False,
                "reason": f"Invalid stage orders: source={source_stage_order}, target={target_stage_order}",
            }

        # Check if source stage has artifacts
        source_artifacts = self.get_stage_artifacts(pipeline_id, source_stage["id"])

        validation_result = {
            "ready": True,
            "source_stage": source_stage,
            "target_stage": target_stage,
            "source_artifacts_count": len(source_artifacts),
            "source_artifacts": [
                artifact["displayName"] for artifact in source_artifacts[:5]
            ],  # First 5
        }

        if len(source_artifacts) == 0:
            validation_result["ready"] = False
            validation_result["reason"] = "No artifacts found in source stage"

        return validation_result


class FabricGitIntegration:
    """Handle Fabric Git Integration workflows"""

    def __init__(self, workspace_name: str):
        self.workspace_name = workspace_name
        self.fabric_client = fabric_client
        self.workspace_id = self.fabric_client.get_workspace_id(workspace_name)

    def connect_to_git(
        self,
        git_provider: str,
        organization: str,
        repository: str,
        branch: str,
        directory_path: str = "/",
    ) -> Dict[str, Any]:
        """Connect workspace to Git repository"""

        payload = {
            "gitProviderDetails": {
                "gitProviderType": git_provider,  # "GitHub", "AzureDevOps"
                "organizationName": organization,
                "projectName": repository if git_provider == "AzureDevOps" else None,
                "repositoryName": repository,
                "branchName": branch,
                "directoryName": directory_path,
            }
        }

        response = self.fabric_client._make_request(
            "POST", f"workspaces/{self.workspace_id}/git/connect", json=payload
        )

        logger.info(
            f"Connected workspace {self.workspace_name} to {git_provider}:{organization}/{repository}#{branch}"
        )
        return response.json()

    def sync_to_git(
        self, commit_message: str, changes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Sync workspace changes to Git"""

        payload = {
            "mode": "CommitToGit",
            "workspaceHead": "",  # Will be populated by Fabric
            "options": {"allowOverrideItems": True},
        }

        if commit_message:
            payload["commitMessage"] = commit_message

        if changes:
            payload["items"] = [{"logicalId": item_id} for item_id in changes]

        response = self.fabric_client._make_request(
            "POST", f"workspaces/{self.workspace_id}/git/commitToGit", json=payload
        )

        logger.info(f"Synced workspace changes to Git with message: {commit_message}")
        return response.json()

    def sync_from_git(self) -> Dict[str, Any]:
        """Sync Git changes to workspace"""

        payload = {"mode": "UpdateFromGit", "options": {"allowOverrideItems": True}}

        response = self.fabric_client._make_request(
            "POST", f"workspaces/{self.workspace_id}/git/updateFromGit", json=payload
        )

        logger.info(f"Synced Git changes to workspace {self.workspace_name}")
        return response.json()

    def get_git_status(self) -> Dict[str, Any]:
        """Get current Git integration status"""
        response = self.fabric_client._make_request(
            "GET", f"workspaces/{self.workspace_id}/git/status"
        )
        return response.json()

    def disconnect_from_git(self) -> Dict[str, Any]:
        """Disconnect workspace from Git"""
        response = self.fabric_client._make_request(
            "POST", f"workspaces/{self.workspace_id}/git/disconnect"
        )
        logger.info(f"Disconnected workspace {self.workspace_name} from Git")
        return response.json()
