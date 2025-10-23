# Quick Reference: Adding Groups to Workspace

## ✅ YES - Full Group Support Available!

## Three Ways to Add Groups

### 1. CLI (Individual)
```bash
python ops/scripts/manage_workspaces.py add-user \
  <workspace_id> \
  <group_object_id> \
  --role Viewer \
  --principal-type Group
```

### 2. File (Bulk) - ricoh_users.txt
```text
# Format: object_id,role,description,type
b2c3d4e5-f6g7-8901-bcde-fg2345678901,Viewer,Engineering Team,Group
```

Run: `python scenarios/leit_ricoh_fresh_setup.py`

### 3. Code
```python
workspace_mgr.add_user(
    workspace_id=workspace_id,
    principal_id=group_object_id,
    role=WorkspaceRole.VIEWER,
    principal_type="Group"
)
```

## Get Group Object ID

```bash
# List groups
az ad group list --query "[].{name:displayName, id:id}" -o table

# Get specific group
az ad group show --group "Team Name" --query id -o tsv
```

## Principal Types Supported

- `User` - Individual users (default)
- `Group` - Azure AD groups **← YOU ASKED ABOUT THIS**
- `ServicePrincipal` - Service principals

## Current ricoh_users.txt

Your file currently has one user:
```text
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Workspace administrator,User
```

To add a group, append:
```bash
# Get your group Object ID
az ad group show --group "Your Group Name" --query id -o tsv

# Add to file
echo "<group_object_id>,Viewer,Your Group,Group" >> scenarios/ricoh_users.txt
```

## Benefits of Groups

✅ Manage users centrally in Azure AD  
✅ Auto-grant/revoke workspace access  
✅ Single entry manages entire team  
✅ Easier compliance and auditing  

## Full Documentation

- `scenarios/GROUP_SUPPORT_SUMMARY.md` - Complete overview
- `scenarios/USER_ADDITION_GUIDE.md` - Updated with group examples
- `scenarios/ricoh_users.txt` - Updated format with examples

## Infrastructure Status

✅ Core API method already supports groups  
✅ CLI already has --principal-type flag  
✅ File format updated to include type column  
✅ Parser updated to read type  
✅ Scenario updated to pass principal_type  
✅ Documentation updated with examples  

**Everything is ready to use!** 🎉
