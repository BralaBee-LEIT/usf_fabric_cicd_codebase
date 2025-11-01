# USF Fabric CI/CD - Project Structure Guide

## 📋 Overview

This document clarifies the purpose of each major folder and how they work together.

---

## 🏗️ Main Folder Structure

```
usf-fabric-cicd/
├── config/                          # ✅ CENTRALIZED CONFIGURATION
│   ├── principals/                  # User/Group/SP definitions (Object IDs)
│   ├── products/                    # Product-specific configs (future)
│   └── scenarios/                   # Scenario configs for demos/testing
│
├── scenarios/                       # ✅ RUNNABLE DEMO SCRIPTS
│   ├── comprehensive-demo/          # Full framework demos
│   ├── automated-deployment/        # CI/CD automation demos
│   └── */                           # Other scenario examples
│
├── data_products/                   # ✅ ACTUAL DATA PRODUCTS (Git Integration)
│   ├── sales_analytics/             # Real data product definitions
│   ├── customer_insights/           # Real data product definitions
│   └── templates/                   # Templates for new products
│
├── ops/                             # ✅ OPERATIONAL SCRIPTS & UTILITIES
│   └── scripts/                     # CLI tools and utilities
│       ├── manage_workspaces.py     # Workspace CRUD operations
│       ├── manage_items.py          # Item management
│       └── utilities/               # Reusable framework code
│
├── tests/                           # ✅ TEST SUITES
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── real_fabric/                 # Real Fabric deployment tests
│
└── docs/                            # ✅ DOCUMENTATION
    ├── architecture/                # Architecture docs
    ├── guides/                      # How-to guides
    └── api/                         # API references
```

---

## 🎯 Clear Separation of Concerns

### 1. `/config` - Centralized Configuration

**Purpose**: Single source of truth for ALL configuration

**What Goes Here**:
- ✅ `config/principals/*.txt` - User/Group/Service Principal definitions with Object IDs
- ✅ `config/scenarios/*.yaml` - Configuration for demo scenarios
- ✅ `config/products/*.yaml` - Configuration for real data products (future)

**Key Rules**:
- **NO email addresses** - Only Azure AD Object IDs in principals files
- **NO code** - Only YAML/JSON/TXT configuration files
- **Centralized** - All scenarios and scripts reference this folder

**Example**:
```
config/
├── principals/
│   ├── sales_analytics_dev_principals.txt     # Object IDs for sales team
│   ├── customer_insights_dev_principals.txt   # Object IDs for customer team
│   └── workspace_principals.template.txt      # Template for new teams
│
└── scenarios/
    ├── sales_analytics_etl.yaml               # Sales ETL demo config
    └── comprehensive_demo.yaml                # Full framework demo config
```

---

### 2. `/scenarios` - Demo & Test Scripts

**Purpose**: Runnable Python scripts that demonstrate framework capabilities

**What Goes Here**:
- ✅ Python scripts that execute deployments
- ✅ README files explaining the scenario
- ✅ Documentation of demo results

**What Does NOT Go Here**:
- ❌ Configuration files (use `/config` instead)
- ❌ Reusable utilities (use `/ops/scripts/utilities` instead)
- ❌ Real data products (use `/data_products` instead)

**Key Rules**:
- Scripts should **reference** config files from `/config`
- Scripts should **use** utilities from `/ops/scripts/utilities`
- Scripts are for **demonstration and testing only**

**Example**:
```
scenarios/
├── comprehensive-demo/
│   ├── run_sales_analytics_demo.py           # Script (references config/)
│   ├── README.md                             # Documentation
│   └── DEPLOYMENT_STATUS.md                  # Results documentation
│
└── automated-deployment/
    ├── run_automated_deployment.py           # Script (references config/)
    └── README.md                             # Documentation
```

---

### 3. `/data_products` - Real Data Products

**Purpose**: Actual data product definitions that get deployed to Fabric and connected to Git

**What Goes Here**:
- ✅ Real data product folder structures
- ✅ Notebook definitions (.ipynb files)
- ✅ SQL scripts, schemas
- ✅ Documentation for each data product
- ✅ Product-specific configuration

**What Does NOT Go Here**:
- ❌ Demo scripts (use `/scenarios` instead)
- ❌ Shared principals (use `/config/principals` instead)

**Key Rules**:
- These folders are **synced to Fabric workspaces via Git**
- Each folder represents a **real, production data product**
- Follow Git integration patterns from `project.config.json`

**Example**:
```
data_products/
├── sales_analytics/
│   ├── notebooks/
│   │   ├── 01_ingest_sales.ipynb
│   │   └── 02_transform_sales.ipynb
│   ├── sql/
│   │   └── create_sales_tables.sql
│   ├── README.md
│   └── product.yaml                         # Product-specific config
│
└── customer_insights/
    ├── notebooks/
    ├── sql/
    ├── README.md
    └── product.yaml
```

---

### 4. `/ops/scripts` - Operational Tools

**Purpose**: Reusable CLI tools and utility functions

**What Goes Here**:
- ✅ CLI scripts (manage_workspaces.py, manage_items.py, etc.)
- ✅ Utility modules (fabric_api.py, fabric_item_manager.py, etc.)
- ✅ Shared code used by scenarios and data products

