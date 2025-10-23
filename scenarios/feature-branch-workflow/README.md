# Feature Branch Workflow Scenario

Create isolated feature workspaces linked to Git feature branches for ticket-based development.

## 📋 What This Scenario Demonstrates

This is the **missing piece** in our earlier scenarios - creating feature branch workspaces for isolated development work tied to specific tickets/stories.

### What Gets Created

1. **DEV Workspace** - `<Product> [DEV]` (if doesn't exist)
2. **Feature Workspace** - `<Product>-feature-<ticket>` (isolated workspace)
3. **Feature Git Branch** - `feature/<product>/<ticket>` (in repository)
4. **Git Connection** - Links feature workspace to feature branch
5. **Scaffold Structure** - `data_products/<product>/` (project files)

## 🎯 Use Cases

### Use Case 1: Developer Working on JIRA Ticket
```bash
# Developer assigned JIRA-12345 to add new data pipeline
python3 ../../ops/scripts/onboard_data_product.py \
  product_descriptor.yaml \
  --feature JIRA-12345
```

**Result:**
- Isolated workspace: `Customer Analytics-feature-JIRA-12345`
- Git branch: `feature/customer_analytics/JIRA-12345`
- Developer can work independently without affecting DEV

### Use Case 2: Testing Breaking Changes
```bash
# Test major refactor in isolation
python3 ../../ops/scripts/onboard_data_product.py \
  product_descriptor.yaml \
  --feature refactor-v2
```

### Use Case 3: Multiple Developers, Same Product
```bash
# Developer A works on feature-A
python3 ../../ops/scripts/onboard_data_product.py product_descriptor.yaml --feature feature-A

# Developer B works on feature-B (parallel, isolated)
python3 ../../ops/scripts/onboard_data_product.py product_descriptor.yaml --feature feature-B
```

## 🚀 Quick Start

### Step 1: Review the Descriptor

```bash
cat product_descriptor.yaml
```

### Step 2: Create Feature Workspace & Branch

```bash
# Using the onboard_data_product script with --feature flag
python3 ../../ops/scripts/onboard_data_product.py \
  product_descriptor.yaml \
  --feature TICKET-001
```

### Step 3: Verify Creation

**Check Git Branch:**
```bash
git branch | grep TICKET-001
# Should show: feature/customer_insights/TICKET-001
```

**Check Fabric Workspace:**
- Go to Microsoft Fabric portal
- Look for workspace: `Customer Insights-feature-TICKET-001`

**Check Git Connection:**
- Open feature workspace in Fabric
- Check Workspace Settings → Git integration
- Should be connected to `feature/customer_insights/TICKET-001`

## 📂 Files in This Scenario

- `product_descriptor.yaml` - Sample product configuration
- `README.md` - This file
- `FEATURE_WORKFLOW_GUIDE.md` - Comprehensive workflow documentation

## 🔄 Complete Development Workflow

### 1. Create Feature Environment
```bash
python3 ../../ops/scripts/onboard_data_product.py \
  product_descriptor.yaml \
  --feature JIRA-789
```

### 2. Develop in Feature Workspace
- Open `Customer Insights-feature-JIRA-789` workspace
- Create notebooks, pipelines, datasets
- Work commits automatically to `feature/customer_insights/JIRA-789`

### 3. Create Pull Request
```bash
# Push feature branch
git push origin feature/customer_insights/JIRA-789

# Create PR to merge into main
gh pr create --base main --head feature/customer_insights/JIRA-789
```

### 4. After PR Merge → Deploy to DEV
```bash
# CI/CD automatically deploys merged code to DEV workspace
# See: .github/workflows/fabric-cicd-pipeline.yml
```

### 5. Cleanup Feature Resources
```bash
# Delete feature workspace (manual in Fabric portal)
# Delete feature branch after merge
git branch -d feature/customer_insights/JIRA-789
git push origin --delete feature/customer_insights/JIRA-789
```

## 🎨 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Feature Branch Workflow                  │
└─────────────────────────────────────────────────────────────┘

Developer gets ticket JIRA-12345
         │
         ├─> Run: onboard_data_product.py --feature JIRA-12345
         │
         ▼
    ┌────────────────────────────────────────┐
    │   1. Create Git Feature Branch         │
    │   feature/customer_insights/JIRA-12345 │
    └────────────────┬───────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────┐
    │   2. Create Feature Workspace          │
    │   Customer Insights-feature-JIRA-12345 │
    └────────────────┬───────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────┐
    │   3. Link Workspace to Branch          │
    │   (Git Integration Setup)              │
    └────────────────┬───────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────┐
    │   4. Developer Works in Isolation      │
    │   - Create notebooks, pipelines        │
    │   - Changes auto-commit to branch      │
    └────────────────┬───────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────┐
    │   5. Create Pull Request               │
    │   feature/... → main                   │
    └────────────────┬───────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────┐
    │   6. CI/CD Pipeline Runs               │
    │   - Code quality checks                │
    │   - Unit tests                         │
    │   - DQ validation                      │
    └────────────────┬───────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────┐
    │   7. Merge → Deploy to DEV             │
    │   Customer Insights [DEV] workspace    │
    └────────────────┬───────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────┐
    │   8. Promote DEV → TEST → PROD         │
    │   (Fabric Deployment Pipeline)         │
    └────────────────────────────────────────┘
```

## 🔍 Key Differences from Other Scenarios

| Scenario | Creates DEV? | Creates Feature? | Git Branch? | Use Case |
|----------|--------------|------------------|-------------|----------|
| **config-driven-workspace** | ✅ | ❌ | ❌ | Standard workspace setup |
| **leit-ricoh-setup** | ✅ | ❌ | ❌ | Project initialization |
| **domain-workspace** | ✅ | ❌ | ❌ | Domain-based organization |
| **feature-branch-workflow** | ✅ | ✅ | ✅ | **Ticket-based development** |

## 📚 Related Documentation

- [Complete User Story 1 Workflow](../../docs/user-stories-validation/COMPLETE_USER_STORY_1_WORKFLOW.md)
- [Environment Promotion Guide](../../docs/workspace-management/ENVIRONMENT_PROMOTION_GUIDE.md)
- [CI/CD Pipeline Documentation](../../.github/workflows/fabric-cicd-pipeline.yml)

## ⚠️ Important Notes

### Feature Workspace Naming
- Pattern: `<ProductName>-feature-<ticket>`
- Example: `Customer Insights-feature-JIRA-12345`
- Must be unique per ticket

### Git Branch Naming
- Pattern: `feature/<product_slug>/<ticket>`
- Example: `feature/customer_insights/JIRA-12345`
- Follows feature_prefix from YAML (default: "feature")

### Cleanup Strategy
- Feature workspaces are **temporary** - delete after merge
- Feature branches should be deleted after PR merge
- DEV/TEST/PROD workspaces are **permanent**

### Cost Considerations
- Feature workspaces typically use **Trial capacity** (free)
- Multiple feature workspaces = multiple capacity units
- Clean up promptly to avoid cost accumulation

## 🧪 Testing This Scenario

```bash
# 1. Create feature environment
python3 ../../ops/scripts/onboard_data_product.py product_descriptor.yaml --feature TEST-001

# 2. Verify Git branch exists
git branch -a | grep TEST-001

# 3. Verify workspace exists (check Fabric portal)

# 4. Verify Git connection (in workspace settings)

# 5. Make a test commit
cd data_products/customer_insights
echo "# Test" > test.md
git add test.md
git commit -m "Test feature branch"
git push origin feature/customer_insights/TEST-001

# 6. Cleanup
git checkout main
git branch -d feature/customer_insights/TEST-001
git push origin --delete feature/customer_insights/TEST-001
# Delete workspace manually in Fabric portal
```

## 🎓 Learning Outcomes

After running this scenario, you'll understand:

1. ✅ How to create isolated development environments per ticket
2. ✅ How Git branches link to Fabric workspaces
3. ✅ How feature work flows into DEV → TEST → PROD
4. ✅ How parallel development works (multiple features simultaneously)
5. ✅ When to use feature branches vs. working directly in DEV
6. ✅ Complete CI/CD workflow from feature to production

---

**This scenario fills the gap in earlier testing - it demonstrates the complete developer workflow with feature branches and isolated workspaces!** 🚀
