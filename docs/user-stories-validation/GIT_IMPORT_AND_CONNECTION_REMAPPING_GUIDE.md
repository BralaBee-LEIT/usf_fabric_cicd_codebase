# Git Import and Workspace Connection Remapping Guide

**Date:** October 29, 2025  
**Topic:** Handling Git repository imports and semantic model connection remapping  
**Context:** Feature workspace Git sync challenges

---

## 📋 Problem Statement

**Original Question:**
> "I had no problem adding users or groups to a workspace, creating a workspace etc. It is only the importing of items from the connected repository that is an issue. It allows to manually update from the UI. However, this is a problem as it may have connections pointed to the wrong workspace. For example semantic models pointed at the 'DEV' workspace rather than the feature workspace. How did you get round this issue?"

---

## ✅ Our Solution: Two-Part Approach

### Part 1: Controlled Git Import via API
### Part 2: Post-Import Connection Remapping

---

## 🔧 Part 1: Git Import Strategy

### Our Implementation: `FabricGitConnector`

**File:** `ops/scripts/utilities/fabric_git_connector.py`

We **intentionally control when items are imported from Git** to avoid the exact issue you're experiencing.

#### Strategy A: Empty Feature Workspace (Recommended)

**What We Do:**
- Create feature workspace **without importing from Git initially**
- Connect to Git branch but **don't pull items**
- Developers create items **directly in feature workspace**
- Commit feature workspace items **to Git feature branch**

**Code Example:**
```python
from utilities.fabric_git_connector import FabricGitConnector

# Step 1: Create and connect feature workspace to Git
connector = FabricGitConnector(
    organization_name="YourOrg",
    repository_name="YourRepo"
)

# Connect but DON'T auto-commit or import
connector.initialize_git_connection(
    workspace_id="feature-workspace-id",
    branch_name="feature/customer-analytics/JIRA-123",
    directory_path="/data_products/customer-analytics/JIRA-123",
    auto_commit=False  # Don't import items yet
)

# Step 2: Developer creates items in Feature workspace via Fabric UI
# (Lakehouses, Notebooks, Semantic Models with FEATURE workspace connections)

# Step 3: Once items are created, commit to Git
connector.commit_to_git(
    workspace_id="feature-workspace-id",
    comment="Initial feature workspace setup",
    commit_mode="All"
)
```

**Why This Works:**
- ✅ No items imported from DEV branch initially
- ✅ All connections created **in context of feature workspace**
- ✅ Semantic models naturally point to **feature workspace lakehouses**
- ✅ No connection remapping needed

---

#### Strategy B: Selective Import with Connection Awareness

**When You Need DEV Items as Starting Point:**

```python
# Step 1: Connect to Git
connector.initialize_git_connection(
    workspace_id="feature-workspace-id",
    branch_name="feature/customer-analytics/JIRA-123",
    directory_path="/data_products/customer-analytics/JIRA-123"
)

# Step 2: Import items from Git
connector.update_from_git(
    workspace_id="feature-workspace-id",
    allow_override=True,
    conflict_resolution="Git"  # Pull from Git
)

# ⚠️ PROBLEM: Semantic models now point to DEV workspace lakehouses
# ✅ SOLUTION: Part 2 (Connection Remapping) - See below
```

---

## 🔧 Part 2: Post-Import Connection Remapping

### The Challenge

When you import items from Git (especially from DEV branch):
- **Semantic Models** have hardcoded connections to **DEV workspace lakehouses**
- **Reports** reference **DEV workspace semantic models**
- **Notebooks** may have connection strings to **DEV lakehouses**

### Our Solution: `FabricItemManager` + Manual Parameter Updates

**File:** `ops/scripts/utilities/fabric_item_manager.py`

We use the Fabric Items API to:
1. **List all items** in feature workspace
2. **Get item definitions** (includes connection metadata)
3. **Update item definitions** with new workspace references
4. **Redeploy items** with corrected connections

---

### Solution 2A: Automated Item Creation (Preferred)

**Instead of importing from Git, recreate items programmatically:**

