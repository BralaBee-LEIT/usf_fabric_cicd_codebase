# User Story 1 - Quick Reference Card

**Status:** ✅ Production-Ready | **Validated:** 21 October 2025

---

## 🎯 The Complete Workflow

### Step 1: Create YAML Descriptor (2 minutes)

```yaml
# File: data_products/onboarding/my_product.yaml
product:
  name: "My Product"
  owner_email: "team@company.com"
  domain: "Data Domain"

environments:
  dev:
    enabled: true
    capacity_type: "trial"
    description: "Development workspace"

git:
  organization: "${GITHUB_ORG}"
  repository: "${GITHUB_REPO}"
  feature_prefix: "feature"
  directory: "data_products/my_product"

automation:
  audit_reference: "JIRA-XXX"
```

### Step 2: Run Onboarding (9 seconds)

```bash
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/my_product.yaml
```

### Step 3: Verify Results

```bash
# Check workspace in Fabric portal
open https://app.fabric.microsoft.com

# Or check via API
python3 ops/scripts/manage_workspaces.py list | grep "My Product"
```

---

## ✅ What You Get

| Item | Details |
|------|---------|
| **DEV Workspace** | `My Product [DEV]` in Microsoft Fabric |
| **Folder Structure** | `data_products/my_product/` with templates |
| **Audit Log** | `.onboarding_logs/TIMESTAMP_my_product.json` |
| **Registry Entry** | Tracked in `data_products/registry.json` |
| **Duration** | ~9 seconds total |

---

## 🚀 Optional: Feature Workflow

```bash
# Create feature workspace + branch for a ticket
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/my_product.yaml \
  --feature JIRA-123

# Creates:
# - Feature workspace: "My Product [FEATURE-JIRA-123]"
# - Git branch: "feature/my-product/JIRA-123"
# - Git sync connection
```

---

## 🔧 Common Options

```bash
# Preview without creating
--dry-run

# Create feature workspace/branch
--feature TICKET-ID

# Skip Git operations
--skip-git

# Skip workspace creation
--skip-workspaces

# Skip folder scaffold
--skip-scaffold

# JSON output
--json
```

---

## 📊 Live Examples

### Example 1: Test Data Product
```bash
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/sample_product.yaml

✅ Created: "Test Data Product" (8070ecd4-xxxx)  # Example ID - yours will differ
```

> **Note:** Workspace IDs shown are examples. Fabric generates unique GUIDs for each workspace.

### Example 2: Customer Analytics
```bash
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/customer_analytics.yaml

✅ Created: "Customer Analytics [DEV]" (be8d1df8-xxxx)
```

---

## 🎓 Key Points

1. ✅ **Descriptor path** = positional argument (not `--descriptor`)
2. ✅ **No `--environment` flag** (environments in YAML)
3. ✅ **Basic workflow** = DEV workspace only
4. ✅ **Full workflow** = Add `--feature TICKET` for feature workspace
5. ✅ **Duration** = ~9 seconds (basic) or ~25 seconds (full)
6. ✅ **Acceptance Criteria** = 7/7 met (100%)

---

## 🔗 Full Documentation

- **COMPLETE_USER_STORY_1_WORKFLOW.md** - Comprehensive guide
- **LIVE_EXECUTION_SUCCESS.md** - Today's successful execution
- **USER_STORY_VALIDATION.md** - Acceptance criteria proof
- **FABRIC_ITEMS_AND_USERS_GUIDE.md** - Post-onboarding operations

---

*Quick Reference | User Story 1 | Microsoft Fabric Workspace Automation*
