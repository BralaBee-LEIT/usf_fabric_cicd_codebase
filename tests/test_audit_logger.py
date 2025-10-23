"""
Unit tests for AuditLogger utility
"""
import pytest
import json
from pathlib import Path
from datetime import datetime
import sys
import tempfile
import shutil

# Add utilities to path
UTILITIES_PATH = Path(__file__).parent.parent / "ops" / "scripts" / "utilities"
if str(UTILITIES_PATH) not in sys.path:
    sys.path.insert(0, str(UTILITIES_PATH))

from audit_logger import AuditLogger, AuditEventType


class TestAuditLogger:
    """Test suite for AuditLogger"""
    
    @pytest.fixture
    def temp_audit_dir(self):
        """Create temporary audit directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def logger(self, temp_audit_dir):
        """Create AuditLogger instance with temporary directory"""
        audit_file = temp_audit_dir / "test_audit.jsonl"
        return AuditLogger(audit_file_path=str(audit_file))
    
    def test_log_workspace_creation(self, logger):
        """Test logging workspace creation event"""
        logger.log_workspace_creation(
            workspace_id="ws-123",
            workspace_name="Test Workspace",
            product_id="test_product",
            environment="dev"
        )
        
        events = logger.read_events(event_type=AuditEventType.WORKSPACE_CREATED)
        assert len(events) == 1
        assert events[0]["workspace_id"] == "ws-123"
        assert events[0]["workspace_name"] == "Test Workspace"
        assert events[0]["event_type"] == "workspace_created"
    
    def test_log_item_creation(self, logger):
        """Test logging item creation event"""
        logger.log_item_creation(
            workspace_id="ws-123",
            item_id="item-456",
            item_name="BRONZE_Test_Lakehouse",
            item_type="Lakehouse",
            validation_passed=True
        )
        
        events = logger.read_events(event_type=AuditEventType.ITEM_CREATED)
        assert len(events) == 1
        assert events[0]["item_id"] == "item-456"
        assert events[0]["item_name"] == "BRONZE_Test_Lakehouse"
        assert events[0]["validation_passed"] is True
    
    def test_log_git_connection(self, logger):
        """Test logging Git connection event"""
        logger.log_git_connection(
            workspace_id="ws-123",
            git_provider="GitHub",
            organization="test-org",
            repository="test-repo",
            branch="main",
            directory="/data_products/test"
        )
        
        events = logger.read_events(event_type=AuditEventType.GIT_CONNECTED)
        assert len(events) == 1
        assert events[0]["git_provider"] == "GitHub"
        assert events[0]["organization"] == "test-org"
        assert events[0]["branch"] == "main"
    
    def test_log_user_addition(self, logger):
        """Test logging user addition event"""
        logger.log_user_addition(
            workspace_id="ws-123",
            user_email="user@example.com",
            role="Admin",
            principal_type="User"
        )
        
        events = logger.read_events(event_type=AuditEventType.USER_ADDED)
        assert len(events) == 1
        assert events[0]["user_email"] == "user@example.com"
        assert events[0]["role"] == "Admin"
    
    def test_log_deployment_started(self, logger):
        """Test logging deployment started event"""
        logger.log_deployment_started(
            workspace_id="ws-123",
            deployment_id="deploy-789",
            deployment_type="full",
            target_environment="prod"
        )
        
        events = logger.read_events(event_type=AuditEventType.DEPLOYMENT_STARTED)
        assert len(events) == 1
        assert events[0]["deployment_id"] == "deploy-789"
        assert events[0]["target_environment"] == "prod"
    
    def test_log_validation_passed(self, logger):
        """Test logging validation passed event"""
        logger.log_validation_passed(
            item_name="BRONZE_Test_Lakehouse",
            item_type="Lakehouse",
            validation_details={"pattern": "medallion"}
        )
        
        events = logger.read_events(event_type=AuditEventType.VALIDATION_PASSED)
        assert len(events) == 1
        assert events[0]["item_name"] == "BRONZE_Test_Lakehouse"
        assert events[0]["validation_details"]["pattern"] == "medallion"
    
    def test_read_events_by_workspace(self, logger):
        """Test filtering events by workspace ID"""
        logger.log_workspace_creation(
            workspace_id="ws-123",
            workspace_name="Workspace 1"
        )
        logger.log_workspace_creation(
            workspace_id="ws-456",
            workspace_name="Workspace 2"
        )
        
        events = logger.read_events(workspace_id="ws-123")
        assert len(events) == 1
        assert events[0]["workspace_id"] == "ws-123"
    
    def test_read_events_by_date_range(self, logger):
        """Test filtering events by date range"""
        logger.log_workspace_creation(
            workspace_id="ws-123",
            workspace_name="Test Workspace"
        )
        
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = datetime.now().replace(day=datetime.now().day + 1).strftime("%Y-%m-%d")
        
        events = logger.read_events(start_date=today, end_date=tomorrow)
        assert len(events) >= 1
    
    def test_generate_compliance_report(self, logger):
        """Test compliance report generation"""
        # Log various events
        logger.log_workspace_creation(workspace_id="ws-1", workspace_name="WS1")
        logger.log_item_creation(workspace_id="ws-1", item_id="i-1", item_name="Test", item_type="Lakehouse", validation_passed=True)
        logger.log_validation_passed(item_name="Test", item_type="Lakehouse")
        logger.log_deployment_started(workspace_id="ws-1", deployment_id="d-1")
        
        report = logger.generate_compliance_report()
        
        assert "total_events" in report
        assert "event_breakdown" in report
        assert report["total_events"] >= 4
        assert "workspace_created" in report["event_breakdown"]
    
    def test_jsonl_format_validity(self, logger, temp_audit_dir):
        """Test that audit log is valid JSONL format"""
        logger.log_workspace_creation(
            workspace_id="ws-123",
            workspace_name="Test Workspace"
        )
        
        audit_file = temp_audit_dir / "test_audit.jsonl"
        with open(audit_file, 'r') as f:
            for line in f:
                # Each line should be valid JSON
                event = json.loads(line.strip())
                assert "timestamp" in event
                assert "event_type" in event
    
    def test_git_context_capture(self, logger):
        """Test that Git context is captured in events"""
        logger.log_workspace_creation(
            workspace_id="ws-123",
            workspace_name="Test Workspace"
        )
        
        events = logger.read_events()
        # Git context fields should be present (even if None)
        assert "git_commit" in events[0]
        assert "git_branch" in events[0]
        assert "git_user" in events[0]
    
    def test_multiple_event_types(self, logger):
        """Test logging multiple different event types"""
        logger.log_workspace_creation(workspace_id="ws-1", workspace_name="WS1")
        logger.log_item_creation(workspace_id="ws-1", item_id="i-1", item_name="Test", item_type="Lakehouse")
        logger.log_git_connection(workspace_id="ws-1", git_provider="GitHub", organization="org", repository="repo", branch="main")
        logger.log_user_addition(workspace_id="ws-1", user_email="user@test.com", role="Admin")
        
        all_events = logger.read_events()
        assert len(all_events) == 4
        
        event_types = [e["event_type"] for e in all_events]
        assert "workspace_created" in event_types
        assert "item_created" in event_types
        assert "git_connected" in event_types
        assert "user_added" in event_types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
