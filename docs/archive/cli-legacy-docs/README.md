# CLI Legacy Documentation Archive

**Archive Date:** October 28, 2025  
**Reason:** Replaced by Enhanced CLI v2.0

---

## 📦 Archived Documents

This directory contains **legacy CLI documentation** that has been superseded by the Enhanced CLI v2.0.

### Files in This Archive

| File | Original Purpose | Replaced By |
|------|------------------|-------------|
| `FABRIC_CLI_QUICKREF_OLD.md` | CLI quick reference (basic workspace ops only) | [`../fabric-items-crud/FABRIC_CLI_QUICKREF.md`](../fabric-items-crud/FABRIC_CLI_QUICKREF.md) |
| `CLI_PATH_UPDATE_SUMMARY.md` | CLI path correction documentation | Integrated into CLI_ENHANCEMENT_SUMMARY.md |

---

## 🚀 Use Current Documentation Instead

**DO NOT USE** these archived documents for new work. They reference the old CLI that only exposed 21% of framework functionality.

### Current CLI Documentation (Use These!)

1. **Quick Reference** → [`docs/fabric-items-crud/FABRIC_CLI_QUICKREF.md`](../fabric-items-crud/FABRIC_CLI_QUICKREF.md)
   - Comprehensive guide to all 37+ commands
   - 10 categories with examples
   - Common workflows and troubleshooting

2. **Enhancement Summary** → [`CLI_ENHANCEMENT_SUMMARY.md`](../../CLI_ENHANCEMENT_SUMMARY.md)
   - Why the CLI was enhanced
   - Coverage comparison (21% → 100%)
   - Migration path and benefits

3. **Testing Report** → [`CLI_COMPREHENSIVE_TESTING.md`](../../CLI_COMPREHENSIVE_TESTING.md)
   - Complete test results for all commands
   - Issues found and fixed
   - Environment requirements

---

## 📊 What Changed

### Old CLI (Archived)
```bash
# Location: ./tools/fabric-cli.sh
# Coverage: 21% (3 of 14 scripts)
# Commands: ~10 commands (workspace & user management only)
```

**Limitations:**
- ❌ No data product onboarding
- ❌ No Fabric items management
- ❌ No Git integration
- ❌ No deployment commands
- ❌ No health checks
- ❌ No data quality tools
- ❌ No Power BI deployment
- ❌ No Purview integration

### Enhanced CLI v2.0 (Current)
```bash
# Location: ./tools/fabric-cli-enhanced.sh
# Coverage: 100% (14 of 14 scripts)
# Commands: 37+ commands across 10 categories
```

**Features:**
- ✅ Complete workspace & user management
- ✅ Data product onboarding (YAML-driven)
- ✅ Fabric items CRUD (Lakehouses, Notebooks, Pipelines)
- ✅ Git integration (GitHub, AzureDevOps)
- ✅ Deployment (bundle, Git, validation)
- ✅ Health monitoring
- ✅ Data quality & governance
- ✅ Power BI deployment
- ✅ Purview integration
- ✅ Organized help system

---

## ⚠️ Migration Note

If you have scripts or documentation referencing the old CLI:

### Update References

**Old:**
```bash
./tools/fabric-cli.sh ls
python ops/scripts/onboard_data_product.py descriptor.yaml
python ops/scripts/manage_fabric_items.py list --workspace dev-ws
```

**New:**
```bash
./tools/fabric-cli-enhanced.sh ls
./tools/fabric-cli-enhanced.sh onboard descriptor.yaml
./tools/fabric-cli-enhanced.sh items list --workspace dev-ws
```

### Old CLI Still Available

The old CLI (`./tools/fabric-cli.sh`) is still available for backward compatibility, but it's recommended to migrate to the enhanced version for access to all framework features.

---

## 📚 Related Archive Sections

Other archived documentation can be found in:
- [`docs/archive/`](../) - General archived docs
- [`docs/archive/bulk functionalities documentation/`](../bulk%20functionalities%20documentation/) - Bulk operations
- [`docs/archive/new_org_and_requirements/`](../new_org_and_requirements/) - Organization setup

---

**Archive Maintained By:** GitHub Copilot  
**Last Updated:** October 28, 2025  
**Status:** Read-only archive - DO NOT UPDATE
