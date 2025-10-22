# Config-Driven Workspace Scenario

## Overview

This scenario demonstrates **enterprise config-driven workspace provisioning** using standardized naming patterns defined in `project.config.json`. Unlike direct-name scenarios where you specify exact workspace names, this approach generates workspace names automatically based on organizational naming standards.

## When to Use This Approach

**✅ Use Config-Driven When:**
- Working in enterprise environments with naming standards
- Managing multiple environments (dev/test/prod) consistently
- Need organization-wide governance and compliance
- Want automated, repeatable naming conventions
- Deploying at scale across teams/departments

**❌ Use Direct-Name Instead When:**
- Simple, one-off workspace creation
- Need explicit control over workspace names
- Working in small teams without naming standards
- Quick prototyping or testing
- See: `scenarios/domain-workspace/` or `scenarios/leit-ricoh-setup/`

## How It Works

### 1. Configuration Pattern

The scenario reads naming patterns from `project.config.json`:

```json
{
  "project": {
    "prefix": "usf2-fabric"
  },
  "naming_patterns": {
    "workspace": "{prefix}-{name}-{environment}"
  },
  "environments": {
    "dev": { "description": "Development environment" },
    "test": { "description": "Test/QA environment" },
    "prod": { "description": "Production environment" }
  }
}
```

### 2. Name Generation

When you run:
```bash
python config_driven_workspace.py --project analytics --environment dev
```

The ConfigManager generates:
- **Input:** project=`analytics`, environment=`dev`
- **Pattern:** `{prefix}-{name}-{environment}`
- **Output:** `usf2-fabric-analytics-dev`

### 3. Workspace Creation

The generated name is used to create the workspace with environment-specific settings:
- Auto-deploy enabled/disabled based on environment
- Approval requirements for prod
- Standardized descriptions

## Usage

### Prerequisites

1. **Initialize Configuration** (one-time):
   ```bash
   python setup/init_project_config.py
   ```
   This creates/updates `project.config.json` with your organizational patterns.

2. **Environment Variables** (always required):
   ```bash
   # Set in .env file
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=your-client-id
   AZURE_CLIENT_SECRET=your-secret
   ```

### Basic Usage

```bash
# Create dev workspace for analytics project
python scenarios/config-driven-workspace/config_driven_workspace.py \
  --project analytics \
  --environment dev \
  --skip-user-prompt

# Create test workspace for sales project
python scenarios/config-driven-workspace/config_driven_workspace.py \
  --project sales \
  --environment test
```

### With Principals File

```bash
# Use existing principals file
python scenarios/config-driven-workspace/config_driven_workspace.py \
  --project finance \
  --environment prod \
  --principals-file config/finance_prod_principals.txt
```

## Command-Line Arguments

| Argument | Required | Description | Example |
|----------|----------|-------------|---------|
| `--project` | Yes | Project/domain name | `analytics`, `sales`, `finance` |
| `--environment` | Yes | Target environment | `dev`, `test`, `prod` |
| `--principals-file` | No | Path to principals file | `config/custom_principals.txt` |
| `--skip-user-prompt` | No | Skip interactive prompts | Flag only |

## Generated Names

### Examples

| Project | Environment | Generated Workspace Name |
|---------|-------------|-------------------------|
| analytics | dev | `usf2-fabric-analytics-dev` |
| analytics | test | `usf2-fabric-analytics-test` |
| analytics | prod | `usf2-fabric-analytics-prod` |
| sales | dev | `usf2-fabric-sales-dev` |
| finance | prod | `usf2-fabric-finance-prod` |

### Lakehouse Names

Lakehouse names follow the pattern in config (CamelCase with underscores):
- Dev: `USF2_FABRIC_Lakehouse_Dev`
- Test: `USF2_FABRIC_Lakehouse_Test`
- Prod: `USF2_FABRIC_Lakehouse_Prod`

## What Gets Created

1. **Workspace** - Generated name with environment settings
2. **Lakehouse** - Config-driven name (if capacity available)
3. **Principals Template** - `{project}_{environment}_principals.txt`
4. **Setup Log** - `{project}_{environment}_setup_log.json`

## Comparison: Config-Driven vs Direct-Name

### Config-Driven (This Scenario)
```bash
# You provide: project + environment
python config_driven_workspace.py --project analytics --environment dev

# System generates: usf2-fabric-analytics-dev
```

