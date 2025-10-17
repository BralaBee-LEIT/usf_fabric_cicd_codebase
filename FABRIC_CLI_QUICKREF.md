# Fabric CLI - Quick Reference Card

## 🚀 Super Short Commands

### Workspace Operations
```bash
./fabric-cli.sh ls                    # List all workspaces
./fabric-cli.sh lsd                   # List with details
./fabric-cli.sh create my-ws -e dev   # Create dev workspace
./fabric-cli.sh get WORKSPACE_ID      # Get workspace info
./fabric-cli.sh delete WORKSPACE_ID   # Delete workspace
```

### Environment Setup
```bash
./fabric-cli.sh create-set analytics  # Create dev/test/prod at once
```

### User Management
```bash
# Add user as Admin
./fabric-cli.sh add-user WORKSPACE_ID user@example.com --role Admin

# Add user as Member
./fabric-cli.sh add-user WORKSPACE_ID user@example.com --role Member

# List users
./fabric-cli.sh list-users WORKSPACE_ID

# Remove user
./fabric-cli.sh remove-user WORKSPACE_ID USER_ID
```

### Bulk Operations
```bash
# Delete multiple workspaces from file
./fabric-cli.sh delete-bulk --file workspaces.txt

# Delete all in dev environment
./fabric-cli.sh delete-all -e dev
```

---

## 📋 Your Current Workspaces

| Environment | Name | ID |
|-------------|------|-----|
| Dev | `usf-fabric-fabric-dev` | `205bdcad-cf08-4785-bcf2-1f656e4599a7` |
| Test | `usf-fabric-fabric-test` | `67333397-e772-4269-baf0-34acdd1b2ac1` |
| Prod | `usf-fabric-fabric-prod` | `6a0a271c-8aac-4b19-a660-edb12c8e16c8` |

---

## 💡 Common Workflows

### Add Team Member to All Environments
```bash
# Dev
./fabric-cli.sh add-user 205bdcad-cf08-4785-bcf2-1f656e4599a7 dev@example.com --role Member

# Test
./fabric-cli.sh add-user 67333397-e772-4269-baf0-34acdd1b2ac1 dev@example.com --role Member

# Prod (Admin only)
./fabric-cli.sh add-user 6a0a271c-8aac-4b19-a660-edb12c8e16c8 admin@example.com --role Admin
```

### Create New Project Workspaces
```bash
./fabric-cli.sh create-set project-name
```

### Check Who Has Access
```bash
./fabric-cli.sh list-users 205bdcad-cf08-4785-bcf2-1f656e4599a7
```

---

## 🎯 Roles Explained

| Role | Permissions |
|------|-------------|
| **Admin** | Full control - manage workspace, users, and content |
| **Member** | Create and edit content, cannot manage workspace |
| **Contributor** | Edit existing content, cannot create new |
| **Viewer** | Read-only access |

---

## ⚡ Pro Tips

1. **Always use shortcuts**: `ls` instead of `list`
2. **Save IDs**: Keep workspace IDs handy for quick access
3. **Use variables**: 
   ```bash
   DEV_WS="205bdcad-cf08-4785-bcf2-1f656e4599a7"
   ./fabric-cli.sh get $DEV_WS
   ```
4. **Check help anytime**: `./fabric-cli.sh help`

---

## 🔧 Troubleshooting

### Command not working?
```bash
# Make sure it's executable
chmod +x fabric-cli.sh

# Check .env file exists
ls -la .env
```

### Need to see more info?
```bash
# Add --details to most commands
./fabric-cli.sh lsd
```

### Want JSON output?
```bash
./fabric-cli.sh list --json
```

---

**Last Updated**: October 16, 2025  
**Your Project**: usf-fabric-cicd
