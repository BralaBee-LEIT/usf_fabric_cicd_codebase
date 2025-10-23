# Feature Branch Workflow - Complete Guide

## Overview

This guide explains how to use **feature branch workspaces** for isolated, ticket-based development in Microsoft Fabric.

## What's Different from Other Scenarios?

| Aspect | Standard Scenarios | Feature Branch Workflow |
|--------|-------------------|------------------------|
| **Purpose** | Setup DEV/TEST/PROD environments | Isolated development per ticket |
| **Workspace Type** | Permanent (DEV/TEST/PROD) | Temporary (feature-specific) |
| **Git Integration** | Optional | **Required** - creates feature branch |
| **Naming** | `Product [DEV]` | `Product-feature-TICKET-123` |
| **Lifecycle** | Long-lived | Short-lived (delete after merge) |
| **Use Case** | Environment setup | Individual developer work |

## Why Use Feature Branches?

### Problem Without Feature Branches
```
┌─────────────────────────────────────────────────────┐
│           Everyone Works in DEV Workspace            │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Developer A: Working on pipeline                   │
│  Developer B: Testing breaking changes ⚠️           │
│  Developer C: Experimenting with new approach       │
│                                                      │
│  CONFLICTS:                                         │
│  • Changes interfere with each other                │
│  • Hard to track who changed what                   │
│  • Testing is risky - might break others' work      │
│  • No isolation between tickets/features            │
└─────────────────────────────────────────────────────┘
```

### Solution With Feature Branches
```
┌───────────────────────────────────────────────────────┐
│            Isolated Feature Workspaces                 │
├───────────────────────────────────────────────────────┤
│                                                        │
│  Developer A: Product-feature-JIRA-101 ✅             │
│  Developer B: Product-feature-JIRA-102 ✅             │
│  Developer C: Product-feature-JIRA-103 ✅             │
│                                                        │
│  BENEFITS:                                            │
│  • Complete isolation between features                │
│  • Safe experimentation                               │
│  • Clear ownership (1 workspace = 1 ticket)           │
│  • Automatic Git sync per feature                     │
│  • PR-based code review before merge                  │
└───────────────────────────────────────────────────────┘
```

## Step-by-Step Workflow

### Phase 1: Create Feature Environment

**Command:**
```bash
python3 ../../ops/scripts/onboard_data_product.py \
  product_descriptor.yaml \
  --feature JIRA-12345
```

**What Happens:**

1. **Git Feature Branch Created**
   ```
   Branch: feature/customer_insights/JIRA-12345
   Location: Your repository
   Parent: main branch
   ```

2. **Feature Workspace Created**
   ```
   Name: Customer Insights-feature-JIRA-12345
   Capacity: Trial (free)
   Status: Active
   ```

3. **Git Connection Established**
   ```
   Workspace: Customer Insights-feature-JIRA-12345
   Connected to: feature/customer_insights/JIRA-12345
   Sync Mode: Bidirectional (workspace ↔ Git)
   ```

4. **Scaffold Generated**
   ```
   data_products/customer_insights/
   ├── workspace/
   ├── notebooks/
   │   ├── ingestion_pipeline.ipynb (template)
   │   ├── transformation_logic.ipynb (template)
   │   └── data_quality_checks.ipynb (template)
   ├── pipelines/
   ├── datasets/
   ├── reports/
   └── README.md
   ```

**Expected Output:**
```
ℹ️ Loaded environment variables from .env
ℹ️ Starting onboarding for product 'Customer Insights' (slug: customer_insights)

✅ Created Git branch: feature/customer_insights/JIRA-12345
✅ Seeded scaffold for customer_insights from template
✅ Created workspace 'Customer Insights [DEV]' (or reused existing)
✅ Created workspace 'Customer Insights-feature-JIRA-12345'
   ID: 9f4a3b2c-1d8e-4f5b-9a7c-8e6d5c4b3a2f
   URL: https://app.fabric.microsoft.com/groups/9f4a3b2c-...

✅ Connected workspace to Git branch feature/customer_insights/JIRA-12345
✅ Updated onboarding registry
✅ Audit log written to .onboarding_logs/20251022_customer_insights_JIRA-12345.json

🎉 Onboarding complete! Feature workspace ready for development.
```

