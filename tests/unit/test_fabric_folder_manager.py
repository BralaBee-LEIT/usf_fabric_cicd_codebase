"""
Unit tests for Microsoft Fabric Folder Manager

Tests the folder management functionality including:
- Folder CRUD operations (create, list, get, update, delete, move)
- Item operations (create in folder, list folder items, move items)
- Structure operations (get structure, create structure, print tree)
- Validation (folder names, depth limits, circular references)
- Error handling and custom exceptions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from ops.scripts.utilities.fabric_folder_manager import (
    FabricFolderManager,
    FolderInfo,
    FolderStructure,
    FolderValidationError,
    FolderOperationError,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_fabric_client():
    """Create mock FabricClient that doesn't require credentials"""
    with patch('ops.scripts.utilities.fabric_folder_manager.FabricClient') as mock_class:
        client_instance = Mock()
        # Mock the methods that FabricFolderManager uses
        client_instance.get.return_value = {"value": []}
        client_instance.post.return_value = {}
        client_instance.patch.return_value = {}
        client_instance.delete.return_value = None
        mock_class.return_value = client_instance
        yield client_instance


@pytest.fixture
def manager(mock_fabric_client):
    """Create FabricFolderManager instance with mocked client"""
    return FabricFolderManager(max_folder_depth=5)


@pytest.fixture
def sample_folders():
    """Sample folder data for testing"""
    return [
        {
            "id": "folder1",
            "displayName": "Bronze Layer",
            "workspaceId": "workspace1",
            "parentFolderId": None,
        },
        {
            "id": "folder2",
            "displayName": "Silver Layer",
            "workspaceId": "workspace1",
            "parentFolderId": None,
        },
        {
            "id": "folder3",
            "displayName": "Raw Data",
            "workspaceId": "workspace1",
            "parentFolderId": "folder1",
        },
        {
            "id": "folder4",
            "displayName": "Processed",
            "workspaceId": "workspace1",
            "parentFolderId": "folder2",
        },
    ]


@pytest.fixture
def sample_items():
    """Sample item data for testing"""
    return [
        {
            "id": "item1",
            "displayName": "Sales Lakehouse",
            "type": "Lakehouse",
            "folderId": "folder1",
        },
        {
            "id": "item2",
            "displayName": "ETL Notebook",
            "type": "Notebook",
            "folderId": "folder3",
        },
        {
            "id": "item3",
            "displayName": "Analytics Warehouse",
            "type": "Warehouse",
            "folderId": None,  # Root level
        },
    ]


# ============================================================================
# TEST FOLDER CRUD OPERATIONS
# ============================================================================

class TestCreateFolder:
    """Test create_folder method"""
    
    def test_create_root_folder(self, manager, mock_fabric_client):
        """Test creating a root-level folder"""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "new-folder-id",
            "displayName": "Test Folder",
        }
        mock_fabric_client._make_request.return_value = mock_response
        
        # Test
        folder_id = manager.create_folder(
            workspace_id="workspace1",
            display_name="Test Folder",
            description="Test Description"
        )
        
        # Verify
        assert folder_id == "new-folder-id"
        mock_fabric_client._make_request.assert_called_once()
        args = mock_fabric_client._make_request.call_args
        assert args[0][0] == "POST"
        assert "workspaces/workspace1/folders" in args[0][1]
        assert args[1]["json"]["displayName"] == "Test Folder"
    
    def test_create_subfolder(self, manager, mock_fabric_client):
        """Test creating a subfolder"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "subfolder-id",
            "displayName": "Subfolder",
        }
        mock_fabric_client._make_request.return_value = mock_response
        
        # Mock depth check (parent is depth 1)
        with patch.object(manager, '_get_folder_depth', return_value=1):
            folder_id = manager.create_folder(
                workspace_id="workspace1",
                display_name="Subfolder",
                parent_folder_id="parent-id"
            )
        
        assert folder_id == "subfolder-id"
        args = mock_fabric_client._make_request.call_args
        assert args[1]["json"]["parentFolderId"] == "parent-id"
    
    def test_create_folder_validates_name(self, manager):
        """Test folder name validation"""
        with pytest.raises(FolderValidationError, match="cannot be empty"):
            manager.create_folder("workspace1", "")
        
        with pytest.raises(FolderValidationError, match="cannot be empty"):
            manager.create_folder("workspace1", "   ")
        
        with pytest.raises(FolderValidationError, match="too long"):
            manager.create_folder("workspace1", "x" * 257)
    
    def test_create_folder_depth_limit(self, manager, mock_fabric_client):
        """Test folder depth limit validation"""
        # Mock depth check at maximum depth
        with patch.object(manager, '_get_folder_depth', return_value=5):
            with pytest.raises(FolderValidationError, match="Maximum folder depth"):
                manager.create_folder(
                    "workspace1",
                    "Too Deep",
                    parent_folder_id="parent-id"
                )
    
    def test_create_folder_skip_validation(self, manager, mock_fabric_client):
        """Test creating folder with validation disabled"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "folder-id"}
        mock_fabric_client._make_request.return_value = mock_response
        
        # Should not raise even with invalid name
        folder_id = manager.create_folder(
            "workspace1",
            "",  # Empty name
            validate=False
        )
        
        assert folder_id == "folder-id"


