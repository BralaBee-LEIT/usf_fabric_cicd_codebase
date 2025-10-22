# Shared Scenario Documentation

This directory contains documentation applicable to all workspace setup scenarios.

## 📁 Contents

### Architecture & Planning
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Overall architecture patterns and design principles
- **[SCENARIO_SUMMARY.md](SCENARIO_SUMMARY.md)** - Summary of all available scenarios

### Setup Guides
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide for getting started
- **[CAPACITY_ASSIGNMENT_GUIDE.md](CAPACITY_ASSIGNMENT_GUIDE.md)** - Capacity management and assignment
- **[USER_ADDITION_GUIDE.md](USER_ADDITION_GUIDE.md)** - User and group management best practices

### Technical Guides
- **[CORE_BULK_ADDITION.md](CORE_BULK_ADDITION.md)** - Bulk user addition patterns
- **[GROUP_SUPPORT_QUICKREF.md](GROUP_SUPPORT_QUICKREF.md)** - Azure AD group support reference
- **[GROUP_SUPPORT_SUMMARY.md](GROUP_SUPPORT_SUMMARY.md)** - Group management summary
- **[ITEM_CREATION_FIXES.md](ITEM_CREATION_FIXES.md)** - Common item creation issues and fixes

## 🎯 When to Use This Documentation

Use shared documentation when:
- Starting a new scenario
- Understanding common patterns
- Troubleshooting cross-scenario issues
- Learning best practices
- Setting up user management
- Configuring capacity assignments

## 📚 Scenario-Specific Docs

For scenario-specific information, see:
- [domain-workspace/](../domain-workspace/) - Domain workspace scenario docs
- [leit-ricoh-setup/](../leit-ricoh-setup/) - LEIT-Ricoh setup docs
- [leit-ricoh-fresh-setup/](../leit-ricoh-fresh-setup/) - Fresh setup variant docs

## 🔗 Related Documentation

- [Main Scenarios README](../README.md) - Overview of all scenarios
- [Core Documentation](../../docs/) - Platform-wide documentation
- [Workspace Management](../../docs/workspace-management/) - Workspace management guides
- [Fabric Items CRUD](../../docs/fabric-items-crud/) - Item management guides

## 💡 Best Practices

Key principles from shared documentation:

1. **Environment Separation** - Use different workspaces for dev/test/prod
2. **Naming Conventions** - Follow CamelCase for Fabric items
3. **User Management** - Use Azure AD Object IDs (GUIDs), not emails
4. **Capacity Planning** - Assign appropriate capacity to workspaces
5. **Version Control** - Keep scenarios and configs in git

## 🤝 Contributing

When adding shared documentation:
1. Ensure it applies to multiple scenarios (not scenario-specific)
2. Use clear, concise titles
3. Include practical examples
4. Cross-reference related docs
5. Update this README

---

**Last Updated:** October 22, 2025
