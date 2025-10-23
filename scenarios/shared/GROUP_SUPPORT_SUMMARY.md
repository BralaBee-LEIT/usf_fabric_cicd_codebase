# Azure AD Group Support for Workspace Access

## ✅ Yes, Full Group Support Exists!

The codebase **already has complete support** for adding Azure AD Groups and Security Groups to workspaces. This functionality has been available all along in the `workspace_manager.add_user()` method.

## Quick Answer

**You can add Azure AD groups to workspaces in three ways:**

### 1. CLI Command
```bash
python ops/scripts/manage_workspaces.py add-user <workspace_id> <group_object_id> \
  --role Viewer \
  --principal-type Group
```

### 2. Bulk File (ricoh_users.txt)
```text
# Add group to file with type column
b2c3d4e5-f6g7-8901-bcde-fg2345678901,Viewer,Engineering Team,Group
```

Then run:
```bash
python scenarios/leit_ricoh_fresh_setup.py
# or
python scenarios/add_users_from_file.py <workspace_id> scenarios/ricoh_users.txt
```

### 3. Programmatically
```python
workspace_mgr.add_user(
    workspace_id=workspace_id,
    principal_id=group_object_id,
    role=WorkspaceRole.VIEWER,
    principal_type="Group"
)
```

## How to Get Group Object ID

```bash
# Azure CLI
az ad group show --group "Engineering Team" --query id -o tsv

# Or use Azure Portal:
# Azure Active Directory > Groups > Select group > Copy Object ID
```

## What Was Updated

To expose this existing functionality to users, the following files were updated:

### 1. `scenarios/ricoh_users.txt` - Updated Format
```text
# NEW: Added optional 4th column for type
# Format: object_id,role,description,type

# Examples:
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Workspace administrator,User
b2c3d4e5-f6g7-8901-bcde-fg2345678901,Viewer,Engineering Team,Group
c3d4e5f6-g7h8-9012-cdef-gh3456789012,Member,CI/CD Pipeline,ServicePrincipal
```

### 2. `scenarios/leit_ricoh_fresh_setup.py` - Updated Parser
- `parse_users_file()` now reads optional 4th column (type)
- Validates type is one of: User, Group, ServicePrincipal
- Defaults to "User" if not specified
- `step_6_configure_users()` passes principal_type to add_user()

### 3. `scenarios/add_users_from_file.py` - Updated Bulk Script
- `parse_users_file()` reads type column
- Display table shows type
- `add_user()` call includes principal_type parameter

### 4. `scenarios/USER_ADDITION_GUIDE.md` - Added Documentation
- Group examples for all three methods
- Azure CLI commands for getting group Object IDs
- Benefits of using groups
- Service principal examples

## Supported Principal Types

| Type | Description | Use Case |
|------|-------------|----------|
| `User` | Individual Azure AD user | Personal access |
| `Group` | Azure AD security/Microsoft 365 group | Team access, easier management |
| `ServicePrincipal` | Service principal/app registration | CI/CD pipelines, automation |

## Benefits of Using Groups

### ✅ Simplified Management
- Add/remove users by managing group membership in Azure AD
- No need to update Fabric workspace for each user change
- Central permission management

### ✅ Scalability
- Single entry in ricoh_users.txt manages entire team
- Automatically grants access to all group members
- Easier to audit and maintain

### ✅ Best Practice
- Aligns with Azure RBAC patterns
- Supports organizational structure
- Easier compliance and governance

## Example Scenario

**Without Groups:** Add 10 engineers individually
```text
engineer1_object_id,Member,Engineer 1,User
engineer2_object_id,Member,Engineer 2,User
engineer3_object_id,Member,Engineer 3,User
# ... 7 more lines
```

**With Groups:** Add entire team at once
```text
engineering_team_object_id,Member,Engineering Team,Group
```

Then manage team membership in Azure AD:
```bash
# Add new engineer to team
az ad group member add --group "Engineering Team" --member-id <new_engineer_object_id>

# Remove engineer from team  
az ad group member remove --group "Engineering Team" --member-id <engineer_object_id>
```

## Testing Group Addition

### Step 1: Get Group Object ID
```bash
# List your groups
az ad group list --query "[].{name:displayName, id:id}" -o table

# Get specific group Object ID
az ad group show --group "Your Group Name" --query id -o tsv
```

### Step 2: Add to ricoh_users.txt
```bash
echo "<group_object_id>,Viewer,Test Group,Group" >> scenarios/ricoh_users.txt
```

### Step 3: Test Addition
```bash
# Via scenario
python scenarios/leit_ricoh_fresh_setup.py

# Or directly via CLI
python ops/scripts/manage_workspaces.py add-user <workspace_id> <group_object_id> \
  --role Viewer \
  --principal-type Group
```

### Step 4: Verify
```bash
# List all workspace role assignments
python ops/scripts/manage_workspaces.py list-users <workspace_id>
```

## Infrastructure Details

### Core Method (Already Existed)
```python
# ops/scripts/utilities/workspace_manager.py (lines 489-539)
def add_user(
    self,
    workspace_id: str,
    principal_id: str,
    principal_type: str = "User",  # ← Supports User, Group, ServicePrincipal
    role: WorkspaceRole = WorkspaceRole.VIEWER
):
    """Add a user, group, or service principal to a workspace"""
    payload = {
        "principal": {
            "id": principal_id,
            "type": principal_type  # ← Sent to Fabric API
        },
        "role": role.value
    }
    # ... API call
```

### CLI Support (Already Existed)
```python
# ops/scripts/manage_workspaces.py (lines 763-778)
parser_add_user.add_argument('--principal-type', default='User',
                            choices=['User', 'Group', 'ServicePrincipal'],
                            help='Principal type (default: User)')
```

## Summary

**Question:** "do we have a functionality that adds users via ad group or security group"

**Answer:** Yes! The functionality was already fully implemented in the codebase. We just updated the user-facing files (ricoh_users.txt format, parsers, and documentation) to expose this capability. You can now add Azure AD groups in all three methods (CLI, bulk file, programmatic) by specifying `principal_type="Group"`.

## Next Steps

1. Get Object ID for your Azure AD group
2. Add to ricoh_users.txt with type "Group"
3. Run scenario or bulk script
4. Manage access by adding/removing users from the group in Azure AD

See `USER_ADDITION_GUIDE.md` for complete examples and troubleshooting.
