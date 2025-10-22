# LEIT-Ricoh Fresh Setup

Fresh variant of the LEIT-Ricoh workspace setup with additional configurations and enhanced features.

## 📋 What This Creates

This is an enhanced version of the LEIT-Ricoh setup with:
- Fresh workspace configuration
- Updated item definitions
- Enhanced error handling
- Additional validation steps

## 🚀 Usage

```bash
python3 leit_ricoh_fresh_setup.py
```

## 📁 Files

- `leit_ricoh_fresh_setup.py` - Main setup script

## 🔧 Configuration

Edit the script to customize:
- Workspace name and domain
- Items to create
- User assignments
- Environment settings (dev/test/prod)

## 📊 Output

The script provides:
- Console progress updates
- JSON log file in `../../.onboarding_logs/`
- Setup summary report

## 🔍 Verification

```bash
# Verify workspace
python3 ../../ops/scripts/manage_workspaces.py get --name leit-ricoh

# List items
python3 ../../ops/scripts/manage_fabric_items.py list --workspace leit-ricoh
```

## 📌 Differences from Standard Setup

This "fresh" variant includes:
- Updated configurations
- Enhanced validation
- Additional error handling
- Refined item definitions

See `leit_ricoh_fresh_setup.py` for specific implementation details.

## 📚 See Also

- [Standard LEIT-Ricoh Setup](../leit-ricoh-setup/)
- [Main Scenarios README](../README.md)
- [Shared Documentation](../shared/)
