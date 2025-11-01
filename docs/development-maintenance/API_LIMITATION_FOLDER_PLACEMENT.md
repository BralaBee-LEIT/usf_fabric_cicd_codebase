# API Limitation Discovery - Folder Item Placement

## Summary

**Issue Reported**: "folders were created yes, but fabric items should be in the respective folder not that they should all be present in the root whilst we have empty folders"

**Root Cause Identified**: Microsoft Fabric Folders API does NOT support programmatic item placement.

## Investigation Results

### What We Found ✓

1. **Folders API Works**:
   - `POST /workspaces/{id}/folders` - Create folders ✅
   - `GET /workspaces/{id}/folders` - List folders ✅
   - `PATCH /workspaces/{id}/folders/{id}` - Update folder name ✅
   - Status: **PREVIEW** (not GA)

2. **Items API Works**:
   - `POST /workspaces/{id}/items` - Create items ✅
   - Items always created at workspace root
   - Response includes `folderId` field (read-only)

### What Does NOT Exist ✗

1. **No Bulk Move API**:
   ```bash
   POST /workspaces/{id}/bulkMoveItems
   # Returns: 404 - EntityNotFound
   ```

2. **No folderId in Item Creation**:
   ```json
   POST /workspaces/{id}/items
   {
     "displayName": "My Lakehouse",
     "type": "Lakehouse",
     "folderId": "..." // NOT SUPPORTED
   }
   ```

3. **No folderId in Item Update**:
   ```json
   PATCH /workspaces/{id}/items/{id}
   {
     "displayName": "New Name",  // Supported
     "description": "...",        // Supported  
     "folderId": "..."            // NOT SUPPORTED
   }
   ```

## Microsoft Documentation

**Item Update API**:
- Docs: https://learn.microsoft.com/en-us/rest/api/fabric/core/items/update-item
- UpdateItemRequest includes ONLY:
  - `displayName` (string)
  - `description` (string)

**Folders API**:
- Docs: https://learn.microsoft.com/en-us/rest/api/fabric/core/folders/
- Status: **PREVIEW**
- No endpoints for item assignment

## Testing Performed

### Test 1: Bulk Move Attempt
```python
from ops.scripts.utilities.fabric_folder_manager import FabricFolderManager

mgr = FabricFolderManager()
results = mgr.move_items_to_folder(
    workspace_id="8ef68ccc-c5d6-4140-8b6f-a77f78eebebc",
    item_ids=["item1", "item2"],
    target_folder_id="folder-id"
)
```

**Result**:
```
ERROR: Fabric API error: 404
{"errorCode":"EntityNotFound","message":"The requested resource could not be found"}
Endpoint: POST /workspaces/{id}/bulkMoveItems
```

### Test 2: Verify Current State
```bash
# All 14 items (lakehouses + notebooks) at workspace ROOT
# 12 folders exist but are EMPTY
```

## Current Solution

### Code Changes Made

**File**: `scenarios/comprehensive-demo/run_sales_analytics_demo.py`

**Before** (Attempted - doesn't work):
```python
# Try to move items to folders
results = folder_manager.move_items_to_folder(
    workspace_id=workspace_id,
    item_ids=item_ids,
    target_folder_id=folder_id
)
# Result: 404 error
```

**After** (Current):
```python
# Document intended folder organization
print_warning("⚠️  API Limitation: Programmatic folder placement not available")
print_info("   Items created at workspace root - manual organization required")

print_info("📋 Recommended Manual Organization:")
print_info("\n   📁 Bronze Layer/Raw Data:")
print_info("      - BRONZE_SalesTransactions_Lakehouse")
print_info("      - 01_Ingest_Sales_Data.ipynb")
# ... etc for all folders
```

## Current Behavior

### Deployment Output
```
[Step 2/6] Creating Items
Created 6 lakehouses
Created 8 notebooks
✓ Created 14 total items

⚠️  API Limitation: Programmatic folder placement not available
   Items created at workspace root - manual organization required

📋 Recommended Manual Organization:

   📁 Bronze Layer/Raw Data:
      - BRONZE_SalesTransactions_Lakehouse
      - BRONZE_CustomerMaster_Lakehouse
      - 01_Ingest_Sales_Data.ipynb
      - 02_Ingest_Customer_Data.ipynb

   📁 Silver Layer/Transformed:
      - SILVER_CleanedSales_Lakehouse
      - 10_Transform_Sales.ipynb
      - 11_Transform_Customers.ipynb

   📁 Gold Layer/Analytics:
      - GOLD_SalesAnalytics_Lakehouse
      - 20_Aggregate_Sales.ipynb
      - 21_Customer_Analytics.ipynb
```

### Manual Organization Required

After deployment, users must:
1. Open workspace in Microsoft Fabric Portal
2. Manually drag and drop items into folders
3. Follow the recommended organization displayed in console

## Workarounds & Alternatives

### Option 1: Clear Documentation (Implemented)
- Display intended folder structure in console output
- Users manually organize via Portal UI
- Naming conventions indicate folder placement

### Option 2: Naming Convention
- Use folder prefixes in item names:
  - `BronzeRaw_` for Bronze Layer/Raw Data
  - `SilverTransformed_` for Silver Layer/Transformed
  - `GoldAnalytics_` for Gold Layer/Analytics
- Items self-document their organization

### Option 3: Post-Deployment Script
- Create a PowerShell/CLI script for manual execution
- Use Fabric Portal automation (if available)
- Users run after deployment completes

### Option 4: Wait for API
- Monitor Fabric REST API updates
- Implement when folder assignment becomes available
- Folders API needs to move from PREVIEW to GA

## Recommendation

**For Now**:
1. ✅ Keep folder creation (provides structure)
2. ✅ Document intended organization clearly
3. ✅ Use naming conventions to indicate placement
4. ✅ Require manual Portal organization

**Future**:
- Monitor Microsoft Fabric roadmap
- Implement programmatic placement when API available
- Update scripts when Folders API reaches GA

## References

- **Microsoft Fabric Folders API**: https://learn.microsoft.com/en-us/rest/api/fabric/core/folders/
- **Microsoft Fabric Items API**: https://learn.microsoft.com/en-us/rest/api/fabric/core/items/
- **Fabric REST API Status**: PREVIEW (as of October 2025)

---

**Conclusion**: The limitation is on Microsoft's side, not our implementation. Folders can be created but items cannot be placed programmatically. Users must organize manually via the Fabric Portal UI until the API is enhanced.
