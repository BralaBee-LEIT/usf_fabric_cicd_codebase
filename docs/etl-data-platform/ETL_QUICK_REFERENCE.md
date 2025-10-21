# ETL Workspace Quick Reference

**Date:** 21 October 2025  
**Purpose:** Quick commands for complete ETL setup  

---

## 🚀 One-Command Setup

```bash
# Run automated setup script (creates everything)
./setup_etl_workspace.sh
```

**What it creates:**
- ✅ ETL Platform [DEV] workspace
- ✅ ETL Platform [TEST] workspace  
- ✅ 3 Lakehouses (Bronze, Silver, Gold)
- ✅ 1 Warehouse (AnalyticsWarehouse)
- ✅ 3 Notebooks (Ingestion, Transformation, Aggregation)
- ✅ 2 Pipelines (orchestration)

---

## 📝 Manual Step-by-Step

### 1. Create Workspaces

```bash
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/etl_platform.yaml
```

### 2. Add Users

```bash
# Admin
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace "ETL Platform [DEV]" \
  --email "admin@company.com" \
  --role Admin

# Engineer
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace "ETL Platform [DEV]" \
  --email "engineer@company.com" \
  --role Member

# Analyst
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace "ETL Platform [DEV]" \
  --email "analyst@company.com" \
  --role Contributor

# Viewer
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace "ETL Platform [DEV]" \
  --email "viewer@company.com" \
  --role Viewer
```

### 3. Create Lakehouses

```bash
# Bronze (Raw data)
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "BronzeLakehouse" \
  --type Lakehouse

# Silver (Cleaned data)
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "SilverLakehouse" \
  --type Lakehouse

# Gold (Business-ready)
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "GoldLakehouse" \
  --type Lakehouse
```

### 4. Create Warehouse

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "AnalyticsWarehouse" \
  --type Warehouse
```

### 5. Create Notebooks

```bash
# Ingestion
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "01_DataIngestion" \
  --type Notebook

# Transformation
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "02_DataTransformation" \
  --type Notebook

# Aggregation
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "03_DataAggregation" \
  --type Notebook
```

### 6. Create Pipelines

```bash
# Ingestion Pipeline
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "Pipeline_DataIngestion" \
  --type DataPipeline

# Transformation Pipeline
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "ETL Platform [DEV]" \
  --name "Pipeline_Transformation" \
  --type DataPipeline
```

---

## 🔍 Verification Commands

### List All Items

```bash
python3 ops/scripts/manage_fabric_items.py list \
  --workspace "ETL Platform [DEV]"
```

### List Users

```bash
python3 ops/scripts/manage_workspaces.py list-users \
  --workspace "ETL Platform [DEV]"
```

### Get Workspace Details

```bash
python3 ops/scripts/manage_workspaces.py describe \
  --workspace "ETL Platform [DEV]"
```

---

## 🏗️ ETL Architecture

```
┌─────────────────────────────────────────────────────┐
│              MEDALLION ARCHITECTURE                  │
└─────────────────────────────────────────────────────┘

Sources              Bronze           Silver          Gold
═══════             ════════         ════════        ═══════

CSV Files                                            Business
JSON APIs    →     Raw Data    →   Cleaned    →     Metrics
Databases          Lakehouse       Lakehouse        Lakehouse
                                                         ↓
                                                    Warehouse
                                                         ↓
                                                     Reports
```

---

## 📊 Item Inventory

| Item | Type | Purpose |
|------|------|---------|
| BronzeLakehouse | Lakehouse | Raw ingestion |
| SilverLakehouse | Lakehouse | Cleaned data |
| GoldLakehouse | Lakehouse | Business metrics |
| AnalyticsWarehouse | Warehouse | SQL queries |
| 01_DataIngestion | Notebook | Load raw data |
| 02_DataTransformation | Notebook | Clean/transform |
| 03_DataAggregation | Notebook | Create metrics |
| Pipeline_DataIngestion | Pipeline | Ingestion orchestration |
| Pipeline_Transformation | Pipeline | Transform orchestration |

---

## 👥 User Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| Admin | Full control | Team lead, owner |
| Member | Create/edit items | Data engineers |
| Contributor | View + limited edit | Analysts |
| Viewer | Read-only | Stakeholders |

---

## 🎯 Common Tasks

### Run Pipeline

```bash
python3 ops/scripts/manage_fabric_items.py run \
  --workspace "ETL Platform [DEV]" \
  --item-name "Pipeline_DataIngestion" \
  --type DataPipeline
```

### Check Pipeline Status

```bash
python3 ops/scripts/manage_fabric_items.py get-status \
  --workspace "ETL Platform [DEV]" \
  --item-name "Pipeline_DataIngestion" \
  --type DataPipeline
```

### Query Warehouse

```bash
python3 ops/scripts/manage_fabric_items.py query \
  --workspace "ETL Platform [DEV]" \
  --item-name "AnalyticsWarehouse" \
  --type Warehouse \
  --sql "SELECT COUNT(*) FROM CustomerSegments"
```

### Export Item Definition

```bash
python3 ops/scripts/manage_fabric_items.py get-definition \
  --workspace "ETL Platform [DEV]" \
  --item-name "BronzeLakehouse" \
  --type Lakehouse \
  --output exports/bronze_lakehouse.json
```

---

## 🚀 Next Steps

1. ✅ **Workspace created** → Add your data sources
2. ✅ **Lakehouses ready** → Configure storage connections
3. ✅ **Notebooks created** → Add ETL logic (see guide for examples)
4. ✅ **Pipelines ready** → Schedule automated runs
5. 📊 **Create reports** → Connect Power BI to warehouse
6. 🔄 **Promote to TEST** → Deploy tested pipelines
7. 🌍 **Deploy to PROD** → Production release

---

## 📚 Documentation

- **Full Guide:** `COMPLETE_ETL_SETUP_GUIDE.md`
- **Promotion:** `ENVIRONMENT_PROMOTION_GUIDE.md`
- **Items/Users:** `FABRIC_ITEMS_AND_USERS_GUIDE.md`
- **Convergence:** `HOW_FLOWS_CONVERGE.md`

---

*Generated: 21 October 2025*  
*Ready for production use* 🎉
