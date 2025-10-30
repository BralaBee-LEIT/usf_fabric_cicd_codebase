"""
Unit tests for Git reliability improvements

Tests the enhanced Git connection functionality including:
- Pre-flight validation
- Retry logic with exponential backoff
- Error message formatting
- Manual fallback workflow
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock, call
from ops.scripts.utilities.fabric_git_connector import FabricGitConnector, GitConnectionState


class TestGitPreFlightValidation:
    """Test suite for validate_git_prerequisites method"""
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    def test_validate_prerequisites_success(self, mock_get_client):
        """Test successful pre-flight validation"""
        # Setup mocks
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock workspace exists
        mock_workspace_response = Mock()
        mock_workspace_response.json.return_value = {"displayName": "Test Workspace"}
        
        # Mock git connection state (not connected yet)
        mock_state_response = Mock()
        mock_state_response.json.return_value = {
            "gitConnectionState": GitConnectionState.DISCONNECTED
        }
        
        # Setup mock client responses
        def mock_request(method, endpoint, **kwargs):
            if "workspaces/" in endpoint and endpoint.endswith("git/status"):
                return mock_state_response
            elif "workspaces/" in endpoint:
                return mock_workspace_response
            return Mock()
        
        mock_client._make_request.side_effect = mock_request
        
        # Test
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        is_valid, error_msg = connector.validate_git_prerequisites(
            workspace_id="test-workspace-id",
            branch_name="main",
            directory_path="/"
        )
        
        assert is_valid is True
        assert error_msg is None
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    def test_validate_prerequisites_workspace_not_found(self, mock_get_client):
        """Test validation fails when workspace doesn't exist"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock workspace not found
        mock_client._make_request.side_effect = Exception("Workspace not found")
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        is_valid, error_msg = connector.validate_git_prerequisites(
            workspace_id="invalid-workspace",
            branch_name="main"
        )
        
        assert is_valid is False
        assert error_msg is not None
        assert "not found or not accessible" in error_msg
        assert "Troubleshooting:" in error_msg
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    def test_validate_prerequisites_already_connected(self, mock_get_client):
        """Test validation passes if workspace already connected"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock workspace exists
        mock_workspace_response = Mock()
        mock_workspace_response.json.return_value = {"displayName": "Test Workspace"}
        
        # Mock already connected state
        mock_state_response = Mock()
        mock_state_response.json.return_value = {
            "gitConnectionState": GitConnectionState.CONNECTED,
            "gitBranchName": "main",
            "gitDirectoryPath": "/"
        }
        
        def mock_request(method, endpoint, **kwargs):
            if "git/status" in endpoint:
                return mock_state_response
            return mock_workspace_response
        
        mock_client._make_request.side_effect = mock_request
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        is_valid, error_msg = connector.validate_git_prerequisites(
            workspace_id="test-workspace-id",
            branch_name="main"
        )
        
        # Should return success even if already connected
        assert is_valid is True
        assert error_msg is None


class TestGitRetryLogic:
    """Test suite for initialize_git_connection_with_retry method"""
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    @patch('ops.scripts.utilities.fabric_git_connector.time.sleep')
    def test_retry_success_on_first_attempt(self, mock_sleep, mock_get_client):
        """Test successful connection on first attempt"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        # Mock successful validation
        with patch.object(connector, 'validate_git_prerequisites') as mock_validate:
            mock_validate.return_value = (True, None)
            
            # Mock successful connection
            with patch.object(connector, 'initialize_git_connection') as mock_init:
                mock_init.return_value = {"status": "connected"}
                
                result = connector.initialize_git_connection_with_retry(
                    workspace_id="test-workspace",
                    branch_name="main",
                    max_retries=3
                )
                
                assert result == {"status": "connected"}
                assert mock_init.call_count == 1
                assert mock_sleep.call_count == 0  # No retries needed
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    @patch('ops.scripts.utilities.fabric_git_connector.time.sleep')
    def test_retry_success_on_second_attempt(self, mock_sleep, mock_get_client):
        """Test successful connection on second attempt with correct backoff"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        # Mock successful validation
        with patch.object(connector, 'validate_git_prerequisites') as mock_validate:
            mock_validate.return_value = (True, None)
            
            # Mock connection fails first time, succeeds second time
            with patch.object(connector, 'initialize_git_connection') as mock_init:
                mock_init.side_effect = [
                    Exception("Transient error"),
                    {"status": "connected"}
                ]
                
                result = connector.initialize_git_connection_with_retry(
                    workspace_id="test-workspace",
                    branch_name="main",
                    max_retries=3,
                    initial_backoff=2.0
                )
                
                assert result == {"status": "connected"}
                assert mock_init.call_count == 2
                assert mock_sleep.call_count == 1
                # Verify exponential backoff: 2.0 * (2^0) = 2.0 seconds
                mock_sleep.assert_called_with(2.0)
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    @patch('ops.scripts.utilities.fabric_git_connector.time.sleep')
    def test_retry_exhausted_all_attempts(self, mock_sleep, mock_get_client):
        """Test all retry attempts exhausted"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        # Mock successful validation
        with patch.object(connector, 'validate_git_prerequisites') as mock_validate:
            mock_validate.return_value = (True, None)
            
            # Mock connection always fails
            with patch.object(connector, 'initialize_git_connection') as mock_init:
                mock_init.side_effect = Exception("Persistent error")
                
                with pytest.raises(Exception) as exc_info:
                    connector.initialize_git_connection_with_retry(
                        workspace_id="test-workspace",
                        branch_name="main",
                        max_retries=3,
                        initial_backoff=2.0
                    )
                
                # Verify error message includes troubleshooting
                assert "failed after 3 attempts" in str(exc_info.value)
                assert "Troubleshooting steps:" in str(exc_info.value)
                assert "Documentation:" in str(exc_info.value)
                
                # Verify retry attempts
                assert mock_init.call_count == 3
                assert mock_sleep.call_count == 2  # Sleep between attempts
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    @patch('ops.scripts.utilities.fabric_git_connector.time.sleep')
    def test_exponential_backoff_timing(self, mock_sleep, mock_get_client):
        """Test exponential backoff timing is correct"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        with patch.object(connector, 'validate_git_prerequisites') as mock_validate:
            mock_validate.return_value = (True, None)
            
            with patch.object(connector, 'initialize_git_connection') as mock_init:
                mock_init.side_effect = Exception("Error")
                
                with pytest.raises(Exception):
                    connector.initialize_git_connection_with_retry(
                        workspace_id="test-workspace",
                        branch_name="main",
                        max_retries=3,
                        initial_backoff=2.0
                    )
                
                # Verify exponential backoff: 2s, 4s (2 sleeps for 3 attempts)
                expected_calls = [call(2.0), call(4.0)]
                assert mock_sleep.call_args_list == expected_calls
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    def test_retry_fails_on_invalid_prerequisites(self, mock_get_client):
        """Test retry aborts if pre-flight validation fails"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        # Mock failed validation
        with patch.object(connector, 'validate_git_prerequisites') as mock_validate:
            mock_validate.return_value = (False, "Workspace not found")
            
            with pytest.raises(ValueError) as exc_info:
                connector.initialize_git_connection_with_retry(
                    workspace_id="invalid-workspace",
                    branch_name="main"
                )
            
            assert "Pre-flight validation failed" in str(exc_info.value)
            assert "Workspace not found" in str(exc_info.value)


