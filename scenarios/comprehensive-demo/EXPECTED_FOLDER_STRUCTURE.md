# Expected Folder Organization - Visual Reference

## 🎨 Complete Structure

```
usf2-fabric-sales-analytics-etl-dev/
│
├── 📂 Bronze Layer/
│   ├── 📂 Raw Data/
│   │   ├── 🗄️  BRONZE_SalesTransactions_Lakehouse
│   │   ├── 🗄️  BRONZE_CustomerMaster_Lakehouse
│   │   ├── 📓 01_IngestSalesTransactions_Notebook
│   │   └── 📓 02_IngestCustomerData_Notebook
│   │
│   ├── 📂 External Sources/
│   │   └── (reserved for external data sources)
│   │
│   └── 📂 Archive/
│       └── (reserved for historical data)
│
├── 📂 Silver Layer/
│   ├── 📂 Cleaned/
│   │   ├── 🗄️  SILVER_SalesTransactions_Lakehouse
│   │   └── 🗄️  SILVER_CustomerData_Lakehouse
│   │
│   ├── 📂 Transformed/
│   │   ├── 📓 10_TransformSalesData_Notebook
│   │   └── 📓 11_TransformCustomerData_Notebook
│   │
│   └── 📂 Validated/
│       └── (reserved for QA-approved datasets)
│
├── 📂 Gold Layer/
│   ├── 📂 Analytics/
│   │   ├── 🗄️  GOLD_SalesAnalytics_Lakehouse
│   │   ├── 🗄️  GOLD_CustomerInsights_Lakehouse
│   │   ├── 📓 20_CalculateSalesKPIs_Notebook
│   │   └── 📓 21_BuildCustomerSegments_Notebook
│   │
│   ├── 📂 Business Metrics/
│   │   └── (reserved for business metric definitions)
│   │
│   └── 📂 Reports/
│       └── (reserved for Power BI reports)
│
└── ROOT/
    ├── 📓 50_MasterETL_Orchestration_Notebook (orchestration)
    └── 📓 70_DataQuality_Checks_Notebook (data quality)
```

---

## 📊 Data Flow Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATION                             │
│                                                                  │
│              50_MasterETL_Orchestration_Notebook                 │
│                            (ROOT)                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      BRONZE LAYER                                │
│                      (Raw Data Ingestion)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📂 Raw Data/                                                    │
│     ├── 🗄️  BRONZE_SalesTransactions_Lakehouse                  │
│     ├── 🗄️  BRONZE_CustomerMaster_Lakehouse                     │
│     ├── 📓 01_IngestSalesTransactions_Notebook                  │
│     └── 📓 02_IngestCustomerData_Notebook                       │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      SILVER LAYER                                │
│                  (Cleaned & Transformed)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📂 Cleaned/                                                     │
│     ├── 🗄️  SILVER_SalesTransactions_Lakehouse                  │
│     └── 🗄️  SILVER_CustomerData_Lakehouse                       │
│                                                                  │
│  📂 Transformed/                                                 │
│     ├── 📓 10_TransformSalesData_Notebook                       │
│     └── 📓 11_TransformCustomerData_Notebook                    │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                       GOLD LAYER                                 │
│                   (Analytics & Insights)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📂 Analytics/                                                   │
│     ├── 🗄️  GOLD_SalesAnalytics_Lakehouse                       │
│     ├── 🗄️  GOLD_CustomerInsights_Lakehouse                     │
│     ├── 📓 20_CalculateSalesKPIs_Notebook                       │
│     └── 📓 21_BuildCustomerSegments_Notebook                    │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA QUALITY                                │
│                                                                  │
│              70_DataQuality_Checks_Notebook                      │
│                            (ROOT)                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Color-Coded Layer Reference

### 🟤 Bronze Layer (Raw Zone)
**Purpose**: Raw data ingestion and landing  
**Naming**: `BRONZE_*` for lakehouses, `01-09_*` for notebooks  
**Processing**: No transformations, just ingestion from sources  
**Subfolders**:
- `Raw Data/` - Active raw data landing zone
- `External Sources/` - Third-party data integrations
- `Archive/` - Historical raw data backups