```python
from utilities.fabric_item_manager import FabricItemManager, FabricItemType
from utilities.workspace_manager import WorkspaceManager

# Get workspace IDs
wm = WorkspaceManager()
dev_workspace = wm.get_workspace_by_name("Customer Analytics [DEV]")
feature_workspace = wm.get_workspace_by_name("Customer Analytics [FEATURE-JIRA-123]")

dev_workspace_id = dev_workspace['id']
feature_workspace_id = feature_workspace['id']

# Create items in feature workspace
manager = FabricItemManager()

# Step 1: Create Lakehouses in Feature workspace
lakehouse_bronze = manager.create_item(
    workspace_id=feature_workspace_id,
    display_name="lh-customer-analytics-bronze",
    item_type=FabricItemType.LAKEHOUSE,
    description="Bronze layer lakehouse"
)

lakehouse_silver = manager.create_item(
    workspace_id=feature_workspace_id,
    display_name="lh-customer-analytics-silver",
    item_type=FabricItemType.LAKEHOUSE,
    description="Silver layer lakehouse"
)

# Step 2: Create Notebooks with FEATURE workspace connections
# Notebooks can reference the newly created lakehouses
notebook = manager.create_item(
    workspace_id=feature_workspace_id,
    display_name="nb-01-ingest-data",
    item_type=FabricItemType.NOTEBOOK,
    description="Data ingestion notebook"
)

# Step 3: Create Semantic Model with FEATURE workspace lakehouse connection
# Note: Semantic models are complex - see detailed example below
```

**Benefits:**
- ✅ All items created in feature workspace context
- ✅ Connections naturally point to feature workspace
- ✅ No remapping needed
- ✅ Clean separation from DEV workspace

---

### Solution 2B: Connection String Remapping (When Import Needed)

**When you MUST import from Git and remap connections:**

#### Step 1: List Items and Identify Connection Issues

```python
from utilities.fabric_item_manager import FabricItemManager

manager = FabricItemManager()

# List all items in feature workspace
items = manager.list_items(workspace_id="feature-workspace-id")

# Find semantic models (they have connections)
semantic_models = [
    item for item in items 
    if item.type == FabricItemType.SEMANTIC_MODEL
]

print(f"Found {len(semantic_models)} semantic models to remap")
```

#### Step 2: Get Item Definition (Includes Connections)

```python
# Get semantic model definition
for model in semantic_models:
    definition = manager.get_item_definition(
        workspace_id="feature-workspace-id",
        item_id=model.id
    )
    
    # Definition contains connection metadata
    print(f"Model: {model.display_name}")
    print(f"Definition format: {definition['format']}")
    
    # Check for workspace references in definition parts
    for part in definition.get('parts', []):
        # Decode base64 content
        import base64
        content = base64.b64decode(part['payload']).decode('utf-8')
        
        # Check if DEV workspace ID is present
        if dev_workspace_id in content:
            print(f"  ⚠️ Found DEV workspace reference in {part['path']}")
```

#### Step 3: Update Definitions with Feature Workspace Connections

**Semantic Model Connection Remapping:**

```python
import base64
import json

def remap_semantic_model_connections(
    manager: FabricItemManager,
    workspace_id: str,
    model_id: str,
    old_workspace_id: str,  # DEV workspace ID
    new_workspace_id: str,  # Feature workspace ID
    lakehouse_mapping: dict  # Map of old lakehouse IDs to new ones
):
    """
    Remap semantic model connections from DEV to Feature workspace
    
    Args:
        lakehouse_mapping: {"old-lakehouse-id": "new-lakehouse-id"}
    """
    # Get current definition
    definition = manager.get_item_definition(workspace_id, model_id)
    
    # Update definition parts
    updated_parts = []
    for part in definition.get('parts', []):
        # Decode content
        content = base64.b64decode(part['payload']).decode('utf-8')
        
        # Replace workspace ID
        content = content.replace(old_workspace_id, new_workspace_id)
        
        # Replace lakehouse IDs
        for old_lh_id, new_lh_id in lakehouse_mapping.items():
            content = content.replace(old_lh_id, new_lh_id)
        
        # Re-encode
        updated_payload = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        updated_parts.append({
            'path': part['path'],
            'payload': updated_payload,
            'payloadType': 'InlineBase64'
        })
    
    # Update item with new definition
    manager.update_item_definition(
        workspace_id=workspace_id,
        item_id=model_id,
        definition={
            'format': definition['format'],
            'parts': updated_parts
        }
    )
    
    print(f"✓ Remapped connections for semantic model {model_id}")
```

**Usage Example:**

