# Workspace Verification Guide

**Date:** 21 October 2025  
**Status:** ✅ Workspaces Created Successfully

---

## 🎯 Your Microsoft Fabric Workspaces

You have **TWO** workspaces successfully created:

### 1. Customer Analytics [DEV]
- **Workspace ID:** `be8d1df8-9067-4557-a179-fd706a38dd20`
- **Portal URL:** https://app.fabric.microsoft.com/groups/be8d1df8-9067-4557-a179-fd706a38dd20
- **Created:** 21 October 2025, 13:35:02 UTC
- **Status:** ✅ **EXISTS** (confirmed by re-run)
- **Folder:** `data_products/customer_analytics/`
- **Audit Log:** `.onboarding_logs/20251021T123502Z_customer_analytics.json`

### 2. Sales Analytics [DEV]
- **Workspace ID:** `f6f36e51-99e7-424e-aba6-1aa70b92d4e2`
- **Portal URL:** https://app.fabric.microsoft.com/groups/f6f36e51-99e7-424e-aba6-1aa70b92d4e2
- **Created:** 21 October 2025, 13:47:14 UTC
- **Status:** ✅ **JUST CREATED**
- **Folder:** `data_products/sales_analytics/`
- **Audit Log:** `.onboarding_logs/20251021T124714Z_sales_analytics.json`

---

## 🔍 How to View in Microsoft Fabric Portal

### Option 1: Direct Links (Fastest)

**Customer Analytics:**
```
https://app.fabric.microsoft.com/groups/be8d1df8-9067-4557-a179-fd706a38dd20
```

**Sales Analytics:**
```
https://app.fabric.microsoft.com/groups/f6f36e51-99e7-424e-aba6-1aa70b92d4e2
```

### Option 2: Navigate in Portal

1. **Open Fabric portal:**
   ```
   https://app.fabric.microsoft.com
   ```

2. **Click on "Workspaces"** (left sidebar or top menu)

3. **Look for:**
   - `Customer Analytics [DEV]`
   - `Sales Analytics [DEV]`

4. **If not visible immediately:**
   - Use search box: type "Customer Analytics" or "Sales Analytics"
   - Check workspace filters (might be filtered by type/capacity)
   - Ensure you're viewing "All workspaces" not just "My workspaces"

---

## 🚨 Troubleshooting: "I Don't See Them"

### Possible Reasons & Solutions

#### 1. **Portal Cache Issue**
**Solution:** Hard refresh the browser
```
- Windows/Linux: Ctrl + F5
- Mac: Cmd + Shift + R
```

#### 2. **Viewing Different Tenant**
**Check:** Are you logged into the correct Microsoft account?
- Top-right corner of portal → verify your email
- Should match the tenant used by your Azure credentials

#### 3. **Permission Issue**
**Check:** Do you have permission to see these workspaces?
- Workspaces are visible to their members
- Service principal that created them may not be your user account
- Try adding yourself as a user (see below)

#### 4. **Workspace Filter Active**
**Check:** Workspace list filters
- Remove any active filters
- Select "All workspaces" view
- Check capacity filter is set to "All"

#### 5. **Browser Issue**
**Try:**
- Different browser (Chrome, Edge, Firefox)
- Incognito/Private window
- Clear browser cache and cookies

---

## 👤 Add Yourself as Workspace User

If you can't see the workspace, add your user account:

```bash
# Get workspace ID from registry or audit log
CUSTOMER_WS_ID="be8d1df8-9067-4557-a179-fd706a38dd20"
SALES_WS_ID="f6f36e51-99e7-424e-aba6-1aa70b92d4e2"

# Add yourself as Admin (replace with your email)
YOUR_EMAIL="your.email@company.com"

# Add to Customer Analytics
python3 ops/scripts/manage_workspaces.py add-user "$CUSTOMER_WS_ID" \
  "$YOUR_EMAIL" --role Admin

# Add to Sales Analytics
python3 ops/scripts/manage_workspaces.py add-user "$SALES_WS_ID" \
  "$YOUR_EMAIL" --role Admin
```

**Note:** This requires the .env to be loaded. Run from the repo directory.

---

## ✅ Verification Commands

### Check Registry (Local Proof)
```bash
cat data_products/registry.json | python3 -m json.tool
```

You should see both products listed with their workspace IDs.

### Check Audit Logs (What Happened)
```bash
# Customer Analytics
cat .onboarding_logs/20251021T123502Z_customer_analytics.json | python3 -m json.tool

# Sales Analytics
cat .onboarding_logs/20251021T124714Z_sales_analytics.json | python3 -m json.tool
```

### List All Workspaces (API Call)
```bash
# Create a simple test script
python3 ops/scripts/onboard_data_product.py \
  data_products/onboarding/customer_analytics.yaml \
  --dry-run 2>&1 | grep "Found.*workspaces"
```

This will show: `Found X workspaces` where X is the count.

---

## 📊 What Was Created

### Customer Analytics
```
✅ Workspace: Customer Analytics [DEV]
✅ Folder structure:
   data_products/customer_analytics/
   ├── workspace/
   ├── notebooks/
   ├── pipelines/
   ├── datasets/
   ├── docs/
   └── README.md
```

### Sales Analytics
```
✅ Workspace: Sales Analytics [DEV]
✅ Folder structure:
   data_products/sales_analytics/
   ├── workspace/
   ├── notebooks/
   ├── pipelines/
   ├── datasets/
   ├── docs/
   └── README.md
```

---

## 🎯 Next Steps: Add Items to Workspaces

### Create Lakehouse in Customer Analytics

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Customer Analytics [DEV]" \
  --name "CustomerDataLakehouse" \
  --type Lakehouse \
  --description "Main customer data storage"
```

### Create Notebook in Sales Analytics

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Sales Analytics [DEV]" \
  --name "SalesETLNotebook" \
  --type Notebook \
  --description "Sales data ETL processing"
```

### Create Pipeline in Customer Analytics

```bash
python3 ops/scripts/manage_fabric_items.py create \
  --workspace "Customer Analytics [DEV]" \
  --name "DailyCustomerPipeline" \
  --type DataPipeline \
  --description "Daily customer data ingestion"
```

---

## 🔗 Portal URLs (Quick Access)

**Customer Analytics [DEV]:**
https://app.fabric.microsoft.com/groups/be8d1df8-9067-4557-a179-fd706a38dd20

**Sales Analytics [DEV]:**
https://app.fabric.microsoft.com/groups/f6f36e51-99e7-424e-aba6-1aa70b92d4e2

**Main Fabric Portal:**
https://app.fabric.microsoft.com

---

## 📝 Confirmation

✅ **Customer Analytics [DEV]** - Workspace exists (confirmed by "already exists" message)  
✅ **Sales Analytics [DEV]** - Workspace just created (ID: f6f36e51-99e7-424e-aba6-1aa70b92d4e2)  
✅ **Folder structures** - Both created with template scaffolding  
✅ **Audit logs** - Both operations logged  
✅ **Registry** - Both products tracked  

**Status: READY FOR USE! 🚀**

---

*Generated: 21 October 2025*  
*Workspaces: 2 active*  
*Next: Add items and users to workspaces*