### Phase 2: Develop in Feature Workspace

**Option A: Work in Fabric Portal**

1. Open Microsoft Fabric portal
2. Navigate to `Customer Insights-feature-JIRA-12345` workspace
3. Create/edit notebooks, pipelines, datasets
4. Changes automatically sync to `feature/customer_insights/JIRA-12345` branch

**Option B: Work in Git First**

1. Checkout feature branch locally:
   ```bash
   git checkout feature/customer_insights/JIRA-12345
   ```

2. Make changes in `data_products/customer_insights/`
   ```bash
   cd data_products/customer_insights/notebooks
   # Edit ingestion_pipeline.ipynb
   ```

3. Commit and push:
   ```bash
   git add .
   git commit -m "JIRA-12345: Add customer data ingestion logic"
   git push origin feature/customer_insights/JIRA-12345
   ```

4. Sync Git → Workspace:
   ```python
   # In Fabric workspace: Workspace Settings → Git Integration → Update from Git
   # Or use API:
   from utilities.fabric_deployment_pipeline import FabricGitIntegration
   
   git_integration = FabricGitIntegration(workspace_id)
   git_integration.sync_from_git()
   ```

### Phase 3: Test Your Feature

**In Feature Workspace:**
```bash
# Run your notebooks, pipelines, data quality checks
# Everything runs in isolation - won't affect DEV or other features
```

**Local Testing:**
```bash
# If you have local environment
cd data_products/customer_insights
python -m pytest tests/
```

### Phase 4: Create Pull Request

**Push Feature Branch:**
```bash
git push origin feature/customer_insights/JIRA-12345
```

**Create PR via GitHub CLI:**
```bash
gh pr create \
  --base main \
  --head feature/customer_insights/JIRA-12345 \
  --title "JIRA-12345: Add customer data ingestion pipeline" \
  --body "
  ## Changes
  - Created ingestion pipeline for customer data
  - Added data quality checks
  - Updated transformation logic
  
  ## Testing
  - Tested in feature workspace: Customer Insights-feature-JIRA-12345
  - All data quality checks pass
  - Pipeline runs successfully
  
  ## Deployment Notes
  - Ready for DEV deployment after merge
  - No breaking changes
  "
```

**Or via GitHub Web UI:**
1. Go to repository on GitHub
2. Click "Compare & pull request" for your feature branch
3. Fill in PR details
4. Request reviewers

### Phase 5: CI/CD Validation (Automatic)

**GitHub Actions Pipeline Runs:**
```yaml
# .github/workflows/fabric-cicd-pipeline.yml triggers on PR

Jobs that run:
  ✅ Code Quality (Black, Flake8, data contracts)
  ✅ Unit Tests (pytest with coverage)
  ✅ Data Quality Gate (Great Expectations)
  ✅ Security Scan (Trivy)
```

**Review Checks:**
- All tests must pass
- Code quality must pass
- Coverage must meet threshold
- Security scan must pass

### Phase 6: Code Review & Approval

**Reviewers Check:**
- [ ] Code follows standards
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No security issues
- [ ] Data quality checks pass

**Approval & Merge:**
```bash
# After approval, merge PR
gh pr merge feature/customer_insights/JIRA-12345 --squash
```

### Phase 7: Automatic Deployment to DEV

**GitHub Actions Triggers (on merge to main):**

```yaml
# Stage 5: Deploy to DEV (automatic)
deploy-to-dev:
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to Dev Workspace
      run: |
        python ops/scripts/deploy_fabric.py \
          --workspace "usf-fabric-dev" \
          --bundle "./artifacts/fabric_bundle.zip" \
          --mode standard
    
    - name: Sync Git Integration
      run: |
        # Sync DEV workspace with main branch
        python ops/scripts/utilities/fabric_deployment_pipeline.py \
          --action sync-to-git
```

