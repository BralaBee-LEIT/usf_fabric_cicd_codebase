"""
Microsoft Fabric Folder Management Module

Provides comprehensive folder management capabilities for Microsoft Fabric workspaces,
including creation, organization, validation, and item placement within folders.

API Documentation:
    https://learn.microsoft.com/en-us/rest/api/fabric/core/folders

Example Usage:
    >>> from fabric_folder_manager import FabricFolderManager
    >>> 
    >>> manager = FabricFolderManager()
    >>> 
    >>> # Create folder structure
    >>> bronze_id = manager.create_folder(workspace_id, "Bronze Layer")
    >>> archive_id = manager.create_folder(workspace_id, "Archive", parent_folder_id=bronze_id)
    >>> 
    >>> # List all folders
    >>> folders = manager.list_folders(workspace_id)
    >>> 
    >>> # Create item in folder
    >>> manager.create_item_in_folder(workspace_id, "CustomerData_Lakehouse", "Lakehouse", bronze_id)

Status: Preview API (October 2025)
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from .fabric_api import FabricClient
from .output import (
    console_info as print_info,
    console_success as print_success,
    console_warning as print_warning,
    console_error as print_error,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FolderValidationError(Exception):
    """Raised when folder validation fails"""
    pass


class FolderOperationError(Exception):
    """Raised when folder operation fails"""
    pass


@dataclass
class FolderInfo:
    """Represents a Fabric folder with its properties"""
    id: str
    display_name: str
    workspace_id: str
    parent_folder_id: Optional[str] = None
    
    def __repr__(self) -> str:
        parent = f" (parent: {self.parent_folder_id[:8]}...)" if self.parent_folder_id else ""
        return f"Folder('{self.display_name}'{parent})"


@dataclass
class FolderStructure:
    """Represents a hierarchical folder structure"""
    root_folders: List[FolderInfo]
    subfolder_map: Dict[str, List[FolderInfo]]  # parent_id -> children
    
    def get_children(self, folder_id: str) -> List[FolderInfo]:
        """Get immediate children of a folder"""
        return self.subfolder_map.get(folder_id, [])
    
    def get_depth(self, folder_id: str) -> int:
        """Calculate depth of a folder in the hierarchy"""
        depth = 0
        current = folder_id
        
        # Find folder in structure
        for folders in [self.root_folders] + list(self.subfolder_map.values()):
            folder = next((f for f in folders if f.id == current), None)
            if folder:
                while folder.parent_folder_id:
                    depth += 1
                    # Find parent
                    for folders in [self.root_folders] + list(self.subfolder_map.values()):
                        parent = next((f for f in folders if f.id == folder.parent_folder_id), None)
                        if parent:
                            folder = parent
                            break
                    else:
                        break  # Parent not found
                break
        
        return depth


class FabricFolderManager:
    """
    Manages folders and item organization in Microsoft Fabric workspaces.
    
    Provides methods for:
    - Creating and deleting folders (including subfolders)
    - Moving folders and items
    - Listing folder contents
    - Validating folder structure
    - Bulk operations
    
    Attributes:
        fabric_client (FabricClient): Client for Fabric API operations
        max_folder_depth (int): Maximum allowed folder nesting depth (default: 5)
    """
    
    def __init__(self, max_folder_depth: int = 5):
        """
        Initialize Fabric Folder Manager
        
        Args:
            max_folder_depth: Maximum nesting depth for folders (default: 5)
        """
        self.fabric_client = FabricClient()
        self.max_folder_depth = max_folder_depth
        logger.info("Initialized FabricFolderManager")
    
    # ========================================================================
    # FOLDER CRUD OPERATIONS
    # ========================================================================
    
    def create_folder(
        self,
        workspace_id: str,
        display_name: str,
        parent_folder_id: Optional[str] = None,
        description: Optional[str] = None,
        validate: bool = True
    ) -> str:
        """
        Create a folder in a Fabric workspace
        
        Args:
            workspace_id: Target workspace GUID
            display_name: Folder name (must meet Fabric naming requirements)
            parent_folder_id: Parent folder ID for subfolders (None for top-level)
            description: Optional folder description
            validate: Whether to validate folder name and depth (default: True)
        
        Returns:
            str: Created folder ID
        
        Raises:
            FolderValidationError: If validation fails
            FolderOperationError: If creation fails
        
        Example:
            >>> manager = FabricFolderManager()
            >>> folder_id = manager.create_folder(workspace_id, "Bronze Layer")
            >>> subfolder_id = manager.create_folder(workspace_id, "Archive", parent_folder_id=folder_id)
        """
        logger.info(f"Creating folder '{display_name}' in workspace {workspace_id[:8]}...")
        
        # Validation
        if validate:
            self._validate_folder_name(display_name)
            
            if parent_folder_id:
                # Check depth limit
                current_depth = self._get_folder_depth(workspace_id, parent_folder_id)
                if current_depth >= self.max_folder_depth:
                    raise FolderValidationError(
                        f"Folder depth limit exceeded: current depth {current_depth}, "
                        f"max allowed {self.max_folder_depth}"
                    )
        
        # Prepare request body
        body = {
            "displayName": display_name
        }
        
        if parent_folder_id:
            body["parentFolderId"] = parent_folder_id
        
        if description:
            body["description"] = description
        
        # Make API request
        try:
            endpoint = f"workspaces/{workspace_id}/folders"
            response = self.fabric_client._make_request("POST", endpoint, json=body)
            data = response.json()
            
            folder_id = data["id"]
            logger.info(f"Created folder '{display_name}' with ID: {folder_id}")
            
            return folder_id
            
        except Exception as e:
            error_msg = f"Failed to create folder '{display_name}': {str(e)}"
            logger.error(error_msg)
            raise FolderOperationError(error_msg) from e
    
    def list_folders(
        self,
        workspace_id: str,
        parent_folder_id: Optional[str] = None,
        include_subfolders: bool = True
    ) -> List[FolderInfo]:
        """
        List folders in a workspace
        
        Args:
            workspace_id: Workspace GUID
            parent_folder_id: Filter by parent folder (None for top-level only)
            include_subfolders: Whether to recursively include all subfolders
        
        Returns:
            List[FolderInfo]: List of folder information objects
        
        Example:
            >>> folders = manager.list_folders(workspace_id)
            >>> for folder in folders:
            ...     print(f"{folder.display_name}: {folder.id}")
        """
        logger.info(f"Listing folders in workspace {workspace_id[:8]}...")
        
        try:
            endpoint = f"workspaces/{workspace_id}/folders"
            response = self.fabric_client._make_request("GET", endpoint)
            data = response.json()
            
            folders = []
            for item in data.get("value", []):
                folder = FolderInfo(
                    id=item["id"],
                    display_name=item["displayName"],
                    workspace_id=item["workspaceId"],
                    parent_folder_id=item.get("parentFolderId")
                )
                
                # Apply filters
                if parent_folder_id is not None:
                    if folder.parent_folder_id == parent_folder_id:
                        folders.append(folder)
                elif not include_subfolders:
                    # Top-level only
                    if folder.parent_folder_id is None:
                        folders.append(folder)
                else:
                    # All folders
                    folders.append(folder)
            
            logger.info(f"Found {len(folders)} folders")
            return folders
            
        except Exception as e:
            error_msg = f"Failed to list folders: {str(e)}"
            logger.error(error_msg)
            raise FolderOperationError(error_msg) from e
    
    def get_folder(self, workspace_id: str, folder_id: str) -> FolderInfo:
        """
        Get folder details by ID
        
        Args:
            workspace_id: Workspace GUID
            folder_id: Folder GUID
        
        Returns:
            FolderInfo: Folder information
        
        Raises:
            FolderOperationError: If folder not found or API error
        """
        logger.debug(f"Getting folder {folder_id[:8]}...")
        
        try:
            endpoint = f"workspaces/{workspace_id}/folders/{folder_id}"
            response = self.fabric_client._make_request("GET", endpoint)
            data = response.json()
            
            return FolderInfo(
                id=data["id"],
                display_name=data["displayName"],
                workspace_id=data["workspaceId"],
                parent_folder_id=data.get("parentFolderId")
            )
            
        except Exception as e:
            error_msg = f"Failed to get folder {folder_id[:8]}: {str(e)}"
            logger.error(error_msg)
            raise FolderOperationError(error_msg) from e
    
    def update_folder(
        self,
        workspace_id: str,
        folder_id: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """
        Update folder properties (rename)
        
        Args:
            workspace_id: Workspace GUID
            folder_id: Folder GUID to update
            display_name: New folder name
            description: New folder description
        
        Raises:
            FolderOperationError: If update fails
        
        Example:
            >>> manager.update_folder(workspace_id, folder_id, display_name="Bronze Archive")
        """
        logger.info(f"Updating folder {folder_id[:8]}...")
        
        if not display_name and not description:
            logger.warning("No updates provided")
            return
        
        body = {}
        if display_name:
            self._validate_folder_name(display_name)
            body["displayName"] = display_name
        
        if description:
            body["description"] = description
        
        try:
            endpoint = f"workspaces/{workspace_id}/folders/{folder_id}"
            self.fabric_client._make_request("PATCH", endpoint, json=body)
            logger.info(f"Updated folder {folder_id[:8]}")
            
        except Exception as e:
            error_msg = f"Failed to update folder: {str(e)}"
            logger.error(error_msg)
            raise FolderOperationError(error_msg) from e
    
    def delete_folder(
        self,
        workspace_id: str,
        folder_id: str,
        force: bool = False
    ) -> None:
        """
        Delete a folder from workspace
        
        Args:
            workspace_id: Workspace GUID
            folder_id: Folder GUID to delete
            force: If True, delete even if folder contains items (default: False)
        
        Raises:
            FolderOperationError: If deletion fails
        
        Warning:
            Deleting a folder with items requires force=True.
            Items will be moved to workspace root, not deleted.
        
        Example:
            >>> manager.delete_folder(workspace_id, folder_id, force=True)
        """
        logger.info(f"Deleting folder {folder_id[:8]}...")
        
        if not force:
            # Check if folder has items
            items = self.list_folder_items(workspace_id, folder_id)
            if items:
                raise FolderOperationError(
                    f"Folder contains {len(items)} items. Use force=True to delete."
                )
        
        try:
            endpoint = f"workspaces/{workspace_id}/folders/{folder_id}"
            self.fabric_client._make_request("DELETE", endpoint)
            logger.info(f"Deleted folder {folder_id[:8]}")
            
        except Exception as e:
            error_msg = f"Failed to delete folder: {str(e)}"
            logger.error(error_msg)
            raise FolderOperationError(error_msg) from e
    
    def move_folder(
        self,
        workspace_id: str,
        folder_id: str,
        new_parent_folder_id: Optional[str] = None
    ) -> None:
        """
        Move folder to a different parent (or to workspace root)
        
        Args:
            workspace_id: Workspace GUID
            folder_id: Folder GUID to move
            new_parent_folder_id: New parent folder ID (None for workspace root)
        
        Raises:
            FolderOperationError: If move fails
            FolderValidationError: If move would create circular reference
        
        Example:
            >>> # Move folder to root
            >>> manager.move_folder(workspace_id, folder_id, None)
            >>> 
            >>> # Move folder to different parent
            >>> manager.move_folder(workspace_id, folder_id, new_parent_id)
        """
        logger.info(f"Moving folder {folder_id[:8]}...")
        
        # Validate no circular reference
        if new_parent_folder_id:
            if folder_id == new_parent_folder_id:
                raise FolderValidationError("Cannot move folder to itself")
            
            # Check if new parent is a descendant
            if self._is_descendant(workspace_id, folder_id, new_parent_folder_id):
                raise FolderValidationError(
                    "Cannot move folder to its own descendant (would create circular reference)"
                )
        
        try:
            endpoint = f"workspaces/{workspace_id}/folders/{folder_id}/move"
            body = {"newParentFolderId": new_parent_folder_id}
            self.fabric_client._make_request("POST", endpoint, json=body)
            logger.info(f"Moved folder {folder_id[:8]}")
            
        except Exception as e:
            error_msg = f"Failed to move folder: {str(e)}"
            logger.error(error_msg)
            raise FolderOperationError(error_msg) from e
    
    # ========================================================================
    # ITEM OPERATIONS
    # ========================================================================
    
    def create_item_in_folder(
        self,
        workspace_id: str,
        display_name: str,
        item_type: str,
        folder_id: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Create a Fabric item and place it in a folder
        
        Args:
            workspace_id: Workspace GUID
            display_name: Item name
            item_type: Item type (Lakehouse, Notebook, Warehouse, etc.)
            folder_id: Target folder ID (None for workspace root)
            description: Optional item description
            **kwargs: Additional item-specific parameters
        
        Returns:
            str: Created item ID
        
        Example:
            >>> item_id = manager.create_item_in_folder(
            ...     workspace_id,
            ...     "CustomerData_Lakehouse",
            ...     "Lakehouse",
            ...     folder_id=bronze_folder_id,
            ...     description="Customer data bronze layer"
            ... )
        """
        logger.info(f"Creating {item_type} '{display_name}' in workspace {workspace_id[:8]}...")
        
        body = {
            "displayName": display_name,
            "type": item_type
        }
        
        if folder_id:
            body["folderId"] = folder_id
            logger.info(f"  Placing in folder: {folder_id[:8]}...")
        
        if description:
            body["description"] = description
        
        # Add any additional parameters
        body.update(kwargs)
        
        try:
            endpoint = f"workspaces/{workspace_id}/items"
            response = self.fabric_client._make_request("POST", endpoint, json=body)
            data = response.json()
            
            item_id = data["id"]
            logger.info(f"Created {item_type} '{display_name}' with ID: {item_id}")
            
            return item_id
            
        except Exception as e:
            error_msg = f"Failed to create item '{display_name}': {str(e)}"
            logger.error(error_msg)
            raise FolderOperationError(error_msg) from e
    
    def list_folder_items(
        self,
        workspace_id: str,
        folder_id: Optional[str] = None,
        item_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List items in a folder (or workspace root)
        
        Args:
            workspace_id: Workspace GUID
            folder_id: Folder ID (None for workspace root items)
            item_type: Filter by item type (optional)
        
        Returns:
            List[Dict]: List of item dictionaries
        
        Example:
            >>> # List all items in a folder
            >>> items = manager.list_folder_items(workspace_id, folder_id)
            >>> 
            >>> # List only lakehouses in folder
            >>> lakehouses = manager.list_folder_items(workspace_id, folder_id, "Lakehouse")
        """
        logger.info(f"Listing items in workspace {workspace_id[:8]}...")
        
        try:
            items = self.fabric_client.list_workspace_items(workspace_id, item_type)
            
            # Filter by folder
            filtered_items = []
            for item in items:
                item_folder_id = item.get("folderId")
                
                if folder_id is None:
                    # Root level items (no folder)
                    if item_folder_id is None:
                        filtered_items.append(item)
                else:
                    # Items in specific folder
                    if item_folder_id == folder_id:
                        filtered_items.append(item)
            
            logger.info(f"Found {len(filtered_items)} items")
            return filtered_items
            
        except Exception as e:
            error_msg = f"Failed to list folder items: {str(e)}"
            logger.error(error_msg)
            raise FolderOperationError(error_msg) from e
    
    def move_items_to_folder(
        self,
        workspace_id: str,
        item_ids: List[str],
        target_folder_id: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Move multiple items to a folder (bulk operation)
        
        Args:
            workspace_id: Workspace GUID
            item_ids: List of item GUIDs to move
            target_folder_id: Target folder ID (None for workspace root)
        
        Returns:
            Dict[str, bool]: Map of item_id -> success status
        
        Example:
            >>> results = manager.move_items_to_folder(
            ...     workspace_id,
            ...     ["item-id-1", "item-id-2"],
            ...     bronze_folder_id
            ... )
            >>> print(f"Moved {sum(results.values())}/{len(results)} items")
        """
        logger.info(f"Moving {len(item_ids)} items to folder...")
        
        try:
            endpoint = f"workspaces/{workspace_id}/bulkMoveItems"
            body = {
                "targetFolderId": target_folder_id,
                "itemIds": item_ids
            }
            
            response = self.fabric_client._make_request("POST", endpoint, json=body)
            data = response.json()
            
            # Parse results
            results = {}
            for result in data.get("results", []):
                item_id = result["itemId"]
                success = result.get("status") == "Success"
                results[item_id] = success
            
            success_count = sum(results.values())
            logger.info(f"Moved {success_count}/{len(item_ids)} items successfully")
            
            return results
            
        except Exception as e:
            error_msg = f"Failed to move items: {str(e)}"
            logger.error(error_msg)
            raise FolderOperationError(error_msg) from e
    
    # ========================================================================
    # FOLDER STRUCTURE OPERATIONS
    # ========================================================================
    
    def get_folder_structure(self, workspace_id: str) -> FolderStructure:
        """
        Get complete folder hierarchy for a workspace
        
        Args:
            workspace_id: Workspace GUID
        
        Returns:
            FolderStructure: Hierarchical folder structure
        
        Example:
            >>> structure = manager.get_folder_structure(workspace_id)
            >>> for folder in structure.root_folders:
            ...     print(f"Root: {folder.display_name}")
            ...     for child in structure.get_children(folder.id):
            ...         print(f"  └─ {child.display_name}")
        """
        folders = self.list_folders(workspace_id, include_subfolders=True)
        
        # Separate root folders and subfolders
        root_folders = [f for f in folders if f.parent_folder_id is None]
        subfolders = [f for f in folders if f.parent_folder_id is not None]
        
        # Build subfolder map
        subfolder_map: Dict[str, List[FolderInfo]] = {}
        for folder in subfolders:
            parent_id = folder.parent_folder_id
            if parent_id not in subfolder_map:
                subfolder_map[parent_id] = []
            subfolder_map[parent_id].append(folder)
        
        return FolderStructure(
            root_folders=root_folders,
            subfolder_map=subfolder_map
        )
    
    def create_folder_structure(
        self,
        workspace_id: str,
        structure: Dict[str, Any],
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create multiple folders from a structure definition
        
        Args:
            workspace_id: Workspace GUID
            structure: Folder structure definition
            parent_folder_id: Parent folder for this structure level
        
        Returns:
            Dict[str, str]: Map of folder_name -> folder_id
        
        Example:
            >>> structure = {
            ...     "Bronze Layer": {
            ...         "subfolders": ["Raw", "Archive"]
            ...     },
            ...     "Silver Layer": {},
            ...     "Gold Layer": {}
            ... }
            >>> folder_ids = manager.create_folder_structure(workspace_id, structure)
        """
        folder_ids = {}
        
        for folder_name, config in structure.items():
            # Create folder
            folder_id = self.create_folder(
                workspace_id,
                folder_name,
                parent_folder_id=parent_folder_id
            )
            folder_ids[folder_name] = folder_id
            
            # Create subfolders recursively
            if isinstance(config, dict) and "subfolders" in config:
                for subfolder_name in config["subfolders"]:
                    subfolder_structure = {subfolder_name: {}}
                    sub_ids = self.create_folder_structure(
                        workspace_id,
                        subfolder_structure,
                        parent_folder_id=folder_id
                    )
                    folder_ids.update(sub_ids)
        
        return folder_ids
    
    def print_folder_tree(
        self,
        workspace_id: str,
        show_items: bool = False,
        folder_id: Optional[str] = None,
        prefix: str = ""
    ) -> None:
        """
        Print folder hierarchy as a tree
        
        Args:
            workspace_id: Workspace GUID
            show_items: Whether to show items in folders
            folder_id: Root folder ID (None for workspace root)
            prefix: Indentation prefix (internal use)
        
        Example:
            >>> manager.print_folder_tree(workspace_id, show_items=True)
            📁 Bronze Layer
              📁 Archive
              📊 CustomerData_Lakehouse
              📊 TransactionData_Lakehouse
            📁 Silver Layer
              📓 Transform_Notebook
        """
        # Get folders at this level
        folders = self.list_folders(workspace_id, parent_folder_id=folder_id, include_subfolders=False)
        
        for i, folder in enumerate(folders):
            is_last = (i == len(folders) - 1)
            connector = "└─" if is_last else "├─"
            
            print_info(f"{prefix}{connector} 📁 {folder.display_name}")
            
            # Show items in folder if requested
            if show_items:
                items = self.list_folder_items(workspace_id, folder.id)
                for item in items:
                    item_connector = "  " if is_last else "│ "
                    icon = self._get_item_icon(item["type"])
                    print_info(f"{prefix}{item_connector}  {icon} {item['displayName']}")
            
            # Recursively show subfolders
            new_prefix = prefix + ("  " if is_last else "│ ")
            self.print_folder_tree(workspace_id, show_items, folder.id, new_prefix)
    
    # ========================================================================
    # VALIDATION & UTILITY METHODS
    # ========================================================================
    
    def _validate_folder_name(self, name: str) -> None:
        """Validate folder name meets Fabric requirements"""
        if not name or len(name.strip()) == 0:
            raise FolderValidationError("Folder name cannot be empty")
        
        if len(name) > 256:
            raise FolderValidationError("Folder name too long (max 256 characters)")
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                raise FolderValidationError(f"Folder name contains invalid character: '{char}'")
    
    def _get_folder_depth(self, workspace_id: str, folder_id: str) -> int:
        """Calculate the depth of a folder in the hierarchy"""
        depth = 0
        current_id = folder_id
        
        while current_id:
            try:
                folder = self.get_folder(workspace_id, current_id)
                if folder.parent_folder_id:
                    depth += 1
                    current_id = folder.parent_folder_id
                else:
                    break
            except:
                break
        
        return depth
    
    def _is_descendant(self, workspace_id: str, ancestor_id: str, potential_descendant_id: str) -> bool:
        """Check if potential_descendant is a descendant of ancestor"""
        current_id = potential_descendant_id
        
        while current_id:
            if current_id == ancestor_id:
                return True
            
            try:
                folder = self.get_folder(workspace_id, current_id)
                current_id = folder.parent_folder_id
            except:
                break
        
        return False
    
    @staticmethod
    def _get_item_icon(item_type: str) -> str:
        """Get emoji icon for item type"""
        icons = {
            "Lakehouse": "📊",
            "Notebook": "📓",
            "Warehouse": "🏢",
            "SemanticModel": "📈",
            "Report": "📄",
            "Dashboard": "📊",
            "DataPipeline": "🔄",
            "Eventstream": "📡",
            "KQLDatabase": "🗄️",
            "KQLQueryset": "📝",
            "MLModel": "🤖",
            "MLExperiment": "🧪"
        }
        return icons.get(item_type, "📦")
