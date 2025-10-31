# Folder Organization Guide
## Sales Analytics ETL Demo

### 📌 Current Status

**Workspace**: `usf2-fabric-sales-analytics-etl-dev`  
**Workspace ID**: `8ef68ccc-c5d6-4140-8b6f-a77f78eebebc`

- ✅ **12 folders created** with medallion architecture (Bronze/Silver/Gold + subfolders)
- ✅ **14 items created** with proper naming standards
- ⚠️ **Items at ROOT** - Fabric API doesn't support programmatic folder placement yet

---

## 📁 Folder Structure

```
📂 Bronze Layer (a7a67c34-ef8a-4fbc-a888-b7fdeea0b18f)
   └─ Archive (66eacf82-4f76-4ccf-851c-2621c6922ce8)
   └─ External Sources (b22e4baa-84b3-47ac-8e63-12488fc14988)
   └─ Raw Data (8575875a-2b42-4df3-b94e-23c964385eb1)

📂 Silver Layer (d2f4b63a-a158-42b4-9108-3ff66ac68547)
   └─ Cleaned (320351ff-cb4d-4736-a611-92e12885951c)
   └─ Transformed (5c24a366-0c7f-4064-bd01-580ab515322c)
   └─ Validated (b83c38ef-a65f-4de8-9690-d78d584c0888)

📂 Gold Layer (790415a1-ffdb-48cc-887b-b468f6117813)
   └─ Analytics (b7e0c3c9-493d-4508-ad7a-298fe46f106e)
   └─ Business Metrics (06213be4-ec34-45c3-87a1-68025b956c07)
   └─ Reports (4056ea9e-169c-4fd7-b92d-f2a8ceb44646)
```

---

## 🎯 Intended Item Placement

### Bronze Layer → Raw Data

**Lakehouses:**
- `BRONZE_SalesTransactions_Lakehouse` - Raw sales transaction data
- `BRONZE_CustomerMaster_Lakehouse` - Raw customer master data

**Notebooks:**
- `01_IngestSalesTransactions_Notebook` - Ingests sales transactions from source
- `02_IngestCustomerData_Notebook` - Ingests customer data from source

---

### Silver Layer → Cleaned

**Lakehouses:**
- `SILVER_SalesTransactions_Lakehouse` - Cleaned sales transactions
- `SILVER_CustomerData_Lakehouse` - Cleaned customer data

---

### Silver Layer → Transformed

**Notebooks:**
- `10_TransformSalesData_Notebook` - Transforms and enriches sales data
- `11_TransformCustomerData_Notebook` - Transforms and enriches customer data

---

### Gold Layer → Analytics

**Lakehouses:**
- `GOLD_SalesAnalytics_Lakehouse` - Aggregated sales analytics
- `GOLD_CustomerInsights_Lakehouse` - Customer insights and segments

**Notebooks:**
- `20_CalculateSalesKPIs_Notebook` - Calculates sales KPIs and metrics
- `21_BuildCustomerSegments_Notebook` - Builds customer segmentation

---

### ROOT (Orchestration & Utility)

**Notebooks:**
- `50_MasterETL_Orchestration_Notebook` - Master orchestration pipeline
- `70_DataQuality_Checks_Notebook` - Data quality validation checks

---

## 🔧 Manual Organization Steps

Since Fabric API doesn't support programmatic folder placement, follow these steps to organize items:

### Option 1: Fabric Portal UI (Drag & Drop)

1. **Open Fabric Portal**: https://app.fabric.microsoft.com
2. **Navigate to workspace**: `usf2-fabric-sales-analytics-etl-dev`
3. **Drag items** into target folders according to the mappings above
   - Select item(s) → Drag → Drop into folder
   - Multiple items can be selected with Ctrl+Click (Windows) or Cmd+Click (Mac)

### Option 2: Bulk Organization (Future)

Once Microsoft publishes the `/bulkMoveItems` endpoint, this framework will support:

```bash
# This will work when API becomes available
python organize_items_into_folders.py --workspace 8ef68ccc-c5d6-4140-8b6f-a77f78eebebc
```

The intelligent placement logic is already implemented and ready:
- ✅ Naming pattern detection (BRONZE_*, SILVER_*, GOLD_*)
- ✅ Notebook numbering logic (01-09, 10-19, 20-29, 50+)
- ✅ Folder mapping configuration
- ⏳ Waiting for Fabric API support

---

## 📊 Item Mapping Quick Reference

