# Setup Scripts

Modularized setup scripts for Microsoft Fabric CI/CD solution.

## Overview

The setup process has been broken down into focused, single-purpose scripts for easier maintenance and debugging.

## Scripts

### Main Script

**`setup.sh`** - Main orchestrator that runs all checks  
```bash
./setup.sh              # Full setup with dependency installation
./setup.sh --skip-deps  # Skip dependency installation
```

### Individual Check Scripts

**`scripts/check_environment.sh`** - Validates Python, pip, git, docker  
```bash
./scripts/check_environment.sh
```

**`scripts/check_structure.sh`** - Validates directory and file structure  
```bash
./scripts/check_structure.sh
```

**`scripts/check_config.sh`** - Validates configuration files (.env, project.config.json)  
```bash
./scripts/check_config.sh
```

**`scripts/validate_yaml.sh`** - Validates YAML syntax for data contracts and DQ rules  
```bash
./scripts/validate_yaml.sh
```

### Utility Script

**`scripts/setup_utils.sh`** - Shared functions (colors, print helpers)  
- Sourced by other scripts
- Not meant to be run directly

## Usage Examples

### Quick Check (No Dependencies)
```bash
# Just check environment and structure
./scripts/check_environment.sh
./scripts/check_structure.sh
```

### Full Setup
```bash
# Run all checks and install dependencies
./setup.sh
```

### Configuration Only
```bash
# Check if configuration is correct
./scripts/check_config.sh
```

### YAML Validation Only
```bash
# Validate all YAML files
./scripts/validate_yaml.sh
```

## Benefits of Modular Approach

✅ **Focused** - Each script does one thing well  
✅ **Debuggable** - Easy to isolate and fix issues  
✅ **Reusable** - Can run individual checks as needed  
✅ **Maintainable** - Changes are localized to specific scripts  
✅ **Fast** - Skip unnecessary checks with individual scripts  
✅ **Clear** - Each script has a single, obvious purpose  

## Script Dependencies

```
setup.sh (main)
├── scripts/setup_utils.sh (sourced)
├── scripts/check_environment.sh
├── scripts/check_structure.sh  
├── scripts/check_config.sh
└── scripts/validate_yaml.sh
```

## Exit Codes

- `0` - Success
- `1` - Failure (specific error messages printed)

## Adding New Checks

1. Create new script in `scripts/` directory
2. Source `setup_utils.sh` for consistent output
3. Add call to `setup.sh` main orchestrator
4. Make executable: `chmod +x scripts/your_new_check.sh`
5. Update this README

## Comparison with quick_setup.sh

**Old (`quick_setup.sh`):**
- Single monolithic script
- 200+ lines
- Hard to maintain
- All-or-nothing execution

**New (Modular):**
- 5 focused scripts
- 30-80 lines each
- Easy to maintain
- Run individual checks
- Shared utilities

## Migration

The old `quick_setup.sh` is still available but the new modular approach is recommended:

```bash
# Old way
./quick_setup.sh

# New way
./setup.sh
```
