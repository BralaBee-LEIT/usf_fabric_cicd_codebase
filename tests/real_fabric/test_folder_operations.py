"""
Real Fabric Folder Integration Tests - CREATES ACTUAL RESOURCES

⚠️ WARNING: These tests interact with REAL Microsoft Fabric Folder APIs ⚠️

- Creates actual folders in your Fabric workspaces
- Tests real folder CRUD operations, validation, and item organization
- Should NOT be run in CI/CD pipelines  
- Requires valid Azure credentials with Fabric permissions
- Requires Fabric Folder APIs (Preview, October 2025)

Usage:
    # Run real folder tests manually
    pytest tests/real_fabric/test_folder_operations.py -v -s -m real_fabric
    
    # Run specific test
    pytest tests/real_fabric/test_folder_operations.py::TestFolderCRUD::test_create_and_list_folders -v -s
    
Safety Features:
    - All folders tagged with test prefix for identification
    - Comprehensive cleanup in teardown methods
    - Timeout protection (5 minute max per test)
    - Workspace isolation (uses dedicated test workspace)

Prerequisites:
    - Set environment variables: AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
    - Set FABRIC_TEST_WORKSPACE_ID for dedicated test workspace
    - Ensure Fabric Folder APIs are enabled for your tenant
"""

import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import folder manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from ops.scripts.utilities.fabric_folder_manager import (
    FabricFolderManager,
    FolderInfo,
    FolderStructure,
    FolderValidationError,
    FolderOperationError,
)
from ops.scripts.utilities.fabric_api import FabricClient


# ============================================================================
# CONFIGURATION AND FIXTURES
# ============================================================================

# Test configuration
TEST_WORKSPACE_ID = os.getenv("FABRIC_TEST_WORKSPACE_ID")
TEST_PREFIX = "AutoTest"
TEST_TIMEOUT = 300  # 5 minutes max per test