**Result:**
- Your feature code is now in `Customer Insights [DEV]` workspace
- Available to entire team for integration testing
- Git main branch reflects current DEV state

### Phase 8: Cleanup Feature Resources

**Delete Feature Workspace:**
```bash
# Option 1: Via Fabric Portal
# 1. Go to workspace settings
# 2. Click "Delete workspace"
# 3. Confirm deletion

# Option 2: Via API (if you have admin rights)
python3 -c "
from utilities.workspace_manager import WorkspaceManager
manager = WorkspaceManager()
manager.delete_workspace('9f4a3b2c-1d8e-4f5b-9a7c-8e6d5c4b3a2f')
"
```

**Delete Feature Branch:**
```bash
# Delete local branch
git checkout main
git branch -d feature/customer_insights/JIRA-12345

# Delete remote branch
git push origin --delete feature/customer_insights/JIRA-12345
```

**Update Onboarding Registry (Optional):**
```bash
# Archive feature workspace record in registry
# Edit data_products/registry.json
```

## Advanced Scenarios

### Scenario 1: Multiple Features Simultaneously

**Developer A:**
```bash
python3 ../../ops/scripts/onboard_data_product.py product_descriptor.yaml --feature JIRA-101
# Works in: Customer Insights-feature-JIRA-101
```

**Developer B (parallel, same product):**
```bash
python3 ../../ops/scripts/onboard_data_product.py product_descriptor.yaml --feature JIRA-102
# Works in: Customer Insights-feature-JIRA-102
```

**Result:**
- Both developers work independently
- No conflicts or interference
- Each has own Git branch + workspace
- Both can merge to DEV when ready

### Scenario 2: Long-Running Feature Development

**Week 1: Create feature workspace**
```bash
python3 ../../ops/scripts/onboard_data_product.py product_descriptor.yaml --feature EPIC-500
```

**Week 2-4: Iterative development**
```bash
# Keep syncing with main to get latest changes
git checkout feature/customer_insights/EPIC-500
git merge main  # Bring in latest changes from DEV
git push origin feature/customer_insights/EPIC-500

# Workspace auto-syncs with updated branch
```

**Week 5: Ready for merge**
```bash
# Final sync with main
git merge main
# Resolve any conflicts
# Create PR
gh pr create --base main --head feature/customer_insights/EPIC-500
```

### Scenario 3: Hotfix in Production

**Emergency fix needed:**
```bash
# Create hotfix branch from main
git checkout -b hotfix/critical-bug-fix main

# Create hotfix workspace
python3 ../../ops/scripts/onboard_data_product.py \
  product_descriptor.yaml \
  --feature hotfix-critical-bug-fix

# Fix the issue
# Test in hotfix workspace
# Create PR with high priority
# Fast-track review and merge
# Deploy immediately: DEV → TEST → PROD
```

## Best Practices

### ✅ DO

1. **Create feature workspace per ticket**
   ```bash
   # One ticket = one workspace = one branch
   python3 onboard_data_product.py descriptor.yaml --feature JIRA-123
   ```

2. **Use descriptive ticket IDs**
   ```bash
   --feature JIRA-12345    # Good: Clear ticket reference
   --feature feature-123   # OK: Numbered
   --feature user-auth     # Good: Descriptive name
   ```

3. **Test thoroughly in feature workspace**
   - Run all notebooks
   - Validate data quality
   - Check pipeline execution
   - Review outputs

4. **Keep feature branches short-lived**
   - Aim for < 2 weeks
   - Merge frequently
   - Avoid long-running branches

5. **Sync with main regularly**
   ```bash
   git checkout feature/customer_insights/JIRA-123
   git merge main  # Get latest changes
   ```

6. **Clean up after merge**
   - Delete feature workspace
   - Delete feature branch
   - Update documentation

### ❌ DON'T

1. **Don't work directly in DEV for experimental changes**
   - Use feature workspace instead
   - DEV should be stable

2. **Don't reuse feature workspaces for multiple tickets**
   - Each ticket gets its own workspace
   - Keeps history clean

