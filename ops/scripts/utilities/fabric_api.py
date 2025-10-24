"""
Microsoft Fabric API utilities using fabric-cicd library and REST APIs
"""

import os
import json
import logging
import base64
from typing import Dict, Any, Optional, List
from functools import lru_cache
import requests
from msal import ConfidentialClientApplication

# Import constants
from .constants import (
    FABRIC_API_BASE_URL,
    FABRIC_API_SCOPE,
    get_azure_authority_url,
    ERROR_MISSING_CREDENTIALS,
    ERROR_AUTHENTICATION_FAILED,
    HTTP_DEFAULT_TIMEOUT,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FabricClient:
    """Enhanced Fabric API client using fabric-cicd and direct REST calls"""

    def __init__(self):
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.base_url = FABRIC_API_BASE_URL
        self.token = None

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError(ERROR_MISSING_CREDENTIALS)

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
            return self.token
        else:
            error_desc = result.get("error_description", "Unknown error")
            raise Exception(ERROR_AUTHENTICATION_FAILED.format(error_desc))

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to Fabric API"""
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self._get_access_token()}"
        headers["Content-Type"] = "application/json"
        kwargs["headers"] = headers

        # Add default timeout if not specified
        if "timeout" not in kwargs:
            kwargs["timeout"] = HTTP_DEFAULT_TIMEOUT

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, **kwargs)

        if not response.ok:
            logger.error(f"Fabric API error: {response.status_code} - {response.text}")
            response.raise_for_status()

        return response

    @lru_cache(maxsize=128)
    def get_workspace_id(self, workspace_name: str) -> str:
        """Get workspace ID by name (cached for performance)"""
        response = self._make_request("GET", "workspaces")
        workspaces = response.json().get("value", [])

        for workspace in workspaces:
            if workspace["displayName"] == workspace_name:
                logger.debug(f"Cached workspace ID for '{workspace_name}'")
                return workspace["id"]

        raise ValueError(f"Workspace '{workspace_name}' not found")

    def list_workspace_items(
        self, workspace_id: str, item_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List items in workspace, optionally filtered by type"""
        endpoint = f"workspaces/{workspace_id}/items"
        if item_type:
            endpoint += f"?type={item_type}"

        response = self._make_request("GET", endpoint)
        return response.json().get("value", [])

    def create_or_update_notebook(
        self, workspace_name: str, notebook_name: str, content_bytes: bytes
    ) -> Dict[str, Any]:
        """Create or update a notebook in Fabric workspace"""
        workspace_id = self.get_workspace_id(workspace_name)

        # Check if notebook exists
        existing_items = self.list_workspace_items(workspace_id, "Notebook")
        existing_notebook = next(
            (item for item in existing_items if item["displayName"] == notebook_name),
            None,
        )

        # Prepare notebook content
        if isinstance(content_bytes, bytes):
            content_str = content_bytes.decode("utf-8")
        else:
            content_str = content_bytes

        # Parse notebook content if it's JSON
        try:
            notebook_content = (
                json.loads(content_str) if isinstance(content_str, str) else content_str
            )
        except json.JSONDecodeError:
            # If not JSON, treat as raw content
            notebook_content = {"cells": [{"cell_type": "code", "source": content_str}]}

        payload = {
            "displayName": notebook_name,
            "type": "Notebook",
            "definition": {
                "format": "ipynb",
                "parts": [
                    {
                        "path": "notebook-content.py",
                        "payload": base64.b64encode(
                            json.dumps(notebook_content).encode()
                        ).decode(),
                        "payloadType": "InlineBase64",
                    }
                ],
            },
        }

        if existing_notebook:
            # Update existing notebook
            endpoint = f"workspaces/{workspace_id}/items/{existing_notebook['id']}"
            response = self._make_request("PATCH", endpoint, json=payload)
            logger.info(
                f"Updated notebook '{notebook_name}' in workspace '{workspace_name}'"
            )
        else:
            # Create new notebook
            endpoint = f"workspaces/{workspace_id}/items"
            response = self._make_request("POST", endpoint, json=payload)
            logger.info(
                f"Created notebook '{notebook_name}' in workspace '{workspace_name}'"
            )

        return response.json()

    def deploy_pipeline_json(
        self, workspace_name: str, pipeline_json: str
    ) -> Dict[str, Any]:
        """Deploy data pipeline from JSON definition"""
        workspace_id = self.get_workspace_id(workspace_name)

        try:
            pipeline_def = (
                json.loads(pipeline_json)
                if isinstance(pipeline_json, str)
                else pipeline_json
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid pipeline JSON: {e}")

        pipeline_name = pipeline_def.get("name", "DefaultPipeline")

        # Check if pipeline exists
        existing_items = self.list_workspace_items(workspace_id, "DataPipeline")
        existing_pipeline = next(
            (item for item in existing_items if item["displayName"] == pipeline_name),
            None,
        )

        payload = {
            "displayName": pipeline_name,
            "type": "DataPipeline",
            "definition": {
                "parts": [
                    {
                        "path": "pipeline-content.json",
                        "payload": base64.b64encode(
                            json.dumps(pipeline_def).encode()
                        ).decode(),
                        "payloadType": "InlineBase64",
                    }
                ]
            },
        }

        if existing_pipeline:
            endpoint = f"workspaces/{workspace_id}/items/{existing_pipeline['id']}"
            response = self._make_request("PATCH", endpoint, json=payload)
            logger.info(
                f"Updated pipeline '{pipeline_name}' in workspace '{workspace_name}'"
            )
        else:
            endpoint = f"workspaces/{workspace_id}/items"
            response = self._make_request("POST", endpoint, json=payload)
            logger.info(
                f"Created pipeline '{pipeline_name}' in workspace '{workspace_name}'"
            )

        return response.json()

    def deploy_dataflow(
        self,
        workspace_name: str,
        dataflow_name: str,
        dataflow_definition: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Deploy Dataflow Gen2"""
        workspace_id = self.get_workspace_id(workspace_name)

        existing_items = self.list_workspace_items(workspace_id, "Dataflow")
        existing_dataflow = next(
            (item for item in existing_items if item["displayName"] == dataflow_name),
            None,
        )

        payload = {
            "displayName": dataflow_name,
            "type": "Dataflow",
            "definition": {
                "parts": [
                    {
                        "path": "dataflow-content.json",
                        "payload": base64.b64encode(
                            json.dumps(dataflow_definition).encode()
                        ).decode(),
                        "payloadType": "InlineBase64",
                    }
                ]
            },
        }

        if existing_dataflow:
            endpoint = f"workspaces/{workspace_id}/items/{existing_dataflow['id']}"
            response = self._make_request("PATCH", endpoint, json=payload)
            logger.info(
                f"Updated dataflow '{dataflow_name}' in workspace '{workspace_name}'"
            )
        else:
            endpoint = f"workspaces/{workspace_id}/items"
            response = self._make_request("POST", endpoint, json=payload)
            logger.info(
                f"Created dataflow '{dataflow_name}' in workspace '{workspace_name}'"
            )

        return response.json()

    def trigger_deployment_pipeline(
        self,
        pipeline_id: str,
        source_stage_id: str,
        target_stage_id: str,
        items: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Trigger deployment between pipeline stages"""
        payload = {
            "sourceStageOrder": source_stage_id,
            "targetStageOrder": target_stage_id,
            "options": {"allowCreateArtifact": True, "allowOverwriteArtifact": True},
        }

        if items:
            payload["artifacts"] = [{"sourceArtifactId": item_id} for item_id in items]

        endpoint = f"pipelines/{pipeline_id}/deployments"
        response = self._make_request("POST", endpoint, json=payload)
        logger.info(
            f"Triggered deployment from stage {source_stage_id} to {target_stage_id}"
        )
        return response.json()


# Global client instance (lazy initialization)
_fabric_client = None


def get_fabric_client() -> FabricClient:
    """Get or create the global FabricClient instance (lazy initialization)"""
    global _fabric_client
    if _fabric_client is None:
        _fabric_client = FabricClient()
    return _fabric_client


# Backward compatibility: fabric_client property that lazily initializes
class _FabricClientProxy:
    """Proxy that provides backward compatibility for direct fabric_client access"""
    def __getattr__(self, name):
        return getattr(get_fabric_client(), name)

fabric_client = _FabricClientProxy()


# Legacy function compatibility
def create_or_update_notebook(
    workspace: str, name: str, content_bytes: bytes
) -> Dict[str, Any]:
    """Legacy compatibility function"""
    return get_fabric_client().create_or_update_notebook(workspace, name, content_bytes)


def deploy_pipeline_json(workspace: str, pipeline_json: str) -> Dict[str, Any]:
    """Legacy compatibility function"""
    return get_fabric_client().deploy_pipeline_json(workspace, pipeline_json)
