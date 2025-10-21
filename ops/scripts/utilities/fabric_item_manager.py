"""
Microsoft Fabric Item CRUD Manager
Handles Create, Read, Update, Delete operations for all Fabric item types
"""
import os
import json
import base64
import logging
from typing import Dict, Any, Optional, List, Literal
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from .fabric_api import FabricClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FabricItemType(str, Enum):
    """Supported Fabric item types with their API names"""
    # Data Factory
    DATA_PIPELINE = "DataPipeline"
    MOUNTED_DATA_FACTORY = "MountedDataFactory"
    COPY_JOB = "CopyJob"
    
    # Data Engineering
    ENVIRONMENT = "Environment"
    GRAPHQL_API = "GraphQLApi"
    LAKEHOUSE = "Lakehouse"
    NOTEBOOK = "Notebook"
    SPARK_JOB_DEFINITION = "SparkJobDefinition"
    
    # Data Science
    ML_MODEL = "MLModel"
    ML_EXPERIMENT = "MLExperiment"
    
    # Data Warehouse
    DATAMART = "Datamart"
    MIRRORED_AZURE_DATABRICKS_CATALOG = "MirroredAzureDatabricksCatalog"
    MIRRORED_DATABASE = "MirroredDatabase"
    MIRRORED_WAREHOUSE = "MirroredWarehouse"
    SQL_ENDPOINT = "SQLEndpoint"
    WAREHOUSE = "Warehouse"
    
    # Power BI
    DASHBOARD = "Dashboard"
    DATAFLOW = "Dataflow"
    PAGINATED_REPORT = "PaginatedReport"
    REPORT = "Report"
    SEMANTIC_MODEL = "SemanticModel"
    
    # Real-Time Intelligence
    DIGITAL_TWIN_BUILDER = "DigitalTwinBuilder"
    DIGITAL_TWIN_BUILDER_FLOW = "DigitalTwinBuilderFlow"
    EVENTHOUSE = "Eventhouse"
    EVENTSTREAM = "Eventstream"
    GRAPH_QUERY_SET = "GraphQuerySet"
    KQL_DATABASE = "KQLDatabase"
    KQL_QUERYSET = "KQLQueryset"
    KQL_DASHBOARD = "KQLDashboard"
    REFLEX = "Reflex"  # Also known as Activator
    
    # Other
    HLS_COHORT = "HLSCohort"


@dataclass
class ItemDefinitionPart:
    """Represents a part of an item definition"""
    path: str
    payload: str  # Base64 encoded content
    payload_type: str = "InlineBase64"


@dataclass
class ItemDefinition:
    """Item definition structure"""
    format: Optional[str] = None
    parts: List[ItemDefinitionPart] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API payload format"""
        result = {}
        if self.format:
            result["format"] = self.format
        if self.parts:
            result["parts"] = [
                {
                    "path": part.path,
                    "payload": part.payload,
                    "payloadType": part.payload_type
                }
                for part in self.parts
            ]
        return result


@dataclass
class FabricItem:
    """Represents a Fabric item"""
    id: Optional[str] = None
    display_name: str = ""
    type: Optional[FabricItemType] = None
    description: Optional[str] = None
    workspace_id: Optional[str] = None
    definition: Optional[ItemDefinition] = None
    
    # Metadata
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    created_by: Optional[str] = None
    modified_by: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'FabricItem':
        """Create FabricItem from API response"""
        return cls(
            id=data.get('id'),
            display_name=data.get('displayName', ''),
            type=FabricItemType(data.get('type')) if data.get('type') else None,
            description=data.get('description'),
            workspace_id=data.get('workspaceId'),
            created_date=datetime.fromisoformat(data['createdDate'].replace('Z', '+00:00')) if data.get('createdDate') else None,
            modified_date=datetime.fromisoformat(data['modifiedDate'].replace('Z', '+00:00')) if data.get('modifiedDate') else None,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API payload format"""
        payload = {
            "displayName": self.display_name,
            "type": self.type.value if self.type else None,
        }
        
        if self.description:
            payload["description"] = self.description
        
        if self.definition:
            payload["definition"] = self.definition.to_dict()
        
        return payload


