"""
Unit tests for workspace_manager module
Tests workspace and user management operations
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import requests
from ops.scripts.utilities.workspace_manager import (
    WorkspaceManager,
    WorkspaceRole,
    CapacityType,
    create_workspace_for_environment,
    setup_complete_environment,
)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables"""
    monkeypatch.setenv("AZURE_TENANT_ID", "test-tenant-id")
    monkeypatch.setenv("AZURE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "test-client-secret")


@pytest.fixture
def workspace_manager(mock_env_vars):
    """Create WorkspaceManager instance with mocked environment"""
    with patch("ops.scripts.utilities.workspace_manager.get_config_manager"):
        return WorkspaceManager(environment="dev")


@pytest.fixture
def mock_workspace_response():
    """Mock workspace API response"""
    return {
        "id": "workspace-123",
        "displayName": "test-workspace-dev",
        "type": "Workspace",
        "capacityId": "capacity-456",
        "state": "Active",
    }


@pytest.fixture
def mock_user_response():
    """Mock user API response"""
    return {
        "identifier": "user@example.com",
        "principalType": "User",
        "workspaceRole": "Admin",
    }


class TestWorkspaceManagerInitialization:
    """Test WorkspaceManager initialization"""

    def test_init_with_valid_credentials(self, mock_env_vars):
        """Test initialization with valid credentials"""
        with patch("ops.scripts.utilities.workspace_manager.get_config_manager"):
            manager = WorkspaceManager(environment="dev")
            assert manager.environment == "dev"
            assert manager.tenant_id == "test-tenant-id"
            assert manager.client_id == "test-client-id"

    def test_init_without_credentials(self, monkeypatch):
        """Test initialization fails without credentials"""
        monkeypatch.delenv("AZURE_TENANT_ID", raising=False)
        monkeypatch.delenv("AZURE_CLIENT_ID", raising=False)
        monkeypatch.delenv("AZURE_CLIENT_SECRET", raising=False)

        with pytest.raises(ValueError, match="Missing required Azure credentials"):
            WorkspaceManager()

    def test_init_with_invalid_environment(self, mock_env_vars):
        """Test initialization with invalid environment"""
        with patch("ops.scripts.utilities.workspace_manager.get_config_manager"):
            with pytest.raises(ValueError, match="Invalid environment"):
                WorkspaceManager(environment="invalid")

    def test_init_without_environment(self, mock_env_vars):
        """Test initialization without environment (all workspaces)"""
        with patch("ops.scripts.utilities.workspace_manager.get_config_manager"):
            manager = WorkspaceManager()
            assert manager.environment is None


class TestWorkspaceOperations:
    """Test workspace CRUD operations"""

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_create_workspace(
        self, mock_token, mock_request, workspace_manager, mock_workspace_response
    ):
        """Test creating a workspace"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_response.json.return_value = mock_workspace_response
        mock_request.return_value = mock_response

        result = workspace_manager.create_workspace(
            name="test-workspace", description="Test workspace"
        )

        assert result["id"] == "workspace-123"
        assert result["displayName"] == "test-workspace-dev"
        mock_request.assert_called_once()

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_create_workspace_duplicate_error(
        self, mock_token, mock_request, workspace_manager
    ):
        """Test creating duplicate workspace raises error"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_response.status_code = 409
        mock_response.ok = False
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_request.side_effect = requests.exceptions.HTTPError(response=mock_response)

        with pytest.raises(ValueError, match="already exists"):
            workspace_manager.create_workspace(name="duplicate-workspace")

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_list_workspaces(
        self, mock_token, mock_request, workspace_manager, mock_workspace_response
    ):
        """Test listing workspaces"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": [
                mock_workspace_response,
                {**mock_workspace_response, "id": "workspace-456"},
            ]
        }
        mock_request.return_value = mock_response

        result = workspace_manager.list_workspaces(filter_by_environment=False)

        assert len(result) == 2
        assert result[0]["id"] == "workspace-123"
        mock_request.assert_called_once()

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_list_workspaces_filtered_by_environment(
        self, mock_token, mock_request, workspace_manager
    ):
        """Test listing workspaces filtered by environment"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": [
                {"id": "1", "displayName": "workspace-dev"},
                {"id": "2", "displayName": "workspace-test"},
                {"id": "3", "displayName": "workspace-prod"},
            ]
        }
        mock_request.return_value = mock_response

        result = workspace_manager.list_workspaces(filter_by_environment=True)

        # Should only return dev workspaces
        assert len(result) == 1
        assert result[0]["displayName"] == "workspace-dev"

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_get_workspace_details(
        self, mock_token, mock_request, workspace_manager, mock_workspace_response
    ):
        """Test getting workspace details"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_response.json.return_value = mock_workspace_response
        mock_request.return_value = mock_response

        result = workspace_manager.get_workspace_details("workspace-123")

        assert result["id"] == "workspace-123"
        assert result["displayName"] == "test-workspace-dev"
        mock_request.assert_called_once_with("GET", "v1/workspaces/workspace-123")

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch(
        "ops.scripts.utilities.workspace_manager.WorkspaceManager.get_workspace_details"
    )
    @patch(
        "ops.scripts.utilities.workspace_manager.WorkspaceManager.list_workspace_items"
    )
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_delete_workspace(
        self,
        mock_token,
        mock_items,
        mock_details,
        mock_request,
        workspace_manager,
        mock_workspace_response,
    ):
        """Test deleting a workspace"""
        mock_token.return_value = "test-token"
        mock_details.return_value = mock_workspace_response
        mock_items.return_value = []  # Empty workspace
        mock_response = Mock()
        mock_request.return_value = mock_response

        result = workspace_manager.delete_workspace("workspace-123")

        assert result is True
        mock_request.assert_called_once_with("DELETE", "v1/workspaces/workspace-123")

    @patch(
        "ops.scripts.utilities.workspace_manager.WorkspaceManager.get_workspace_details"
    )
    @patch(
        "ops.scripts.utilities.workspace_manager.WorkspaceManager.list_workspace_items"
    )
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_delete_workspace_with_items_error(
        self,
        mock_token,
        mock_items,
        mock_details,
        workspace_manager,
        mock_workspace_response,
    ):
        """Test deleting workspace with items raises error"""
        mock_token.return_value = "test-token"
        mock_details.return_value = mock_workspace_response
        mock_items.return_value = [{"id": "item-1", "type": "Notebook"}]

        with pytest.raises(ValueError, match="contains .* items"):
            workspace_manager.delete_workspace("workspace-123", force=False)

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_update_workspace(
        self, mock_token, mock_request, workspace_manager, mock_workspace_response
    ):
        """Test updating workspace"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_response.json.return_value = {
            **mock_workspace_response,
            "displayName": "updated-workspace-dev",
        }
        mock_request.return_value = mock_response

        result = workspace_manager.update_workspace(
            "workspace-123", name="updated-workspace", description="Updated description"
        )

        assert result["displayName"] == "updated-workspace-dev"
        mock_request.assert_called_once()


