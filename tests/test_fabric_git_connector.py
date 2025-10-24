"""
Unit tests for FabricGitConnector utility
"""
import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch

# Add utilities to path
UTILITIES_PATH = Path(__file__).parent.parent / "ops" / "scripts" / "utilities"
if str(UTILITIES_PATH) not in sys.path:
    sys.path.insert(0, str(UTILITIES_PATH))

from fabric_git_connector import FabricGitConnector, GitProviderType, GitConnectionState


class TestFabricGitConnector:
    """Test suite for FabricGitConnector"""
    
    @pytest.fixture
    def mock_fabric_client(self):
        """Create mock Fabric API client"""
        client = Mock()
        client.get_access_token.return_value = "mock-token"
        return client
    
    @pytest.fixture
    def connector(self, mock_fabric_client):
        """Create FabricGitConnector instance with mock client"""
        with patch.dict('os.environ', {
            'GIT_ORGANIZATION': 'test-org',
            'GIT_REPOSITORY': 'test-repo'
        }):
            return FabricGitConnector(fabric_client=mock_fabric_client)
    
    def test_initialize_git_connection(self, connector, mock_fabric_client):
        """Test initializing Git connection"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"remoteCommitHash": "abc123"}
        
        with patch('requests.post', return_value=mock_response):
            result = connector.initialize_git_connection(
                workspace_id="ws-123",
                git_provider_type="GitHub",
                organization_name="test-org",
                repository_name="test-repo",
                branch_name="main",
                directory_path="/data_products/test"
            )
            
            assert result is not None
            assert "remoteCommitHash" in result
    
    def test_commit_to_git(self, connector, mock_fabric_client):
        """Test committing workspace items to Git"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"commitId": "abc123"}
        
        with patch('requests.post', return_value=mock_response):
            result = connector.commit_to_git(
                workspace_id="ws-123",
                comment="Test commit",
                commit_mode="All"
            )
            
            assert result is not None
            assert "commitId" in result
    
    def test_update_from_git(self, connector, mock_fabric_client):
        """Test updating workspace from Git"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        
        with patch('requests.post', return_value=mock_response):
            result = connector.update_from_git(
                workspace_id="ws-123",
                allow_override=False,
                conflict_resolution="Workspace"
            )
            
            assert result is not None
    
    def test_disconnect_git(self, connector, mock_fabric_client):
        """Test disconnecting Git integration"""
        mock_response = Mock()
        mock_response.status_code = 200
        
        with patch('requests.post', return_value=mock_response):
            success = connector.disconnect_git(workspace_id="ws-123")
            assert success is True
    
    def test_get_git_status(self, connector, mock_fabric_client):
        """Test getting Git connection status"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "workspaceHead": "abc123",
            "remoteCommitHash": "def456"
        }
        
        with patch('requests.get', return_value=mock_response):
            status = connector.get_git_status(workspace_id="ws-123")
            
            assert status is not None
            assert "workspaceHead" in status
    
    def test_get_git_connection_state(self, connector, mock_fabric_client):
        """Test getting Git connection state"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "gitProviderDetails": {
                "gitProviderType": "GitHub"
            }
        }
        
        with patch('requests.get', return_value=mock_response):
            state = connector.get_git_connection_state(workspace_id="ws-123")
            assert state == GitConnectionState.CONNECTED
    
    def test_sync_workspace_bidirectional(self, connector, mock_fabric_client):
        """Test bidirectional sync (pull then commit)"""
        mock_update_response = Mock()
        mock_update_response.status_code = 200
        mock_update_response.json.return_value = {"status": "updated"}
        
        mock_commit_response = Mock()
        mock_commit_response.status_code = 200
        mock_commit_response.json.return_value = {"commitId": "abc123"}
        
        with patch('requests.post', side_effect=[mock_update_response, mock_commit_response]):
            result = connector.sync_workspace_bidirectional(
                workspace_id="ws-123",
                commit_message="Sync commit",
                pull_first=True
            )
            
            assert result is not None
            assert "commitId" in result
    
    def test_provider_type_enum(self):
        """Test GitProviderType enum values"""
        assert GitProviderType.GITHUB == "GitHub"
        assert GitProviderType.AZURE_DEVOPS == "AzureDevOps"
    
    def test_connection_state_enum(self):
        """Test GitConnectionState enum values"""
        assert GitConnectionState.CONNECTED == "Connected"
        assert GitConnectionState.DISCONNECTED == "Disconnected"
        assert GitConnectionState.NOT_SUPPORTED == "NotSupported"
    
    def test_missing_environment_variables(self):
        """Test behavior when environment variables are missing"""
        with patch.dict('os.environ', {}, clear=True):
            connector = FabricGitConnector()
            # Should still work but use None for org/repo
            assert connector.default_organization is None
            assert connector.default_repository is None
    
    def test_error_handling_on_failed_connection(self, connector, mock_fabric_client):
        """Test error handling when connection fails"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.raise_for_status.side_effect = Exception("Connection failed")
        
        with patch('requests.post', return_value=mock_response):
            with pytest.raises(Exception):
                connector.initialize_git_connection(
                    workspace_id="ws-123",
                    git_provider_type="GitHub",
                    organization_name="test-org",
                    repository_name="test-repo",
                    branch_name="main"
                )
    
    def test_commit_with_specific_items(self, connector, mock_fabric_client):
        """Test committing specific items to Git"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"commitId": "abc123"}
        
        items = [
            {"logicalId": "item-1", "displayName": "Item 1"},
            {"logicalId": "item-2", "displayName": "Item 2"}
        ]
        
        with patch('requests.post', return_value=mock_response):
            result = connector.commit_to_git(
                workspace_id="ws-123",
                comment="Commit specific items",
                items=items,
                commit_mode="Selective"
            )
            
            assert result is not None
    
    def test_update_with_conflict_resolution(self, connector, mock_fabric_client):
        """Test update from Git with conflict resolution strategy"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "resolved"}
        
        with patch('requests.post', return_value=mock_response):
            result = connector.update_from_git(
                workspace_id="ws-123",
                conflict_resolution="Git"  # Prefer Git version
            )
            
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