```python
# Step 1: Get lakehouse IDs from both workspaces
dev_lakehouses = manager.list_items(
    workspace_id=dev_workspace_id,
    item_type=FabricItemType.LAKEHOUSE
)

feature_lakehouses = manager.list_items(
    workspace_id=feature_workspace_id,
    item_type=FabricItemType.LAKEHOUSE
)

# Build mapping (assumes same names)
lakehouse_mapping = {}
for dev_lh in dev_lakehouses:
    feature_lh = next(
        (lh for lh in feature_lakehouses if lh.display_name == dev_lh.display_name),
        None
    )
    if feature_lh:
        lakehouse_mapping[dev_lh.id] = feature_lh.id

print(f"Lakehouse mapping: {lakehouse_mapping}")

# Step 2: Remap all semantic models
semantic_models = manager.list_items(
    workspace_id=feature_workspace_id,
    item_type=FabricItemType.SEMANTIC_MODEL
)

for model in semantic_models:
    remap_semantic_model_connections(
        manager=manager,
        workspace_id=feature_workspace_id,
        model_id=model.id,
        old_workspace_id=dev_workspace_id,
        new_workspace_id=feature_workspace_id,
        lakehouse_mapping=lakehouse_mapping
    )
```

---

### Solution 2C: Parameters.yml Approach (Alternative)

**If your semantic models use a parameters file:**

Some organizations use a `parameters.yml` or `config.json` for environment-specific settings.

**Structure:**
```yaml
# parameters.yml (committed to Git)
environments:
  dev:
    workspace_id: "abc-123-dev-workspace"
    lakehouse_bronze_id: "lh-bronze-dev-id"
    lakehouse_silver_id: "lh-silver-dev-id"
  
  feature:
    workspace_id: "xyz-789-feature-workspace"
    lakehouse_bronze_id: "lh-bronze-feature-id"
    lakehouse_silver_id: "lh-silver-feature-id"
```

**Post-Import Script:**

```python
import yaml

# Load parameters
with open('parameters.yml', 'r') as f:
    params = yaml.safe_load(f)

# Get feature workspace parameters
feature_params = params['environments']['feature']

# Update all semantic models using parameters
for model in semantic_models:
    update_model_from_parameters(
        model_id=model.id,
        workspace_id=feature_params['workspace_id'],
        parameters=feature_params
    )
```

**Benefits:**
- ✅ Configuration-driven
- ✅ Easy to maintain multiple environments
- ✅ Can be automated in CI/CD pipeline

---

## 🎯 Our Recommended Workflow

### Workflow: Feature Development with Clean Connections

**Step 1: Create Feature Workspace + Git Branch**
```bash
python ops/scripts/onboard_data_product.py \
  data_products/onboarding/customer_analytics.yaml \
  --feature JIRA-123
```

**What Happens:**
- ✅ Creates feature workspace: "Customer Analytics [FEATURE-JIRA-123]"
- ✅ Creates Git branch: `feature/customer-analytics/JIRA-123`
- ✅ Connects workspace to Git branch
- ✅ **Does NOT import items from DEV branch**

**Step 2: Developer Creates Items in Feature Workspace**

**Via Fabric UI:**
1. Open feature workspace in Fabric portal
2. Create lakehouses manually
3. Create notebooks manually (connections auto-set to feature workspace)
4. Create semantic models manually (select feature workspace lakehouses)

**Via API (Automated):**
```python
# Script: scripts/setup_feature_workspace_items.py

from utilities.fabric_item_manager import FabricItemManager, FabricItemType
from utilities.workspace_manager import WorkspaceManager

def setup_feature_workspace_items(workspace_name: str):
    """Create standardized items in feature workspace"""
    
    wm = WorkspaceManager()
    workspace = wm.get_workspace_by_name(workspace_name)
    workspace_id = workspace['id']
    
    manager = FabricItemManager()
    
    # Create Bronze lakehouse
    bronze = manager.create_item(
        workspace_id=workspace_id,
        display_name="lh-customer-analytics-bronze",
        item_type=FabricItemType.LAKEHOUSE
    )
    
    # Create Silver lakehouse
    silver = manager.create_item(
        workspace_id=workspace_id,
        display_name="lh-customer-analytics-silver",
        item_type=FabricItemType.LAKEHOUSE
    )
    
    # Create Gold lakehouse
    gold = manager.create_item(
        workspace_id=workspace_id,
        display_name="lh-customer-analytics-gold",
        item_type=FabricItemType.LAKEHOUSE
    )
    
    print(f"✓ Created 3 lakehouses in {workspace_name}")
    
    return {
        'bronze_id': bronze.id,
        'silver_id': silver.id,
        'gold_id': gold.id
    }

# Usage
lakehouses = setup_feature_workspace_items("Customer Analytics [FEATURE-JIRA-123]")
```

**Step 3: Commit Feature Workspace to Git**

