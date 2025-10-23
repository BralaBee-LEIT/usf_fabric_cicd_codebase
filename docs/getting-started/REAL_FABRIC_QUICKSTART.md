# Real Fabric Execution - Quick Command Reference

**Quick Links:**
- 📖 Full Guide: `documentation/REAL_FABRIC_EXECUTION_GUIDE.md`
- 🔍 Live Behavior: `documentation/LIVE_FABRIC_RUN_GUIDE.md`
- ✅ Preflight Check: `./preflight_check.sh`

---

## Essential Commands

### Pre-Flight Check
```bash
# Run automated environment validation
./preflight_check.sh
```

### Basic Workflow
```bash
# 1. Activate environment
conda activate fabric-cicd

# 2. Create descriptor
nano data_products/onboarding/my_product.yaml

# 3. Dry run (ALWAYS DO THIS FIRST!)
python ops/scripts/onboard_data_product.py \
  data_products/onboarding/my_product.yaml \
  --dry-run

# 4. Execute against real Fabric
python ops/scripts/onboard_data_product.py \
  data_products/onboarding/my_product.yaml

# 5. Verify in Fabric portal
# https://app.fabric.microsoft.com
```

### Feature Branch Workflow
```bash
# Create feature workspace + branch
python ops/scripts/onboard_data_product.py \
  data_products/onboarding/my_product.yaml \
  --feature ABC-123
```

### Verification Commands
```bash
# Check registry
cat data_products/registry.json | python -m json.tool

# Check audit logs
ls -lh .onboarding_logs/
cat .onboarding_logs/*.json | python -m json.tool | tail -50

# List workspaces via API
python -c "
from ops.scripts.utilities.workspace_manager import WorkspaceManager
wm = WorkspaceManager()
for ws in wm.list_workspaces():
    print(f'{ws[\"displayName\"]:50} {ws[\"id\"]}')
"

# Test authentication
python -c "
from ops.scripts.utilities.workspace_manager import WorkspaceManager
wm = WorkspaceManager()
print('✅ Authentication successful')
"
```

---

## Sample Data Product Descriptor

Save as `data_products/onboarding/my_product.yaml`:

```yaml
product:
  name: My Data Product
  description: "Sample data product for testing"
  owner: data-engineering@company.com
  team: Data Engineering

environments:
  dev:
    enabled: true
    capacity_type: trial  # or premium_p1, fabric_f8, etc.
    capacity_id: null     # optional for Trial
    description: "Development environment"

git:
  provider: GitHub
  organization: "${GITHUB_ORG}"    # Uses value from .env file
  repository: "${GITHUB_REPO}"     # Uses value from .env file
  default_branch: main

scaffold:
  directories:
    - data/bronze
    - data/silver
    - data/gold
    - notebooks
    - pipelines
  notebooks:
    - name: etl_bronze_to_silver
      language: PySpark
      description: "Bronze to silver transformation"
```

---

## Environment Variables (.env)

Minimum required configuration:

```bash
# Azure Service Principal (Required)
AZURE_CLIENT_ID=<your-sp-client-id>
AZURE_CLIENT_SECRET=<your-sp-secret>
AZURE_TENANT_ID=<your-tenant-id>
AZURE_SUBSCRIPTION_ID=<your-subscription-id>

# GitHub (Required for Git integration)
GITHUB_TOKEN=ghp_<your-github-token>
GITHUB_ORG=<your-org>
GITHUB_REPO=<your-repo>

# Optional Configuration
FABRIC_API_MAX_RETRIES=3
LOG_LEVEL=INFO
```

---

## Troubleshooting

### Authentication Failed
```bash
# Verify credentials
source .env
echo "Tenant: $AZURE_TENANT_ID"
echo "Client: $AZURE_CLIENT_ID"

# Test authentication
python -c "
from ops.scripts.utilities.workspace_manager import WorkspaceManager
try:
    wm = WorkspaceManager()
    print('✅ Auth successful')
except Exception as e:
    print(f'❌ Auth failed: {e}')
"
```

### Git Not Initialized
```bash
# Initialize git repository
git init
git remote add origin https://github.com/your-org/your-repo.git
git fetch
git checkout -b main origin/main
```

### Workspace Already Exists
```bash
# Script will reuse existing workspace (safe)
# Or delete manually via API:
python -c "
from ops.scripts.utilities.workspace_manager import WorkspaceManager
wm = WorkspaceManager()
wm.delete_workspace('<workspace-id>')
"
```

---

## Flags Reference

| Flag | Description | Example |
|------|-------------|---------|
| `--dry-run` | Preview without changes | `--dry-run` |
| `--feature <ID>` | Create feature workspace | `--feature ABC-123` |
| `--skip-workspaces` | Skip workspace creation | `--skip-workspaces` |
| `--skip-git` | Skip Git operations | `--skip-git` |
| `--skip-scaffold` | Skip directory creation | `--skip-scaffold` |
| `--json` | JSON output for CI/CD | `--json` |

---

## Expected Execution Time

| Operation | Time |
|-----------|------|
| Dry run | < 1 second |
| DEV workspace only | 20-30 seconds |
| DEV + Feature workspace | 35-45 seconds |
| Full with Git sync | 45-60 seconds |

---

## Success Indicators

✅ **Script completes without errors**  
✅ **Workspace visible in Fabric portal**  
✅ **Git integration shows "Connected"**  
✅ **Registry updated with workspace ID**  
✅ **Audit log created**  
✅ **All 9 tests passing**

---

## Security Notes

- 🔒 **Never commit .env file**
- 🔒 **Logs are automatically sanitized** (credentials redacted)
- 🔒 **Service principal uses least-privilege permissions**
- 🔒 **Audit logs track all operations**

---

## Next Steps After Success

1. **Share workspace URL** with team
2. **Add team members** via Fabric portal
3. **Sync Git** to pull notebooks into workspace
4. **Develop pipelines** using Fabric tools
5. **Set up TEST/PROD** environments
6. **Configure monitoring**

---

## Support Resources

- **Full Guide**: 70+ page step-by-step walkthrough
- **Live Behavior**: API call details and responses
- **Troubleshooting**: Common issues and solutions
- **Tests**: 9 automated tests validate functionality

---

**Ready? Run the preflight check first:**
```bash
./preflight_check.sh
```

**Then execute against real Fabric! 🚀**