class TestManualFallback:
    """Test suite for manual fallback functionality"""
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    @patch('builtins.input')
    def test_manual_fallback_user_confirms_success(self, mock_input, mock_get_client):
        """Test manual fallback when user confirms successful connection"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock user confirms manual connection
        mock_input.return_value = "yes"
        
        # Mock connection state verification
        mock_state_response = Mock()
        mock_state_response.json.return_value = {
            "gitConnectionState": GitConnectionState.CONNECTED,
            "gitBranchName": "main",
            "gitDirectoryPath": "/"
        }
        mock_client._make_request.return_value = mock_state_response
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        result = connector.prompt_manual_connection(
            workspace_id="test-workspace",
            branch_name="main",
            wait_for_user=True
        )
        
        assert result is True
        mock_input.assert_called_once()
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    @patch('builtins.input')
    def test_manual_fallback_user_cancels(self, mock_input, mock_get_client):
        """Test manual fallback when user cancels"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock user cancels
        mock_input.return_value = "no"
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        result = connector.prompt_manual_connection(
            workspace_id="test-workspace",
            branch_name="main",
            wait_for_user=True
        )
        
        assert result is False
        mock_input.assert_called_once()
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    @patch('builtins.input')
    def test_manual_fallback_verification_fails(self, mock_input, mock_get_client):
        """Test manual fallback when verification shows not connected"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock user confirms but connection not actually established
        mock_input.return_value = "yes"
        
        mock_state_response = Mock()
        mock_state_response.json.return_value = {
            "gitConnectionState": GitConnectionState.DISCONNECTED
        }
        mock_client._make_request.return_value = mock_state_response
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        result = connector.prompt_manual_connection(
            workspace_id="test-workspace",
            branch_name="main",
            wait_for_user=True
        )
        
        assert result is False
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    def test_manual_fallback_skip_when_wait_disabled(self, mock_get_client):
        """Test manual fallback returns False when wait_for_user=False"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        result = connector.prompt_manual_connection(
            workspace_id="test-workspace",
            branch_name="main",
            wait_for_user=False
        )
        
        assert result is False


