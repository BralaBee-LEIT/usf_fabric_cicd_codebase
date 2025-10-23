# Microsoft Fabric CI/CD Framework - Configuration Guide

## Overview

This framework now supports **multi-project deployment** through a configurable system that eliminates hardcoded values. Each project can define its own naming conventions, resource patterns, and environment configurations.

## Quick Start

### 1. Initialize Your Project Configuration

```bash
# Run the interactive setup wizard
python init_project_config.py
```

This will create:
- `project.config.json` - Main project configuration
- `.env.example` - Template for environment variables
- Updated environment files in `ops/config/`

### 2. Set Up Environment Variables

```bash
# Copy and customize environment variables
cp .env.example .env
# Edit .env with your specific values
```

### 3. Validate Configuration

```bash
# Test the configuration
python -m ops.scripts.utilities.config_manager

# Validate specific environment
python -m ops.scripts.utilities.environment_config dev
```

## Configuration Structure

### Project Configuration (`project.config.json`)

```json
{
  "project": {
    "name": "your-project-name",
    "prefix": "your-prefix",
    "organization": "your-org"
  },
  "naming_patterns": {
    "workspace": "{prefix}-fabric-{environment}",
    "lakehouse": "{prefix_upper}_Lakehouse_{environment_title}",
    "storage_account": "{prefix_clean}data{environment}"
  },
  "environments": {
    "dev": { "requires_approval": false },
    "test": { "requires_approval": true },
    "prod": { "requires_approval": true }
  }
}
```

### Naming Pattern Variables

- `{prefix}` - Project prefix (e.g., "myproject")
- `{prefix_upper}` - Uppercase with underscores (e.g., "MYPROJECT")  
- `{prefix_clean}` - No hyphens (e.g., "myproject")
- `{environment}` - Environment name (dev, test, prod)
- `{environment_title}` - Title case (Dev, Test, Prod)
- `{organization}` - GitHub organization name

## Environment-Specific Configurations

Each environment (`ops/config/{env}.json`) uses template placeholders:

```json
{
  "workspace": {
    "name": "{{workspace}}"
  },
  "data_sources": {
    "lakehouse_name": "{{lakehouse}}",
    "storage_account": "{{storage_account}}"
  },
  "connection_strings": {
    "sql_server": "{{sql_server}}",
    "cosmos_db": "{{cosmos_db}}"
  }
}
```

## Usage Examples

### Using ConfigManager in Scripts

```python
from ops.scripts.utilities.config_manager import get_config_manager

# Get configuration manager
config = get_config_manager()

# Generate resource names
workspace_name = config.generate_name("workspace", "dev")
lakehouse_name = config.generate_name("lakehouse", "prod") 

# Get environment config
env_config = config.get_environment_config("test")
```

### Using Environment Configuration

```python
from ops.scripts.utilities.environment_config import EnvironmentConfigManager

# Load environment configuration
env_config = EnvironmentConfigManager("prod")

# Get workspace name
workspace = env_config.get_workspace_name()

# Get connection strings
sql_conn = env_config.get_connection_string("sql_server")
```

### Deployment with Dynamic Configuration

```bash
# Deploy to any environment - workspace name resolved automatically
python ops/scripts/deploy_fabric.py --environment dev

# Sync Git integration - uses configured workspace names
python ops/scripts/sync_fabric_git.py --environment test --action sync

# Health check - dynamic workspace resolution
python ops/scripts/health_check_fabric.py --environment prod
```

## Multi-Project Setup

### Scenario: Multiple Teams/Projects

Each team can have their own configuration:

**Team A (Data Platform):**
```json
{
  "project": {
    "prefix": "dataplatform",
    "organization": "company-data"
  }
}
```
Generates: `dataplatform-fabric-dev`, `DATAPLATFORM_Lakehouse_Dev`

**Team B (Analytics):**
```json
{
  "project": {
    "prefix": "analytics", 
    "organization": "company-analytics"
  }
}
```
Generates: `analytics-fabric-dev`, `ANALYTICS_Lakehouse_Dev`

### Sharing Configuration Across Projects

1. **Fork the Repository** for each project
2. **Run `init_project_config.py`** in each fork
3. **Customize** naming patterns as needed
4. **Deploy independently** using the same CI/CD framework

## Environment Variables

Set these environment variables for each project:

```bash
# Core Azure Configuration
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id  
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Project-specific
GITHUB_ORG=your-github-org
GITHUB_REPO=your-repo-name
DATA_OWNER_EMAIL=data-owner@company.com

# Fabric Capacities (per environment)
FABRIC_CAPACITY_DEV_ID=your-dev-capacity-id
FABRIC_CAPACITY_TEST_ID=your-test-capacity-id
FABRIC_CAPACITY_PROD_ID=your-prod-capacity-id
```

## GitHub Actions Integration

Workflows automatically use the configured naming patterns:

```yaml
- name: Deploy to Environment
  env:
    ENVIRONMENT: ${{ inputs.environment }}
  run: |
    # Workspace name resolved from project configuration
    python ops/scripts/deploy_fabric.py --environment $ENVIRONMENT
```

## Migration from Hardcoded Setup

### Automatic Migration

1. **Run initialization:**
   ```bash
   python init_project_config.py
   ```

2. **Choose your project prefix** (replaces "usf")

3. **Update environment variables** in GitHub/Azure DevOps

4. **Test configuration:**
   ```bash
   python -m ops.scripts.utilities.config_manager
   ```

### Manual Updates Required

- **CODEOWNERS file**: Update GitHub organization references
- **Documentation**: Replace example workspace names
- **Custom scripts**: Update any hardcoded references

## Best Practices

### Naming Conventions

- **Prefix**: 3-15 characters, lowercase, descriptive
- **Environment names**: Use standard dev/test/prod
- **Resource names**: Follow Azure naming conventions

### Security

- **Never commit**: `.env` files or secrets to Git
- **Use variables**: For all environment-specific values
- **Rotate secrets**: Regularly update service principal credentials

### Multi-Environment Strategy

- **Development**: Auto-deploy, minimal validation
- **Test**: Manual approval, full validation  
- **Production**: Strict approval, comprehensive monitoring

## Troubleshooting

### Configuration Issues

```bash
# Validate project configuration
python -c "from ops.scripts.utilities.config_manager import ConfigManager; ConfigManager()"

# Check environment configuration
python ops/scripts/utilities/environment_config.py dev

# List all generated names
python -c "
from ops.scripts.utilities.config_manager import get_config_manager
config = get_config_manager()
for env in ['dev', 'test', 'prod']:
    print(f'{env}: {config.generate_name(\"workspace\", env)}')
"
```

### Common Problems

1. **Missing project.config.json**: Run `init_project_config.py`
2. **Invalid naming patterns**: Check Azure resource naming rules
3. **Environment variables not set**: Review `.env.example`
4. **Permission issues**: Verify service principal permissions

## Support

- **Configuration Issues**: Check `project.config.json` syntax
- **Deployment Problems**: Validate environment variables
- **Naming Conflicts**: Choose unique project prefix
- **GitHub Actions**: Verify repository secrets are set