class TestUserManagement:
    """Test user management operations"""

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_add_user(
        self, mock_token, mock_request, workspace_manager, mock_user_response
    ):
        """Test adding user to workspace"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_response.json.return_value = mock_user_response
        mock_request.return_value = mock_response

        result = workspace_manager.add_user(
            "workspace-123", "user@example.com", role=WorkspaceRole.ADMIN
        )

        assert result["identifier"] == "user@example.com"
        assert result["workspaceRole"] == "Admin"
        mock_request.assert_called_once()

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_add_user_duplicate_error(
        self, mock_token, mock_request, workspace_manager
    ):
        """Test adding duplicate user raises error"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_response.status_code = 409
        mock_response.ok = False
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_request.side_effect = requests.exceptions.HTTPError(response=mock_response)

        with pytest.raises(ValueError, match="already has access"):
            workspace_manager.add_user("workspace-123", "user@example.com")

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_remove_user(self, mock_token, mock_request, workspace_manager):
        """Test removing user from workspace"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_request.return_value = mock_response

        result = workspace_manager.remove_user("workspace-123", "user@example.com")

        assert result is True
        mock_request.assert_called_once_with(
            "DELETE", "v1/workspaces/workspace-123/roleAssignments/user@example.com"
        )

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_list_users(
        self, mock_token, mock_request, workspace_manager, mock_user_response
    ):
        """Test listing users in workspace"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_response.json.return_value = {
            "value": [
                mock_user_response,
                {
                    **mock_user_response,
                    "identifier": "user2@example.com",
                    "workspaceRole": "Member",
                },
            ]
        }
        mock_request.return_value = mock_response

        result = workspace_manager.list_users("workspace-123")

        assert len(result) == 2
        assert result[0]["identifier"] == "user@example.com"
        assert result[1]["workspaceRole"] == "Member"

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._make_request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_update_user_role(
        self, mock_token, mock_request, workspace_manager, mock_user_response
    ):
        """Test updating user role"""
        mock_token.return_value = "test-token"
        mock_response = Mock()
        mock_response.json.return_value = {
            **mock_user_response,
            "workspaceRole": "Contributor",
        }
        mock_request.return_value = mock_response

        result = workspace_manager.update_user_role(
            "workspace-123", "user@example.com", WorkspaceRole.CONTRIBUTOR
        )

        assert result["workspaceRole"] == "Contributor"
        mock_request.assert_called_once()


