# Feature Branch Workflow - Quick Reference

## Quick Commands

### Create Feature Environment
```bash
cd /path/to/usf-fabric-cicd/scenarios/feature-branch-workflow

# Create feature workspace + branch
python3 ../../ops/scripts/onboard_data_product.py \
  product_descriptor.yaml \
  --feature JIRA-12345
```

### Verify Creation
```bash
# Check Git branch
git branch -a | grep JIRA-12345

# Check workspace (via Fabric portal or API)
# Look for: "Customer Insights-feature-JIRA-12345"
```

### Develop & Sync
```bash
# Checkout feature branch
git checkout feature/customer_insights/JIRA-12345

# Make changes
cd data_products/customer_insights
# Edit files...

# Commit
git add .
git commit -m "JIRA-12345: Your changes"
git push origin feature/customer_insights/JIRA-12345

# Sync Git → Workspace (in Fabric portal or via API)
```

### Create Pull Request
```bash
# Via GitHub CLI
gh pr create \
  --base main \
  --head feature/customer_insights/JIRA-12345 \
  --title "JIRA-12345: Feature description"

# Via GitHub UI
# Go to repo → "Compare & pull request"
```

### Cleanup After Merge
```bash
# Delete local branch
git checkout main
git branch -d feature/customer_insights/JIRA-12345

# Delete remote branch
git push origin --delete feature/customer_insights/JIRA-12345

# Delete workspace (Fabric portal)
# Workspace Settings → Delete
```

## Common Scenarios

### Scenario: Start New Feature
```bash
# 1. Create isolated environment
python3 ../../ops/scripts/onboard_data_product.py product_descriptor.yaml --feature TICKET-001

# 2. Work in feature workspace (Fabric portal)
# 3. Changes auto-sync to feature branch
# 4. Create PR when ready
# 5. After merge → auto-deploys to DEV
```

### Scenario: Multiple Developers, Same Product
```bash
# Developer A
python3 onboard_data_product.py product_descriptor.yaml --feature FEAT-A

# Developer B (parallel)
python3 onboard_data_product.py product_descriptor.yaml --feature FEAT-B

# Both work independently, merge separately
```

### Scenario: Sync with Latest Changes
```bash
# Your feature branch is behind main
git checkout feature/customer_insights/JIRA-123
git merge main  # Get latest DEV changes
git push origin feature/customer_insights/JIRA-123

# Workspace auto-syncs with updated branch
```

## Workspace Naming Patterns

| Type | Pattern | Example |
|------|---------|---------|
| **DEV** | `<Product> [DEV]` | `Customer Insights [DEV]` |
| **Feature** | `<Product>-feature-<ticket>` | `Customer Insights-feature-JIRA-123` |
| **Git Branch** | `feature/<slug>/<ticket>` | `feature/customer_insights/JIRA-123` |

## CI/CD Flow

```
Feature Branch → PR → CI/CD Validation → Merge → Deploy to DEV → Promote to TEST/PROD
     ↓            ↓          ↓              ↓            ↓              ↓
  Isolated    Review   Tests Pass       main       Auto-deploy    Manual approval
 Workspace              ✅ Quality                  via GitHub      
                        ✅ Tests                    Actions
                        ✅ Security
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| Workspace exists | Delete old workspace: `WorkspaceManager().delete_workspace_by_name(...)` |
| Branch exists | Delete branch: `git push origin --delete feature/...` |
| Git sync fails | Check GitHub token scopes: repo, workflow |
| No environment vars | Load `.env` file: Copy `.env.template` → `.env`, fill values |

## Key Differences

| Action | Without --feature | With --feature |
|--------|------------------|----------------|
| **Workspaces** | DEV, TEST, PROD | DEV + Feature workspace |
| **Git Branch** | None created | feature/<slug>/<ticket> |
| **Use Case** | Environment setup | Ticket-based development |
| **Lifecycle** | Permanent | Temporary (delete after merge) |
| **Isolation** | Shared DEV | Isolated per ticket |

## File Locations

```
scenarios/feature-branch-workflow/
├── README.md                      # Overview & use cases
├── FEATURE_WORKFLOW_GUIDE.md      # Complete guide
├── QUICK_REFERENCE.md             # This file
├── product_descriptor.yaml        # Sample product config
└── test_feature_workflow.sh       # Test script

After running:
data_products/customer_insights/   # Scaffold created here
.onboarding_logs/                  # Audit logs
data_products/registry.json        # Updated with workspace info
```

## Cost Management

| Capacity | Cost | Best For |
|----------|------|----------|
| Trial | **Free** | Feature workspaces (recommended) |
| Fabric F8 | ~$0.18/hr | Short-term paid capacity |
| Premium P1 | ~$0.13/hr | Long-running features |

**💡 Tip:** Use Trial capacity for feature workspaces to avoid costs!

## Next Steps

1. **Test this scenario:**
   ```bash
   cd /path/to/scenarios/feature-branch-workflow
   python3 ../../ops/scripts/onboard_data_product.py product_descriptor.yaml --feature TEST-001
   ```

2. **Read complete guide:** [FEATURE_WORKFLOW_GUIDE.md](FEATURE_WORKFLOW_GUIDE.md)

3. **Check CI/CD integration:** [.github/workflows/fabric-cicd-pipeline.yml](../../.github/workflows/fabric-cicd-pipeline.yml)

4. **Review parallel systems:** See PROJECT_LESSONS_LEARNED.md for architecture overview

---

**This is the missing piece - feature branch workspaces for isolated, ticket-based development!** ✨