class TestListFolders:
    """Test list_folders method"""
    
    def test_list_all_folders(self, manager, mock_fabric_client, sample_folders):
        """Test listing all folders in workspace"""
        mock_response = Mock()
        mock_response.json.return_value = {"value": sample_folders}
        mock_fabric_client._make_request.return_value = mock_response
        
        folders = manager.list_folders("workspace1")
        
        assert len(folders) == 4
        assert isinstance(folders[0], FolderInfo)
        assert folders[0].display_name == "Bronze Layer"
        assert folders[2].parent_folder_id == "folder1"
    
    def test_list_root_folders_only(self, manager, mock_fabric_client, sample_folders):
        """Test listing only root-level folders"""
        mock_response = Mock()
        mock_response.json.return_value = {"value": sample_folders}
        mock_fabric_client._make_request.return_value = mock_response
        
        folders = manager.list_folders("workspace1", include_subfolders=False)
        
        # Should only return folders without parent
        root_folders = [f for f in folders if f.parent_folder_id is None]
        assert len(root_folders) == 2
    
    def test_list_folders_by_parent(self, manager, mock_fabric_client, sample_folders):
        """Test listing subfolders of specific parent"""
        mock_response = Mock()
        # Return only subfolders of folder1
        subfolders = [f for f in sample_folders if f.get("parentFolderId") == "folder1"]
        mock_response.json.return_value = {"value": subfolders}
        mock_fabric_client._make_request.return_value = mock_response
        
        folders = manager.list_folders("workspace1", parent_folder_id="folder1")
        
        assert len(folders) == 1
        assert folders[0].display_name == "Raw Data"
        assert folders[0].parent_folder_id == "folder1"


class TestGetFolder:
    """Test get_folder method"""
    
    def test_get_folder_success(self, manager, mock_fabric_client):
        """Test getting folder details"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "folder1",
            "displayName": "Test Folder",
            "workspaceId": "workspace1",
            "parentFolderId": None,
        }
        mock_fabric_client._make_request.return_value = mock_response
        
        folder = manager.get_folder("workspace1", "folder1")
        
        assert isinstance(folder, FolderInfo)
        assert folder.id == "folder1"
        assert folder.display_name == "Test Folder"
        assert folder.workspace_id == "workspace1"
    
    def test_get_folder_not_found(self, manager, mock_fabric_client):
        """Test error handling when folder not found"""
        mock_fabric_client._make_request.side_effect = Exception("404 Not Found")
        
        with pytest.raises(FolderOperationError, match="Failed to get folder"):
            manager.get_folder("workspace1", "invalid-id")


class TestUpdateFolder:
    """Test update_folder method"""
    
    def test_update_folder_name(self, manager, mock_fabric_client):
        """Test renaming a folder"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_fabric_client._make_request.return_value = mock_response
        
        manager.update_folder("workspace1", "folder1", display_name="New Name")
        
        args = mock_fabric_client._make_request.call_args
        assert args[0][0] == "PATCH"
        assert "workspaces/workspace1/folders/folder1" in args[0][1]
        assert args[1]["json"]["displayName"] == "New Name"
    
    def test_update_folder_validates_name(self, manager):
        """Test name validation during update"""
        with pytest.raises(FolderValidationError, match="cannot be empty"):
            manager.update_folder("workspace1", "folder1", display_name="")


