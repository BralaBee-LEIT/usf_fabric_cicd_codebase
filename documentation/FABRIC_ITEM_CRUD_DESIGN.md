# Fabric Item CRUD - Design & Architecture

## Overview

This document outlines the design and implementation of the Fabric Item CRUD (Create, Read, Update, Delete) management system for Microsoft Fabric. The system provides comprehensive capabilities for managing all Fabric item types programmatically through Python APIs and CLI tools.

## Table of Contents

- [Architecture](#architecture)
- [Supported Item Types](#supported-item-types)
- [Core Components](#core-components)
- [API Design](#api-design)
- [CLI Interface](#cli-interface)
- [Data Models](#data-models)
- [Implementation Details](#implementation-details)
- [Best Practices](#best-practices)
- [Future Enhancements](#future-enhancements)

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌────────────────────┐      ┌──────────────────────────┐  │
│  │  CLI Interface     │      │  Python API              │  │
│  │  manage_fabric_    │      │  Direct Import Usage     │  │
│  │  items.py          │      │                          │  │
│  └────────────────────┘      └──────────────────────────┘  │
└─────────────────────┬───────────────────┬───────────────────┘
                      │                   │
                      ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          FabricItemManager                            │  │
│  │  • create_item()                                      │  │
│  │  • get_item()                                         │  │
│  │  • update_item()                                      │  │
│  │  • delete_item()                                      │  │
│  │  • list_items()                                       │  │
│  │  • get_item_definition()                             │  │
│  │  • update_item_definition()                          │  │
│  │  • find_item_by_name()                               │  │
│  │  • create_or_update_item()                           │  │
│  │  • bulk_delete_items()                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Data Access Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          FabricClient                                 │  │
│  │  • _make_request()                                    │  │
│  │  • _get_access_token()                               │  │
│  │  • Authentication via MSAL                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Microsoft Fabric REST API                    │
│         https://api.fabric.microsoft.com/v1                  │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User Command
    ↓
CLI Parser (argparse)
    ↓
Command Handler (cmd_*)
    ↓
FabricItemManager Method
    ↓
FabricClient._make_request()
    ↓
Microsoft Fabric API
    ↓
Response Processing
    ↓
Console Output / Return Value
```

## Supported Item Types

### Data Factory
- **DataPipeline**: Orchestration pipelines for data movement
- **MountedDataFactory**: External Data Factory connections
- **CopyJob**: Data copy operations

### Data Engineering
- **Environment**: Spark/Python runtime environments
- **GraphQLApi**: GraphQL API endpoints
- **Lakehouse**: Delta Lake storage with SQL analytics
- **Notebook**: Interactive Jupyter notebooks
- **SparkJobDefinition**: Batch Spark job definitions

### Data Science
- **MLModel**: Machine learning models
- **MLExperiment**: ML experiment tracking

### Data Warehouse
- **Datamart**: Self-service data marts
- **MirroredAzureDatabricksCatalog**: Mirrored Databricks catalogs
- **MirroredDatabase**: Mirrored database connections
- **MirroredWarehouse**: Mirrored warehouse instances
- **SQLEndpoint**: SQL query endpoints
- **Warehouse**: Synapse Data Warehouse instances

### Power BI
- **Dashboard**: Power BI dashboards
- **Dataflow**: Dataflow (Gen1)
- **PaginatedReport**: Paginated reports (SSRS-style)
- **Report**: Power BI reports (.pbix)
- **SemanticModel**: Semantic models (datasets)

### Real-Time Intelligence
- **DigitalTwinBuilder**: Digital twin modeling
- **DigitalTwinBuilderFlow**: Digital twin data flows
- **Eventhouse**: Real-time data storage
- **Eventstream**: Event streaming pipelines
- **GraphQuerySet**: Graph query collections
- **KQLDatabase**: Kusto databases
- **KQLQueryset**: KQL query collections
- **KQLDashboard**: Real-time dashboards
- **Reflex**: Reflex (Activator) alerts

### Other
- **HLSCohort**: Healthcare Life Sciences cohorts

## Core Components

### 1. FabricItemManager (`fabric_item_manager.py`)

**Purpose**: Core business logic for Fabric item management

**Key Responsibilities**:
- Item CRUD operations
- Item definition management
- Bulk operations
- Item search and filtering

**Key Methods**:

```python
create_item(workspace_id, display_name, item_type, description, definition)
    → FabricItem
    
get_item(workspace_id, item_id)
    → FabricItem
    
update_item(workspace_id, item_id, display_name, description)
    → FabricItem
    
delete_item(workspace_id, item_id)
    → bool
    
list_items(workspace_id, item_type)
    → List[FabricItem]
    
get_item_definition(workspace_id, item_id, format)
    → Dict[str, Any]
    
update_item_definition(workspace_id, item_id, definition)
    → bool
    
find_item_by_name(workspace_id, display_name, item_type)
    → Optional[FabricItem]
    
create_or_update_item(workspace_id, display_name, item_type, ...)
    → Tuple[FabricItem, bool]
    
bulk_delete_items(workspace_id, item_ids)
    → Dict[str, Any]
```

### 2. Data Models

#### FabricItemType (Enum)
Enumeration of all supported Fabric item types with their API names.

#### ItemDefinitionPart (Dataclass)
Represents a single part of an item definition:
- `path`: File path within the item
- `payload`: Base64-encoded content
- `payload_type`: Typically "InlineBase64"

#### ItemDefinition (Dataclass)
Complete item definition:
- `format`: Optional format specifier (e.g., "ipynb" for notebooks)
- `parts`: List of ItemDefinitionPart objects

#### FabricItem (Dataclass)
Represents a Fabric item with metadata:
- `id`: Unique item identifier
- `display_name`: Human-readable name
- `type`: FabricItemType
- `description`: Optional description
- `workspace_id`: Parent workspace ID
- `definition`: Optional ItemDefinition
- `created_date`: Creation timestamp
- `modified_date`: Last modification timestamp
- `created_by`: Creator user ID
- `modified_by`: Last modifier user ID

### 3. CLI Interface (`manage_fabric_items.py`)

**Purpose**: Command-line interface for item management

**Commands**:

| Command | Description | Key Arguments |
|---------|-------------|---------------|
| `list` | List items in workspace | `--workspace`, `--type`, `--json` |
| `get` | Get item details | `--workspace`, `--item-name/--item-id`, `--json` |
| `create` | Create new item | `--workspace`, `--name`, `--type`, `--definition-file` |
| `update` | Update item properties | `--workspace`, `--item-name/--item-id`, `--new-name`, `--description` |
| `delete` | Delete an item | `--workspace`, `--item-name/--item-id`, `--force` |
| `get-definition` | Get item definition | `--workspace`, `--item-name/--item-id`, `--output` |
| `bulk-delete` | Delete multiple items | `--workspace`, `--ids/--file/--type`, `--force` |

## API Design

### RESTful Endpoints

The system uses Microsoft Fabric REST API v1:

```
Base URL: https://api.fabric.microsoft.com/v1

Endpoints:
  GET    /workspaces/{workspaceId}/items
  GET    /workspaces/{workspaceId}/items?type={itemType}
  GET    /workspaces/{workspaceId}/items/{itemId}
  POST   /workspaces/{workspaceId}/items
  PATCH  /workspaces/{workspaceId}/items/{itemId}
  DELETE /workspaces/{workspaceId}/items/{itemId}
  POST   /workspaces/{workspaceId}/items/{itemId}/getDefinition
  POST   /workspaces/{workspaceId}/items/{itemId}/updateDefinition
```

### Authentication

Uses Azure AD Service Principal authentication via MSAL:

```python
ConfidentialClientApplication(
    client_id=AZURE_CLIENT_ID,
    authority=https://login.microsoftonline.com/{TENANT_ID},
    client_credential=AZURE_CLIENT_SECRET
)

Scope: https://api.fabric.microsoft.com/.default
```

### Request/Response Formats

#### Create Item Request
```json
{
  "displayName": "My Lakehouse",
  "type": "Lakehouse",
  "description": "Development lakehouse",
  "definition": {
    "format": "lakehouse",
    "parts": []
  }
}
```

#### Get Item Response
```json
{
  "id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
  "displayName": "My Lakehouse",
  "type": "Lakehouse",
  "description": "Development lakehouse",
  "workspaceId": "11111111-2222-3333-4444-555555555555",
  "createdDate": "2025-10-11T10:30:00Z",
  "modifiedDate": "2025-10-11T11:45:00Z"
}
```

#### List Items Response
```json
{
  "value": [
    {
      "id": "...",
      "displayName": "Item 1",
      "type": "Lakehouse",
      ...
    },
    {
      "id": "...",
      "displayName": "Item 2",
      "type": "Notebook",
      ...
    }
  ]
}
```

## Implementation Details

### Item Definition Handling

Different item types have different definition requirements:

**1. Empty Definition Items** (created without content):
- Lakehouse
- Warehouse
- ML Model
- ML Experiment

**2. Definition-Based Items** (require content on creation):
- Notebook (requires .ipynb JSON)
- Data Pipeline (requires pipeline JSON)
- Spark Job Definition (requires Python/Scala files)
- Report (requires .pbix file data)

**3. Payload-Only Items**:
- Lakehouse (payload-only creation supported)
- Dataflow (definition-only creation)

### Definition Helper Functions

```python
create_notebook_definition(notebook_content: Dict) -> ItemDefinition
    Converts .ipynb JSON to ItemDefinition

create_pipeline_definition(pipeline_content: Dict) -> ItemDefinition
    Converts pipeline JSON to ItemDefinition

create_spark_job_definition(main_file: str, additional_files: Dict) -> ItemDefinition
    Creates Spark job with main file and dependencies
```

### Error Handling

The system implements comprehensive error handling:

1. **Authentication Errors**: Token acquisition failures
2. **Authorization Errors**: Insufficient permissions
3. **Not Found Errors**: Invalid workspace/item IDs
4. **Validation Errors**: Invalid item types or payloads
5. **Conflict Errors**: Item name conflicts
6. **Network Errors**: Timeout, connection issues

All errors are logged and propagated with meaningful messages.

### Bulk Operations

Bulk delete supports three modes:

1. **Direct ID List**: `--ids id1 id2 id3`
2. **File-Based**: `--file items.txt` (one ID per line, # for comments)
3. **Type-Based**: `--type Notebook` (deletes all of that type)

Safety confirmations required unless `--force` flag used.

## Best Practices

### 1. Naming Conventions
- Use descriptive display names
- Follow organizational naming standards
- Include environment prefix when appropriate

### 2. Item Organization
- Group related items in same workspace
- Use descriptions to document purpose
- Maintain item lifecycle (dev → test → prod)

### 3. Definition Management
- Version control definition files
- Use JSON for all definitions
- Test definitions in dev before prod

### 4. Security
- Use service principals for automation
- Grant least privilege permissions
- Rotate credentials regularly
- Never commit credentials to source control

### 5. Performance
- Use type filters when listing items
- Cache workspace IDs when possible
- Batch operations for multiple items
- Handle rate limiting gracefully

### 6. Error Handling
- Always check return values
- Log all operations
- Implement retry logic for transient failures
- Provide meaningful error messages to users

### 7. Testing
- Test in non-production environments first
- Verify permissions before bulk operations
- Use `--json` output for automation
- Always use `--force` cautiously

## Usage Examples

### Python API Usage

```python
from ops.scripts.utilities.fabric_item_manager import (
    FabricItemManager,
    FabricItemType,
    create_notebook_definition
)

# Initialize manager
manager = FabricItemManager()

# Create a lakehouse (no definition needed)
lakehouse = manager.create_item(
    workspace_id="workspace-guid",
    display_name="MyLakehouse",
    item_type=FabricItemType.LAKEHOUSE,
    description="Development lakehouse"
)

# Create a notebook with content
notebook_json = {...}  # .ipynb content
definition = create_notebook_definition(notebook_json)

notebook = manager.create_item(
    workspace_id="workspace-guid",
    display_name="MyNotebook",
    item_type=FabricItemType.NOTEBOOK,
    definition=definition
)

# List all items
items = manager.list_items(workspace_id="workspace-guid")

# List only notebooks
notebooks = manager.list_items(
    workspace_id="workspace-guid",
    item_type=FabricItemType.NOTEBOOK
)

# Update item
manager.update_item(
    workspace_id="workspace-guid",
    item_id=lakehouse.id,
    display_name="MyLakehouse_v2",
    description="Updated description"
)

# Delete item
manager.delete_item(
    workspace_id="workspace-guid",
    item_id=notebook.id
)

# Bulk delete
results = manager.bulk_delete_items(
    workspace_id="workspace-guid",
    item_ids=["id1", "id2", "id3"]
)
```

### CLI Usage

```bash
# List all items
python ops/scripts/manage_fabric_items.py list \
    --workspace dev-workspace

# List only lakehouses
python ops/scripts/manage_fabric_items.py list \
    --workspace dev-workspace \
    --type Lakehouse

# Create a lakehouse
python ops/scripts/manage_fabric_items.py create \
    --workspace dev-workspace \
    --name MyLakehouse \
    --type Lakehouse \
    --description "Dev lakehouse"

# Create a notebook with definition
python ops/scripts/manage_fabric_items.py create \
    --workspace dev-workspace \
    --name MyNotebook \
    --type Notebook \
    --definition-file notebook.json

# Get item details
python ops/scripts/manage_fabric_items.py get \
    --workspace dev-workspace \
    --item-name MyLakehouse

# Get item details as JSON
python ops/scripts/manage_fabric_items.py get \
    --workspace dev-workspace \
    --item-name MyLakehouse \
    --json

# Update item
python ops/scripts/manage_fabric_items.py update \
    --workspace dev-workspace \
    --item-name MyLakehouse \
    --new-name MyLakehouse_v2 \
    --description "Updated"

# Delete item with confirmation
python ops/scripts/manage_fabric_items.py delete \
    --workspace dev-workspace \
    --item-name MyNotebook

# Delete item without confirmation
python ops/scripts/manage_fabric_items.py delete \
    --workspace dev-workspace \
    --item-name MyNotebook \
    --force

# Get item definition
python ops/scripts/manage_fabric_items.py get-definition \
    --workspace dev-workspace \
    --item-name MyNotebook \
    --output notebook_def.json

# Bulk delete by type
python ops/scripts/manage_fabric_items.py bulk-delete \
    --workspace dev-workspace \
    --type Notebook \
    --force

# Bulk delete from file
python ops/scripts/manage_fabric_items.py bulk-delete \
    --workspace dev-workspace \
    --file item_ids.txt

# Bulk delete specific IDs
python ops/scripts/manage_fabric_items.py bulk-delete \
    --workspace dev-workspace \
    --ids id1 id2 id3 \
    --force
```

## Future Enhancements

### Planned Features

1. **Item Cloning**
   - Clone items within same workspace
   - Clone items across workspaces
   - Clone with name transformation

2. **Item Export/Import**
   - Export item definitions to files
   - Import items from definition files
   - Batch import/export operations

3. **Item Dependencies**
   - Analyze item dependencies
   - Visualize dependency graph
   - Safe deletion with dependency checking

4. **Item Templates**
   - Pre-defined item templates
   - Custom template creation
   - Template marketplace

5. **Item Versioning**
   - Track item definition changes
   - Version history
   - Rollback capabilities

6. **Advanced Search**
   - Search by metadata
   - Full-text search in descriptions
   - Tag-based organization

7. **Item Monitoring**
   - Usage statistics
   - Performance metrics
   - Health checks

8. **Deployment Pipelines**
   - Automated item promotion (dev → test → prod)
   - Approval workflows
   - Rollback mechanisms

### Potential Improvements

1. **Performance Optimization**
   - Implement caching layer
   - Parallel bulk operations
   - Pagination for large lists

2. **Enhanced Error Handling**
   - Retry with exponential backoff
   - Circuit breaker pattern
   - Detailed error reporting

3. **Testing**
   - Unit test coverage
   - Integration tests
   - Mock API for testing

4. **Documentation**
   - Interactive API documentation
   - Video tutorials
   - More code examples

5. **CLI Enhancements**
   - Interactive mode
   - Shell autocompletion
   - Progress bars for long operations
   - Colored output themes

## Conclusion

The Fabric Item CRUD system provides a comprehensive, production-ready solution for managing Microsoft Fabric items programmatically. With support for all major item types, robust error handling, and both Python API and CLI interfaces, it enables efficient automation of Fabric workspace management tasks.

The modular architecture ensures maintainability and extensibility, while the comprehensive documentation and examples make it accessible to developers of all skill levels.

---

**Document Version**: 1.0  
**Last Updated**: October 11, 2025  
**Author**: USF Fabric CI/CD Team
