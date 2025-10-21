# Quick Reference: Bulk Delete Workspaces

## Installation
No installation needed - just ensure you have:
- Python 3.8+
- `.env` file configured with Azure credentials
- `ops/scripts/utilities/workspace_manager.py` available

## Quick Start

### 1️⃣ Delete specific workspaces (direct)
```bash
python3 bulk_delete_workspaces.py <id1> <id2> <id3>
```

### 2️⃣ Delete from file
```bash
# Create a file with workspace IDs
cat > my_workspaces.txt << EOF
workspace-id-abc123
workspace-id-def456
workspace-id-ghi789
EOF

# Delete them
python3 bulk_delete_workspaces.py --file my_workspaces.txt
# Then type: DELETE 3
```

### 3️⃣ Delete all workspaces
```bash
python3 bulk_delete_workspaces.py --all
# Then type: DELETE ALL
```

## File Format

**my_workspaces.txt:**
```txt
# One ID per line
workspace-id-1
workspace-id-2

# Comments are allowed
workspace-id-3  # inline comments ignored
```

## Get Workspace IDs

```bash
# List all workspaces
python3 ops/scripts/manage_workspaces.py list

# Export IDs to file
python3 ops/scripts/manage_workspaces.py list --format json | \
  jq -r '.[].id' > workspaces.txt
```

## Safety Tips

✅ **DO:**
- Review the confirmation prompt carefully
- Test with non-production workspaces first
- Keep deletion lists in version control
- Export workspace configs before bulk deletion

❌ **DON'T:**
- Use `--all` in production without review
- Delete workspaces without backup
- Ignore failed deletions in the summary

## Automation

For CI/CD pipelines:

```bash
# Automated with confirmation
echo "DELETE ALL" | python3 bulk_delete_workspaces.py --all

# From file
echo "DELETE 5" | python3 bulk_delete_workspaces.py -f cleanup.txt
```

## Troubleshooting

**Problem:** "File not found"
```bash
# Use absolute path
python3 bulk_delete_workspaces.py -f /full/path/to/file.txt
```

**Problem:** "No workspace IDs found in file"
```bash
# Check file has IDs (not just comments)
cat workspaces.txt | grep -v '^#' | grep -v '^$'
```

**Problem:** Failed deletions
```bash
# Check the summary - retry failed IDs individually
python3 ops/scripts/manage_workspaces.py delete <failed-id>
```

## Examples

**Example 1: Cleanup old test workspaces**
```bash
# Step 1: Find test workspaces
python3 ops/scripts/manage_workspaces.py list -e test > test_workspaces.txt

# Step 2: Extract IDs (manual or with jq)
# Edit test_workspaces.txt to keep only IDs

# Step 3: Delete them
python3 bulk_delete_workspaces.py -f test_workspaces.txt
```

**Example 2: Emergency cleanup**
```bash
# Delete all workspaces immediately
echo "DELETE ALL" | python3 bulk_delete_workspaces.py --all
```

**Example 3: Selective cleanup**
```bash
# Delete specific environments
python3 bulk_delete_workspaces.py \
  <dev-workspace-id> \
  <test-workspace-id> \
  <staging-workspace-id>
```

## See Full Documentation
[BULK_DELETE_README.md](BULK_DELETE_README.md)
