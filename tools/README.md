# Operational Tools

Command-line tools for day-to-day Microsoft Fabric workspace operations, bulk actions, and administrative tasks.

## 📁 Tools

### CLI Wrapper

**`fabric-cli.sh`** - User-friendly CLI wrapper
- Simplifies workspace management commands
- Auto-loads `.env` environment variables
- Color-coded output
- Built-in shortcuts and aliases

**Usage:**
```bash
# Show help
./tools/fabric-cli.sh help

# List workspaces
./tools/fabric-cli.sh list
./tools/fabric-cli.sh ls        # shortcut

# List with details
./tools/fabric-cli.sh list --details
./tools/fabric-cli.sh lsd       # shortcut

# Create workspace
./tools/fabric-cli.sh create <name> -e <env>

# Add user
./tools/fabric-cli.sh add-user <workspace-id> <email> --role <role>

# Delete workspace
./tools/fabric-cli.sh delete <workspace-id>
```

**Common Shortcuts:**
- `ls` → list
- `lsd` → list --details

---

### Bulk Operations

**`bulk_delete_workspaces.py`** - Bulk workspace deletion tool
- Delete multiple workspaces at once
- Three deletion modes with safety confirmations

**Mode 1: Direct IDs**
```bash
python tools/bulk_delete_workspaces.py <id1> <id2> <id3>
```

**Mode 2: From File**
```bash
# Create file with workspace IDs (one per line)
# demo_workspaces.txt:
# 8070ecd4-d1f2-4b08-addc-4a78adf2e1a4
# 4f2a427d-9040-4bc6-b410-cbeb8e7c7bf4

python tools/bulk_delete_workspaces.py --file demo_workspaces.txt
python tools/bulk_delete_workspaces.py -f demo_workspaces.txt
```

**Mode 3: Delete All**
```bash
python tools/bulk_delete_workspaces.py --all
# Requires typing: DELETE ALL
```

**Safety Features:**
- ⚠️ Confirmation prompts for all modes
- 📊 Summary report (success/failed counts)
- 💬 Supports comments in files (lines starting with #)

---

## 🚀 Common Workflows

### Quick Workspace Operations

```bash
# List all workspaces
./tools/fabric-cli.sh ls

# Get workspace details
./tools/fabric-cli.sh get <workspace-id>

# Create development workspace
./tools/fabric-cli.sh create "My Workspace" -e dev

# Add admin user
./tools/fabric-cli.sh add-user <workspace-id> admin@company.com --role Admin
```

### Bulk Cleanup

```bash
# Create list of test workspaces to delete
cat > cleanup_list.txt << EOF
# Test workspaces created during development
abc123-def456-ghi789
def456-ghi789-abc123
# Leave production workspaces alone!
EOF

# Preview (dry-run - modify script if needed)
python tools/bulk_delete_workspaces.py --file cleanup_list.txt
# Confirm deletion
```

### Environment Management

```bash
# Delete all dev workspaces
# (requires modifying script to filter by environment)
python tools/bulk_delete_workspaces.py --all
```

---

## 🔧 Tool Comparison

| Tool | Purpose | Safety | Use When |
|------|---------|--------|----------|
| `fabric-cli.sh` | Daily operations | Safe | Single workspace tasks |
| `bulk_delete_workspaces.py` | Bulk cleanup | Confirmations required | Multiple deletions |

---

## 💡 Best Practices

### Using fabric-cli.sh

1. **Always use shortcuts** - `ls` and `lsd` are faster
2. **Set up aliases** - Add to your `.bashrc`:
   ```bash
   alias fabric='./tools/fabric-cli.sh'
   ```
3. **Use tab completion** - If available in your shell

### Using bulk_delete_workspaces.py

1. **Always use file mode for multiple deletions** - Safer and auditable
2. **Add comments to files** - Document why workspaces are being deleted
3. **Keep deletion lists in version control** - Audit trail
4. **Test with small batches first** - Verify before bulk operations
5. **Never use --all in production** - Too risky!

---

## 📋 File Format for Bulk Operations

```text
# Workspace Deletion List
# Format: One workspace ID per line
# Lines starting with # are comments

# Test workspaces from yesterday's demo
8070ecd4-d1f2-4b08-addc-4a78adf2e1a4
4f2a427d-9040-4bc6-b410-cbeb8e7c7bf4

# Failed deployment workspaces
e5ca7fe9-e1f2-470b-97aa-5723ffef40de
```

---

## 🚦 Safety Features

### fabric-cli.sh
- ✅ Loads environment automatically
- ✅ Color-coded output for clarity
- ✅ Built-in help system

### bulk_delete_workspaces.py
- ⚠️ Confirmation prompts required
- 📝 Shows what will be deleted before action
- 📊 Provides success/failure summary
- 🔒 Type-to-confirm for dangerous operations

---

## 🔍 Troubleshooting

### "Command not found: fabric-cli.sh"
```bash
# Make executable
chmod +x tools/fabric-cli.sh

# Or use full path
./tools/fabric-cli.sh
```

### "bulk_delete_workspaces.py can't find workspace_manager"
```bash
# Run from repository root
cd /path/to/usf-fabric-cicd
python tools/bulk_delete_workspaces.py --help
```

### ".env not loaded"
```bash
# fabric-cli.sh auto-loads, but ensure .env exists in root
ls -la .env

# Or source manually
source .env
```

---

## 📚 Related Documentation

- [Main README](../README.md) - Project overview
- [Workspace Management Guide](../docs/workspace-management/WORKSPACE_MANAGEMENT_QUICKREF.md)
- [Setup Scripts](../setup/README.md) - Environment setup
- [Bulk User Management](../BULK_USER_QUICKSTART.md) - User operations

---

## 🎯 Quick Reference

```bash
# Daily operations
./tools/fabric-cli.sh ls
./tools/fabric-cli.sh create "workspace" -e dev
./tools/fabric-cli.sh add-user <id> user@email.com --role Admin

# Bulk cleanup
python tools/bulk_delete_workspaces.py --file cleanup.txt

# Emergency cleanup (USE WITH CAUTION!)
python tools/bulk_delete_workspaces.py --all
```

---

**Location:** `/tools/`  
**Purpose:** Operational utilities  
**Type:** Command-line tools