class FabricItemManager:
    """Manager for Fabric item CRUD operations"""
    
    def __init__(self, fabric_client: Optional[FabricClient] = None):
        """Initialize the item manager
        
        Args:
            fabric_client: Optional FabricClient instance. If not provided, creates a new one.
        """
        self.client = fabric_client or FabricClient()
    
    def create_item(
        self,
        workspace_id: str,
        display_name: str,
        item_type: FabricItemType,
        description: Optional[str] = None,
        definition: Optional[ItemDefinition] = None
    ) -> FabricItem:
        """Create a new Fabric item
        
        Args:
            workspace_id: The workspace ID where the item will be created
            display_name: Display name for the item
            item_type: Type of the item to create
            description: Optional description
            definition: Optional item definition with content
        
        Returns:
            FabricItem: The created item
        
        Raises:
            ValueError: If item type is not supported for creation
            requests.HTTPError: If the API request fails
        """
        logger.info(f"Creating {item_type.value} '{display_name}' in workspace {workspace_id}")
        
        item = FabricItem(
            display_name=display_name,
            type=item_type,
            description=description,
            definition=definition
        )
        
        payload = item.to_dict()
        
        try:
            response = self.client._make_request(
                'POST',
                f'workspaces/{workspace_id}/items',
                json=payload
            )
            
            result = response.json()
            created_item = FabricItem.from_api_response(result)
            
            logger.info(f"Successfully created {item_type.value} '{display_name}' with ID: {created_item.id}")
            return created_item
            
        except Exception as e:
            logger.error(f"Failed to create {item_type.value} '{display_name}': {str(e)}")
            raise
    
    def get_item(self, workspace_id: str, item_id: str) -> FabricItem:
        """Get a Fabric item by ID
        
        Args:
            workspace_id: The workspace ID
            item_id: The item ID
        
        Returns:
            FabricItem: The requested item
        
        Raises:
            requests.HTTPError: If the item is not found or request fails
        """
        logger.info(f"Getting item {item_id} from workspace {workspace_id}")
        
        try:
            response = self.client._make_request(
                'GET',
                f'workspaces/{workspace_id}/items/{item_id}'
            )
            
            result = response.json()
            item = FabricItem.from_api_response(result)
            
            logger.info(f"Successfully retrieved {item.type.value if item.type else 'item'} '{item.display_name}'")
            return item
            
        except Exception as e:
            logger.error(f"Failed to get item {item_id}: {str(e)}")
            raise
    
    def update_item(
        self,
        workspace_id: str,
        item_id: str,
        display_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> FabricItem:
        """Update a Fabric item's properties
        
        Args:
            workspace_id: The workspace ID
            item_id: The item ID
            display_name: New display name (optional)
            description: New description (optional)
        
        Returns:
            FabricItem: The updated item
        
        Raises:
            requests.HTTPError: If the update fails
        """
        logger.info(f"Updating item {item_id} in workspace {workspace_id}")
        
        payload = {}
        if display_name:
            payload["displayName"] = display_name
        if description is not None:
            payload["description"] = description
        
        if not payload:
            logger.warning("No updates provided")
            return self.get_item(workspace_id, item_id)
        
        try:
            response = self.client._make_request(
                'PATCH',
                f'workspaces/{workspace_id}/items/{item_id}',
                json=payload
            )
            
            result = response.json()
            updated_item = FabricItem.from_api_response(result)
            
            logger.info(f"Successfully updated item '{updated_item.display_name}'")
            return updated_item
            
        except Exception as e:
            logger.error(f"Failed to update item {item_id}: {str(e)}")
            raise
    
    def delete_item(self, workspace_id: str, item_id: str) -> bool:
        """Delete a Fabric item
        
        Args:
            workspace_id: The workspace ID
            item_id: The item ID to delete
        
        Returns:
            bool: True if deletion was successful
        
        Raises:
            requests.HTTPError: If the deletion fails
        """
        logger.info(f"Deleting item {item_id} from workspace {workspace_id}")
        
        try:
            self.client._make_request(
                'DELETE',
                f'workspaces/{workspace_id}/items/{item_id}'
            )
            
            logger.info(f"Successfully deleted item {item_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete item {item_id}: {str(e)}")
            raise
    
    def list_items(
        self,
        workspace_id: str,
        item_type: Optional[FabricItemType] = None
    ) -> List[FabricItem]:
        """List items in a workspace
        
        Args:
            workspace_id: The workspace ID
            item_type: Optional filter by item type
        
        Returns:
            List[FabricItem]: List of items in the workspace
        
        Raises:
            requests.HTTPError: If the request fails
        """
        logger.info(f"Listing items in workspace {workspace_id}" + 
                   (f" (type: {item_type.value})" if item_type else ""))
        
        endpoint = f'workspaces/{workspace_id}/items'
        if item_type:
            endpoint += f'?type={item_type.value}'
        
        try:
            response = self.client._make_request('GET', endpoint)
            result = response.json()
            
            items = [FabricItem.from_api_response(item_data) 
                    for item_data in result.get('value', [])]
            
            logger.info(f"Found {len(items)} items")
            return items
            
        except Exception as e:
            logger.error(f"Failed to list items: {str(e)}")
            raise
    
    def get_item_definition(self, workspace_id: str, item_id: str, format: Optional[str] = None) -> Dict[str, Any]:
        """Get the definition of an item
        
        Args:
            workspace_id: The workspace ID
            item_id: The item ID
            format: Optional format parameter
        
        Returns:
            Dict containing the item definition
        
        Raises:
            requests.HTTPError: If the request fails
        """
        logger.info(f"Getting definition for item {item_id}")
        
        endpoint = f'workspaces/{workspace_id}/items/{item_id}/getDefinition'
        params = {}
        if format:
            params['format'] = format
        
        try:
            response = self.client._make_request('POST', endpoint, params=params)
            result = response.json()
            
            logger.info(f"Successfully retrieved item definition")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get item definition: {str(e)}")
            raise
    
    def update_item_definition(
        self,
        workspace_id: str,
        item_id: str,
        definition: ItemDefinition
    ) -> bool:
        """Update the definition of an item
        
        Args:
            workspace_id: The workspace ID
            item_id: The item ID
            definition: The new item definition
        
        Returns:
            bool: True if update was successful
        
        Raises:
            requests.HTTPError: If the update fails
        """
        logger.info(f"Updating definition for item {item_id}")
        
        payload = {"definition": definition.to_dict()}
        
        try:
            self.client._make_request(
                'POST',
                f'workspaces/{workspace_id}/items/{item_id}/updateDefinition',
                json=payload
            )
            
            logger.info(f"Successfully updated item definition")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update item definition: {str(e)}")
            raise
    
    def find_item_by_name(
        self,
        workspace_id: str,
        display_name: str,
        item_type: Optional[FabricItemType] = None
    ) -> Optional[FabricItem]:
        """Find an item by display name
        
        Args:
            workspace_id: The workspace ID
            display_name: The display name to search for
            item_type: Optional item type filter
        
        Returns:
            FabricItem if found, None otherwise
        """
        items = self.list_items(workspace_id, item_type)
        
        for item in items:
            if item.display_name == display_name:
                return item
        
        return None
    
    def create_or_update_item(
        self,
        workspace_id: str,
        display_name: str,
        item_type: FabricItemType,
        description: Optional[str] = None,
        definition: Optional[ItemDefinition] = None
    ) -> tuple[FabricItem, bool]:
        """Create an item or update it if it already exists
        
        Args:
            workspace_id: The workspace ID
            display_name: Display name for the item
            item_type: Type of the item
            description: Optional description
            definition: Optional item definition
        
        Returns:
            Tuple of (FabricItem, is_new) where is_new is True if item was created
        """
        existing_item = self.find_item_by_name(workspace_id, display_name, item_type)
        
        if existing_item:
            logger.info(f"Item '{display_name}' already exists, updating...")
            
            # Update properties
            if description:
                self.update_item(workspace_id, existing_item.id, description=description)
            
            # Update definition if provided
            if definition:
                self.update_item_definition(workspace_id, existing_item.id, definition)
            
            updated_item = self.get_item(workspace_id, existing_item.id)
            return updated_item, False
        else:
            logger.info(f"Item '{display_name}' not found, creating...")
            new_item = self.create_item(
                workspace_id=workspace_id,
                display_name=display_name,
                item_type=item_type,
                description=description,
                definition=definition
            )
            return new_item, True
    
    def bulk_delete_items(
        self,
        workspace_id: str,
        item_ids: List[str]
    ) -> Dict[str, Any]:
        """Delete multiple items
        
        Args:
            workspace_id: The workspace ID
            item_ids: List of item IDs to delete
        
        Returns:
            Dict with success/failure counts and details
        """
        results = {
            "total": len(item_ids),
            "succeeded": 0,
            "failed": 0,
            "errors": []
        }
        
        for item_id in item_ids:
            try:
                self.delete_item(workspace_id, item_id)
                results["succeeded"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "item_id": item_id,
                    "error": str(e)
                })
        
        logger.info(f"Bulk delete completed: {results['succeeded']}/{results['total']} succeeded")
        return results


