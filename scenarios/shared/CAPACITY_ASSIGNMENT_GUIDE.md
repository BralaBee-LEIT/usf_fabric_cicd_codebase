# Fabric Capacity Assignment Guide

## Overview

This guide explains how to assign and manage Fabric capacity for workspaces using the updated `manage_workspaces.py` CLI.

## Background

Microsoft Fabric workspaces require a capacity assignment to create items like:
- Notebooks
- Lakehouses
- Warehouses
- Pipelines
- Semantic Models
- Reports

Without capacity, item creation fails with **403 FeatureNotAvailable** errors.

## Prerequisites

1. **Fabric Capacity Available:**
   - Trial capacity (free, limited duration)
   - Premium capacity (P1-P3 SKUs)
   - Fabric capacity (F2-F64 SKUs)

2. **Capacity ID:**
   - Obtain from Fabric Portal → Capacity Settings
   - Or use Azure Portal → Microsoft Fabric Capacities
   - Format: GUID (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

3. **Permissions:**
   - Capacity Admin role (to view/assign capacity)
   - Workspace Admin role (on target workspace)

## Finding Your Capacity ID

### Option 1: Fabric Portal
```bash
1. Navigate to: https://app.fabric.microsoft.com
2. Click Settings (gear icon) → Admin portal
3. Go to: Capacity settings → Trial/Premium/Fabric
4. Click on your capacity
5. Copy the Capacity ID (GUID)
```

### Option 2: Azure Portal
```bash
1. Navigate to: https://portal.azure.com
2. Search for: "Microsoft Fabric Capacities"
3. Select your capacity
4. Copy the Resource ID (contains capacity GUID)
```

### Option 3: API Query
```bash
# List available capacities (if you have Capacity Admin role)
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.fabric.microsoft.com/v1/capacities
```

## Commands

### 1. Assign Capacity to Workspace

**Syntax:**
```bash
python ops/scripts/manage_workspaces.py assign-capacity <workspace_id> <capacity_id>
```

**Example:**
```bash
# Assign trial capacity to workspace
python ops/scripts/manage_workspaces.py assign-capacity \
  06ca81b0-8135-4c89-90b4-b6a9a3bd1879 \
  a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Output:**
```
ℹ Assigning capacity to workspace: usf2-fabric-fabric-dev
  Workspace ID: 06ca81b0-8135-4c89-90b4-b6a9a3bd1879
  Capacity ID:  a1b2c3d4-e5f6-7890-abcd-ef1234567890
✓ Successfully assigned capacity to workspace 'usf2-fabric-fabric-dev'
  New Capacity ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### 2. Check Current Capacity Assignment

**Syntax:**
```bash
python ops/scripts/manage_workspaces.py get --id <workspace_id>
```

**Example:**
```bash
python ops/scripts/manage_workspaces.py get --id 06ca81b0-8135-4c89-90b4-b6a9a3bd1879
```

**Output:**
```
============================================================
Workspace: usf2-fabric-fabric-dev
============================================================
ID:          06ca81b0-8135-4c89-90b4-b6a9a3bd1879
Type:        Workspace
Capacity:    a1b2c3d4-e5f6-7890-abcd-ef1234567890  ← Capacity assigned
State:       Active
```

### 3. Remove Capacity Assignment

**Syntax:**
```bash
python ops/scripts/manage_workspaces.py unassign-capacity <workspace_id> [-y]
```

**Example:**
```bash
# Interactive (prompts for confirmation)
python ops/scripts/manage_workspaces.py unassign-capacity \
  06ca81b0-8135-4c89-90b4-b6a9a3bd1879

# Force (skip confirmation)
python ops/scripts/manage_workspaces.py unassign-capacity \
  06ca81b0-8135-4c89-90b4-b6a9a3bd1879 -y
```

**Output:**
```
ℹ Removing capacity assignment from workspace: usf2-fabric-fabric-dev
  Workspace ID:     06ca81b0-8135-4c89-90b4-b6a9a3bd1879
  Current Capacity: a1b2c3d4-e5f6-7890-abcd-ef1234567890

This will revert the workspace to Trial/Shared capacity. Continue? (y/N): y
✓ Successfully removed capacity assignment from workspace 'usf2-fabric-fabric-dev'
  Workspace reverted to Trial/Shared capacity
```

## Programmatic Usage (Python)

```python
from ops.scripts.utilities.workspace_manager import WorkspaceManager

# Initialize manager
manager = WorkspaceManager()

# Assign capacity
workspace_id = "06ca81b0-8135-4c89-90b4-b6a9a3bd1879"
capacity_id = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

updated_workspace = manager.assign_capacity(
    workspace_id=workspace_id,
    capacity_id=capacity_id
)

print(f"Capacity assigned: {updated_workspace.get('capacityId')}")

# Verify assignment
workspace = manager.get_workspace_details(workspace_id)
print(f"Current capacity: {workspace.get('capacityId')}")

# Remove capacity (revert to Trial)
manager.unassign_capacity(workspace_id)
```

## Complete Workflow: Fix LEIT-Ricoh Scenario

### Step 1: Get Capacity ID

**Option A: Use Trial Capacity (if available)**
```bash
# Check Fabric Portal for trial capacity GUID
# Usually auto-assigned when trial is enabled
```

**Option B: Request Premium/Fabric Capacity**
```bash
# Contact Azure administrator
# Or provision via Azure Portal
```

### Step 2: Assign Capacity to Workspace

```bash
# Replace with your actual capacity ID
export CAPACITY_ID="your-capacity-guid-here"
export WORKSPACE_ID="06ca81b0-8135-4c89-90b4-b6a9a3bd1879"

cd /home/sanmi/Documents/J\'TOYE_DIGITAL/LEIT_TEKSYSTEMS/1_Project_Rhico/usf-fabric-cicd
source fabric-env/bin/activate
export $(cat .env | grep -v '^#' | xargs)

python ops/scripts/manage_workspaces.py assign-capacity \
  $WORKSPACE_ID \
  $CAPACITY_ID
```

### Step 3: Re-run LEIT-Ricoh Scenario

```bash
# Now that capacity is assigned, items should create successfully
python scenarios/leit_ricoh_setup.py
```

### Step 4: Verify Items Created

```bash
# Check workspace items
python ops/scripts/manage_workspaces.py get --id $WORKSPACE_ID --show-items
```

**Expected Output:**
```
Items:       8

Workspace Items:
Name                      | Type           | State
01_DataIngestion          | Notebook       | Active
02_DataTransformation     | Notebook       | Active
03_DataValidation         | Notebook       | Active
RicohDataLakehouse        | Lakehouse      | Active
RicohAnalyticsWarehouse   | Warehouse      | Active
RicohDataPipeline         | Pipeline       | Active
RicohSemanticModel        | SemanticModel  | Active
RicohExecutiveDashboard   | Report         | Active
```

## Troubleshooting

### Error: "Feature is not available"

**Symptom:**
```
ERROR: 403 - {"errorCode":"FeatureNotAvailable","message":"The feature is not available"}
```

**Cause:** Workspace has no capacity assigned (`capacityId: None`)

**Solution:**
```bash
# Assign capacity first
python ops/scripts/manage_workspaces.py assign-capacity <workspace_id> <capacity_id>
```

### Error: "Trial capacity expired"

**Symptom:**
- Workspace shows `capacityId: None` in API response
- Portal shows "Trial" but items fail to create

**Solution:**
```bash
# Option 1: Re-enable trial in Fabric Portal
# Settings → Trial → Start trial (if available)

# Option 2: Assign Premium/Fabric capacity
python ops/scripts/manage_workspaces.py assign-capacity \
  <workspace_id> <premium_capacity_id>
```

### Error: "Invalid capacity ID"

**Symptom:**
```
ERROR: 400 - Invalid capacity ID
```

**Cause:** Capacity ID doesn't exist or you don't have access

**Solution:**
```bash
# Verify capacity ID in Fabric Portal
# Ensure you have Capacity Admin role
# Check capacity is in same region as workspace
```

### Check Capacity Assignment via API

```bash
cd /home/sanmi/Documents/J\'TOYE_DIGITAL/LEIT_TEKSYSTEMS/1_Project_Rhico/usf-fabric-cicd
source fabric-env/bin/activate
export $(cat .env | grep -v '^#' | xargs)

python3 << 'EOF'
from ops.scripts.utilities.fabric_api import FabricClient

client = FabricClient()
workspace_id = "06ca81b0-8135-4c89-90b4-b6a9a3bd1879"

response = client._make_request('GET', f'workspaces/{workspace_id}')
workspace = response.json()

print(f"Workspace: {workspace.get('displayName')}")
print(f"Capacity ID: {workspace.get('capacityId', 'None')}")

if not workspace.get('capacityId'):
    print("\n❌ No capacity assigned!")
else:
    print("\n✅ Capacity is assigned")
EOF
```

## API Reference

### Fabric REST API - Assign Capacity

**Endpoint:**
```
PATCH https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}
```

**Headers:**
```json
{
  "Authorization": "Bearer {token}",
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "capacityId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Response (200 OK):**
```json
{
  "id": "06ca81b0-8135-4c89-90b4-b6a9a3bd1879",
  "displayName": "usf2-fabric-fabric-dev",
  "type": "Workspace",
  "capacityId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

## Best Practices

1. **Check before assigning:**
   ```bash
   # Verify workspace exists and check current capacity
   python ops/scripts/manage_workspaces.py get --id <workspace_id>
   ```

2. **Use environment variables:**
   ```bash
   # Store capacity IDs in .env or config
   FABRIC_DEV_CAPACITY_ID=xxx
   FABRIC_PROD_CAPACITY_ID=yyy
   ```

3. **Document capacity assignments:**
   ```bash
   # Keep track in project.config.json or docs
   {
     "workspaces": {
       "dev": {
         "id": "...",
         "capacityId": "..."
       }
     }
   }
   ```

4. **Test with trial first:**
   - Always test with trial capacity before using paid capacity
   - Trial limits: 1 capacity per user, expires after 60 days

5. **Monitor capacity usage:**
   - Check Fabric Portal → Capacity settings → Usage metrics
   - Avoid overloading trial capacity

## Related Documentation

- [Workspace Management Guide](../documentation/WORKSPACE_MANAGEMENT_GUIDE.md)
- [LEIT-Ricoh Scenario README](./README.md)
- [Microsoft Fabric Capacity Docs](https://learn.microsoft.com/en-us/fabric/enterprise/licenses)

## Support

For issues with capacity assignment:
1. Check workspace has no items blocking assignment
2. Verify capacity ID is correct (valid GUID format)
3. Ensure you have Capacity Admin permissions
4. Check Fabric service health status
5. Review audit logs in Fabric Portal

---

**Last Updated:** 2025-10-22  
**Version:** 1.0.0