class TestDeleteFolder:
    """Test delete_folder method"""
    
    def test_delete_empty_folder(self, manager, mock_fabric_client):
        """Test deleting an empty folder"""
        # Mock empty folder
        mock_items_response = Mock()
        mock_items_response.json.return_value = {"value": []}
        
        mock_delete_response = Mock()
        mock_delete_response.status_code = 200
        
        mock_fabric_client._make_request.side_effect = [
            mock_items_response,  # list_folder_items call
            mock_delete_response,  # delete call
        ]
        
        manager.delete_folder("workspace1", "folder1")
        
        # Verify delete was called
        delete_call = mock_fabric_client._make_request.call_args_list[1]
        assert delete_call[0][0] == "DELETE"
        assert "folders/folder1" in delete_call[0][1]
    
    def test_delete_folder_with_items_fails(self, manager, mock_fabric_client, sample_items):
        """Test deleting folder with items fails without force"""
        mock_response = Mock()
        mock_response.json.return_value = {"value": sample_items[:2]}
        mock_fabric_client._make_request.return_value = mock_response
        
        with pytest.raises(FolderOperationError, match="contains items"):
            manager.delete_folder("workspace1", "folder1", force=False)
    
    def test_delete_folder_with_items_forced(self, manager, mock_fabric_client, sample_items):
        """Test force deleting folder with items"""
        mock_items_response = Mock()
        mock_items_response.json.return_value = {"value": sample_items[:2]}
        
        mock_delete_response = Mock()
        mock_delete_response.status_code = 200
        
        mock_fabric_client._make_request.side_effect = [
            mock_items_response,
            mock_delete_response,
        ]
        
        manager.delete_folder("workspace1", "folder1", force=True)
        
        # Should still call delete even with items
        assert mock_fabric_client._make_request.call_count == 2


class TestMoveFolder:
    """Test move_folder method"""
    
    def test_move_folder_to_root(self, manager, mock_fabric_client):
        """Test moving folder to workspace root"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_fabric_client._make_request.return_value = mock_response
        
        with patch.object(manager, '_is_descendant', return_value=False):
            manager.move_folder("workspace1", "folder1", new_parent_folder_id=None)
        
        args = mock_fabric_client._make_request.call_args
        assert args[0][0] == "POST"
        assert "folders/folder1/move" in args[0][1]
        assert args[1]["json"]["newParentFolderId"] is None
    
    def test_move_folder_to_parent(self, manager, mock_fabric_client):
        """Test moving folder to different parent"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_fabric_client._make_request.return_value = mock_response
        
        with patch.object(manager, '_is_descendant', return_value=False):
            with patch.object(manager, '_get_folder_depth', return_value=2):
                manager.move_folder("workspace1", "folder1", new_parent_folder_id="folder2")
        
        args = mock_fabric_client._make_request.call_args
        assert args[1]["json"]["newParentFolderId"] == "folder2"
    
    def test_move_folder_circular_reference(self, manager):
        """Test moving folder to its own descendant fails"""
        with patch.object(manager, '_is_descendant', return_value=True):
            with pytest.raises(FolderValidationError, match="circular reference"):
                manager.move_folder("workspace1", "folder1", new_parent_folder_id="folder3")
    
    def test_move_folder_exceeds_depth(self, manager):
        """Test moving folder exceeds depth limit"""
        with patch.object(manager, '_is_descendant', return_value=False):
            with patch.object(manager, '_get_folder_depth', return_value=5):
                with pytest.raises(FolderValidationError, match="Maximum folder depth"):
                    manager.move_folder("workspace1", "folder1", "folder2")


# ============================================================================
# TEST ITEM OPERATIONS
# ============================================================================

class TestCreateItemInFolder:
    """Test create_item_in_folder method"""
    
    def test_create_lakehouse_in_folder(self, manager, mock_fabric_client):
        """Test creating lakehouse in folder"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "lakehouse-id"}
        mock_fabric_client._make_request.return_value = mock_response
        
        item_id = manager.create_item_in_folder(
            workspace_id="workspace1",
            display_name="Test Lakehouse",
            item_type="Lakehouse",
            folder_id="folder1",
            description="Test lakehouse"
        )
        
        assert item_id == "lakehouse-id"
        args = mock_fabric_client._make_request.call_args
        assert args[1]["json"]["displayName"] == "Test Lakehouse"
        assert args[1]["json"]["type"] == "Lakehouse"
        assert args[1]["json"]["folderId"] == "folder1"
    
    def test_create_item_at_root(self, manager, mock_fabric_client):
        """Test creating item at workspace root"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "item-id"}
        mock_fabric_client._make_request.return_value = mock_response
        
        item_id = manager.create_item_in_folder(
            workspace_id="workspace1",
            display_name="Root Item",
            item_type="Notebook",
            folder_id=None  # Root level
        )
        
        assert item_id == "item-id"
        args = mock_fabric_client._make_request.call_args
        assert "folderId" not in args[1]["json"]