**Pros:**
- Enforces naming standards
- Consistent across teams
- Easy to manage multiple environments
- Governance-friendly

**Cons:**
- Requires config setup
- Less flexible naming
- More complex for simple use cases

### Direct-Name (Other Scenarios)
```bash
# You provide: exact workspace name
python domain_workspace_with_existing_items.py --workspace-name "my-analytics-workspace"

# System uses: my-analytics-workspace
```

**Pros:**
- Simple and direct
- Full naming control
- No config required
- Quick for one-offs

**Cons:**
- Manual naming can be inconsistent
- Hard to enforce standards
- More prone to naming conflicts

## Workflow Steps

The scenario executes 4 automated steps:

### Step 1: Create Workspace
- Generates workspace name from config pattern
- Applies environment-specific settings
- Creates workspace via Fabric API

### Step 2: Create Items
- Generates lakehouse name from config
- Attempts to create lakehouse (gracefully handles licensing limits)
- Optionally creates warehouse (commented out by default)

### Step 3: Configure Principals
- Creates or uses principals file
- Prompts to add users/groups (unless `--skip-user-prompt`)
- Assigns workspace roles

### Step 4: Save Setup Log
- Records workspace details
- Saves configuration used
- Creates timestamped JSON log

## Files Created

```
config/
├── {project}_{environment}_principals.txt   # Principal assignments template

scenarios/config-driven-workspace/
└── {project}_{environment}_setup_log.json   # Execution log with details
```

## Example Output

```
======================================================================
  Config-Driven Workspace Provisioning
======================================================================

📋 Configuration:
   Project Name:    analytics
   Environment:     dev
   Workspace Name:  usf2-fabric-analytics-dev (generated from config)
   Config Prefix:   usf2-fabric
   Naming Pattern:  {prefix}-{name}-{environment}

======================================================================

STEP 1: Creating Workspace (Config-Driven)
✓ Workspace created successfully
  Workspace ID: abc-123-def
  Display Name: usf2-fabric-analytics-dev

STEP 2: Creating Fabric Items
ℹ Creating lakehouse: USF2_FABRIC_Lakehouse_Dev
⚠️ Lakehouse creation skipped (requires Fabric capacity)

STEP 3: Configuring Workspace Principals
📝 Creating principals template
⏩ Skipping user prompt (automation mode)

STEP 4: Saving Setup Log
✓ Log saved to: analytics_dev_setup_log.json

======================================================================
  ✅ Setup Complete!
======================================================================
```

## Troubleshooting

### "project.config.json not found"
Initialize the config file:
```bash
python setup/init_project_config.py
```

### "Workspace name already exists"
The workspace with generated name already exists. Either:
- Use a different project name
- Use a different environment
- Delete the existing workspace first

### "FeatureNotAvailable" (Lakehouse creation)
Lakehouse/Warehouse creation requires Fabric capacity or premium workspace. The scenario handles this gracefully and continues with workspace creation.

### "Invalid choice for environment"
Only `dev`, `test`, `prod` are configured by default. To add more environments, edit `project.config.json`:
```json
"environments": {
  "dev": {...},
  "test": {...},
  "prod": {...},
  "staging": {
    "description": "Staging environment",
    "requires_approval": true,
    "auto_deploy": false
  }
}
```

## Best Practices

1. **Initialize Config Once**: Run `init_project_config.py` at project start
2. **Use Consistent Project Names**: Stick to lowercase, no spaces (e.g., `analytics`, `sales-ops`)
3. **Follow Environment Progression**: dev → test → prod
4. **Automate with CI/CD**: Use `--skip-user-prompt` in pipelines
5. **Version Control Configs**: Commit `project.config.json` to git

## Related Documentation

- **Setup Guide**: `setup/README.md` - Initialize `project.config.json`
- **Direct-Name Scenarios**: `scenarios/domain-workspace/` - Alternative approach
- **Main README**: `README.md` - Full project documentation
- **Config Manager**: `ops/scripts/utilities/config_manager.py` - Implementation details

## Support

For issues or questions:
1. Check `project.config.json` is properly configured
2. Verify `.env` has correct Azure credentials
3. Review `setup/README.md` for initialization steps
4. See main `README.md` for general troubleshooting