```python
from utilities.fabric_git_connector import FabricGitConnector

connector = FabricGitConnector(
    organization_name="YourOrg",
    repository_name="YourRepo"
)

# Commit all items in feature workspace to feature branch
connector.commit_to_git(
    workspace_id="feature-workspace-id",
    comment="Initial feature workspace setup with clean connections",
    commit_mode="All"
)
```

**Benefits:**
- ✅ All items created in feature workspace context
- ✅ No DEV workspace references
- ✅ Semantic models automatically reference feature workspace lakehouses
- ✅ Clean Git history on feature branch
- ✅ When merged to main, items are correctly isolated

---

## 📊 Comparison: Import vs. Create

| Aspect | Import from DEV Git | Create in Feature Workspace |
|--------|---------------------|----------------------------|
| **Connections** | ❌ Point to DEV workspace | ✅ Point to Feature workspace |
| **Remapping Needed** | ✅ Yes (manual work) | ❌ No |
| **Setup Time** | ⏱️ Fast initial import | ⏱️ Slower initial setup |
| **Maintenance** | 🔧 Ongoing remapping | ✅ Self-contained |
| **Merge Conflicts** | ⚠️ Higher risk | ✅ Lower risk |
| **Recommended For** | Quick prototypes | Production workflows |

**Our Approach:** ✅ **Create in Feature Workspace**

---

## 🚀 Complete End-to-End Example

### Scenario: Customer Analytics Feature Development

**Step 1: Initialize Feature Environment**

```bash
# Create feature workspace + Git branch
python ops/scripts/onboard_data_product.py \
  data_products/onboarding/customer_analytics.yaml \
  --feature CUST-456
```

**Output:**
```
✓ Created workspace: Customer Analytics [FEATURE-CUST-456]
✓ Created Git branch: feature/customer-analytics/CUST-456
✓ Connected workspace to Git branch
⚠️ Workspace is empty - ready for development
```

**Step 2: Create Items in Feature Workspace**

```python
# Script: setup_customer_analytics_feature.py

from utilities.fabric_item_manager import FabricItemManager, FabricItemType
from utilities.workspace_manager import WorkspaceManager

# Get workspace
wm = WorkspaceManager()
workspace = wm.get_workspace_by_name("Customer Analytics [FEATURE-CUST-456]")
workspace_id = workspace['id']

# Create item manager
manager = FabricItemManager()

# Step 1: Create Lakehouses
print("Creating lakehouses...")
lakehouses = {}

for layer in ['bronze', 'silver', 'gold']:
    lh = manager.create_item(
        workspace_id=workspace_id,
        display_name=f"lh-customer-analytics-{layer}",
        item_type=FabricItemType.LAKEHOUSE,
        description=f"{layer.title()} layer lakehouse"
    )
    lakehouses[layer] = lh.id
    print(f"  ✓ Created {layer} lakehouse: {lh.id}")

# Step 2: Create Notebooks
print("\nCreating notebooks...")
notebooks = [
    ("nb-01-ingest-raw-data", "Ingest raw customer data to Bronze"),
    ("nb-02-cleanse-data", "Cleanse and transform data to Silver"),
    ("nb-03-aggregate-metrics", "Aggregate customer metrics to Gold")
]

for nb_name, nb_desc in notebooks:
    nb = manager.create_item(
        workspace_id=workspace_id,
        display_name=nb_name,
        item_type=FabricItemType.NOTEBOOK,
        description=nb_desc
    )
    print(f"  ✓ Created notebook: {nb_name}")

# Step 3: Create Semantic Model (connected to Gold lakehouse)
print("\nCreating semantic model...")
# Note: Semantic models require detailed schema definition
# This is a placeholder - full implementation depends on your schema

print("\n✅ Feature workspace setup complete!")
print(f"Workspace ID: {workspace_id}")
print(f"Lakehouses: {lakehouses}")
```

**Step 3: Develop Feature**

Developers work in Fabric UI:
1. Open notebooks in feature workspace
2. Write code referencing feature workspace lakehouses
3. Create semantic models pointing to feature workspace Gold lakehouse
4. Create reports using feature workspace semantic models

**All connections stay within feature workspace** - no DEV references!

**Step 4: Commit to Git**

```python
from utilities.fabric_git_connector import FabricGitConnector

connector = FabricGitConnector("YourOrg", "YourRepo")

# Commit everything
connector.commit_to_git(
    workspace_id=workspace_id,
    comment="Completed customer segmentation feature",
    commit_mode="All"
)
```

**Step 5: Create Pull Request**