**Key Rules**:
- Code here should be **reusable**
- Should be **well-tested**
- Should follow **project standards**

---

## 🔄 How They Work Together

### Demo Scenario Workflow

```
1. Developer runs:
   $ cd scenarios/comprehensive-demo
   $ python run_sales_analytics_demo.py

2. Script loads config:
   - Reads: config/scenarios/sales_analytics_etl.yaml
   - Finds principals: config/principals/sales_analytics_dev_principals.txt

3. Script uses utilities:
   - Imports from: ops/scripts/utilities/
   - Uses: FabricItemManager, WorkspaceManager, etc.

4. Script creates resources:
   - Creates workspace in Fabric
   - Creates folders, lakehouses, notebooks
   - Adds users from principals file
```

### Real Data Product Workflow

```
1. Developer creates data product:
   $ cd data_products/
   $ mkdir new_product
   $ cp templates/product.yaml new_product/

2. Configure principals:
   $ vi config/principals/new_product_dev_principals.txt
   # Add Object IDs (NOT emails!)

3. Deploy to Fabric:
   $ python ops/scripts/deploy_data_product.py new_product

4. Script:
   - Reads: data_products/new_product/product.yaml
   - Uses principals: config/principals/new_product_dev_principals.txt
   - Creates workspace
   - Connects to Git
   - Syncs notebooks and SQL from data_products/new_product/
```

---

## ✅ Best Practices

### Configuration Management

1. **All configs in `/config`**
   ```yaml
   # ✅ Good
   config/scenarios/sales_analytics_etl.yaml
   
   # ❌ Bad
   scenarios/comprehensive-demo/sales_analytics_etl.yaml
   ```

2. **All principals in `/config/principals`**
   ```
   # ✅ Good
   config/principals/sales_analytics_dev_principals.txt
   
   # ❌ Bad
   scenarios/comprehensive-demo/principals.txt
   data_products/sales_analytics/principals.txt
   ```

3. **Scripts reference centralized config**
   ```python
   # ✅ Good
   config_path = Path(__file__).parent.parent.parent / "config" / "scenarios" / "sales_analytics_etl.yaml"
   
   # ❌ Bad
   config_path = Path(__file__).parent / "sales_analytics_etl.yaml"
   ```

### User Management

1. **Always use Object IDs, never emails**
   ```
   # ✅ Good (in config/principals/sales_dev_principals.txt)
   9117cbfa-f0a7-43b7-846f-96ba66a3c1c0,Admin,Sanmi Ibitoye,User
   
   # ❌ Bad (in any YAML)
   users:
     - email: "sanmi@leit-teksystems.com"  # DON'T DO THIS!
   ```

2. **Get Object IDs before deployment**
   ```bash
   # User
   az ad user show --id sanmi@leit-teksystems.com --query id -o tsv
   
   # Group
   az ad group show --group "Data Engineering" --query id -o tsv
   
   # Service Principal
   az ad sp show --id <client-id> --query id -o tsv
   ```

### Script Organization

1. **Scenarios = Demos**
   - Should be **runnable examples**
   - Should **reference centralized config**
   - Should **document their purpose**

2. **Data Products = Real Workspaces**
   - Should contain **actual notebook code**
   - Should have **Git integration**
   - Should follow **naming standards**

---

## 🔧 Migration Guide

### If You Have Config Files in Wrong Locations

```bash
# Move scenario configs to centralized location
mv scenarios/comprehensive-demo/*.yaml config/scenarios/

# Update scripts to reference new locations
# (see examples above)

# Create symbolic links if needed (NOT recommended)
# Better to update the scripts properly
```

### If You Have Principals in Multiple Places

```bash
# Consolidate all principals to config/principals/
cp scenarios/*/principals.txt config/principals/
cp data_products/*/principals.txt config/principals/

# Delete duplicates
rm scenarios/*/principals.txt
rm data_products/*/principals.txt

# Update scripts to always use config/principals/
```

---

## 📚 Quick Reference

| Need to... | Look in... | Example |
|------------|------------|---------|
| Add users to workspace | `config/principals/` | `sales_analytics_dev_principals.txt` |
| Configure a demo | `config/scenarios/` | `sales_analytics_etl.yaml` |
| Run a demo | `scenarios/` | `scenarios/comprehensive-demo/run_sales_analytics_demo.py` |
| Deploy real product | `data_products/` | `data_products/sales_analytics/` |
| Use framework utilities | `ops/scripts/utilities/` | `from utilities.fabric_item_manager import ...` |
| Manage workspaces | `ops/scripts/` | `python ops/scripts/manage_workspaces.py` |

---

## 🎯 Summary

**Single Source of Truth**:
- `/config` = ALL configuration (scenarios, principals, products)
- NO config files scattered in other folders
- NO email addresses anywhere - only Object IDs in principals files

**Clear Separation**:
- `/scenarios` = Demo scripts (reference config)
- `/data_products` = Real products (reference config)
- `/ops/scripts` = Reusable utilities
- `/tests` = Test suites

**Consistent Patterns**:
- Scripts → reference → `/config`
- Principals → always from → `/config/principals`
- Object IDs → never emails
- Centralized → never duplicated