class TestListFolderItems:
    """Test list_folder_items method"""
    
    def test_list_items_in_folder(self, manager, mock_fabric_client, sample_items):
        """Test listing items in specific folder"""
        mock_response = Mock()
        mock_response.json.return_value = {"value": sample_items}
        mock_fabric_client._make_request.return_value = mock_response
        
        items = manager.list_folder_items("workspace1", folder_id="folder1")
        
        # Should filter to only items in folder1
        folder_items = [i for i in items if i.get("folderId") == "folder1"]
        assert len(folder_items) == 1
        assert folder_items[0]["displayName"] == "Sales Lakehouse"
    
    def test_list_items_by_type(self, manager, mock_fabric_client, sample_items):
        """Test listing items filtered by type"""
        mock_response = Mock()
        mock_response.json.return_value = {"value": sample_items}
        mock_fabric_client._make_request.return_value = mock_response
        
        items = manager.list_folder_items("workspace1", item_type="Notebook")
        
        notebook_items = [i for i in items if i.get("type") == "Notebook"]
        assert len(notebook_items) == 1
        assert notebook_items[0]["displayName"] == "ETL Notebook"


class TestMoveItemsToFolder:
    """Test move_items_to_folder method"""
    
    def test_move_single_item(self, manager, mock_fabric_client):
        """Test moving single item to folder"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_fabric_client._make_request.return_value = mock_response
        
        results = manager.move_items_to_folder(
            workspace_id="workspace1",
            item_ids=["item1"],
            target_folder_id="folder1"
        )
        
        assert results["item1"] is True
        assert mock_fabric_client._make_request.call_count == 1
    
    def test_move_multiple_items(self, manager, mock_fabric_client):
        """Test moving multiple items in bulk"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_fabric_client._make_request.return_value = mock_response
        
        item_ids = ["item1", "item2", "item3"]
        results = manager.move_items_to_folder("workspace1", item_ids, "folder1")
        
        assert len(results) == 3
        assert all(results.values())
        assert mock_fabric_client._make_request.call_count == 3
    
    def test_move_items_partial_failure(self, manager, mock_fabric_client):
        """Test handling partial failures in bulk move"""
        # First succeeds, second fails, third succeeds
        mock_fabric_client._make_request.side_effect = [
            Mock(status_code=200),
            Exception("API Error"),
            Mock(status_code=200),
        ]
        
        results = manager.move_items_to_folder(
            workspace_id="workspace1",
            item_ids=["item1", "item2", "item3"],
            target_folder_id="folder1"
        )
        
        assert results["item1"] is True
        assert results["item2"] is False
        assert results["item3"] is True


# ============================================================================
# TEST STRUCTURE OPERATIONS
# ============================================================================

class TestGetFolderStructure:
    """Test get_folder_structure method"""
    
    def test_get_structure(self, manager, mock_fabric_client, sample_folders):
        """Test building folder structure"""
        mock_response = Mock()
        mock_response.json.return_value = {"value": sample_folders}
        mock_fabric_client._make_request.return_value = mock_response
        
        structure = manager.get_folder_structure("workspace1")
        
        assert isinstance(structure, FolderStructure)
        assert len(structure.root_folders) == 2
        assert "folder1" in structure.subfolder_map
        assert len(structure.subfolder_map["folder1"]) == 1
    
    def test_get_root_folders(self, manager, mock_fabric_client, sample_folders):
        """Test getting root folders from structure"""
        mock_response = Mock()
        mock_response.json.return_value = {"value": sample_folders}
        mock_fabric_client._make_request.return_value = mock_response
        
        structure = manager.get_folder_structure("workspace1")
        roots = structure.get_root_folders()
        
        assert len(roots) == 2
        assert all(f.parent_folder_id is None for f in roots)
    
    def test_get_subfolders(self, manager, mock_fabric_client, sample_folders):
        """Test getting subfolders from structure"""
        mock_response = Mock()
        mock_response.json.return_value = {"value": sample_folders}
        mock_fabric_client._make_request.return_value = mock_response
        
        structure = manager.get_folder_structure("workspace1")
        subfolders = structure.get_subfolders("folder1")
        
        assert len(subfolders) == 1
        assert subfolders[0].display_name == "Raw Data"