class TestBulkOperations:
    """Test bulk operations"""

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager.create_workspace")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_create_workspace_set(
        self, mock_token, mock_create, workspace_manager, mock_workspace_response
    ):
        """Test creating workspace set for multiple environments"""
        mock_token.return_value = "test-token"
        mock_create.return_value = mock_workspace_response

        # Create manager without environment for bulk operation
        manager = WorkspaceManager()
        manager.token = "test-token"

        with patch("ops.scripts.utilities.workspace_manager.get_config_manager"):
            result = manager.create_workspace_set(
                "test-workspace", environments=["dev", "test"]
            )

        assert len(result) == 2
        assert "dev" in result
        assert "test" in result
        assert mock_create.call_count == 2

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager.list_users")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager.add_user")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_copy_users_between_workspaces(
        self, mock_token, mock_add, mock_list, workspace_manager
    ):
        """Test copying users between workspaces"""
        mock_token.return_value = "test-token"
        mock_list.return_value = [
            {
                "identifier": "user1@example.com",
                "principalType": "User",
                "workspaceRole": "Admin",
            },
            {
                "identifier": "user2@example.com",
                "principalType": "User",
                "workspaceRole": "Member",
            },
        ]
        mock_add.return_value = {}

        result = workspace_manager.copy_users_between_workspaces(
            "source-workspace", "target-workspace"
        )

        assert len(result["success"]) == 2
        assert mock_add.call_count == 2


class TestErrorHandling:
    """Test error handling and retry logic"""

    @patch("ops.scripts.utilities.workspace_manager.requests.request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_retry_on_rate_limit(self, mock_token, mock_request, workspace_manager):
        """Test retry logic on rate limiting (429)"""
        mock_token.return_value = "test-token"

        # First call returns 429, second call succeeds
        mock_response_429 = Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "1"}
        mock_response_429.ok = False

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.ok = True
        mock_response_success.json.return_value = {"id": "workspace-123"}

        mock_request.side_effect = [mock_response_429, mock_response_success]

        with patch("time.sleep"):  # Mock sleep to speed up test
            result = workspace_manager._make_request("GET", "v1/workspaces")

        assert result.json()["id"] == "workspace-123"
        assert mock_request.call_count == 2

    @patch("ops.scripts.utilities.workspace_manager.requests.request")
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager._get_access_token")
    def test_retry_on_transient_error(
        self, mock_token, mock_request, workspace_manager
    ):
        """Test retry logic on transient errors (500, 502, 503)"""
        mock_token.return_value = "test-token"

        # First call returns 503, second call succeeds
        mock_response_503 = Mock()
        mock_response_503.status_code = 503
        mock_response_503.ok = False

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.ok = True
        mock_response_success.json.return_value = {"id": "workspace-123"}

        mock_request.side_effect = [mock_response_503, mock_response_success]

        with patch("time.sleep"):  # Mock sleep to speed up test
            result = workspace_manager._make_request("GET", "v1/workspaces")

        assert result.json()["id"] == "workspace-123"
        assert mock_request.call_count == 2


class TestConvenienceFunctions:
    """Test convenience functions"""

    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager.create_workspace")
    @patch("ops.scripts.utilities.workspace_manager.get_config_manager")
    def test_create_workspace_for_environment(
        self, mock_config, mock_create, mock_env_vars, mock_workspace_response
    ):
        """Test convenience function for creating workspace"""
        mock_create.return_value = mock_workspace_response

        result = create_workspace_for_environment(
            "test-workspace", "dev", "Test workspace"
        )

        assert result["id"] == "workspace-123"
        mock_create.assert_called_once()

    @patch(
        "ops.scripts.utilities.workspace_manager.WorkspaceManager.create_workspace_set"
    )
    @patch("ops.scripts.utilities.workspace_manager.WorkspaceManager.add_user")
    @patch("ops.scripts.utilities.workspace_manager.get_config_manager")
    def test_setup_complete_environment(
        self, mock_config, mock_add, mock_create_set, mock_env_vars
    ):
        """Test convenience function for setting up complete environment"""
        mock_create_set.return_value = {
            "dev": {"id": "workspace-dev", "displayName": "project-dev"},
            "test": {"id": "workspace-test", "displayName": "project-test"},
            "prod": {"id": "workspace-prod", "displayName": "project-prod"},
        }
        mock_add.return_value = {}

        result = setup_complete_environment(
            "test-project", ["admin@example.com"], ["member@example.com"]
        )

        assert len(result) == 3
        assert "dev" in result
        assert "test" in result
        assert "prod" in result
        # Should call add_user for each workspace (3) x each user (2) = 6 times
        assert mock_add.call_count == 6