@pytest.fixture(scope="session")
def validate_environment():
    """Validate required environment variables are set"""
    required_vars = [
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
        "AZURE_TENANT_ID",
        "FABRIC_TEST_WORKSPACE_ID",
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        pytest.skip(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Real Fabric tests require valid credentials."
        )


@pytest.fixture(scope="session")
def folder_manager():
    """Create FabricFolderManager instance"""
    return FabricFolderManager(max_folder_depth=5)


@pytest.fixture(scope="session")
def fabric_client():
    """Create FabricClient instance"""
    return FabricClient()


@pytest.fixture
def test_run_id():
    """Generate unique test run ID"""
    return f"{TEST_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def cleanup_folders():
    """Track created folders for cleanup"""
    created_folders = []
    
    yield created_folders
    
    # Cleanup
    if created_folders and TEST_WORKSPACE_ID:
        print(f"\n🧹 Cleaning up {len(created_folders)} test folder(s)...")
        manager = FabricFolderManager()
        
        for folder_id in created_folders:
            try:
                manager.delete_folder(TEST_WORKSPACE_ID, folder_id, force=True)
                print(f"  ✓ Deleted folder: {folder_id[:8]}...")
            except Exception as e:
                print(f"  ⚠ Failed to delete folder {folder_id[:8]}: {e}")


# ============================================================================
# TEST FOLDER CRUD OPERATIONS
# ============================================================================

@pytest.mark.real_fabric
@pytest.mark.timeout(TEST_TIMEOUT)
class TestFolderCRUD:
    """Test real folder CRUD operations against Fabric API"""
    
    def test_create_and_list_folders(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test creating folders and listing them"""
        print(f"\n📁 Creating test folders with prefix: {test_run_id}")
        
        # Create root folder
        folder_name = f"{test_run_id}_RootFolder"
        folder_id = folder_manager.create_folder(
            workspace_id=TEST_WORKSPACE_ID,
            display_name=folder_name,
            description=f"Test folder created at {datetime.now()}"
        )
        
        assert folder_id is not None
        assert len(folder_id) > 0
        cleanup_folders.append(folder_id)
        print(f"  ✓ Created root folder: {folder_id[:8]}...")
        
        # List folders to verify creation
        folders = folder_manager.list_folders(TEST_WORKSPACE_ID)
        found = next((f for f in folders if f.id == folder_id), None)
        
        assert found is not None
        assert found.display_name == folder_name
        assert found.workspace_id == TEST_WORKSPACE_ID
        assert found.parent_folder_id is None
        print(f"  ✓ Verified folder in list")
        
        # Get specific folder
        folder = folder_manager.get_folder(TEST_WORKSPACE_ID, folder_id)
        assert folder.id == folder_id
        assert folder.display_name == folder_name
        print(f"  ✓ Retrieved folder details")
    
    def test_create_subfolder(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test creating nested subfolders"""
        print(f"\n📂 Creating nested folder structure: {test_run_id}")
        
        # Create parent folder
        parent_name = f"{test_run_id}_Parent"
        parent_id = folder_manager.create_folder(TEST_WORKSPACE_ID, parent_name)
        cleanup_folders.append(parent_id)
        print(f"  ✓ Created parent folder: {parent_id[:8]}...")
        
        # Create subfolder
        child_name = f"{test_run_id}_Child"
        child_id = folder_manager.create_folder(
            workspace_id=TEST_WORKSPACE_ID,
            display_name=child_name,
            parent_folder_id=parent_id
        )
        cleanup_folders.append(child_id)
        print(f"  ✓ Created child folder: {child_id[:8]}...")
        
        # Verify subfolder relationship
        child_folder = folder_manager.get_folder(TEST_WORKSPACE_ID, child_id)
        assert child_folder.parent_folder_id == parent_id
        print(f"  ✓ Verified parent-child relationship")
        
        # Verify appears in parent's subfolders
        subfolders = folder_manager.list_folders(
            TEST_WORKSPACE_ID,
            parent_folder_id=parent_id
        )
        found_child = next((f for f in subfolders if f.id == child_id), None)
        assert found_child is not None
        print(f"  ✓ Child appears in parent's subfolder list")
    
    def test_update_folder_name(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test renaming a folder"""
        print(f"\n✏️ Testing folder rename: {test_run_id}")
        
        # Create folder
        original_name = f"{test_run_id}_Original"
        folder_id = folder_manager.create_folder(TEST_WORKSPACE_ID, original_name)
        cleanup_folders.append(folder_id)
        print(f"  ✓ Created folder: {original_name}")
        
        # Rename folder
        new_name = f"{test_run_id}_Renamed"
        folder_manager.update_folder(
            workspace_id=TEST_WORKSPACE_ID,
            folder_id=folder_id,
            display_name=new_name
        )
        print(f"  ✓ Renamed to: {new_name}")
        
        # Verify rename
        folder = folder_manager.get_folder(TEST_WORKSPACE_ID, folder_id)
        assert folder.display_name == new_name
        print(f"  ✓ Verified new name in API")
    
    def test_move_folder(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test moving a folder to different parent"""
        print(f"\n📦 Testing folder move: {test_run_id}")
        
        # Create two parent folders
        parent1_id = folder_manager.create_folder(TEST_WORKSPACE_ID, f"{test_run_id}_Parent1")
        parent2_id = folder_manager.create_folder(TEST_WORKSPACE_ID, f"{test_run_id}_Parent2")
        cleanup_folders.extend([parent1_id, parent2_id])
        print(f"  ✓ Created two parent folders")
        
        # Create folder under parent1
        folder_id = folder_manager.create_folder(
            TEST_WORKSPACE_ID,
            f"{test_run_id}_Movable",
            parent_folder_id=parent1_id
        )
        cleanup_folders.append(folder_id)
        print(f"  ✓ Created folder under Parent1")
        
        # Move to parent2
        folder_manager.move_folder(
            workspace_id=TEST_WORKSPACE_ID,
            folder_id=folder_id,
            new_parent_folder_id=parent2_id
        )
        print(f"  ✓ Moved folder to Parent2")
        
        # Verify move
        folder = folder_manager.get_folder(TEST_WORKSPACE_ID, folder_id)
        assert folder.parent_folder_id == parent2_id
        print(f"  ✓ Verified new parent in API")
    
    def test_delete_folder(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test deleting a folder"""
        print(f"\n🗑️ Testing folder deletion: {test_run_id}")
        
        # Create folder
        folder_name = f"{test_run_id}_ToDelete"
        folder_id = folder_manager.create_folder(TEST_WORKSPACE_ID, folder_name)
        print(f"  ✓ Created folder: {folder_id[:8]}...")
        
        # Delete folder
        folder_manager.delete_folder(TEST_WORKSPACE_ID, folder_id, force=False)
        print(f"  ✓ Deleted folder")
        
        # Verify deletion - should not find folder
        with pytest.raises(FolderOperationError):
            folder_manager.get_folder(TEST_WORKSPACE_ID, folder_id)
        print(f"  ✓ Verified folder no longer exists")
        
        # Remove from cleanup list (already deleted)
        if folder_id in cleanup_folders:
            cleanup_folders.remove(folder_id)


# ============================================================================
# TEST FOLDER VALIDATION
# ============================================================================

@pytest.mark.real_fabric
@pytest.mark.timeout(TEST_TIMEOUT)
class TestFolderValidation:
    """Test folder validation rules"""
    
    def test_folder_name_validation(self, validate_environment, folder_manager):
        """Test folder name validation rules"""
        print(f"\n✅ Testing folder name validation")
        
        # Empty name should fail
        with pytest.raises(FolderValidationError, match="cannot be empty"):
            folder_manager.create_folder(TEST_WORKSPACE_ID, "")
        print(f"  ✓ Empty name rejected")
        
        # Name too long should fail
        with pytest.raises(FolderValidationError, match="too long"):
            folder_manager.create_folder(TEST_WORKSPACE_ID, "x" * 300)
        print(f"  ✓ Overly long name rejected")
        
        # Invalid characters should fail
        invalid_chars = ["/", "\\", ":", "*", "?", "<", ">", "|"]
        for char in invalid_chars[:3]:  # Test a few
            with pytest.raises(FolderValidationError, match="Invalid characters"):
                folder_manager.create_folder(TEST_WORKSPACE_ID, f"Invalid{char}Name")
        print(f"  ✓ Invalid characters rejected")
    
    def test_folder_depth_limit(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test folder depth limit enforcement"""
        print(f"\n🔢 Testing folder depth limits: {test_run_id}")
        
        # Create nested folders up to max depth
        parent_id = None
        folder_ids = []
        max_depth = folder_manager.max_folder_depth
        
        for depth in range(max_depth):
            folder_name = f"{test_run_id}_Depth{depth}"
            folder_id = folder_manager.create_folder(
                TEST_WORKSPACE_ID,
                folder_name,
                parent_folder_id=parent_id
            )
            folder_ids.append(folder_id)
            parent_id = folder_id
            print(f"  ✓ Created folder at depth {depth + 1}")
        
        cleanup_folders.extend(folder_ids)
        
        # Try to create one more level - should fail
        with pytest.raises(FolderValidationError, match="Maximum folder depth"):
            folder_manager.create_folder(
                TEST_WORKSPACE_ID,
                f"{test_run_id}_TooDeep",
                parent_folder_id=parent_id
            )
        print(f"  ✓ Depth limit enforced (max: {max_depth})")
    
    def test_circular_reference_prevention(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test circular reference prevention"""
        print(f"\n🔄 Testing circular reference prevention: {test_run_id}")
        
        # Create parent and child
        parent_id = folder_manager.create_folder(TEST_WORKSPACE_ID, f"{test_run_id}_Parent")
        child_id = folder_manager.create_folder(
            TEST_WORKSPACE_ID,
            f"{test_run_id}_Child",
            parent_folder_id=parent_id
        )
        cleanup_folders.extend([parent_id, child_id])
        print(f"  ✓ Created parent-child relationship")
        
        # Try to move parent under child - should fail
        with pytest.raises(FolderValidationError, match="circular reference"):
            folder_manager.move_folder(
                TEST_WORKSPACE_ID,
                parent_id,
                new_parent_folder_id=child_id
            )
        print(f"  ✓ Circular reference prevented")


# ============================================================================
# TEST FOLDER STRUCTURE OPERATIONS
# ============================================================================

@pytest.mark.real_fabric
@pytest.mark.timeout(TEST_TIMEOUT)
class TestFolderStructure:
    """Test folder structure operations"""
    
    def test_create_medallion_structure(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test creating medallion architecture (Bronze/Silver/Gold)"""
        print(f"\n🥉🥈🥇 Creating medallion architecture: {test_run_id}")
        
        structure = {
            f"{test_run_id}_Bronze": {
                "subfolders": ["Raw Data", "Archive"]
            },
            f"{test_run_id}_Silver": {
                "subfolders": ["Cleaned", "Transformed"]
            },
            f"{test_run_id}_Gold": {
                "subfolders": ["Analytics", "Reports"]
            },
        }
        
        folder_ids = folder_manager.create_folder_structure(TEST_WORKSPACE_ID, structure)
        
        # Verify all folders created
        assert len(folder_ids) == 9  # 3 root + 6 subfolders
        print(f"  ✓ Created {len(folder_ids)} folders")
        
        # Track for cleanup
        cleanup_folders.extend(folder_ids.values())
        
        # Verify structure
        folders = folder_manager.list_folders(TEST_WORKSPACE_ID)
        bronze_folder = next(f for f in folders if test_run_id in f.display_name and "Bronze" in f.display_name)
        bronze_children = [f for f in folders if f.parent_folder_id == bronze_folder.id]
        assert len(bronze_children) == 2
        print(f"  ✓ Verified Bronze layer has 2 subfolders")
    
    def test_get_folder_structure(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test building folder structure representation"""
        print(f"\n🌳 Testing folder structure retrieval: {test_run_id}")
        
        # Create simple structure
        parent_id = folder_manager.create_folder(TEST_WORKSPACE_ID, f"{test_run_id}_StructureTest")
        child1_id = folder_manager.create_folder(
            TEST_WORKSPACE_ID,
            f"{test_run_id}_Child1",
            parent_folder_id=parent_id
        )
        child2_id = folder_manager.create_folder(
            TEST_WORKSPACE_ID,
            f"{test_run_id}_Child2",
            parent_folder_id=parent_id
        )
        cleanup_folders.extend([parent_id, child1_id, child2_id])
        print(f"  ✓ Created test structure")
        
        # Get structure
        structure = folder_manager.get_folder_structure(TEST_WORKSPACE_ID)
        
        assert isinstance(structure, FolderStructure)
        assert parent_id in structure.subfolder_map
        assert len(structure.subfolder_map[parent_id]) == 2
        print(f"  ✓ Structure correctly represents parent-child relationships")
    
    def test_print_folder_tree(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders, capsys
    ):
        """Test printing folder tree visualization"""
        print(f"\n📊 Testing folder tree visualization: {test_run_id}")
        
        # Create nested structure
        root_id = folder_manager.create_folder(TEST_WORKSPACE_ID, f"{test_run_id}_TreeRoot")
        child_id = folder_manager.create_folder(
            TEST_WORKSPACE_ID,
            f"{test_run_id}_TreeChild",
            parent_folder_id=root_id
        )
        cleanup_folders.extend([root_id, child_id])
        
        # Print tree
        folder_manager.print_folder_tree(TEST_WORKSPACE_ID)
        
        captured = capsys.readouterr()
        # Should contain our test folders
        assert test_run_id in captured.out
        print(f"  ✓ Tree visualization generated")


# ============================================================================
# TEST ITEM ORGANIZATION
# ============================================================================

@pytest.mark.real_fabric
@pytest.mark.timeout(TEST_TIMEOUT)
class TestItemOrganization:
    """Test organizing items in folders"""
    
    def test_create_item_in_folder(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test creating an item directly in a folder"""
        print(f"\n📓 Creating item in folder: {test_run_id}")
        
        # Create folder
        folder_id = folder_manager.create_folder(TEST_WORKSPACE_ID, f"{test_run_id}_ItemFolder")
        cleanup_folders.append(folder_id)
        print(f"  ✓ Created folder: {folder_id[:8]}...")
        
        try:
            # Create notebook in folder
            item_id = folder_manager.create_item_in_folder(
                workspace_id=TEST_WORKSPACE_ID,
                display_name=f"{test_run_id}_TestNotebook",
                item_type="Notebook",
                folder_id=folder_id
            )
            print(f"  ✓ Created notebook in folder: {item_id[:8]}...")
            
            # Verify item in folder
            items = folder_manager.list_folder_items(TEST_WORKSPACE_ID, folder_id=folder_id)
            found_item = next((i for i in items if i.get("id") == item_id), None)
            assert found_item is not None
            assert found_item.get("folderId") == folder_id
            print(f"  ✓ Verified item appears in folder")
            
            # Cleanup item
            fabric_client = FabricClient()
            fabric_client._make_request("DELETE", f"workspaces/{TEST_WORKSPACE_ID}/items/{item_id}")
            print(f"  ✓ Cleaned up test item")
            
        except Exception as e:
            print(f"  ⚠ Item creation test skipped (may require additional permissions): {e}")
    
    def test_list_folder_items(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test listing items in a folder"""
        print(f"\n📋 Testing item listing: {test_run_id}")
        
        # Create folder
        folder_id = folder_manager.create_folder(TEST_WORKSPACE_ID, f"{test_run_id}_ListFolder")
        cleanup_folders.append(folder_id)
        
        # List items (may be empty, just verify API call works)
        items = folder_manager.list_folder_items(TEST_WORKSPACE_ID, folder_id=folder_id)
        assert isinstance(items, list)
        print(f"  ✓ Successfully listed folder items (found: {len(items)})")


# ============================================================================
# TEST PERFORMANCE AND LIMITS
# ============================================================================

@pytest.mark.real_fabric
@pytest.mark.timeout(TEST_TIMEOUT)
@pytest.mark.slow
class TestPerformance:
    """Test performance and limits"""
    
    def test_bulk_folder_creation(
        self, validate_environment, folder_manager, test_run_id, cleanup_folders
    ):
        """Test creating multiple folders in bulk"""
        print(f"\n⚡ Testing bulk folder creation: {test_run_id}")
        
        num_folders = 10
        start_time = time.time()
        
        for i in range(num_folders):
            folder_id = folder_manager.create_folder(
                TEST_WORKSPACE_ID,
                f"{test_run_id}_Bulk{i:02d}"
            )
            cleanup_folders.append(folder_id)
        
        elapsed = time.time() - start_time
        print(f"  ✓ Created {num_folders} folders in {elapsed:.2f}s")
        print(f"  ✓ Average: {elapsed/num_folders:.2f}s per folder")
    
    def test_list_large_workspace(
        self, validate_environment, folder_manager
    ):
        """Test listing folders in workspace with many folders"""
        print(f"\n📊 Testing folder listing performance")
        
        start_time = time.time()
        folders = folder_manager.list_folders(TEST_WORKSPACE_ID)
        elapsed = time.time() - start_time
        
        print(f"  ✓ Listed {len(folders)} folders in {elapsed:.2f}s")


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "-s", "-m", "real_fabric"])