3. **Don't forget to delete feature resources**
   - Costs accumulate with unused workspaces
   - Clutter makes management harder

4. **Don't merge without CI/CD validation**
   - Wait for all checks to pass
   - Get proper code review

5. **Don't create feature workspace for tiny changes**
   - Simple fixes can go directly to DEV
   - Feature workspaces are for significant work

## Troubleshooting

### Issue: "Feature workspace already exists"

**Cause:** Workspace name collision (ticket ID reused)

**Solution:**
```bash
# Option 1: Delete old workspace first
# Option 2: Use different ticket ID
python3 onboard_data_product.py descriptor.yaml --feature JIRA-123-v2

# Option 3: Delete workspace via API
from utilities.workspace_manager import WorkspaceManager
manager = WorkspaceManager()
manager.delete_workspace_by_name("Customer Insights-feature-JIRA-123")
```

### Issue: "Git branch already exists"

**Cause:** Branch wasn't deleted after previous merge

**Solution:**
```bash
# Delete old branch
git push origin --delete feature/customer_insights/JIRA-123
git branch -d feature/customer_insights/JIRA-123

# Re-run onboarding
python3 onboard_data_product.py descriptor.yaml --feature JIRA-123
```

### Issue: "Failed to connect workspace to Git"

**Cause:** Git integration permissions missing

**Solution:**
```bash
# Check environment variables
echo $GITHUB_ORG
echo $GITHUB_REPO

# Verify GitHub token has correct scopes:
# - repo (full control)
# - workflow
```

### Issue: "Changes not syncing between workspace and Git"

**Cause:** Git integration not configured or failing

**Solution:**
```bash
# Check workspace Git settings in Fabric portal
# Workspace Settings → Git Integration → Status

# Manual sync:
# In Fabric: Click "Sync" button
# Or via API:
from utilities.fabric_deployment_pipeline import FabricGitIntegration
git = FabricGitIntegration(workspace_id)
git.sync_to_git("Manual sync", changes=[])
```

## Cost Optimization

### Feature Workspaces Cost Considerations

| Capacity Type | Cost | Recommended For |
|--------------|------|-----------------|
| **Trial** | Free (60 days) | Development, testing |
| **Fabric F8** | ~$0.18/hour | Short-lived features |
| **Premium P1** | ~$0.13/hour | Long-running features |

**Cost Saving Tips:**

1. **Use Trial capacity for feature workspaces**
   ```yaml
   # In product_descriptor.yaml
   environments:
     dev:
       capacity_type: "trial"  # Free!
   ```

2. **Delete promptly after merge**
   ```bash
   # Don't let feature workspaces accumulate
   # Delete within 1 week of PR merge
   ```

3. **Pause workspaces during non-working hours** (if using paid capacity)
   ```bash
   # Use Fabric API to pause/resume
   # Or delete and recreate when needed
   ```

4. **Share DEV workspace, isolate only when needed**
   - Simple changes: Work in DEV
   - Complex/risky changes: Use feature workspace

## Summary

### Feature Branch Workflow Recap

```
1. Create:     onboard_data_product.py --feature TICKET-123
2. Develop:    Work in isolated feature workspace
3. Test:       Validate in feature environment
4. PR:         Create pull request for review
5. CI/CD:      Automated validation runs
6. Review:     Code review and approval
7. Merge:      PR merged to main
8. Deploy:     Auto-deploy to DEV workspace
9. Promote:    DEV → TEST → PROD (via pipeline)
10. Cleanup:   Delete feature workspace & branch
```

### Key Benefits

- ✅ **Isolation**: No interference between features
- ✅ **Safety**: Experiment without affecting others
- ✅ **Traceability**: Clear link between ticket and changes
- ✅ **Collaboration**: Parallel development on same product
- ✅ **Quality**: PR-based review before merge
- ✅ **Automation**: CI/CD validates before deployment

---

**This is the complete feature branch workflow that ties together isolated development, Git integration, and the CI/CD pipeline!** 🚀
