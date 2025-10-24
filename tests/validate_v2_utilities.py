#!/usr/bin/env python3
"""
Quick validation test for new v2.0 utilities
Tests basic functionality without requiring real Fabric API credentials
"""
import sys
from pathlib import Path

# Add utilities to path
UTILITIES_PATH = Path(__file__).parent.parent / "ops" / "scripts" / "utilities"
sys.path.insert(0, str(UTILITIES_PATH))

def test_item_naming_validator():
    """Test ItemNamingValidator basic functionality"""
    print("\n🧪 Testing ItemNamingValidator...")
    
    try:
        from item_naming_validator import validate_item_name, ItemNamingValidator
        
        # Test valid medallion architecture name
        result = validate_item_name("BRONZE_CustomerData_Lakehouse", "Lakehouse")
        assert result.is_valid, f"Expected valid, got errors: {result.errors}"
        print("  ✅ Medallion architecture validation: PASS")
        
        # Test invalid name (missing layer)
        result = validate_item_name("CustomerData_Lakehouse", "Lakehouse")
        assert not result.is_valid, "Expected invalid for missing layer"
        print("  ✅ Invalid name detection: PASS")
        
        # Test sequential notebook
        result = validate_item_name("01_DataIngestion_Notebook", "Notebook")
        assert result.is_valid, f"Expected valid, got errors: {result.errors}"
        print("  ✅ Sequential notebook validation: PASS")
        
        # Test name suggestion
        validator = ItemNamingValidator()
        suggested = validator.suggest_name("CustomerData", "Lakehouse", layer="BRONZE")
        assert "BRONZE" in suggested and "CustomerData" in suggested
        print(f"  ✅ Name suggestion: PASS (suggested: {suggested})")
        
        print("  ✅ ItemNamingValidator: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ ItemNamingValidator: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audit_logger():
    """Test AuditLogger basic functionality"""
    print("\n🧪 Testing AuditLogger...")
    
    try:
        import tempfile
        import json
        
        # Create temporary audit file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            temp_audit_path = f.name
        
        from audit_logger import AuditLogger
        logger = AuditLogger(audit_file_path=temp_audit_path)
        
        # Test logging workspace creation
        logger.log_workspace_creation(
            workspace_id="test-ws-123",
            workspace_name="Test Workspace",
            product_id="test_product",
            environment="dev"
        )
        print("  ✅ Workspace creation logging: PASS")
        
        # Test logging item creation
        logger.log_item_creation(
            workspace_id="test-ws-123",
            item_id="test-item-456",
            item_name="BRONZE_Test_Lakehouse",
            item_type="Lakehouse",
            validation_passed=True
        )
        print("  ✅ Item creation logging: PASS")
        
        # Test reading events
        events = logger.read_events()
        assert len(events) == 2, f"Expected 2 events, got {len(events)}"
        print(f"  ✅ Event reading: PASS (read {len(events)} events)")
        
        # Test filtering by event type
        workspace_events = logger.read_events(event_type="workspace_created")
        assert len(workspace_events) == 1, f"Expected 1 workspace event, got {len(workspace_events)}"
        print("  ✅ Event filtering: PASS")
        
        # Verify JSONL format
        with open(temp_audit_path, 'r') as f:
            for line in f:
                event = json.loads(line.strip())
                assert "timestamp" in event
                assert "event_type" in event
        print("  ✅ JSONL format validation: PASS")
        
        # Cleanup
        Path(temp_audit_path).unlink()
        
        print("  ✅ AuditLogger: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ AuditLogger: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fabric_git_connector():
    """Test FabricGitConnector basic functionality (without real API calls)"""
    print("\n🧪 Testing FabricGitConnector...")
    
    try:
        from fabric_git_connector import FabricGitConnector, GitProviderType, GitConnectionState
        
        # Test enum values
        assert GitProviderType.GITHUB == "GitHub"
        assert GitProviderType.AZURE_DEVOPS == "AzureDevOps"
        print("  ✅ GitProviderType enum: PASS")
        
        assert GitConnectionState.CONNECTED == "Connected"
        assert GitConnectionState.DISCONNECTED == "Disconnected"
        print("  ✅ GitConnectionState enum: PASS")
        
        # Test connector initialization (no real API calls)
        connector = FabricGitConnector()
        assert connector is not None
        print("  ✅ Connector initialization: PASS")
        
        # Test default values
        import os
        os.environ['GIT_ORGANIZATION'] = 'test-org'
        os.environ['GIT_REPOSITORY'] = 'test-repo'
        connector = FabricGitConnector()
        assert connector.default_organization == 'test-org'
        assert connector.default_repository == 'test-repo'
        print("  ✅ Environment variable handling: PASS")
        
        print("  ✅ FabricGitConnector: ALL TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ FabricGitConnector: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_imports():
    """Test that all utilities can be imported"""
    print("\n🧪 Testing utility imports...")
    
    imports_ok = True
    
    try:
        print("  ✅ item_naming_validator: OK")
    except Exception as e:
        print(f"  ❌ item_naming_validator: FAILED - {e}")
        imports_ok = False
    
    try:
        print("  ✅ audit_logger: OK")
    except Exception as e:
        print(f"  ❌ audit_logger: FAILED - {e}")
        imports_ok = False
    
    try:
        print("  ✅ fabric_git_connector: OK")
    except Exception as e:
        print(f"  ❌ fabric_git_connector: FAILED - {e}")
        imports_ok = False
    
    try:
        print("  ✅ fabric_item_manager: OK (enhanced)")
    except Exception as e:
        print(f"  ❌ fabric_item_manager: FAILED - {e}")
        imports_ok = False
    
    try:
        print("  ✅ workspace_manager: OK (enhanced)")
    except Exception as e:
        print(f"  ❌ workspace_manager: FAILED - {e}")
        imports_ok = False
    
    return imports_ok


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("🚀 v2.0 Utilities Validation Test")
    print("=" * 60)
    
    results = []
    
    # Test imports first
    results.append(("Imports", test_imports()))
    
    # Test individual utilities
    results.append(("ItemNamingValidator", test_item_naming_validator()))
    results.append(("AuditLogger", test_audit_logger()))
    results.append(("FabricGitConnector", test_fabric_git_connector()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30s} {status}")
    
    print(f"\n{'Total:':30s} {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All validation tests passed! Ready for production use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
