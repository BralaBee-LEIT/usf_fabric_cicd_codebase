# Quick Reference: Core Bulk User Addition

## ✅ Now Available as Core CLI Command!

## One-Liner Commands

### Preview (Safe)
```bash
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file> --dry-run
```

### Add Users (Interactive)
```bash
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file>
```

### Add Users (Automated)
```bash
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> <file> --yes
```

## Quick Setup

```bash
# 1. Copy template
cp config/workspace_principals.template.txt my_users.txt

# 2. Get Object IDs
az ad user show --id user@domain.com --query id -o tsv
az ad group show --group "Team Name" --query id -o tsv

# 3. Edit file
nano my_users.txt

# 4. Preview
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> my_users.txt --dry-run

# 5. Apply
python ops/scripts/manage_workspaces.py add-users-from-file <workspace_id> my_users.txt
```

## File Format

```text
principal_id,role,description,type
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Administrator,User
a1b2c3d4-e5f6-7890-abcd-ef1234567890,Viewer,Engineering Team,Group
```

## Why This is Better

✅ Works with **any workspace** (not just scenarios)  
✅ Part of core ops toolkit  
✅ Automation-ready (--yes, --dry-run)  
✅ Environment-aware  
✅ Discoverable in help menu  

## Full Docs

- `CORE_BULK_ADDITION.md` - Complete guide
- `USER_ADDITION_GUIDE.md` - All methods
- `GROUP_SUPPORT_SUMMARY.md` - Group details
