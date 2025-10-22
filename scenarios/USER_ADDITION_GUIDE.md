# User & Group Addition Guide - LEIT-Ricoh Workspace

## Overview

Users, Azure AD Groups, and Service Principals are added to Fabric workspaces via **API calls**. This functionality is now available as **core CLI commands** for dynamic reuse across any workspace.

## Quick Start

### Single User/Group (Core CLI)
```bash
python ops/scripts/manage_workspaces.py add-user <workspace_id> <object_id> --role Admin --principal-type User
```

### Bulk Addition (Core CLI) - **RECOMMENDED**
```bash
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file_path>
```

## ⚠️ CRITICAL REQUIREMENT

**The Microsoft Fabric API requires Azure AD Object IDs (GUIDs), NOT email addresses or group names!**

### Users
❌ Wrong: `user@domain.com`  
✅ Correct: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

```bash
az ad user show --id user@domain.com --query id -o tsv
```

### Groups
❌ Wrong: `Engineering Team`  
✅ Correct: `b2c3d4e5-f6g7-8901-bcde-fg2345678901`

```bash
az ad group show --group "Engineering Team" --query id -o tsv
```

### Service Principals
❌ Wrong: `my-sp-name`  
✅ Correct: `c3d4e5f6-g7h8-9012-cdef-gh3456789012`

```bash
az ad sp show --id <client-id> --query id -o tsv
```

## Prerequisites

- Workspace must be created
- You must have Admin permissions on the workspace
- Service principal or user account with proper Azure AD permissions
- **Azure AD Object IDs for all principals to be added**

## Method 1: Core CLI - Bulk (Recommended for Reusability)

### Add Multiple Principals from File

```bash
# Preview what will be added (dry run)
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file> --dry-run

# Add principals (with confirmation)
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file>

# Add principals (skip confirmation)
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file> --yes
```

**Example:**
```bash
# Create your principals file
cp config/workspace_principals.template.txt my_workspace_users.txt

# Edit and add your principals
nano my_workspace_users.txt

# Preview
python ops/scripts/manage_workspaces.py add-users-from-file 8a324e1c-d309-4c77-a047-cc7a8c065456 my_workspace_users.txt --dry-run

# Add to workspace
python ops/scripts/manage_workspaces.py add-users-from-file 8a324e1c-d309-4c77-a047-cc7a8c065456 my_workspace_users.txt
```

### File Format

```text
# Format: principal_id,role,description,type
# Types: User (default), Group, ServicePrincipal

9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Workspace administrator,User
a1b2c3d4-e5f6-7890-abcd-ef1234567890,Viewer,Engineering Team,Group
b2c3d4e5-f6g7-8901-bcde-fg2345678901,Member,CI/CD Pipeline,ServicePrincipal
```

## Method 2: Core CLI - Single Principal (Quick Add)

### Add Single User
```bash
python ops/scripts/manage_workspaces.py add-user <workspace_id> <object_id> --role <role> --principal-type User
```

### Examples

#### Users
```bash
# Add a user as admin
python ops/scripts/manage_workspaces.py add-user 8a324e1c-d309-4c77-a047-cc7a8c065456 9117cbfa-f0a7-43b7-846f-96ba66a3c1c0 --role Admin --principal-type User

# Add a user as member (default type is User)
python ops/scripts/manage_workspaces.py add-user 8a324e1c-d309-4c77-a047-cc7a8c065456 a1b2c3d4-e5f6-7890-abcd-ef1234567890 --role Member
```

#### Groups
```bash
# Add an entire Azure AD group as viewers
python ops/scripts/manage_workspaces.py add-user 8a324e1c-d309-4c77-a047-cc7a8c065456 b2c3d4e5-f6g7-8901-bcde-fg2345678901 --role Viewer --principal-type Group

# Add data engineering team as members
python ops/scripts/manage_workspaces.py add-user 8a324e1c-d309-4c77-a047-cc7a8c065456 c3d4e5f6-g7h8-9012-cdef-gh3456789012 --role Member --principal-type Group
```

#### Service Principals
```bash
# Add CI/CD service principal
python ops/scripts/manage_workspaces.py add-user 8a324e1c-d309-4c77-a047-cc7a8c065456 d4e5f6g7-h8i9-0123-defg-hi4567890123 --role Member --principal-type ServicePrincipal
```

### Available Roles
- `Admin` - Full control of workspace
- `Member` - Can edit content and manage items
- `Contributor` - Can edit content but not manage workspace
- `Viewer` - Read-only access

### Principal Types
- `User` - Individual Azure AD user (default)
- `Group` - Azure AD security or Microsoft 365 group
- `ServicePrincipal` - Service principal for automation

## Method 3: Scenario-Specific Helper (Legacy)

### Step 1: Get Azure AD Object IDs

**IMPORTANT:** The Fabric API requires **Azure AD Object IDs** (GUIDs), not names or emails!

```bash
# Get Object ID for a user
az ad user show --id user@domain.com --query id -o tsv

# Get Object ID for a group
az ad group show --group "Engineering Team" --query id -o tsv

# Get Object ID for a service principal (use client ID)
az ad sp show --id <client-id> --query id -o tsv

# Or use Azure Portal:
# Azure Active Directory > Users/Groups > Select item > Copy Object ID
```

### Step 2: Create Principals File

Create `scenarios/ricoh_users.txt`:
```text
# LEIT-Ricoh Workspace Principals
# Format: object_id,role,description,type
# Types: User (default), Group, ServicePrincipal

# Individual users
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Workspace administrator,User
a1b2c3d4-e5f6-7890-abcd-ef1234567890,Member,Data engineer - Senior,User

# Azure AD Groups (recommended for managing multiple users)
b2c3d4e5-f6g7-8901-bcde-fg2345678901,Viewer,Engineering Team,Group
c3d4e5f6-g7h8-9012-cdef-gh3456789012,Member,Data Science Team,Group

# Service Principals (for automation)
d4e5f6g7-h8i9-0123-defg-hi4567890123,Member,CI/CD Pipeline,ServicePrincipal
```

