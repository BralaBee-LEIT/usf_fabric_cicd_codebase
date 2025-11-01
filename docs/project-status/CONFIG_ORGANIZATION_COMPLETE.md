# Configuration Organization - Implementation Complete

## ✅ What Was Fixed

### Problem
- Config files scattered across multiple locations
- Principals defined with emails instead of Object IDs
- Confusion between `/scenarios`, `/data_products`, and `/config`
- Duplicated configuration files

### Solution
**Centralized Configuration Structure**:

```
config/                                    # ✅ SINGLE SOURCE OF TRUTH
├── principals/                            # User/Group/SP Object IDs
│   ├── sales_analytics_dev_principals.txt # Object IDs ONLY
│   ├── customer_insights_dev_principals.txt
│   └── workspace_principals.template.txt
│
├── scenarios/                             # Demo configurations
│   └── sales_analytics_etl.yaml          # ✅ Centralized here
│
└── products/                              # Product configurations (future)
```

---

## 🎯 Key Principles Established

### 1. **Centralized Configuration**
- **All** config files in `/config`
- **NO** duplication in `/scenarios` or `/data_products`
- Scripts **reference** central config, never copy

### 2. **Object IDs Only**
- **Principals files** use Azure AD Object IDs (GUIDs)
- **NO emails** anywhere in configuration
- Get Object IDs via: `az ad user show --id user@domain.com --query id -o tsv`

### 3. **Clear Folder Purposes**

| Folder | Purpose | Contains |
|--------|---------|----------|
| `/config` | Configuration | YAML configs, principals files |
| `/scenarios` | Demo scripts | Python scripts that run demos |
| `/data_products` | Real products | Notebooks, SQL, product definitions |
| `/ops/scripts` | Utilities | Reusable framework code |

---

## 📝 Updated Files

### 1. Created Centralized Config
```
config/scenarios/sales_analytics_etl.yaml  # ✅ NEW
```

### 2. Updated Demo Script
```
scenarios/comprehensive-demo/run_sales_analytics_demo.py
```

**Changes**:
- ✅ Loads config from `config/scenarios/` by default
- ✅ Looks up principals in `config/principals/`
- ✅ Uses `manage_workspaces.py add-users-from-file` with Object IDs
- ✅ NO email addresses in code

**New user management function**:
```python
def add_workspace_users(workspace_id, product_config, dry_run=False):
    # Get product name
    product_name = product_config.get('product', {}).get('name', '').lower()
    
    # Look for principals file in centralized location
    config_dir = Path(__file__).parent.parent.parent / "config" / "principals"
    principals_file = config_dir / f"{product_name}_dev_principals.txt"
    
    # Use manage_workspaces.py with Object IDs from file
    subprocess.run([
        python, "ops/scripts/manage_workspaces.py",
        "add-users-from-file", workspace_id, str(principals_file), "--yes"
    ])
```

### 3. Created Documentation
```
PROJECT_STRUCTURE.md          # ✅ Overall project organization
config/README.md              # ✅ Config folder guide
```

---

## 🚀 Usage Examples

### Run Demo with Centralized Config

```bash
# Default: uses config/scenarios/sales_analytics_etl.yaml
cd scenarios/comprehensive-demo
python run_sales_analytics_demo.py

# Custom config location
python run_sales_analytics_demo.py --config config/scenarios/my_demo.yaml

# Dry run to preview
python run_sales_analytics_demo.py --dry-run
```

### Add Users from Principals File

```bash
# 1. Create principals file with Object IDs
cat > config/principals/myproduct_dev_principals.txt << EOF
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Sanmi Ibitoye,User
EOF

# 2. Script automatically uses this file
# Product name "myproduct" → looks for config/principals/myproduct_dev_principals.txt
python run_sales_analytics_demo.py
```

### Get Object IDs for Principals

```bash
# User Object ID
az ad user show --id sanmi@leit-teksystems.com --query id -o tsv

# Group Object ID  
az ad group show --group "Data Engineering" --query id -o tsv

# Service Principal Object ID
az ad sp show --id <client-id> --query id -o tsv
```

---

## 📋 Migration Checklist

For any existing scenarios or products:

- [ ] Move config YAML files to `config/scenarios/`
- [ ] Create principals files in `config/principals/`
- [ ] Get Object IDs for all users (NO emails!)
- [ ] Update scripts to reference `config/scenarios/`
- [ ] Update scripts to use `config/principals/`
- [ ] Remove any hardcoded emails from YAML
- [ ] Test with `--dry-run` first
- [ ] Delete old config files from scenario folders

---

## 🎯 Example: Create New Demo

```bash
# 1. Create scenario config (centralized)
cat > config/scenarios/my_new_demo.yaml << 'EOF'
product:
  name: "my-new-demo"
  description: "My demo description"
  owner_email: "${FABRIC_USER_EMAIL}"

environments:
  dev:
    enabled: true
    capacity_id: "${FABRIC_CAPACITY_ID}"

items:
  lakehouses:
    - name: "BRONZE_MyData_Lakehouse"
      description: "Raw data"
# NO users section - use principals file!
EOF

# 2. Create principals file with Object IDs
cat > config/principals/my_new_demo_dev_principals.txt << 'EOF'
# Get this ID: az ad user show --id user@domain.com --query id -o tsv
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Your Name,User
EOF

# 3. Create demo script (in scenarios/)
cat > scenarios/my-new-demo/run_my_demo.py << 'EOF'
from pathlib import Path
# Load config from centralized location
config_path = Path(__file__).parent.parent.parent / "config" / "scenarios" / "my_new_demo.yaml"

# Principals automatically loaded by add_workspace_users()
# based on product name "my-new-demo" → my_new_demo_dev_principals.txt
EOF

# 4. Run demo
cd scenarios/my-new-demo
python run_my_demo.py
```

---

## ✅ Benefits

### Before (Problems)
- ❌ Config files in multiple locations
- ❌ Emails hardcoded in YAML
- ❌ Principals scattered across folders
- ❌ Confusion about folder purposes
- ❌ Duplication and inconsistency

### After (Solutions)
- ✅ Single source of truth: `/config`
- ✅ Object IDs only (NO emails)
- ✅ Centralized principals management
- ✅ Clear folder separation
- ✅ Consistent patterns everywhere
- ✅ Easy to find and update configs
- ✅ Scales for multiple products/teams

---

## 📚 Documentation

**Main Docs**:
- `/PROJECT_STRUCTURE.md` - Overall project organization guide
- `/config/README.md` - Config folder usage guide

**Config Files**:
- `/config/scenarios/*.yaml` - Scenario configurations
- `/config/principals/*.txt` - User/Group/SP definitions

**Principals Template**:
- `/config/principals/workspace_principals.template.txt` - Template for new teams

---

## 🎓 Key Learnings

1. **Centralization is Critical**
   - One location for all config
   - Easier to find and maintain
   - Prevents duplication and drift

2. **Object IDs, Not Emails**
   - Fabric API requires Object IDs
   - Emails don't work programmatically
   - Get IDs via Azure CLI before deployment

3. **Clear Folder Roles**
   - Config = configuration only
   - Scenarios = demo scripts
   - Data Products = real deployments
   - Ops/Scripts = reusable utilities

4. **Reference, Don't Duplicate**
   - Scripts reference config/
   - Never copy config files locally
   - Update one place, works everywhere

---

## 🔄 Next Steps

1. **Migrate Other Scenarios**
   - Review `/scenarios/automated-deployment/`
   - Move any local configs to `/config/scenarios/`
   - Update to use principals files

2. **Data Products Integration**
   - Consider moving product configs to `/config/products/`
   - Standardize on centralized pattern
   - Document product-specific workflows

3. **Validation Tools**
   - Create `validate_principals.py` script
   - Validate config references
   - Check for email usage (should be none!)

4. **Documentation Updates**
   - Update main README.md with new structure
   - Update scenario READMEs
   - Create migration guide for teams

---

## ✨ Summary

**Configuration organization is now standardized**:
- ✅ All config in `/config` (scenarios, principals, products)
- ✅ Object IDs only (NO emails anywhere)
- ✅ Scripts reference centralized config
- ✅ Clear documentation and examples
- ✅ Tested and working

**Ready for**:
- Multiple teams/products
- Consistent deployment patterns
- Scalable principal management
- Clear onboarding for new developers