| Item Name | Type | Target Folder | Rationale |
|-----------|------|---------------|-----------|
| `BRONZE_SalesTransactions_Lakehouse` | Lakehouse | Bronze Layer/Raw Data | Raw ingestion |
| `BRONZE_CustomerMaster_Lakehouse` | Lakehouse | Bronze Layer/Raw Data | Raw ingestion |
| `01_IngestSalesTransactions_Notebook` | Notebook | Bronze Layer/Raw Data | 01-09 = Bronze ingestion |
| `02_IngestCustomerData_Notebook` | Notebook | Bronze Layer/Raw Data | 01-09 = Bronze ingestion |
| `SILVER_SalesTransactions_Lakehouse` | Lakehouse | Silver Layer/Cleaned | Cleaned data |
| `SILVER_CustomerData_Lakehouse` | Lakehouse | Silver Layer/Cleaned | Cleaned data |
| `10_TransformSalesData_Notebook` | Notebook | Silver Layer/Transformed | 10-19 = Silver transform |
| `11_TransformCustomerData_Notebook` | Notebook | Silver Layer/Transformed | 10-19 = Silver transform |
| `GOLD_SalesAnalytics_Lakehouse` | Lakehouse | Gold Layer/Analytics | Analytics layer |
| `GOLD_CustomerInsights_Lakehouse` | Lakehouse | Gold Layer/Analytics | Analytics layer |
| `20_CalculateSalesKPIs_Notebook` | Notebook | Gold Layer/Analytics | 20-29 = Gold analytics |
| `21_BuildCustomerSegments_Notebook` | Notebook | Gold Layer/Analytics | 20-29 = Gold analytics |
| `50_MasterETL_Orchestration_Notebook` | Notebook | ROOT | 50+ = Orchestration |
| `70_DataQuality_Checks_Notebook` | Notebook | ROOT | 70+ = Utility |

---

## 🔍 Verification

### Check Current State

```bash
# List all items
cd /home/sanmi/Documents/J'TOYE_DIGITAL/LEIT_TEKSYSTEMS/1_Project_Rhico/usf-fabric-cicd
set -a && source .env && set +a && python check_items.py

# List folder structure
set -a && source .env && set +a && python check_folders.py
```

### Verify Organization (After Manual Move)

```python
from utilities.fabric_item_manager import FabricItemManager

manager = FabricItemManager()
workspace_id = '8ef68ccc-c5d6-4140-8b6f-a77f78eebebc'

items = manager.list_items(workspace_id)

# Count items by location
locations = {}
for item in items:
    location = item.workspace_object_id if hasattr(item, 'workspace_object_id') else 'ROOT'
    locations[location] = locations.get(location, 0) + 1

print(f"Items by location: {locations}")
```

---

## 🚀 Future Enhancements

### When Fabric API Supports Folder Placement

The framework will automatically:

1. **Create items directly in folders** during deployment
   ```python
   item_manager.create_item(
       workspace_id=workspace_id,
       display_name="BRONZE_SalesTransactions_Lakehouse",
       item_type=FabricItemType.LAKEHOUSE,
       folder_id=bronze_raw_data_folder_id  # ← Will work when API ready
   )
   ```

2. **Move items to folders** programmatically
   ```python
   folder_manager.move_items_to_folder(
       workspace_id=workspace_id,
       folder_id=target_folder_id,
       item_ids=[item1_id, item2_id, item3_id]  # ← Will work when API ready
   )
   ```

3. **Validate folder organization** in CI/CD
   ```bash
   python validate_folder_organization.py --workspace ${WORKSPACE_ID}
   ```

---

## 📚 Related Documentation

- **Folder API Implementation**: `FOLDER_API_IMPLEMENTATION.md`
- **Intelligent Placement Logic**: `INTELLIGENT_FOLDER_PLACEMENT.md`
- **Naming Standards**: `../../naming_standards.yaml`
- **Deployment Guide**: `README.md`

---

## 💡 Best Practices

### Naming Conventions for Auto-Placement

When the API becomes available, these naming patterns will enable automatic folder placement:

**Lakehouses:**
- `BRONZE_*` → Bronze Layer/Raw Data
- `SILVER_*` → Silver Layer/Cleaned
- `GOLD_*` → Gold Layer/Analytics

**Notebooks:**
- `01-09_*` → Bronze Layer/Raw Data (ingestion)
- `10-19_*` → Silver Layer/Transformed (transformation)
- `20-29_*` → Gold Layer/Analytics (analytics/aggregation)
- `50-59_*` → ROOT (orchestration)
- `70-79_*` → ROOT (data quality/validation)
- `90-99_*` → ROOT (utilities)

### Folder Organization Tips

1. **Consistent Layer Grouping**: Keep medallion architecture (Bronze/Silver/Gold) clear
2. **Process Flow**: Organize by data flow (Raw → Cleaned → Transformed → Analytics)
3. **Separation of Concerns**: Keep orchestration and utilities at root level
4. **Subfolder Usage**: Use subfolders for specific purposes:
   - Archive: Historical/backup data
   - External Sources: Third-party integrations
   - Validated: Data quality-approved datasets

---

## ⚠️ Known Limitations

### Fabric API Constraints (as of January 2025)

1. **No folder parameter during item creation**: Items always created at root
   - Tried: `?workspaceObjectId={folder_id}` query parameter → Doesn't work
   - Tried: `folder_id` in request body → Not supported

2. **No move items endpoint**: `/bulkMoveItems` returns 404
   - API not published yet
   - Expected in future Fabric API update

3. **Workaround**: Manual drag-and-drop in Fabric Portal
   - Framework documents intended locations
   - Intelligent logic ready for when API available

---

## 🎯 Summary

✅ **What Works:**
- Workspace creation with project naming standards
- Folder structure creation (medallion architecture)
- Item creation with naming validation
- Intelligent folder determination logic
- Documentation of intended folder mappings

⚠️ **What Requires Manual Steps:**
- Moving items into folders (drag-and-drop in Portal)

🔮 **What's Coming:**
- Automatic folder placement when Fabric API supports it
- Framework already implements the logic
- Zero code changes needed when API becomes available
