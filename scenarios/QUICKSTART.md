# LEIT-Ricoh Workspace - Quick Start

## 🚀 One-Command Setup

```bash
python3 scenarios/leit_ricoh_setup.py
```

---

## 📦 What Gets Created

```
leit-ricoh workspace
├── Storage (2)
│   ├── RicohDataLakehouse
│   └── RicohAnalyticsWarehouse
│
├── Processing (3)
│   ├── 01_DataIngestion
│   ├── 02_DataTransformation
│   └── 03_DataValidation
│
└── Analytics (3)
    ├── RicohDataPipeline
    ├── RicohSemanticModel
    └── RicohExecutiveDashboard
```

**Total:** 8 Fabric items in 1 workspace

---

## ✅ Prerequisites Checklist

- [ ] Environment variables set (`AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`)
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Fabric authentication working (`python3 ops/scripts/manage_workspaces.py list`)
- [ ] Sufficient permissions (Workspace Creator role minimum)

---

## 📝 Quick Commands

### Run Setup
```bash
# Full setup
python3 scenarios/leit_ricoh_setup.py

# Or using bash script
./scenarios/leit_ricoh_setup.sh
```

### Verify Setup
```bash
# List all items
python3 ops/scripts/manage_fabric_items.py list --workspace leit-ricoh

# Check workspace
python3 ops/scripts/manage_workspaces.py get --name leit-ricoh
```

### Add Users (After Setup)
```bash
# Update emails in the script first, then run:
python3 ops/scripts/manage_workspaces.py add-user \
  --workspace leit-ricoh \
  --email user@company.com \
  --role Admin
```

---

## 🎯 Expected Output

```
================================================================================
  LEIT-Ricoh Domain - Complete Workspace Setup
================================================================================

✓ Step 1: Creating Workspace - leit-ricoh
✓ Step 2: Creating Lakehouse
✓ Step 3: Creating Warehouse
✓ Step 4: Creating Notebooks (3/3)
✓ Step 5: Creating Additional Items (3/3)
⚠ Step 6: User configuration ready (update emails)
✓ Step 7: Verifying Setup

================================================================================
  SETUP COMPLETE - Summary
================================================================================

✓ Workspace Setup Successful!

📊 Fabric Items Created: 8
📄 Setup log: .onboarding_logs/YYYYMMDDTHHMMSSZ_leit_ricoh_setup.json
🚀 LEIT-Ricoh workspace is ready for use!
```

---

## ⏱️ Estimated Time

- **Setup:** ~2-3 minutes
- **Verification:** ~30 seconds
- **User addition:** ~1 minute per user

**Total:** ~5 minutes for complete setup

---

## 🔗 Next Steps

1. **Configure Data Sources**
   - Connect to source systems
   - Set up data ingestion schedules

2. **Develop Notebooks**
   - Add processing logic to notebooks
   - Test data transformations

3. **Build Pipeline**
   - Configure pipeline activities
   - Set up orchestration

4. **Create Semantic Model**
   - Define relationships
   - Add measures and calculations

5. **Design Dashboard**
   - Build visualizations
   - Configure report parameters

---

## 📞 Need Help?

- **Documentation:** `scenarios/README.md`
- **Troubleshooting:** Enable debug with `export LOG_LEVEL=DEBUG`
- **Support:** Check `docs/` for detailed guides

---

**Quick Ref Version:** 1.0  
**Last Updated:** October 22, 2025