```bash
# (Manual for now - see User Story 3 gap analysis for automation)
gh pr create \
  --base main \
  --head feature/customer-analytics/CUST-456 \
  --title "Customer Segmentation Feature" \
  --body "Implements RFM analysis and customer segmentation"
```

**Step 6: Cleanup After Merge**

```python
from utilities.workspace_manager import WorkspaceManager

# Delete feature workspace after PR is merged
wm = WorkspaceManager()
wm.delete_workspace(workspace_id, force=True)
```

---

## 💡 Key Takeaways

### 1. **Avoid Importing from DEV Git Branch**
- Creates connection remapping headaches
- Manual UI import has same issue as API import

### 2. **Create Items Fresh in Feature Workspace**
- Connections automatically set to feature workspace
- No remapping needed
- Clean separation between DEV and Feature

### 3. **If You Must Import, Remap Programmatically**
- Use `FabricItemManager` to get/update item definitions
- Replace workspace IDs and lakehouse IDs in definitions
- Automate with parameters.yml file

### 4. **Semantic Models Are Complex**
- Contain embedded workspace references
- Connection strings to lakehouses
- Report references
- Best to create fresh or use parameters file

### 5. **Our Framework Supports Both Approaches**
- `FabricGitConnector` - Git sync control
- `FabricItemManager` - Item creation and update
- `WorkspaceManager` - Workspace operations
- Combine these for your workflow

---

## 📚 References

### Implementation Files

**Git Integration:**
- `ops/scripts/utilities/fabric_git_connector.py` - Git sync APIs
- `ops/scripts/onboard_data_product.py` - Feature workspace creation

**Item Management:**
- `ops/scripts/utilities/fabric_item_manager.py` - Item CRUD operations
- `ops/scripts/manage_fabric_items.py` - CLI for item management

**Workspace Management:**
- `ops/scripts/utilities/workspace_manager.py` - Workspace APIs
- `ops/scripts/manage_workspaces.py` - CLI for workspace management

### Documentation

**User Stories:**
- `docs/user-stories-validation/USER_STORIES_2_3_GAP_ANALYSIS.md` - Feature completion workflow
- `docs/user-stories-validation/USER_STORY_1_ASSESSMENT.md` - Feature workspace validation

**Guides:**
- `docs/guides/WORKSPACE_PROVISIONING_GUIDE.md` - Workspace creation
- `docs/guides/IMPLEMENTATION_GUIDE.md` - Git integration details
- `scenarios/feature-branch-workflow/FEATURE_WORKFLOW_GUIDE.md` - Feature workflow

### API Endpoints Used

**Git Integration:**
- `POST /v1/workspaces/{id}/git/connect` - Connect workspace to Git
- `POST /v1/workspaces/{id}/git/commitToGit` - Commit to Git
- `POST /v1/workspaces/{id}/git/updateFromGit` - Pull from Git
- `GET /v1/workspaces/{id}/git/status` - Get Git status

**Item Management:**
- `POST /v1/workspaces/{id}/items` - Create item
- `GET /v1/workspaces/{id}/items` - List items
- `GET /v1/workspaces/{id}/items/{itemId}` - Get item details
- `POST /v1/workspaces/{id}/items/{itemId}/getDefinition` - Get item definition
- `POST /v1/workspaces/{id}/items/{itemId}/updateDefinition` - Update item definition

---

## 🎯 Next Steps

### For Your Specific Use Case

1. **Short-term (Immediate Fix):**
   - Use `FabricItemManager` to list semantic models in feature workspace
   - Get item definitions
   - Manually remap workspace IDs in definitions
   - Update item definitions

2. **Medium-term (Process Improvement):**
   - Adopt "Create Fresh" approach for feature workspaces
   - Build item creation templates/scripts
   - Standardize lakehouse naming conventions

3. **Long-term (Full Automation):**
   - Implement parameters.yml approach
   - Automate connection remapping in CI/CD
   - Build connection validation tests

### Community Discussion Points

**Microsoft Fabric Community:**
- Ask about official connection remapping APIs
- Request workspace-aware item import
- Suggest relative references in semantic models
- Share your use case for feature branch workflows

**Potential API Enhancements (Future):**
```
POST /v1/workspaces/{id}/git/updateFromGit
{
  "remapConnections": {
    "enabled": true,
    "sourceWorkspaceId": "dev-workspace-id",
    "targetWorkspaceId": "feature-workspace-id"
  }
}
```

---

**Document Version:** 1.0  
**Last Updated:** October 29, 2025  
**Feedback:** Open issue on GitHub or discuss in Microsoft Fabric Community
