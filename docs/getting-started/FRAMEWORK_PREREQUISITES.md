# Framework Prerequisites Guide

## Overview

As of **v2.0**, the Microsoft Fabric CI/CD Framework enforces mandatory prerequisites to ensure governance, consistency, and compliance across all operations.

## Core Framework Principles (Enforced)

The framework is built on three foundational principles:

1. **Standardized Naming** - All workspaces and items follow organizational patterns
2. **Infrastructure-as-Code** - Declarative configurations for repeatable deployments
3. **Governance & Compliance** - Automated validation and audit trails

**These principles are now enforced at runtime.**

---

## 🚨 Mandatory Files (REQUIRED)

### 1. `project.config.json` - Organization Naming Standards

**Purpose:** Defines HOW resources should be named across your entire organization

**Location:** Repository root

**Content:**
```json
{
  "project": {
    "prefix": "usf2",
    "organization": "Your-Org-Name"
  },
  "naming_patterns": {
    "workspace": "{prefix}-{name}-{environment}",
    "lakehouse": "{prefix_upper}_Lakehouse_{environment_title}"
  },
  "environments": {
    "dev": {...},
    "test": {...},
    "prod": {...}
  }
}
```

**Setup:**
```bash
cp project.config.template.json project.config.json
nano project.config.json  # Edit with your organization details
```

**Why Required:**
- Ensures consistent naming across ALL workspaces and items
- Enforces organizational governance policies
- Enables multi-environment deployments (dev/test/prod)
- Required for audit trail and compliance

---

### 2. `.env` - Azure Credentials

**Purpose:** Authentication to Azure and Microsoft Fabric APIs

**Location:** Repository root

**Content:**
```env
# Azure Service Principal
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Fabric Configuration
FABRIC_CAPACITY_ID=your-capacity-id

# Optional
GITHUB_ORG=your-github-org
GITHUB_REPO=your-repo-name
```

**Setup:**
```bash
cp .env.example .env
nano .env  # Edit with your Azure credentials
```

**Why Required:**
- Required for authentication to Azure AD
- Required for Fabric API operations
- Contains sensitive credentials (NEVER commit to Git)
- Loaded automatically by all scripts

---

### 3. `naming_standards.yaml` - Naming Validation Rules

**Purpose:** Defines WHAT naming patterns are valid and enforced

**Location:** Repository root (or `config/naming_standards.yaml`)

**Content:**
```yaml
naming_patterns:
  workspace:
    pattern: "^[a-z0-9]+(-[a-z0-9]+)*-(dev|test|prod)$"
    
  lakehouse:
    pattern: "^(BRONZE|SILVER|GOLD)_[A-Z][a-zA-Z0-9]+_Lakehouse$"
    
  notebook:
    pattern: "^(0[0-9]|[1-9][0-9])_[A-Z][a-zA-Z0-9]+_Notebook$"
```

**Setup:**
```bash
# File already exists in repository
# Customize if needed for your organization
nano naming_standards.yaml
```

**Why Required:**
- Validates resource names against organizational standards
- Ensures medallion architecture compliance (Bronze/Silver/Gold)
- Enforces sequential notebook numbering
- Provides auto-fix suggestions for non-compliant names

---

## 🔍 Framework Validation

### Automatic Validation

**Every scenario and CLI tool now validates prerequisites on startup:**

```python
from utilities.framework_validator import validate_framework_prerequisites

# This runs automatically before any operation
validate_framework_prerequisites("operation name")
```

### Manual Validation

**Test prerequisites manually:**

```bash
# Validate all prerequisites
python ops/scripts/utilities/framework_validator.py

# Expected output (success):
# ✅ project.config.json: Found
# ✅ .env: Found
# ✅ naming_standards.yaml: Found
# 
# ✅ All framework prerequisites are satisfied!
```

### Validation Failure

**If prerequisites are missing, you'll see:**

```
================================================================================
❌ FRAMEWORK PREREQUISITES NOT MET
================================================================================

Cannot perform workspace operations without required configuration files.

Core Framework Principles:
  1. Standardized naming via project.config.json
  2. Proper authentication via .env
  3. Naming validation via naming_standards.yaml

Missing Files:
--------------------------------------------------------------------------------

Missing required file: project.config.json
  Purpose: Ensures consistent naming across all workspaces and items
  Create it: cp project.config.template.json project.config.json

================================================================================
Quick Setup:
================================================================================

# 1. Copy templates:
   cp project.config.template.json project.config.json
   cp .env.example .env

# 2. Edit with your values:
   nano project.config.json  # Set organization prefix and naming patterns
   nano .env  # Set Azure credentials and Fabric capacity

# 3. Re-run your command

For more information, see: docs/getting-started/
================================================================================
```

---

## 🎯 What's Enforced

### All Scenarios

**Before v2.0 (Permissive):**
- ❌ Could create workspaces with ANY name
- ❌ Could bypass organizational standards
- ❌ No validation of prerequisites

**After v2.0 (Enforced):**
- ✅ Must have `project.config.json` before running
- ✅ Workspace names follow organizational patterns
- ✅ All operations validated against naming standards
- ✅ Complete audit trail of all changes

### Example: Domain Workspace Scenario

