# Core Bulk User Addition Feature

## ✅ Moved to Core CLI for Dynamic Reuse

The bulk user/group addition functionality has been promoted from scenario-specific helper to **core reusable CLI command**.

## What Changed

### Before (Scenario-Specific)
```bash
# Only available in scenarios folder
python scenarios/add_users_from_file.py <workspace_id> <file>
```

### After (Core Functionality) ✅
```bash
# Available as core CLI command for any workspace
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file>
```

## New Command Usage

### Basic Usage
```bash
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file>
```

### With Options
```bash
# Preview without changes
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file> --dry-run

# Skip confirmation prompt (for automation)
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file> --yes

# Both options
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file> --dry-run --yes
```

## File Format

```text
# Format: principal_id,role,description,type
# Types: User (default), Group, ServicePrincipal
# Roles: Admin, Member, Contributor, Viewer

# Users
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Workspace administrator,User

# Groups (recommended for teams)
a1b2c3d4-e5f6-7890-abcd-ef1234567890,Viewer,Engineering Team,Group
b2c3d4e5-f6g7-8901-bcde-fg2345678901,Member,Data Science Team,Group

# Service Principals (for automation)
c3d4e5f6-g7h8-9012-cdef-gh3456789012,Member,CI/CD Pipeline,ServicePrincipal
```

## Template File

A reusable template is available:
```bash
# Copy template for your workspace
cp config/workspace_principals.template.txt my_workspace_users.txt

# Edit with your principals
nano my_workspace_users.txt

# Preview
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> my_workspace_users.txt --dry-run

# Apply
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> my_workspace_users.txt
```

## Benefits of Core CLI

### ✅ Dynamic Reusability
- Use with **any workspace**, not just LEIT-Ricoh scenario
- Standardized across all projects
- Part of core ops toolkit

### ✅ Better Integration
- Works with environment configuration (`--environment dev/test/prod`)
- Consistent with other workspace management commands
- Proper logging and error handling

### ✅ Automation-Friendly
- `--yes` flag for CI/CD pipelines
- `--dry-run` for validation
- Exit codes for scripting

### ✅ Discoverability
```bash
python ops/scripts/manage_workspaces.py --help
```
Shows `add-users-from-file` alongside other workspace commands

## Example Workflows

### Workflow 1: New Project Setup
```bash
# Create workspace
python ops/scripts/manage_workspaces.py create "Project Alpha" --environment dev

# Create principals file
cp config/workspace_principals.template.txt project_alpha_users.txt
# Edit file...

# Add team
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> project_alpha_users.txt
```

### Workflow 2: Multi-Environment Sync
```bash
# Same team across dev/test/prod
python ops/scripts/manage_workspaces.py add-users-from-file <dev_workspace_id> team.txt
python ops/scripts/manage_workspaces.py add-users-from-file <test_workspace_id> team.txt
python ops/scripts/manage_workspaces.py add-users-from-file <prod_workspace_id> team.txt
```

### Workflow 3: CI/CD Integration
```bash
#!/bin/bash
# deploy_workspace_access.sh

WORKSPACE_ID=$1
PRINCIPALS_FILE=$2

# Validate first
python ops/scripts/manage_workspaces.py add-users-from-file "$WORKSPACE_ID" "$PRINCIPALS_FILE" --dry-run

# Apply if validation passes
if [ $? -eq 0 ]; then
    python ops/scripts/manage_workspaces.py add-users-from-file "$WORKSPACE_ID" "$PRINCIPALS_FILE" --yes
fi
```

### Workflow 4: Group-Based Access (Recommended)
```bash
# Get group Object IDs
az ad group show --group "Engineering Team" --query id -o tsv > eng_team_id.txt
az ad group show --group "Data Science Team" --query id -o tsv > ds_team_id.txt

# Create principals file with groups
cat > workspace_groups.txt << EOF
$(cat eng_team_id.txt),Viewer,Engineering Team,Group
$(cat ds_team_id.txt),Member,Data Science Team,Group
EOF

# Add groups to workspace
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> workspace_groups.txt

# Now manage access via Azure AD group membership!
az ad group member add --group "Engineering Team" --member-id <user_object_id>
```

## Implementation Details

### Location
`ops/scripts/manage_workspaces.py` (lines 427-530)

### Function
`cmd_add_users_from_file(args)`

### Features
- ✅ CSV parsing with validation
- ✅ Supports User, Group, ServicePrincipal types
- ✅ Role validation (Admin, Member, Contributor, Viewer)
- ✅ Dry-run mode for preview
- ✅ Interactive confirmation (can be skipped with --yes)
- ✅ Summary statistics (success/failed counts)
- ✅ Proper error handling and logging
- ✅ Table display for preview

### Error Handling
- Invalid file format → Warning with line number
- Missing file → Clear error message
- Invalid type → Defaults to "User" with warning
- Invalid role → Defaults to "Viewer" with warning
- Duplicate users → Warning (already has access)
- API failures → Error logged, continues with other principals

## Legacy Scenario Helper

The scenario-specific `scenarios/add_users_from_file.py` still exists for backward compatibility but is **no longer recommended**. Use the core CLI instead.

## Related Commands

```bash
# List all workspace management commands
python ops/scripts/manage_workspaces.py --help

# Single user addition
python ops/scripts/manage_workspaces.py add-user <workspace_id> <object_id> --role Admin --principal-type User

# List current users
python ops/scripts/manage_workspaces.py list-users <workspace_id>

# Remove user
python ops/scripts/manage_workspaces.py remove-user <workspace_id> <object_id>

# Update role
python ops/scripts/manage_workspaces.py update-role <workspace_id> <object_id> Admin

# Copy users between workspaces
python ops/scripts/manage_workspaces.py copy-users <source_workspace_id> <target_workspace_id>
```

## Documentation

- **USER_ADDITION_GUIDE.md** - Updated to prioritize core CLI
- **GROUP_SUPPORT_SUMMARY.md** - Complete group support overview
- **GROUP_SUPPORT_QUICKREF.md** - Quick reference card
- **config/workspace_principals.template.txt** - Reusable template

## Summary

✅ Bulk user addition is now core functionality  
✅ Available for any workspace, not just scenarios  
✅ Supports Users, Groups, and Service Principals  
✅ Automation-ready with --yes and --dry-run flags  
✅ Standardized with other workspace commands  
✅ Template file for quick starts  
✅ Backward compatible (scenario helper still works)  

**Use this for all future workspace access management!**