class TestErrorMessageFormatting:
    """Test suite for enhanced error messages"""
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    def test_error_message_includes_troubleshooting(self, mock_get_client):
        """Test that error messages include troubleshooting steps"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock connection failure
        mock_client._make_request.side_effect = Exception("400 Bad Request")
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        with pytest.raises(Exception) as exc_info:
            connector.initialize_git_connection(
                workspace_id="test-workspace",
                branch_name="main",
                directory_path="/"
            )
        
        error_msg = str(exc_info.value)
        
        # Verify enhanced error message structure
        assert "Common Issues & Solutions:" in error_msg
        assert "Documentation:" in error_msg
        assert "test-workspace" in error_msg
        assert "test-org/test-repo" in error_msg
        assert "main" in error_msg


class TestIntegration:
    """Integration tests for complete workflow"""
    
    @patch('ops.scripts.utilities.fabric_git_connector.get_fabric_client')
    @patch('ops.scripts.utilities.fabric_git_connector.time.sleep')
    @patch('builtins.input')
    def test_complete_workflow_with_manual_fallback(
        self, mock_input, mock_sleep, mock_get_client
    ):
        """Test complete workflow: retry fails, manual fallback succeeds"""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        connector = FabricGitConnector(
            organization_name="test-org",
            repository_name="test-repo"
        )
        
        # Test automated connection with retry (fails)
        with patch.object(connector, 'validate_git_prerequisites') as mock_validate:
            mock_validate.return_value = (True, None)
            
            with patch.object(connector, 'initialize_git_connection') as mock_init:
                mock_init.side_effect = Exception("Persistent error")
                
                with pytest.raises(Exception) as exc_info:
                    connector.initialize_git_connection_with_retry(
                        workspace_id="test-workspace",
                        branch_name="main",
                        max_retries=2
                    )
                
                assert "failed after 2 attempts" in str(exc_info.value)
        
        # Test manual fallback (succeeds)
        mock_input.return_value = "yes"
        mock_state_response = Mock()
        mock_state_response.json.return_value = {
            "gitConnectionState": GitConnectionState.CONNECTED,
            "gitBranchName": "main",
            "gitDirectoryPath": "/"
        }
        mock_client._make_request.return_value = mock_state_response
        
        result = connector.prompt_manual_connection(
            workspace_id="test-workspace",
            branch_name="main",
            wait_for_user=True
        )
        
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