class TestCreateFolderStructure:
    """Test create_folder_structure method"""
    
    def test_create_simple_structure(self, manager, mock_fabric_client):
        """Test creating simple folder structure"""
        structure = {
            "Folder1": {},
            "Folder2": {},
        }
        
        # Mock responses for folder creation
        mock_fabric_client._make_request.side_effect = [
            Mock(json=lambda: {"id": "folder1-id"}),
            Mock(json=lambda: {"id": "folder2-id"}),
        ]
        
        folder_ids = manager.create_folder_structure("workspace1", structure)
        
        assert len(folder_ids) == 2
        assert "Folder1" in folder_ids
        assert "Folder2" in folder_ids
        assert folder_ids["Folder1"] == "folder1-id"
    
    def test_create_nested_structure(self, manager, mock_fabric_client):
        """Test creating nested folder structure"""
        structure = {
            "Parent": {
                "subfolders": ["Child1", "Child2"]
            }
        }
        
        # Mock responses
        mock_fabric_client._make_request.side_effect = [
            Mock(json=lambda: {"id": "parent-id"}),
            Mock(json=lambda: {"id": "child1-id"}),
            Mock(json=lambda: {"id": "child2-id"}),
        ]
        
        with patch.object(manager, '_get_folder_depth', return_value=1):
            folder_ids = manager.create_folder_structure("workspace1", structure)
        
        assert len(folder_ids) == 3
        assert "Parent" in folder_ids
        assert "Parent/Child1" in folder_ids
        assert "Parent/Child2" in folder_ids


class TestPrintFolderTree:
    """Test print_folder_tree method"""
    
    def test_print_tree(self, manager, mock_fabric_client, sample_folders, capsys):
        """Test printing folder tree"""
        mock_response = Mock()
        mock_response.json.return_value = {"value": sample_folders}
        mock_fabric_client._make_request.return_value = mock_response
        
        manager.print_folder_tree("workspace1")
        
        captured = capsys.readouterr()
        assert "Bronze Layer" in captured.out
        assert "Silver Layer" in captured.out
        assert "Raw Data" in captured.out
    
    def test_print_tree_with_items(self, manager, mock_fabric_client, sample_folders, sample_items, capsys):
        """Test printing folder tree with items"""
        # Mock folders
        mock_folders_response = Mock()
        mock_folders_response.json.return_value = {"value": sample_folders}
        
        # Mock items
        mock_items_response = Mock()
        mock_items_response.json.return_value = {"value": sample_items}
        
        mock_fabric_client._make_request.side_effect = [
            mock_folders_response,
            mock_items_response,
        ]
        
        manager.print_folder_tree("workspace1", show_items=True)
        
        captured = capsys.readouterr()
        assert "Sales Lakehouse" in captured.out
        assert "ETL Notebook" in captured.out


# ============================================================================
# TEST VALIDATION METHODS
# ============================================================================

class TestValidateFolderName:
    """Test _validate_folder_name method"""
    
    def test_valid_names(self, manager):
        """Test valid folder names pass validation"""
        valid_names = [
            "Folder",
            "My Folder",
            "Folder-123",
            "Folder_Name",
            "a" * 256,  # Max length
        ]
        
        for name in valid_names:
            manager._validate_folder_name(name)  # Should not raise
    
    def test_empty_name(self, manager):
        """Test empty folder name fails"""
        with pytest.raises(FolderValidationError, match="cannot be empty"):
            manager._validate_folder_name("")
        
        with pytest.raises(FolderValidationError, match="cannot be empty"):
            manager._validate_folder_name("   ")
    
    def test_name_too_long(self, manager):
        """Test folder name too long fails"""
        with pytest.raises(FolderValidationError, match="too long"):
            manager._validate_folder_name("x" * 257)
    
    def test_invalid_characters(self, manager):
        """Test invalid characters in folder name"""
        invalid_names = [
            "Folder/Name",
            "Folder\\Name",
            "Folder:Name",
            "Folder*Name",
            "Folder?Name",
            "Folder<Name>",
            "Folder|Name",
        ]
        
        for name in invalid_names:
            with pytest.raises(FolderValidationError, match="Invalid characters"):
                manager._validate_folder_name(name)