# Helper functions for creating common item types

def create_lakehouse_definition(display_name: str) -> ItemDefinition:
    """Create a basic lakehouse definition (payload-only)
    
    Note: Lakehouses support payload-only creation
    """
    # Lakehouse uses payload, not definition parts
    return None  # Create with empty definition


def create_notebook_definition(notebook_content: Dict[str, Any]) -> ItemDefinition:
    """Create a notebook definition from notebook JSON
    
    Args:
        notebook_content: Notebook content in .ipynb format
    
    Returns:
        ItemDefinition for the notebook
    """
    content_json = json.dumps(notebook_content)
    encoded_content = base64.b64encode(content_json.encode()).decode()
    
    return ItemDefinition(
        format="ipynb",
        parts=[
            ItemDefinitionPart(
                path="notebook-content.py",
                payload=encoded_content
            )
        ]
    )


def create_pipeline_definition(pipeline_content: Dict[str, Any]) -> ItemDefinition:
    """Create a data pipeline definition
    
    Args:
        pipeline_content: Pipeline JSON definition
    
    Returns:
        ItemDefinition for the pipeline
    """
    content_json = json.dumps(pipeline_content)
    encoded_content = base64.b64encode(content_json.encode()).decode()
    
    return ItemDefinition(
        parts=[
            ItemDefinitionPart(
                path="pipeline-content.json",
                payload=encoded_content
            )
        ]
    )


def create_spark_job_definition(main_file: str, additional_files: Optional[Dict[str, str]] = None) -> ItemDefinition:
    """Create a Spark job definition
    
    Args:
        main_file: Main Python/Scala file content
        additional_files: Optional dict of filename -> content
    
    Returns:
        ItemDefinition for the Spark job
    """
    parts = [
        ItemDefinitionPart(
            path="main.py",
            payload=base64.b64encode(main_file.encode()).decode()
        )
    ]
    
    if additional_files:
        for filename, content in additional_files.items():
            parts.append(
                ItemDefinitionPart(
                    path=filename,
                    payload=base64.b64encode(content.encode()).decode()
                )
            )
    
    return ItemDefinition(parts=parts)


# Global instance for convenience
_item_manager_instance = None

def get_item_manager() -> FabricItemManager:
    """Get or create the global FabricItemManager instance"""
    global _item_manager_instance
    if _item_manager_instance is None:
        _item_manager_instance = FabricItemManager()
    return _item_manager_instance