**Before v2.0:**
```bash
python domain_workspace_with_existing_items.py --domain-name "random-name"
# Created: "random-name-workspace" (no pattern enforcement)
```

**After v2.0:**
```bash
# Requires setup first
cp project.config.template.json project.config.json
cp .env.example .env

# Now follows organizational pattern
python domain_workspace_with_existing_items.py --domain-name finance --environment dev
# Creates: "usf2-fabric-finance-dev" (follows project.config.json pattern)
```

### All CLI Tools

**All management CLIs now validate prerequisites:**

```bash
# Workspace management
python ops/scripts/manage_workspaces.py list
# ✅ Validates prerequisites first

# Item management
python ops/scripts/manage_fabric_items.py list --workspace "MyWorkspace"
# ✅ Validates prerequisites first

# Folder management
python tools/manage_fabric_folders.py list --workspace "MyWorkspace"
# ✅ Validates prerequisites first
```

---

## 🔧 Bypassing Validation (NOT RECOMMENDED)

**For testing purposes only**, validation can be skipped:

```python
# In Python code (utilities only)
from utilities.workspace_manager import WorkspaceManager

manager = WorkspaceManager(skip_framework_validation=True)  # NOT RECOMMENDED
```

**⚠️ WARNING:** Skipping validation:
- Bypasses organizational governance
- Risks inconsistent naming
- Breaks audit trail
- Should NEVER be used in production

---

## 📊 Benefits of Enforcement

### Governance & Compliance
- ✅ All resources follow organizational standards
- ✅ No ad-hoc resource creation
- ✅ Complete audit trail
- ✅ Compliance with naming policies

### Consistency
- ✅ Workspaces named consistently across environments
- ✅ Items follow medallion architecture patterns
- ✅ Predictable resource names
- ✅ Easy to identify resource purpose/owner

### Infrastructure-as-Code
- ✅ All deployments use declarative configs
- ✅ Version-controlled infrastructure
- ✅ Repeatable deployments
- ✅ Automated validation

### Developer Experience
- ✅ Clear error messages when setup incomplete
- ✅ Helpful guidance for fixing issues
- ✅ Fast feedback (fail early)
- ✅ Consistent behavior across all tools

---

## 🚀 Quick Start Checklist

**First-Time Setup:**

- [ ] 1. Clone repository
- [ ] 2. Copy templates:
  ```bash
  cp project.config.template.json project.config.json
  cp .env.example .env
  ```
- [ ] 3. Edit `project.config.json` with your org details
- [ ] 4. Edit `.env` with your Azure credentials
- [ ] 5. Validate setup:
  ```bash
  python ops/scripts/utilities/framework_validator.py
  ```
- [ ] 6. Run any scenario or CLI command

**For Existing Projects:**

If upgrading from pre-v2.0:

- [ ] 1. Ensure `project.config.json` exists (or create from template)
- [ ] 2. Ensure `.env` exists with proper credentials
- [ ] 3. Update any custom scripts that bypass ConfigManager
- [ ] 4. Test all scenarios/CLIs to verify they work
- [ ] 5. Review workspace names - may change to follow patterns

---

## 📚 Related Documentation

- **Setup Guide**: [NEW_PROJECT_SETUP.md](NEW_PROJECT_SETUP.md)
- **Scenarios Guide**: [../../scenarios/README.md](../../scenarios/README.md)
- **Implementation Guide**: [../guides/IMPLEMENTATION_GUIDE.md](../guides/IMPLEMENTATION_GUIDE.md)
- **Workspace Provisioning**: [../guides/WORKSPACE_PROVISIONING_GUIDE.md](../guides/WORKSPACE_PROVISIONING_GUIDE.md)

---

## ❓ FAQ

**Q: Can I disable prerequisite validation?**  
A: Not recommended. Validation ensures governance and consistency. For testing, use `skip_framework_validation=True` parameter in code.

**Q: What if I don't want standardized naming?**  
A: The framework is designed for enterprise governance. If you don't need standardized naming, consider using raw Fabric APIs instead of this framework.

**Q: Will my existing workspaces be renamed?**  
A: No. The framework only affects NEW resource creation. Existing workspaces are not modified.

**Q: Can I customize naming patterns?**  
A: Yes! Edit `project.config.json` and `naming_standards.yaml` to match your organization's requirements.

**Q: What happens if validation fails?**  
A: The operation stops immediately with a clear error message explaining what's missing and how to fix it. No partial operations occur.

**Q: Does this affect manual Fabric operations?**  
A: No. Manual operations via Fabric UI are unaffected. This only applies to framework-based automation.

---

## 🆘 Troubleshooting

### "Framework prerequisites not met" error

**Solution:**
```bash
# Validate which files are missing
python ops/scripts/utilities/framework_validator.py

# Copy missing templates
cp project.config.template.json project.config.json
cp .env.example .env

# Edit with your values
nano project.config.json
nano .env
```

### "Invalid environment" error

**Solution:**
Check that `project.config.json` defines your environment:
```json
{
  "environments": {
    "dev": {...},
    "test": {...},
    "prod": {...}
  }
}
```

### "Naming validation failed" error

**Solution:**
Resource name doesn't match patterns in `naming_standards.yaml`. Check the error message for auto-fix suggestions.

---

**For more help, see**: [../../README.md](../../README.md) or open an issue on GitHub.
