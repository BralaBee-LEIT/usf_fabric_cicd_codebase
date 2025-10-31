# Comprehensive Demo - Quick Reference

**⚡ Fast access guide for common operations**

---

## 🚀 Quick Commands

```bash
# Preview deployment (safe - no changes)
python run_comprehensive_demo.py --dry-run

# Deploy to development
python run_comprehensive_demo.py

# Deploy to production
python run_comprehensive_demo.py --environment prod

# Use custom config
python run_comprehensive_demo.py --config my_config.yaml

# Test without folders
python run_comprehensive_demo.py --skip-folders
```

---

## 📁 File Quick Reference

| File | Purpose | Lines | Use When |
|------|---------|-------|----------|
| `comprehensive_demo_config.yaml` | Full-featured config | 440 | Production, client demos |
| `example_basic_medallion.yaml` | Simple 3-layer setup | 100 | Learning, quick tests |
| `example_ml_lifecycle.yaml` | ML/data science | 180 | ML projects |
| `example_multi_tenant.yaml` | Departmental | 280 | Multi-tenant workspaces |

---

## 🎯 Folder Organization Patterns

### Medallion Architecture
```
🥉 Bronze Layer/       # Raw data
  ├── Source Systems/
  └── Staging/
🥈 Silver Layer/       # Cleansed data
  ├── Core Entities/
  └── Transformations/
🥇 Gold Layer/         # Analytics ready
  ├── Analytics/
  └── Machine Learning/
```

### Pattern Rules (Auto-Organization)
```yaml
BRONZE_* → 🥉 Bronze Layer
SILVER_* → 🥈 Silver Layer
GOLD_*   → 🥇 Gold Layer
01-03_*Ingest* → Bronze/Source Systems
04-06_*Transform* → Silver/Transformations
07-09_*Analytics* → Gold/Analytics
Pipeline_* → Orchestration
Utility_* → Utilities
```

---

## ⚙️ Configuration Essentials

### Minimal Config
```yaml
product:
  name: "My Product"
  owner_email: "me@company.com"

environments:
  dev:
    enabled: true
    capacity_type: "trial"
    folder_structure:
      enabled: true
      template: "medallion"

folder_structure:
  template: "medallion"
  organization:
    auto_organize: true

items:
  lakehouses:
    - name: "BRONZE_Data_Lakehouse"
    - name: "SILVER_Data_Lakehouse"
    - name: "GOLD_Analytics_Lakehouse"
```

### Feature Flags
```yaml
features:
  enable_folders: true              # Folder creation
  enable_git: true                  # Git integration
  enable_naming_validation: true    # Naming standards
  enable_user_management: true      # User addition
  enable_audit_logging: true        # Audit trail
  enable_auto_organization: true    # Pattern-based placement
```

---

## 🔍 Common Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| `FabricFolderManager not available` | Merge feature/folder-api-implementation |
| `Authentication failed` | Check `.env` file credentials |
| `Capacity not found` | Use `capacity_type: "trial"` for testing |
| Items not auto-organized | Verify `auto_organize: true` and patterns |
| Git connection fails | Check org/repo names and permissions |

---

## 📊 Deployment Workflow Steps

1. **Load Configuration** → Parse YAML
2. **Create Workspace** → Basic workspace setup
3. **Create Folders** → Build folder structure
4. **Create Items** → Lakehouses, notebooks (auto-placed)
5. **Connect Git** → Repository integration
6. **Add Users** → Role-based access
7. **Validate** → Naming + deployment checks

---

## 🎓 Learning Path

### Beginner (30 min)
1. Run dry-run: `--dry-run`
2. Deploy basic: `--config example_basic_medallion.yaml`
3. Explore workspace in Fabric UI

### Intermediate (2 hours)
1. Customize config
2. Add your naming patterns
3. Test with `--dry-run`
4. Deploy to dev

### Advanced (1 day)
1. Create custom template
2. Add CI/CD integration
3. Set up service principals
4. Deploy to production

---

## 📈 Metrics at a Glance

| Metric | Value |
|--------|-------|
| **Total Files** | 6 |
| **Total Lines** | 2,700+ |
| **Configuration Options** | 50+ |
| **Folder Templates** | 4 |
| **Example Configs** | 3 |
| **Features Demonstrated** | 8 |

---

## 🔗 Quick Links

- [Full Documentation](./README.md)
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md)
- [Folder Management Guide](../../docs/workspace-management/FOLDER_MANAGEMENT_GUIDE.md)
- [Main Scenarios README](../README.md)

---

## 💡 Pro Tips

1. **Always dry-run first**: `--dry-run` prevents mistakes
2. **Use comments**: YAML configs support `#` comments
3. **Start simple**: Use `example_basic_medallion.yaml` first
4. **Pattern testing**: Add `description` to rules for clarity
5. **Version control**: Commit configs to git
6. **Naming consistency**: Follow patterns for auto-organization
7. **Feature flags**: Disable features you don't need
8. **Audit logs**: Keep for compliance and debugging

---

## 🎯 Use Cases

| Use Case | Config | Command |
|----------|--------|---------|
| **Client Demo** | `comprehensive_demo_config.yaml` | `--dry-run` |
| **Learning** | `example_basic_medallion.yaml` | Default |
| **ML Project** | `example_ml_lifecycle.yaml` | Default |
| **Enterprise** | `example_multi_tenant.yaml` | `--environment prod` |
| **Testing** | Any config | `--dry-run --skip-folders` |

---

**Last Updated**: 2025-01-XX  
**Version**: 2.0