### 🥈 Silver Layer (Cleaned Zone)
**Purpose**: Cleaned, validated, and transformed data  
**Naming**: `SILVER_*` for lakehouses, `10-19_*` for notebooks  
**Processing**: Data cleaning, deduplication, validation, enrichment  
**Subfolders**:
- `Cleaned/` - Cleaned datasets ready for transformation
- `Transformed/` - Transformed and enriched datasets
- `Validated/` - QA-approved datasets for analytics

### 🥇 Gold Layer (Analytics Zone)
**Purpose**: Business-ready analytics and insights  
**Naming**: `GOLD_*` for lakehouses, `20-29_*` for notebooks  
**Processing**: Aggregations, KPIs, metrics, ML models  
**Subfolders**:
- `Analytics/` - Analytics-ready datasets and models
- `Business Metrics/` - Business metric definitions
- `Reports/` - Power BI reports and dashboards

---

## 📋 Item Checklist for Manual Organization

### Step 1: Bronze Layer Organization

- [ ] Move `BRONZE_SalesTransactions_Lakehouse` → **Bronze Layer/Raw Data/**
- [ ] Move `BRONZE_CustomerMaster_Lakehouse` → **Bronze Layer/Raw Data/**
- [ ] Move `01_IngestSalesTransactions_Notebook` → **Bronze Layer/Raw Data/**
- [ ] Move `02_IngestCustomerData_Notebook` → **Bronze Layer/Raw Data/**

### Step 2: Silver Layer Organization

- [ ] Move `SILVER_SalesTransactions_Lakehouse` → **Silver Layer/Cleaned/**
- [ ] Move `SILVER_CustomerData_Lakehouse` → **Silver Layer/Cleaned/**
- [ ] Move `10_TransformSalesData_Notebook` → **Silver Layer/Transformed/**
- [ ] Move `11_TransformCustomerData_Notebook` → **Silver Layer/Transformed/**

### Step 3: Gold Layer Organization

- [ ] Move `GOLD_SalesAnalytics_Lakehouse` → **Gold Layer/Analytics/**
- [ ] Move `GOLD_CustomerInsights_Lakehouse` → **Gold Layer/Analytics/**
- [ ] Move `20_CalculateSalesKPIs_Notebook` → **Gold Layer/Analytics/**
- [ ] Move `21_BuildCustomerSegments_Notebook` → **Gold Layer/Analytics/**

### Step 4: Verify ROOT Items

- [ ] Confirm `50_MasterETL_Orchestration_Notebook` stays at **ROOT**
- [ ] Confirm `70_DataQuality_Checks_Notebook` stays at **ROOT**

---

## 📸 Screenshots Guide

### Before Organization
```
Workspace Root/
├── 📂 Bronze Layer/
│   ├── 📂 Raw Data/ (empty)
│   ├── 📂 External Sources/ (empty)
│   └── 📂 Archive/ (empty)
├── 📂 Silver Layer/
│   ├── 📂 Cleaned/ (empty)
│   ├── 📂 Transformed/ (empty)
│   └── 📂 Validated/ (empty)
├── 📂 Gold Layer/
│   ├── 📂 Analytics/ (empty)
│   ├── 📂 Business Metrics/ (empty)
│   └── 📂 Reports/ (empty)
├── 🗄️  BRONZE_SalesTransactions_Lakehouse (at root ❌)
├── 🗄️  BRONZE_CustomerMaster_Lakehouse (at root ❌)
├── 📓 01_IngestSalesTransactions_Notebook (at root ❌)
├── 📓 02_IngestCustomerData_Notebook (at root ❌)
├── 🗄️  SILVER_SalesTransactions_Lakehouse (at root ❌)
├── 🗄️  SILVER_CustomerData_Lakehouse (at root ❌)
├── 📓 10_TransformSalesData_Notebook (at root ❌)
├── 📓 11_TransformCustomerData_Notebook (at root ❌)
├── 🗄️  GOLD_SalesAnalytics_Lakehouse (at root ❌)
├── 🗄️  GOLD_CustomerInsights_Lakehouse (at root ❌)
├── 📓 20_CalculateSalesKPIs_Notebook (at root ❌)
├── 📓 21_BuildCustomerSegments_Notebook (at root ❌)
├── 📓 50_MasterETL_Orchestration_Notebook (at root ✅)
└── 📓 70_DataQuality_Checks_Notebook (at root ✅)
```

### After Organization ✅
```
Workspace Root/
├── 📂 Bronze Layer/
│   ├── 📂 Raw Data/
│   │   ├── 🗄️  BRONZE_SalesTransactions_Lakehouse ✅
│   │   ├── 🗄️  BRONZE_CustomerMaster_Lakehouse ✅
│   │   ├── 📓 01_IngestSalesTransactions_Notebook ✅
│   │   └── 📓 02_IngestCustomerData_Notebook ✅
│   ├── 📂 External Sources/ (empty)
│   └── 📂 Archive/ (empty)
├── 📂 Silver Layer/
│   ├── 📂 Cleaned/
│   │   ├── 🗄️  SILVER_SalesTransactions_Lakehouse ✅
│   │   └── 🗄️  SILVER_CustomerData_Lakehouse ✅
│   ├── 📂 Transformed/
│   │   ├── 📓 10_TransformSalesData_Notebook ✅
│   │   └── 📓 11_TransformCustomerData_Notebook ✅
│   └── 📂 Validated/ (empty)
├── 📂 Gold Layer/
│   ├── 📂 Analytics/
│   │   ├── 🗄️  GOLD_SalesAnalytics_Lakehouse ✅
│   │   ├── 🗄️  GOLD_CustomerInsights_Lakehouse ✅
│   │   ├── 📓 20_CalculateSalesKPIs_Notebook ✅
│   │   └── 📓 21_BuildCustomerSegments_Notebook ✅
│   ├── 📂 Business Metrics/ (empty)
│   └── 📂 Reports/ (empty)
├── 📓 50_MasterETL_Orchestration_Notebook ✅
└── 📓 70_DataQuality_Checks_Notebook ✅
```

---

## 🚀 Quick Organization Commands

### Fabric Portal UI
1. Select multiple items (Ctrl+Click or Cmd+Click)
2. Drag to target folder
3. Drop to complete move

### Future API-Based Organization
```bash
# When API becomes available
python organize_items_into_folders.py \
  --workspace 8ef68ccc-c5d6-4140-8b6f-a77f78eebebc \
  --dry-run  # Preview changes first

# Then apply
python organize_items_into_folders.py \
  --workspace 8ef68ccc-c5d6-4140-8b6f-a77f78eebebc \
  --apply
```

---

## 💡 Tips & Best Practices

### Efficient Organization Strategy

1. **Organize by Layer**: Do all Bronze items first, then Silver, then Gold
2. **Use Multi-Select**: Select all items for a folder at once (Ctrl/Cmd+Click)
3. **Verify as You Go**: Check each folder after moving items
4. **Follow the Numbers**: Notebook prefixes (01, 10, 20) match their target layer

### Naming Pattern Recognition

- **BRONZE_** prefix → Bronze Layer/Raw Data
- **SILVER_** prefix → Silver Layer/Cleaned  
- **GOLD_** prefix → Gold Layer/Analytics
- **01-09** prefix → Bronze notebooks
- **10-19** prefix → Silver notebooks
- **20-29** prefix → Gold notebooks
- **50+** prefix → ROOT orchestration/utilities

---

## 📚 Related Files

- **Main Guide**: `FOLDER_ORGANIZATION_GUIDE.md`
- **Deployment Script**: `run_sales_analytics_demo.py`
- **Folder Manager**: `../../ops/scripts/utilities/fabric_folder_manager.py`
- **Item Manager**: `../../ops/scripts/utilities/fabric_item_manager.py`
