# Workspace Management Guide

Complete guide for managing Microsoft Fabric workspaces across dev, test, and prod environments.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
- [Python API](#python-api)
- [Environment Management](#environment-management)
- [User Management](#user-management)
- [Bulk Operations](#bulk-operations)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Overview

The Workspace Management module provides comprehensive tools for managing Microsoft Fabric workspaces, including:

- **Workspace CRUD operations**: Create, read, update, delete workspaces
- **User management**: Add, remove, and manage user permissions
- **Environment awareness**: Automatic handling of dev, test, prod environments
- **Bulk operations**: Create workspace sets, copy users between workspaces
- **Error handling**: Retry logic for transient failures, rate limiting support
- **CLI & API**: Both command-line interface and Python API available

## Features

### Core Capabilities

✅ **Workspace Operations**
- Create workspaces with environment-specific naming
- List workspaces with filtering options
- Get detailed workspace information
- Update workspace properties
- Delete workspaces with safety checks

✅ **User Management**
- Add users with specific roles (Admin, Member, Contributor, Viewer)
- Remove users from workspaces
- List all users in a workspace
- Update user roles
- Support for Users, Groups, and Service Principals

✅ **Environment Support**
- Automatic workspace naming: `workspace-name-{env}`
- Environment-specific configurations
- Filter workspaces by environment
- Create workspace sets for all environments

✅ **Robustness**
- Automatic retry on rate limiting (429)
- Retry on transient errors (500, 502, 503)
- Exponential backoff
- Comprehensive error messages

## Installation

### Prerequisites

```bash
# Required environment variables
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

### Install Dependencies

```bash
pip install msal requests
```

## Quick Start

### CLI Usage

```bash
# List all workspaces
python3 ops/scripts/manage_workspaces.py list

# List workspaces for specific environment
python3 ops/scripts/manage_workspaces.py list -e dev --filter-env

# Create a workspace (auto-adds environment suffix)
python3 ops/scripts/manage_workspaces.py create my-workspace -e dev

# Add a user to workspace
python3 ops/scripts/manage_workspaces.py add-user WORKSPACE_ID user@example.com --role Admin

# Create complete environment (dev + test + prod)
python3 ops/scripts/manage_workspaces.py create-set my-project
```

### Python API Usage

```python
from ops.scripts.utilities.workspace_manager import WorkspaceManager, WorkspaceRole

# Initialize for specific environment
manager = WorkspaceManager(environment='dev')

# Create workspace (automatically named "my-workspace-dev")
workspace = manager.create_workspace(
    name='my-workspace',
    description='Development workspace'
)

# Add user with admin role
manager.add_user(
    workspace['id'],
    'user@example.com',
    role=WorkspaceRole.ADMIN
)

# List all dev workspaces
workspaces = manager.list_workspaces(filter_by_environment=True)
```

## CLI Reference

### Global Options

```bash
-e, --environment {dev,test,prod}  # Target environment
--json                              # Output in JSON format
-v, --verbose                       # Enable verbose logging
```

### Workspace Commands

#### List Workspaces

```bash
python3 ops/scripts/manage_workspaces.py list [OPTIONS]

Options:
  --filter-env     # Filter by current environment
  --details        # Include detailed information
```

**Example:**
```bash
python3 ops/scripts/manage_workspaces.py list -e dev --filter-env --details
```

#### Create Workspace

```bash
python3 ops/scripts/manage_workspaces.py create NAME [OPTIONS]

Arguments:
  NAME             # Workspace name (without environment suffix)

Options:
  --description TEXT          # Workspace description
  --capacity-id TEXT          # Capacity ID
  --capacity-type TYPE        # Capacity type (Trial, Premium_P1, etc.)
  -e, --environment {dev,test,prod}
```

**Examples:**
```bash
# Create dev workspace
python3 ops/scripts/manage_workspaces.py create data-platform -e dev

# Create with specific capacity
python3 ops/scripts/manage_workspaces.py create analytics \
  --capacity-id "12345-abcde" \
  --capacity-type Premium_P1 \
  -e prod
```

#### Get Workspace Details

```bash
python3 ops/scripts/manage_workspaces.py get {--id ID | --name NAME} [OPTIONS]

Options:
  --id TEXT          # Workspace ID
  --name TEXT        # Workspace name
  --show-items       # Show workspace items
```

**Examples:**
```bash
# Get by ID
python3 ops/scripts/manage_workspaces.py get --id workspace-123 --show-items

# Get by name
python3 ops/scripts/manage_workspaces.py get --name my-workspace -e dev
```

#### Update Workspace

```bash
python3 ops/scripts/manage_workspaces.py update WORKSPACE_ID [OPTIONS]

Arguments:
  WORKSPACE_ID     # Workspace ID

Options:
  --name TEXT          # New workspace name
  --description TEXT   # New description
```

**Example:**
```bash
python3 ops/scripts/manage_workspaces.py update workspace-123 \
  --name updated-workspace \
  --description "Updated description"
```

#### Delete Workspace

```bash
python3 ops/scripts/manage_workspaces.py delete WORKSPACE_ID [OPTIONS]

Arguments:
  WORKSPACE_ID     # Workspace ID

Options:
  --force          # Force deletion even if workspace has items
  -y, --yes        # Skip confirmation prompt
```

**Example:**
```bash
# Safe delete (prompts for confirmation)
python3 ops/scripts/manage_workspaces.py delete workspace-123

# Force delete
python3 ops/scripts/manage_workspaces.py delete workspace-123 --force -y
```

### User Management Commands

#### List Users

```bash
python3 ops/scripts/manage_workspaces.py list-users WORKSPACE_ID

Arguments:
  WORKSPACE_ID     # Workspace ID
```

**Example:**
```bash
python3 ops/scripts/manage_workspaces.py list-users workspace-123 --json
```

#### Add User

```bash
python3 ops/scripts/manage_workspaces.py add-user WORKSPACE_ID PRINCIPAL_ID [OPTIONS]

Arguments:
  WORKSPACE_ID     # Workspace ID
  PRINCIPAL_ID     # User email or service principal ID

Options:
  --role {Admin,Member,Contributor,Viewer}  # Workspace role (default: Viewer)
  --principal-type {User,Group,ServicePrincipal}  # Principal type (default: User)
```

**Examples:**
```bash
# Add user as admin
python3 ops/scripts/manage_workspaces.py add-user workspace-123 user@example.com --role Admin

# Add service principal
python3 ops/scripts/manage_workspaces.py add-user workspace-123 \
  spn-client-id \
  --principal-type ServicePrincipal \
  --role Contributor
```

#### Remove User

```bash
python3 ops/scripts/manage_workspaces.py remove-user WORKSPACE_ID PRINCIPAL_ID

Arguments:
  WORKSPACE_ID     # Workspace ID
  PRINCIPAL_ID     # User email or service principal ID
```

**Example:**
```bash
python3 ops/scripts/manage_workspaces.py remove-user workspace-123 user@example.com
```

#### Update User Role

```bash
python3 ops/scripts/manage_workspaces.py update-role WORKSPACE_ID PRINCIPAL_ID ROLE

Arguments:
  WORKSPACE_ID     # Workspace ID
  PRINCIPAL_ID     # User email or service principal ID
  ROLE             # New role (Admin, Member, Contributor, Viewer)
```

**Example:**
```bash
python3 ops/scripts/manage_workspaces.py update-role workspace-123 user@example.com Member
```

### Bulk Operations

#### Create Workspace Set

```bash
python3 ops/scripts/manage_workspaces.py create-set NAME [OPTIONS]

Arguments:
  NAME             # Base workspace name

Options:
  --environments TEXT  # Comma-separated environments (default: dev,test,prod)
  --description TEXT   # Description template (use {env} for environment)
```

**Examples:**
```bash
# Create dev, test, prod workspaces
python3 ops/scripts/manage_workspaces.py create-set data-platform

# Create only dev and test
python3 ops/scripts/manage_workspaces.py create-set analytics --environments dev,test

# Custom description
python3 ops/scripts/manage_workspaces.py create-set ml-platform \
  --description "Machine Learning Platform - {env} Environment"
```

#### Copy Users Between Workspaces

```bash
python3 ops/scripts/manage_workspaces.py copy-users SOURCE_WS_ID TARGET_WS_ID

Arguments:
  SOURCE_WS_ID     # Source workspace ID
  TARGET_WS_ID     # Target workspace ID
```

**Example:**
```bash
python3 ops/scripts/manage_workspaces.py copy-users workspace-dev workspace-test
```

#### Setup Complete Environment

```bash
python3 ops/scripts/manage_workspaces.py setup PROJECT_NAME --admins EMAILS [OPTIONS]

Arguments:
  PROJECT_NAME     # Project name

Options:
  --admins TEXT    # Comma-separated admin emails (required)
  --members TEXT   # Comma-separated member emails (optional)
```

**Example:**
```bash
python3 ops/scripts/manage_workspaces.py setup data-platform \
  --admins admin1@example.com,admin2@example.com \
  --members dev1@example.com,dev2@example.com
```

## Python API

### WorkspaceManager Class

```python
from ops.scripts.utilities.workspace_manager import (
    WorkspaceManager,
    WorkspaceRole,
    CapacityType
)

# Initialize
manager = WorkspaceManager(environment='dev')  # or 'test', 'prod', None
```

### Workspace Operations

```python
# Create workspace
workspace = manager.create_workspace(
    name='my-workspace',
    description='My workspace',
    capacity_id='optional-capacity-id',
    capacity_type=CapacityType.TRIAL
)
# Returns: {'id': '...', 'displayName': 'my-workspace-dev', ...}

# List workspaces
workspaces = manager.list_workspaces(
    filter_by_environment=True,  # Only show workspaces for current env
    include_details=False         # Include detailed info
)
# Returns: [{'id': '...', 'displayName': '...', ...}, ...]

# Get workspace details
workspace = manager.get_workspace_details('workspace-id')
# Returns: {'id': '...', 'displayName': '...', 'capacityId': '...', ...}

# Get workspace by name
workspace = manager.get_workspace_by_name('my-workspace')
# Returns: Workspace dict or None

# Update workspace
workspace = manager.update_workspace(
    'workspace-id',
    name='new-name',
    description='New description'
)
# Returns: Updated workspace dict

# Delete workspace
success = manager.delete_workspace(
    'workspace-id',
    force=False  # Set True to delete even if workspace has items
)
# Returns: True if successful

# List workspace items
items = manager.list_workspace_items('workspace-id', item_type='Notebook')
# Returns: [{'id': '...', 'displayName': '...', 'type': 'Notebook'}, ...]
```

### User Management

```python
# Add user
user = manager.add_user(
    workspace_id='workspace-123',
    principal_id='user@example.com',
    principal_type='User',  # or 'Group', 'ServicePrincipal'
    role=WorkspaceRole.ADMIN  # or MEMBER, CONTRIBUTOR, VIEWER
)
# Returns: {'identifier': '...', 'principalType': '...', 'workspaceRole': '...'}

# Remove user
success = manager.remove_user('workspace-123', 'user@example.com')
# Returns: True if successful

# List users
users = manager.list_users('workspace-123')
# Returns: [{'identifier': '...', 'principalType': '...', 'workspaceRole': '...'}, ...]

# Update user role
user = manager.update_user_role(
    'workspace-123',
    'user@example.com',
    WorkspaceRole.CONTRIBUTOR
)
# Returns: Updated user dict
```

### Bulk Operations

```python
# Create workspace set (dev, test, prod)
workspaces = manager.create_workspace_set(
    base_name='my-project',
    environments=['dev', 'test', 'prod'],
    description_template='My Project - {env} environment'
)
# Returns: {'dev': {...}, 'test': {...}, 'prod': {...}}

# Copy users between workspaces
results = manager.copy_users_between_workspaces(
    source_workspace_id='workspace-dev',
    target_workspace_id='workspace-test',
    role_mapping={  # Optional: map specific users to different roles
        'user@example.com': WorkspaceRole.VIEWER
    }
)
# Returns: {'success': [...], 'failed': [...], 'skipped': [...]}
```

### Convenience Functions

```python
from ops.scripts.utilities.workspace_manager import (
    create_workspace_for_environment,
    setup_complete_environment
)

# Quick workspace creation
workspace = create_workspace_for_environment(
    workspace_name='analytics',
    environment='dev',
    description='Analytics workspace'
)

# Complete environment setup
workspaces = setup_complete_environment(
    project_name='data-platform',
    admin_emails=['admin@example.com'],
    member_emails=['user1@example.com', 'user2@example.com']
)
# Returns: {'dev': {...}, 'test': {...}, 'prod': {...}}
```

## Environment Management

### Environment Naming Convention

Workspaces are automatically named with environment suffixes:

```
Base name: "data-platform"
Dev:  "data-platform-dev"
Test: "data-platform-test"
Prod: "data-platform-prod"
```

### Environment-Specific Behavior

| Environment | Capacity Default | Approval Required | Auto-deploy |
|-------------|-----------------|-------------------|-------------|
| dev         | Trial           | No                | Yes         |
| test        | Trial           | Yes               | No          |
| prod        | Premium         | Yes               | No          |

### Working Across Environments

```python
# Work with specific environment
dev_manager = WorkspaceManager(environment='dev')
test_manager = WorkspaceManager(environment='test')
prod_manager = WorkspaceManager(environment='prod')

# Work with all environments
all_manager = WorkspaceManager()  # No environment filter
```

## User Management

### Workspace Roles

| Role        | Permissions                                           |
|-------------|-------------------------------------------------------|
| Admin       | Full control: manage workspace, items, and users      |
| Member      | Create and manage items, cannot manage users          |
| Contributor | Edit existing items, cannot create new items          |
| Viewer      | Read-only access to all workspace items               |

### Principal Types

- **User**: Individual user account (email address)
- **Group**: Azure AD security group
- **ServicePrincipal**: Application/service principal ID

### Adding Users Example

```python
# Add individual user
manager.add_user('workspace-123', 'user@example.com', role=WorkspaceRole.MEMBER)

# Add security group
manager.add_user(
    'workspace-123',
    'group-object-id',
    principal_type='Group',
    role=WorkspaceRole.CONTRIBUTOR
)

# Add service principal
manager.add_user(
    'workspace-123',
    'service-principal-id',
    principal_type='ServicePrincipal',
    role=WorkspaceRole.CONTRIBUTOR
)
```

## Bulk Operations

### Creating Workspace Sets

```python
manager = WorkspaceManager()

# Create all three environments
workspaces = manager.create_workspace_set('data-platform')

# Access individual workspaces
dev_ws = workspaces['dev']
test_ws = workspaces['test']
prod_ws = workspaces['prod']

print(f"Dev workspace ID: {dev_ws['id']}")
```

### Promoting Users Across Environments

```python
# Copy dev users to test (common scenario)
manager.copy_users_between_workspaces(
    source_workspace_id='data-platform-dev-id',
    target_workspace_id='data-platform-test-id'
)

# Copy test users to prod with role downgrade
manager.copy_users_between_workspaces(
    source_workspace_id='data-platform-test-id',
    target_workspace_id='data-platform-prod-id',
    role_mapping={
        'user@example.com': WorkspaceRole.VIEWER  # Downgrade specific user
    }
)
```

## Best Practices

### 1. Environment Naming

✅ **Do:**
- Use consistent base names across environments
- Let the tool handle environment suffixes
- Use descriptive names: `data-platform`, `analytics-hub`, `ml-workspace`

❌ **Don't:**
- Manually add environment suffixes
- Use special characters (only alphanumeric, hyphens, underscores)

### 2. User Management

✅ **Do:**
- Use least privilege principle (start with Viewer, escalate as needed)
- Prefer Azure AD groups over individual users for team access
- Document admin users in your project

❌ **Don't:**
- Grant Admin role unnecessarily
- Forget to remove users when they leave the project

### 3. Workspace Deletion

✅ **Do:**
- Always backup important workspaces before deletion
- Review workspace contents before deleting
- Use `--force` flag cautiously

❌ **Don't:**
- Delete production workspaces without approval
- Skip the confirmation prompt in scripts

### 4. Bulk Operations

✅ **Do:**
- Test with dev environment first
- Review results after bulk operations
- Use JSON output for automation

❌ **Don't:**
- Run bulk operations without testing
- Ignore failed operations in results

## Troubleshooting

### Common Issues

#### Authentication Failures

```bash
Error: Missing required Azure credentials
```

**Solution:**
```bash
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

#### Rate Limiting

```
WARNING: Rate limited. Retrying after 60 seconds...
```

**Solution:** The tool automatically handles rate limiting with retry logic. No action needed.

#### Workspace Already Exists

```
ValueError: Workspace 'data-platform-dev' already exists
```

**Solution:**
- List workspaces to verify: `python3 ops/scripts/manage_workspaces.py list -e dev`
- Use a different name or delete the existing workspace

#### Permission Denied

```
Error: 403 Forbidden
```

**Solution:**
- Verify your service principal has Fabric Admin permissions
- Check workspace-level permissions
- Verify Azure AD group memberships

### Debug Mode

Enable verbose logging:

```bash
python3 ops/scripts/manage_workspaces.py list -v --json
```

### Testing Credentials

```python
from ops.scripts.utilities.workspace_manager import WorkspaceManager

try:
    manager = WorkspaceManager()
    workspaces = manager.list_workspaces()
    print(f"✓ Authentication successful! Found {len(workspaces)} workspaces")
except Exception as e:
    print(f"✗ Authentication failed: {e}")
```

## Examples

### Example 1: Complete Project Setup

```bash
#!/bin/bash
# setup_fabric_project.sh

PROJECT_NAME="data-analytics"
ADMINS="admin1@company.com,admin2@company.com"
MEMBERS="dev1@company.com,dev2@company.com,dev3@company.com"

# Create complete environment (dev, test, prod)
python3 ops/scripts/manage_workspaces.py setup "$PROJECT_NAME" \
  --admins "$ADMINS" \
  --members "$MEMBERS" \
  --json > workspace_setup.json

echo "✓ Project setup complete!"
echo "Workspace IDs saved to workspace_setup.json"
```

### Example 2: Promote Workspace from Test to Prod

```python
from ops.scripts.utilities.workspace_manager import WorkspaceManager, WorkspaceRole

# Initialize managers
test_manager = WorkspaceManager(environment='test')
prod_manager = WorkspaceManager(environment='prod')

# Get test workspace
test_ws = test_manager.get_workspace_by_name('data-platform')
print(f"Test workspace: {test_ws['id']}")

# Create prod workspace
prod_ws = prod_manager.create_workspace(
    name='data-platform',
    description='Production data platform',
    capacity_type=CapacityType.PREMIUM_P1
)
print(f"Prod workspace: {prod_ws['id']}")

# Copy users from test to prod (downgrade admins to contributors)
results = prod_manager.copy_users_between_workspaces(
    source_workspace_id=test_ws['id'],
    target_workspace_id=prod_ws['id'],
    role_mapping={
        'devteam@company.com': WorkspaceRole.CONTRIBUTOR  # Downgrade for prod
    }
)

print(f"✓ Copied {len(results['success'])} users to prod")
```

### Example 3: Workspace Inventory Report

```python
from ops.scripts.utilities.workspace_manager import WorkspaceManager
import json

manager = WorkspaceManager()

# Get all workspaces with details
workspaces = manager.list_workspaces(
    filter_by_environment=False,
    include_details=True
)

# Generate report
report = {
    'total_workspaces': len(workspaces),
    'by_environment': {'dev': 0, 'test': 0, 'prod': 0, 'other': 0},
    'workspaces': []
}

for ws in workspaces:
    name = ws['displayName']
    
    # Categorize by environment
    if name.endswith('-dev'):
        report['by_environment']['dev'] += 1
    elif name.endswith('-test'):
        report['by_environment']['test'] += 1
    elif name.endswith('-prod'):
        report['by_environment']['prod'] += 1
    else:
        report['by_environment']['other'] += 1
    
    # Get user count
    users = manager.list_users(ws['id'])
    
    # Get item count
    items = manager.list_workspace_items(ws['id'])
    
    report['workspaces'].append({
        'name': name,
        'id': ws['id'],
        'users': len(users),
        'items': len(items),
        'capacity': ws.get('capacityId', 'Trial')
    })

# Save report
with open('workspace_inventory.json', 'w') as f:
    json.dump(report, f, indent=2)

print(f"✓ Inventory report saved: workspace_inventory.json")
print(f"  Total workspaces: {report['total_workspaces']}")
print(f"  Dev: {report['by_environment']['dev']}, Test: {report['by_environment']['test']}, Prod: {report['by_environment']['prod']}")
```

### Example 4: Automated Cleanup

```python
from ops.scripts.utilities.workspace_manager import WorkspaceManager
from datetime import datetime, timedelta

manager = WorkspaceManager(environment='dev')

# List all dev workspaces
workspaces = manager.list_workspaces(filter_by_environment=True)

# Delete empty workspaces older than 30 days
cutoff_date = datetime.now() - timedelta(days=30)

for ws in workspaces:
    items = manager.list_workspace_items(ws['id'])
    
    if len(items) == 0:  # Empty workspace
        print(f"Deleting empty workspace: {ws['displayName']}")
        manager.delete_workspace(ws['id'], force=True)
    else:
        print(f"Keeping workspace: {ws['displayName']} ({len(items)} items)")
```

---

## Additional Resources

- [Microsoft Fabric REST API Documentation](https://learn.microsoft.com/en-us/rest/api/fabric/)
- [Project QUICKSTART Guide](../QUICKSTART.md)
- [CI/CD Strategy](../docs/ci_cd_strategy.md)
- [Environment Setup](ENVIRONMENT_SETUP.md)

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review test cases in `ops/tests/test_workspace_manager.py`
3. Enable verbose logging with `-v` flag
4. Contact your Fabric administrator
