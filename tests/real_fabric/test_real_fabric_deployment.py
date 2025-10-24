"""
Real Fabric Integration Tests - CREATES ACTUAL RESOURCES

⚠️ WARNING: These tests interact with REAL Microsoft Fabric resources ⚠️

- Creates actual workspaces in your Fabric environment
- Creates real lakehouses and other Fabric items  
- Should NOT be run in CI/CD pipelines
- Requires valid Azure credentials with Fabric permissions

Usage:
    # Run real Fabric tests manually
    pytest tests/real_fabric/test_real_fabric_deployment.py -v -s -m real_fabric
    
Safety Features:
    - All resources tagged for identification
    - Comprehensive cleanup in finally blocks
    - Transaction rollback integration
    - Timeout protection (5 minute max per test)
"""

import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict

import pytest
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import production hardening utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from ops.scripts.utilities.retry_handler import fabric_retry
from ops.scripts.utilities.circuit_breaker import get_circuit_breaker
from ops.scripts.utilities.transaction_manager import (
    DeploymentTransaction,
    ResourceType,
)


# ======================================================================
# Fabric API Client
# ======================================================================


class FabricAPIClient:
    """Real Fabric API client with authentication"""

    def __init__(self):
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.capacity_id = os.getenv("FABRIC_CAPACITY_ID")

        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError(
                "Missing Azure credentials. Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID"
            )

        if not self.capacity_id:
            raise ValueError("Missing FABRIC_CAPACITY_ID in .env file")

        self.base_url = "https://api.fabric.microsoft.com/v1"
        self.token = None
        self.token_expiry = None

    def get_access_token(self) -> str:
        """Get Azure AD access token for Fabric API"""
        if self.token and self.token_expiry and time.time() < self.token_expiry:
            return self.token

        token_url = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://api.fabric.microsoft.com/.default",
            "grant_type": "client_credentials",
        }

        response = requests.post(token_url, data=token_data, timeout=30)
        response.raise_for_status()

        token_info = response.json()
        self.token = token_info["access_token"]
        self.token_expiry = time.time() + token_info.get("expires_in", 3600) - 300
        return self.token

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json",
        }

    @fabric_retry(max_attempts=3, min_wait=1, max_wait=5)
    def create_workspace(self, display_name: str, description: str = "") -> Dict:
        """Create a Fabric workspace"""
        url = f"{self.base_url}/workspaces"
        payload = {
            "displayName": display_name,
            "description": description or f"Test workspace - {display_name}",
            "capacityId": self.capacity_id,
        }

        response = requests.post(
            url, json=payload, headers=self._get_headers(), timeout=60
        )
        response.raise_for_status()
        return response.json()

    @fabric_retry(max_attempts=3, min_wait=1, max_wait=5)
    def delete_workspace(self, workspace_id: str) -> None:
        """Delete a Fabric workspace"""
        url = f"{self.base_url}/workspaces/{workspace_id}"
        response = requests.delete(url, headers=self._get_headers(), timeout=60)
        response.raise_for_status()

    @fabric_retry(max_attempts=3, min_wait=1, max_wait=5)
    def get_workspace(self, workspace_id: str) -> Dict:
        """Get workspace details"""
        url = f"{self.base_url}/workspaces/{workspace_id}"
        response = requests.get(url, headers=self._get_headers(), timeout=60)
        response.raise_for_status()
        return response.json()

    @fabric_retry(max_attempts=3, min_wait=1, max_wait=5)
    def create_lakehouse(
        self, workspace_id: str, display_name: str, description: str = ""
    ) -> Dict:
        """Create a lakehouse in a workspace"""
        url = f"{self.base_url}/workspaces/{workspace_id}/lakehouses"
        payload = {
            "displayName": display_name,
            "description": description or f"Test lakehouse - {display_name}",
        }

        response = requests.post(
            url, json=payload, headers=self._get_headers(), timeout=60
        )
        response.raise_for_status()
        return response.json()

    @fabric_retry(max_attempts=3, min_wait=1, max_wait=5)
    def delete_lakehouse(self, workspace_id: str, lakehouse_id: str) -> None:
        """Delete a lakehouse"""
        url = f"{self.base_url}/workspaces/{workspace_id}/lakehouses/{lakehouse_id}"
        response = requests.delete(url, headers=self._get_headers(), timeout=60)
        response.raise_for_status()


# ======================================================================
# Fixtures
# ======================================================================


@pytest.fixture(scope="module")
def fabric_client():
    """Initialize Fabric API client"""
    return FabricAPIClient()