**Benefits of Using Groups:**
- Add/remove users by managing group membership in Azure AD
- Automatically grants/revokes Fabric workspace access
- Simplifies permission management at scale
- Single entry manages multiple users

### Step 2: Preview (Dry Run)
```bash
cd scenarios
python add_users_from_file.py <workspace_id> ricoh_users.txt --dry-run
```

### Step 3: Add Users
```bash
python add_users_from_file.py <workspace_id> ricoh_users.txt
```

**Example:**
```bash
# Using the latest workspace from our scenario
python add_users_from_file.py 8a324e1c-d309-4c77-a047-cc7a8c065456 ricoh_users.txt
```

## Method 3: Programmatically in Scenario

### Uncomment in `leit_ricoh_fresh_setup.py`

Currently the code is commented out in `step_6_configure_users()`:

```python
# TO ENABLE: Uncomment the following lines (around line 465)

for user in users:
    try:
        self.workspace_mgr.add_user(
            workspace_id=self.workspace_id,
            principal_id=user["email"],
            role=user["role"]
        )
        print_success(f"✓ Added {user['email']} as {user['role'].value}")
    except Exception as e:
        print_warning(f"Could not add {user['email']}: {e}")
```

**Why it's commented out:**
- Email addresses are placeholders
- Need to update with real organizational emails first
- Prevents errors during automated testing

## User Types Supported

### 1. Azure AD Users (Email)
```python
workspace_mgr.add_user(
    workspace_id="...",
    principal_id="user@domain.com",
    principal_type="User",  # Default
    role=WorkspaceRole.MEMBER
)
```

### 2. Azure AD Groups
```python
workspace_mgr.add_user(
    workspace_id="...",
    principal_id="group-object-id",  # Get from Azure AD
    principal_type="Group",
    role=WorkspaceRole.VIEWER
)
```

### 3. Service Principals
```python
workspace_mgr.add_user(
    workspace_id="...",
    principal_id="service-principal-object-id",
    principal_type="ServicePrincipal",
    role=WorkspaceRole.ADMIN
)
```

## Complete Workflow Example

### After Running Fresh Setup Scenario

```bash
# 1. Run the workspace setup
cd /path/to/usf-fabric-cicd
source fabric-env/bin/activate
export $(cat .env | grep -v '^#' | xargs)
python scenarios/leit_ricoh_fresh_setup.py

# Output will show workspace ID:
# Workspace ID: 8a324e1c-d309-4c77-a047-cc7a8c065456

# 2. Update the users file with real emails
vi scenarios/ricoh_users.txt

# 3. Preview user additions
cd scenarios
python add_users_from_file.py 8a324e1c-d309-4c77-a047-cc7a8c065456 ricoh_users.txt --dry-run

# 4. Add users
python add_users_from_file.py 8a324e1c-d309-4c77-a047-cc7a8c065456 ricoh_users.txt
```

## Verifying Users

### List Users in Workspace
```bash
python ops/scripts/manage_workspaces.py list-users <workspace_id>
```

### Example Output
```
Email                               | Role        | Type
-------------------------------------------------------------------
ricoh.admin@leit-teksystems.com     | Admin       | User
ricoh.engineer1@leit-teksystems.com | Member      | User
ricoh.analyst@leit-teksystems.com   | Contributor | User
```

## Removing Users

```bash
# Remove single user
python ops/scripts/manage_workspaces.py remove-user <workspace_id> <email>

# Example
python ops/scripts/manage_workspaces.py remove-user 8a324e1c-d309-4c77-a047-cc7a8c065456 ricoh.business1@leit-teksystems.com
```

## Updating User Roles

```bash
# Update user role
python ops/scripts/manage_workspaces.py update-role <workspace_id> <email> --role <new_role>

# Example: Promote viewer to contributor
python ops/scripts/manage_workspaces.py update-role 8a324e1c-d309-4c77-a047-cc7a8c065456 ricoh.analyst@leit-teksystems.com --role Contributor
```

## Troubleshooting

### User Already Exists
```
⚠️  user@example.com already has access
```
**Solution:** User is already added. Use `update-role` to change their role.

### User Not Found in Azure AD
```
❌ Failed to add user@example.com: User not found
```
**Solution:** 
- Verify email address is correct
- Ensure user exists in your Azure AD tenant
- User must be in the same tenant as the Fabric workspace

### Permission Denied
```
❌ Failed to add user: 403 Forbidden
```
**Solution:**
- Ensure you have Admin role on the workspace
- Service principal needs proper permissions in Azure AD
- Check if workspace is in a secured capacity

## API Details

### Endpoint
```
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/roleAssignments
```

### Request Body
```json
{
  "principal": {
    "id": "user@example.com",
    "type": "User"
  },
  "role": "Member"
}
```

### Response (Success)
```json
{
  "id": "role-assignment-id",
  "principal": {
    "id": "user@example.com",
    "type": "User",
    "displayName": "User Name"
  },
  "role": "Member"
}
```

## Files Created

1. **scenarios/ricoh_users.txt** - Sample user list
2. **scenarios/add_users_from_file.py** - Bulk user addition script

## Summary

✅ Users added via **API calls** (not definition files)  
✅ Three methods: CLI, Bulk file, Programmatic  
✅ Supports Users, Groups, and Service Principals  
✅ Built-in verification and error handling  
✅ Easy role management (add, remove, update)
