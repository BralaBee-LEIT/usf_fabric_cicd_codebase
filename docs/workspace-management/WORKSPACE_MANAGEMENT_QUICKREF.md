# Workspace Management - Quick Reference

**Important**: Use the **existing tools** in the project, don't create new ones!

---

## 🎯 Existing Tools Overview

| Tool | Purpose | Location |
|------|---------|----------|
| `fabric-cli.sh` | Main CLI wrapper | Root directory |
| `manage_workspaces.py` | Full workspace management | `ops/scripts/` |
| `bulk_delete_workspaces.py` | Bulk deletion tool | Root directory |
| `manage_fabric_items.py` | Fabric items CRUD | `ops/scripts/` |
| `workspace_manager.py` | Python API | `ops/scripts/utilities/` |
| `fabric_item_manager.py` | Items API | `ops/scripts/utilities/` |

---

## 📋 Common Workspace Operations

### List Workspaces
```bash
# Using CLI wrapper
./tools/fabric-cli.sh list
./tools/fabric-cli.sh list --details

# Using Python directly
python ops/scripts/manage_workspaces.py list
python ops/scripts/manage_workspaces.py list --details
```

### Create Workspace
```bash
# Using CLI
./tools/fabric-cli.sh create "My Workspace" -e dev

# Using Python (note: -e flag goes before subcommand)
python ops/scripts/manage_workspaces.py -e dev create \
  --name "My Workspace" \
  --capacity-type trial
```

### Delete Single Workspace
```bash
# Using Python
python ops/scripts/manage_workspaces.py delete <workspace-id>

# Using bulk delete tool
python bulk_delete_workspaces.py <workspace-id>
```

### Delete Multiple Workspaces
```bash
# Delete all
python bulk_delete_workspaces.py --all

# Delete from file
python bulk_delete_workspaces.py --file workspaces.txt

# Delete specific IDs
python bulk_delete_workspaces.py <id1> <id2> <id3>
```

---

## 🗑️ Fabric Items Management

### List Items in Workspace
```bash
python ops/scripts/manage_fabric_items.py list \
  --workspace <workspace-id>
```

### Delete Item
```bash
python ops/scripts/manage_fabric_items.py delete \
  --workspace <workspace-id> \
  --item-id <item-id>
```

### Bulk Delete Items
```bash
python ops/scripts/manage_fabric_items.py bulk-delete \
  --workspace <workspace-id> \
  --type Notebook
```

---

## 🔄 Typical Workflow

### 1. Create Test Workspace
```bash
# Create via onboarding automation
python ops/scripts/onboard_data_product.py \
  data_products/onboarding/test_product.yaml
```

### 2. List All Workspaces
```bash
./tools/fabric-cli.sh list
```

### 3. Clean Up After Testing
```bash
# Delete all test workspaces
python bulk_delete_workspaces.py --all
```

---

## 🎯 Use Existing Tools Checklist

Before creating a new script, check if it already exists:

- [ ] Check `fabric-cli.sh` commands
- [ ] Check `ops/scripts/` directory
- [ ] Check `utilities/` directory
- [ ] Review `FABRIC_CLI_QUICKREF.md`
- [ ] Review `FABRIC_ITEM_CRUD_QUICKREF.md`

---

## 📚 Documentation References

- **CLI Quick Reference**: `FABRIC_CLI_QUICKREF.md`
- **Item CRUD Reference**: `FABRIC_ITEM_CRUD_QUICKREF.md`
- **Item CRUD Summary**: `FABRIC_ITEM_CRUD_SUMMARY.md`
- **Bulk Delete Guide**: `BULK_DELETE_QUICKREF.md`

---

## ✅ Example: Complete Cleanup

```bash
# 1. List what exists
./tools/fabric-cli.sh list

# 2. Delete all workspaces
python bulk_delete_workspaces.py --all

# 3. Verify deletion
./tools/fabric-cli.sh list
# Should show: "No workspaces found"
```

---

## 🚀 Key Takeaway

**Use existing tools!** The project already has:
- ✅ Complete workspace management
- ✅ Bulk operations
- ✅ Item CRUD operations
- ✅ CLI wrappers
- ✅ Python APIs

No need to create new scripts unless adding completely new functionality.