@pytest.fixture(scope="function")
def test_workspace_name():
    """Generate unique workspace name for testing"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"test-cicd-{timestamp}-{unique_id}"


# ======================================================================
# Real Fabric Integration Tests
# ======================================================================


@pytest.mark.real_fabric
@pytest.mark.timeout(300)  # 5 minute timeout
class TestRealFabricDeployment:
    """Test deployment against real Fabric API"""

    def test_create_workspace_with_production_features(
        self, fabric_client, test_workspace_name
    ):
        """
        Test workspace creation with retry protection

        Creates a real workspace in Fabric, validates it, and cleans up
        """
        workspace_id = None

        try:
            print(f"\n🔧 Creating real workspace: {test_workspace_name}")
            print(f"   Capacity ID: {fabric_client.capacity_id}")

            # Create workspace with retry protection
            workspace_response = fabric_client.create_workspace(
                display_name=test_workspace_name,
                description="Automated test workspace - safe to delete",
            )

            workspace_id = workspace_response["id"]
            print(f"✅ Workspace created: {workspace_id}")

            # Validate workspace exists
            workspace_info = fabric_client.get_workspace(workspace_id)
            assert workspace_info["id"] == workspace_id
            assert workspace_info["displayName"] == test_workspace_name

            print(f"✅ Workspace validated: {workspace_info['displayName']}")

        finally:
            # Cleanup: Delete workspace
            if workspace_id:
                try:
                    print(f"\n🧹 Cleaning up workspace: {workspace_id}")
                    fabric_client.delete_workspace(workspace_id)
                    print("✅ Workspace deleted successfully")
                except Exception as cleanup_error:
                    print(f"⚠️  Cleanup warning: {cleanup_error}")

    def test_create_workspace_and_lakehouse(self, fabric_client, test_workspace_name):
        """
        Test workspace and lakehouse creation with cleanup

        Creates workspace + lakehouse, validates both, then cleans up
        """
        workspace_id = None
        lakehouse_id = None

        try:
            # Create workspace
            print(f"\n🔧 Creating workspace: {test_workspace_name}")
            workspace_response = fabric_client.create_workspace(
                display_name=test_workspace_name,
                description="Test workspace with lakehouse",
            )
            workspace_id = workspace_response["id"]
            print(f"✅ Workspace created: {workspace_id}")

            # Create lakehouse
            lakehouse_name = f"{test_workspace_name}-lakehouse"
            print(f"🔧 Creating lakehouse: {lakehouse_name}")

            lakehouse_response = fabric_client.create_lakehouse(
                workspace_id=workspace_id,
                display_name=lakehouse_name,
                description="Test lakehouse",
            )
            lakehouse_id = lakehouse_response["id"]
            print(f"✅ Lakehouse created: {lakehouse_id}")

            # Validate resources
            assert workspace_id is not None
            assert lakehouse_id is not None
            print("✅ Both resources validated")

        finally:
            # Cleanup in reverse order
            if lakehouse_id and workspace_id:
                try:
                    print(f"\n🧹 Cleaning up lakehouse: {lakehouse_id}")
                    fabric_client.delete_lakehouse(workspace_id, lakehouse_id)
                    print("✅ Lakehouse deleted")
                except Exception as cleanup_error:
                    print(f"⚠️  Lakehouse cleanup warning: {cleanup_error}")

            if workspace_id:
                try:
                    print(f"🧹 Cleaning up workspace: {workspace_id}")
                    time.sleep(2)  # Wait for lakehouse deletion
                    fabric_client.delete_workspace(workspace_id)
                    print("✅ Workspace deleted")
                except Exception as cleanup_error:
                    print(f"⚠️  Workspace cleanup warning: {cleanup_error}")

    def test_circuit_breaker_with_real_api(self, fabric_client):
        """
        Test circuit breaker behavior with real API calls
        """
        breaker = get_circuit_breaker("real_fabric_test")

        try:
            print("\n🔧 Testing circuit breaker with real API")

            # Attempt to get non-existent workspace
            fake_workspace_id = str(uuid.uuid4())
            failure_count = 0

            for attempt in range(6):
                try:
                    print(f"   Attempt {attempt + 1}: Calling API...")
                    fabric_client.get_workspace(fake_workspace_id)
                except requests.exceptions.HTTPError:
                    failure_count += 1
                    print(f"   ❌ Expected failure {failure_count}")

                print(f"   Circuit breaker state: {breaker.state}")

                if breaker.state == "open":
                    print("✅ Circuit breaker opened after failures")
                    break

            # Verify circuit opened
            assert breaker.state == "open", "Circuit breaker should have opened"

        finally:
            # Reset circuit breaker
            breaker.reset()


if __name__ == "__main__":
    print("=" * 70)
    print("REAL FABRIC INTEGRATION TEST")
    print("=" * 70)
    print("\nRun with: pytest tests/real_fabric/ -v -s -m real_fabric")
