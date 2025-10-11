# Bulk Delete Workspaces Tool

A utility for deleting multiple Microsoft Fabric workspaces efficiently.

## Features

- ✅ Delete multiple workspaces by ID (command-line arguments)
- ✅ Delete workspaces from a file list
- ✅ Delete all workspaces with confirmation
- ✅ Safety confirmations to prevent accidents
- ✅ Progress tracking and summary statistics
- ✅ Support for comments in workspace files

## Usage

### Method 1: Direct Workspace IDs

Delete specific workspaces by providing their IDs as arguments:

```bash
python3 bulk_delete_workspaces.py <workspace_id_1> <workspace_id_2> <workspace_id_3>
```

**Example:**
```bash
python3 bulk_delete_workspaces.py \
  8070ecd4-d1f2-4b08-addc-4a78adf2e1a4 \
  4f2a427d-9040-4bc6-b410-cbeb8e7c7bf4
```

### Method 2: From a File

Delete workspaces listed in a text file (one ID per line):

```bash
python3 bulk_delete_workspaces.py --file <path/to/file.txt>
# or
python3 bulk_delete_workspaces.py -f <path/to/file.txt>
```

**Example:**
```bash
python3 bulk_delete_workspaces.py --file workspaces_to_delete.txt
```

**File Format:**
```txt
# Workspaces to Delete
# One workspace ID per line
# Lines starting with # are comments

8070ecd4-d1f2-4b08-addc-4a78adf2e1a4
4f2a427d-9040-4bc6-b410-cbeb8e7c7bf4

# Dev workspace - no longer needed
e5ca7fe9-e1f2-470b-97aa-5723ffef40de
```

### Method 3: Delete All Workspaces

Delete all workspaces in the Fabric environment:

```bash
python3 bulk_delete_workspaces.py --all
```

**With piped confirmation:**
```bash
echo "DELETE ALL" | python3 bulk_delete_workspaces.py --all
```

## Safety Features

### Confirmation Prompts

- **Direct IDs**: No confirmation required (you explicitly listed them)
- **From File**: Must type `DELETE <count>` where count is the number of workspaces
- **Delete All**: Must type `DELETE ALL` to confirm

### Visual Feedback

The tool displays:
- ⚠️ Warning messages with workspace list
- 🗑️ Progress updates during deletion
- ✅ Success confirmations
- ❌ Error messages for failed deletions
- 📊 Summary statistics

## Examples

### Example 1: Clean up dev/test workspaces from file

**workspaces_to_delete.txt:**
```txt
# Dev and Test workspaces to clean up
8070ecd4-d1f2-4b08-addc-4a78adf2e1a4  # dev workspace
4f2a427d-9040-4bc6-b410-cbeb8e7c7bf4  # test workspace
```

**Command:**
```bash
python3 bulk_delete_workspaces.py -f workspaces_to_delete.txt
```

**Output:**
```
⚠️  WARNING: You are about to delete 2 workspace(s) from file:
   File: workspaces_to_delete.txt
   - 8070ecd4-d1f2-4b08-addc-4a78adf2e1a4
   - 4f2a427d-9040-4bc6-b410-cbeb8e7c7bf4

Type 'DELETE 2' to confirm: DELETE 2

🗑️  Deleting 2 workspace(s)...
✅ Deleted workspace: 8070ecd4-d1f2-4b08-addc-4a78adf2e1a4
✅ Deleted workspace: 4f2a427d-9040-4bc6-b410-cbeb8e7c7bf4

📊 Summary:
   ✅ Deleted: 2
   ❌ Failed: 0
   📋 Total: 2
```

### Example 2: Delete specific workspaces immediately

```bash
python3 bulk_delete_workspaces.py \
  abc123-workspace-id-1 \
  def456-workspace-id-2
```

### Example 3: Delete all workspaces (with confirmation)

```bash
python3 bulk_delete_workspaces.py --all
```

Then type `DELETE ALL` when prompted.

### Example 4: Automated deletion (CI/CD)

For automated scripts where you can't interact with prompts:

```bash
# Delete all
echo "DELETE ALL" | python3 bulk_delete_workspaces.py --all

# Delete from file
echo "DELETE 3" | python3 bulk_delete_workspaces.py -f cleanup_list.txt
```

## Workflow Integration

### Get Workspace IDs First

Use the workspace management CLI to list workspaces and get their IDs:

```bash
# List all workspaces
python3 ops/scripts/manage_workspaces.py list

# List dev workspaces only
python3 ops/scripts/manage_workspaces.py list -e dev

# Save IDs to file for bulk deletion
python3 ops/scripts/manage_workspaces.py list --format json | \
  jq -r '.[].id' > workspaces_to_delete.txt
```

### Combine with Git Workflow

```bash
# 1. List current workspaces
python3 ops/scripts/manage_workspaces.py list > before_cleanup.txt

# 2. Create deletion list
cat << EOF > workspaces_to_delete.txt
workspace-id-1
workspace-id-2
EOF

# 3. Commit the list (for audit trail)
git add workspaces_to_delete.txt
git commit -m "Workspaces scheduled for deletion"

# 4. Execute deletion
python3 bulk_delete_workspaces.py -f workspaces_to_delete.txt

# 5. Verify cleanup
python3 ops/scripts/manage_workspaces.py list > after_cleanup.txt
```

## Requirements

- Python 3.8+
- Microsoft Fabric API access
- Configured `.env` file with:
  - `AZURE_CLIENT_ID`
  - `AZURE_CLIENT_SECRET`
  - `AZURE_TENANT_ID`
  - `FABRIC_API_BASE_URL`

## Error Handling

The tool handles:
- ✅ Missing files
- ✅ Invalid workspace IDs
- ✅ API authentication failures
- ✅ Network errors
- ✅ Partial failures (continues with remaining workspaces)

Failed deletions are reported in the summary, allowing you to retry them separately.

## Best Practices

1. **Always review the list** before confirming deletion
2. **Use file method** for large-scale deletions (easier to review and audit)
3. **Keep deletion lists** in version control for audit trail
4. **Test with dev workspaces first** before production cleanup
5. **Export workspace configurations** before deletion (if needed for recovery)

## See Also

- [Workspace Management Guide](documentation/WORKSPACE_MANAGEMENT_GUIDE.md)
- [Workspace CLI Reference](ops/scripts/manage_workspaces.py)
