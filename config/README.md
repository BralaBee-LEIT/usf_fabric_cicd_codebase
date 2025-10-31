# Configuration Folder

**Purpose**: Centralized configuration for all scenarios, products, and principals

---

## 📁 Folder Structure

```
config/
├── principals/          # User/Group/Service Principal definitions
├── scenarios/           # Demo scenario configurations
├── products/            # Real data product configurations
└── setup-logs/          # Setup and initialization logs
```

---

## 🔑 Principals (User Management)

**Location**: `config/principals/`

**Purpose**: Define users, groups, and service principals with their Azure AD Object IDs

**Format**:
```
# Format: object_id,role,description,type
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Sanmi Ibitoye,User
a1b2c3d4-e5f6-7890-abcd-ef1234567890,Viewer,Data Engineering Team,Group
b2c3d4e5-f6g7-8901-bcde-fg2345678901,Member,CI/CD Pipeline,ServicePrincipal
```

**Key Rules**:
- ✅ **ONLY Object IDs (GUIDs)** - Never use emails or names
- ✅ One file per workspace/product (e.g., `sales_analytics_dev_principals.txt`)
- ✅ Use template: `workspace_principals.template.txt`

**Get Object IDs**:
```bash
# User
az ad user show --id user@domain.com --query id -o tsv

# Group
az ad group show --group "Team Name" --query id -o tsv

# Service Principal
az ad sp show --id <client-id> --query id -o tsv
```

**Roles**:
- `Admin` - Full workspace control
- `Member` - Edit content and manage items
- `Contributor` - Edit content only
- `Viewer` - Read-only access

---

## 🎬 Scenarios (Demo Configurations)

**Location**: `config/scenarios/`

**Purpose**: Configuration files for demo scenarios and framework testing

**Example**: `sales_analytics_etl.yaml`
```yaml
product:
  name: "sales-analytics-etl"
  description: "Sales Analytics ETL demo"
  owner_email: "${FABRIC_USER_EMAIL}"  # From .env

environments:
  dev:
    enabled: true
    capacity_id: "${FABRIC_CAPACITY_ID}"  # From .env

items:
  lakehouses:
    - name: "BRONZE_SalesTransactions_Lakehouse"
      description: "Raw sales data"

# NO email addresses in config!
# Users are loaded from config/principals/sales_analytics_dev_principals.txt
```

**Referenced By**:
- `scenarios/comprehensive-demo/run_sales_analytics_demo.py`
- `scenarios/automated-deployment/run_automated_deployment.py`

---

## 📦 Products (Real Data Products)

**Location**: `config/products/` (future use)

**Purpose**: Configuration for real, production data products

**Note**: Currently, data products use their own `product.yaml` files in `/data_products/*/`

**Future**: Consolidate product configs here for consistency

---

## 🔄 How Scripts Use This Folder

### Demo Scenario Example

```python
# scenarios/comprehensive-demo/run_sales_analytics_demo.py

# 1. Load scenario config
config_path = Path(__file__).parent.parent.parent / "config" / "scenarios" / "sales_analytics_etl.yaml"

# 2. Get product name from config
product_name = config['product']['name']  # "sales-analytics-etl"

# 3. Load principals for this product
principals_path = Path(__file__).parent.parent.parent / "config" / "principals" / f"{product_name}_dev_principals.txt"

# 4. Add users using Object IDs from principals file
subprocess.run([
    "python", "ops/scripts/manage_workspaces.py",
    "add-users-from-file",
    workspace_id,
    str(principals_path),
    "--yes"
])
```

### Data Product Example

```python
# Future: ops/scripts/deploy_data_product.py

# 1. Load product config
product_config = Path(__file__).parent.parent / "config" / "products" / f"{product_name}.yaml"

# 2. Load principals
principals = Path(__file__).parent.parent / "config" / "principals" / f"{product_name}_dev_principals.txt"

# 3. Deploy with centralized config
deploy_product(product_config, principals)
```

---

## ✅ Best Practices

### Creating New Configurations

1. **For a new demo scenario**:
   ```bash
   # 1. Create scenario config
   cp config/scenarios/sales_analytics_etl.yaml config/scenarios/my_demo.yaml
   
   # 2. Edit configuration
   vi config/scenarios/my_demo.yaml
   
   # 3. Create principals file
   cp config/principals/workspace_principals.template.txt config/principals/my_demo_dev_principals.txt
   
   # 4. Add Object IDs (NOT emails!)
   vi config/principals/my_demo_dev_principals.txt
   ```

2. **For a new data product**:
   ```bash
   # 1. Create product folder
   mkdir data_products/my_product
   
   # 2. Create principals file
   cp config/principals/workspace_principals.template.txt config/principals/my_product_dev_principals.txt
   
   # 3. Add Object IDs
   vi config/principals/my_product_dev_principals.txt
   ```

### Updating Principals

```bash
# Get new user's Object ID
NEW_USER_ID=$(az ad user show --id newuser@domain.com --query id -o tsv)

# Add to principals file
echo "${NEW_USER_ID},Member,New User Name,User" >> config/principals/my_product_dev_principals.txt

# Apply to existing workspace
python ops/scripts/manage_workspaces.py add-users-from-file \
  <workspace-id> \
  config/principals/my_product_dev_principals.txt \
  --yes
```

---

## 🚫 Common Mistakes to Avoid

### ❌ DON'T: Put emails in YAML files

```yaml
# ❌ BAD
users:
  - email: "user@domain.com"
    role: "Admin"
```

### ✅ DO: Use principals file with Object IDs

```
# ✅ GOOD (in config/principals/product_dev_principals.txt)
9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,User Name,User
```

### ❌ DON'T: Duplicate config files

```
# ❌ BAD
scenarios/my-demo/config.yaml
data_products/my-product/config.yaml
```

### ✅ DO: Use centralized config

```
# ✅ GOOD
config/scenarios/my_demo.yaml
config/principals/my_product_dev_principals.txt
```

### ❌ DON'T: Hardcode credentials

```yaml
# ❌ BAD
capacity_id: "0749B635-C51B-46C6-948A-02F05D7FE177"
owner_email: "user@domain.com"
```

### ✅ DO: Use environment variables

```yaml
# ✅ GOOD
capacity_id: "${FABRIC_CAPACITY_ID}"  # From .env
owner_email: "${FABRIC_USER_EMAIL}"   # From .env
```

---

## 📚 Related Documentation

- **Project Structure**: `/PROJECT_STRUCTURE.md` - Overall project organization
- **Naming Standards**: `/naming_standards.yaml` - Item naming rules
- **Project Config**: `/project.config.json` - Workspace naming patterns
- **Environment Setup**: `/.env.example` - Required environment variables

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Create principals file | `cp config/principals/workspace_principals.template.txt config/principals/myproduct_dev_principals.txt` |
| Get user Object ID | `az ad user show --id user@domain.com --query id -o tsv` |
| Get group Object ID | `az ad group show --group "Team Name" --query id -o tsv` |
| Add users to workspace | `python ops/scripts/manage_workspaces.py add-users-from-file <workspace-id> config/principals/myproduct_dev_principals.txt --yes` |
| List principals files | `ls -la config/principals/` |
| Validate principals format | `python ops/scripts/validate_principals.py config/principals/myproduct_dev_principals.txt` |

---

## 💡 Summary

- **ONE centralized config folder** - `/config`
- **NO emails** - Only Object IDs in principals files
- **Scenarios reference config** - Never duplicate
- **Products reference config** - Consistent pattern
- **Environment variables** - For sensitive values (.env)