class TestGetFolderDepth:
    """Test _get_folder_depth method"""
    
    def test_root_folder_depth(self, manager, mock_fabric_client):
        """Test root folder has depth 0"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "folder1",
            "parentFolderId": None,
        }
        mock_fabric_client._make_request.return_value = mock_response
        
        depth = manager._get_folder_depth("workspace1", "folder1")
        assert depth == 0
    
    def test_nested_folder_depth(self, manager, mock_fabric_client):
        """Test nested folder depth calculation"""
        # Setup chain: folder3 -> folder2 -> folder1 (root)
        mock_fabric_client._make_request.side_effect = [
            Mock(json=lambda: {"id": "folder3", "parentFolderId": "folder2"}),
            Mock(json=lambda: {"id": "folder2", "parentFolderId": "folder1"}),
            Mock(json=lambda: {"id": "folder1", "parentFolderId": None}),
        ]
        
        depth = manager._get_folder_depth("workspace1", "folder3")
        assert depth == 2


class TestIsDescendant:
    """Test _is_descendant method"""
    
    def test_direct_child(self, manager, mock_fabric_client):
        """Test detecting direct child relationship"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "child",
            "parentFolderId": "parent",
        }
        mock_fabric_client._make_request.return_value = mock_response
        
        result = manager._is_descendant("workspace1", "parent", "child")
        assert result is True
    
    def test_indirect_descendant(self, manager, mock_fabric_client):
        """Test detecting indirect descendant relationship"""
        # Setup chain: grandchild -> child -> parent
        mock_fabric_client._make_request.side_effect = [
            Mock(json=lambda: {"id": "grandchild", "parentFolderId": "child"}),
            Mock(json=lambda: {"id": "child", "parentFolderId": "parent"}),
        ]
        
        result = manager._is_descendant("workspace1", "parent", "grandchild")
        assert result is True
    
    def test_not_descendant(self, manager, mock_fabric_client):
        """Test folders not in ancestor relationship"""
        mock_fabric_client._make_request.side_effect = [
            Mock(json=lambda: {"id": "folder2", "parentFolderId": "other"}),
            Mock(json=lambda: {"id": "other", "parentFolderId": None}),
        ]
        
        result = manager._is_descendant("workspace1", "folder1", "folder2")
        assert result is False


class TestGetItemIcon:
    """Test _get_item_icon method"""
    
    def test_item_icons(self, manager):
        """Test getting correct icons for item types"""
        assert manager._get_item_icon("Lakehouse") == "🏠"
        assert manager._get_item_icon("Notebook") == "📓"
        assert manager._get_item_icon("Warehouse") == "🏢"
        assert manager._get_item_icon("Report") == "📊"
        assert manager._get_item_icon("Dashboard") == "📈"
        assert manager._get_item_icon("Unknown") == "📄"


# ============================================================================
# TEST ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Test error handling and custom exceptions"""
    
    def test_folder_validation_error(self):
        """Test FolderValidationError exception"""
        error = FolderValidationError("Invalid folder name")
        assert str(error) == "Invalid folder name"
        assert isinstance(error, Exception)
    
    def test_folder_operation_error(self):
        """Test FolderOperationError exception"""
        error = FolderOperationError("API call failed")
        assert str(error) == "API call failed"
        assert isinstance(error, Exception)
    
    def test_create_folder_api_error(self, manager, mock_fabric_client):
        """Test handling API errors during folder creation"""
        mock_fabric_client._make_request.side_effect = Exception("API Error")
        
        with pytest.raises(FolderOperationError, match="Failed to create folder"):
            manager.create_folder("workspace1", "Test Folder")
    
    def test_list_folders_api_error(self, manager, mock_fabric_client):
        """Test handling API errors during folder listing"""
        mock_fabric_client._make_request.side_effect = Exception("API Error")
        
        with pytest.raises(FolderOperationError, match="Failed to list folders"):
            manager.list_folders("workspace1")


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

class TestConfiguration:
    """Test FabricFolderManager configuration"""
    
    def test_default_max_depth(self, mock_fabric_client):
        """Test default max folder depth"""
        manager = FabricFolderManager()
        assert manager.max_folder_depth == 5
    
    def test_custom_max_depth(self, mock_fabric_client):
        """Test custom max folder depth"""
        manager = FabricFolderManager(max_folder_depth=3)
        assert manager.max_folder_depth == 3
    
    def test_max_depth_validation(self, mock_fabric_client):
        """Test max depth is enforced"""
        manager = FabricFolderManager(max_folder_depth=2)
        
        with patch.object(manager, '_get_folder_depth', return_value=2):
            with pytest.raises(FolderValidationError, match="(Maximum folder depth|Folder depth limit exceeded)"):
                manager.create_folder("workspace1", "Too Deep", parent_folder_id="parent")
