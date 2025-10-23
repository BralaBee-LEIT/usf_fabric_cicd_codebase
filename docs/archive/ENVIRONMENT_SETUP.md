# Environment Configuration Guide

## Quick Setup

### Option 1: Using Conda (Recommended)
```bash
# Create and activate conda environment
conda env create -f environment.yml
conda activate fabric-cicd

# Copy environment template
cp .env.example .env

# Edit with your values
nano .env

# Run setup validation
./setup.sh
```

### Option 2: Using Python venv
```bash
# Create and activate virtual environment
python3 -m venv fabric-cicd-env
source fabric-cicd-env/bin/activate  # On Windows: fabric-cicd-env\Scripts\activate

# Copy environment template  
cp .env.example .env

# Edit with your values
nano .env

# Run setup validation
./setup.sh
```

### Option 3: Global Installation (Not Recommended)
```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env

# Run setup (will prompt about virtual environment)
./setup.sh
```

## Required Environment Variables

### Azure Authentication (Required)
```bash
AZURE_CLIENT_ID=your-service-principal-client-id
AZURE_CLIENT_SECRET=your-service-principal-secret  
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_SUBSCRIPTION_ID=your-azure-subscription-id
```

### GitHub Integration (Required for CI/CD)
```bash
GITHUB_TOKEN=ghp_your-github-personal-access-token
GITHUB_ORGANIZATION=your-github-org
GITHUB_REPOSITORY=your-repo-name
```

### Data Governance (Optional)
```bash
DATA_OWNER_EMAIL=data-owner@your-company.com
TECHNICAL_LEAD_EMAIL=tech-lead@your-company.com
DATA_ENGINEERING_EMAIL=data-engineering@your-company.com
```

## Azure Service Principal Setup

### 1. Create Service Principal
```bash
az ad sp create-for-rbac --name "fabric-cicd-sp" --role contributor
```

### 2. Grant Fabric Permissions
The service principal needs:
- **Fabric Administrator** role in Fabric tenant
- **Contributor** role on Azure subscription
- **Storage Blob Data Contributor** (if using Azure Storage)

### 3. Get Required Values
```bash
# Client ID and Secret from step 1 output
# Tenant ID
az account show --query tenantId -o tsv

# Subscription ID  
az account show --query id -o tsv
```

## GitHub Token Setup

### 1. Create Personal Access Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `read:org` (Read org and team membership)

### 2. Add to Repository Secrets
Add these secrets to your GitHub repository:
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`  
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`
- `FABRIC_DEPLOYMENT_PIPELINE_ID` (optional)

## Fabric Workspace Setup

### 1. Create Workspaces
Create workspaces following your naming pattern:
- `{prefix}-fabric-dev`
- `{prefix}-fabric-test`  
- `{prefix}-fabric-prod`

### 2. Configure Git Integration
For each workspace:
1. Go to Workspace settings → Git integration
2. Connect to your GitHub repository
3. Set branch mapping (main → prod, develop → test, feature → dev)

### 3. Create Deployment Pipeline (Optional)
1. In Fabric portal, go to Deployment pipelines
2. Create new pipeline with 3 stages: Development → Test → Production
3. Assign your workspaces to each stage
4. Copy the pipeline ID to `FABRIC_DEPLOYMENT_PIPELINE_ID`

## Validation

### Test Configuration
```bash
# Run setup script
./setup.sh

# Test Azure connection
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# Test Fabric API access
python -c "
from ops.scripts.utilities.fabric_api import FabricClient
client = FabricClient()
workspaces = client.list_workspaces()
print(f'✅ Found {len(workspaces)} workspaces')
"
```

### Verify GitHub Integration
```bash
# Test GitHub token
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user

# Check repository access
gh repo view $GITHUB_ORGANIZATION/$GITHUB_REPOSITORY
```

## Security Best Practices

### 1. Use Azure Key Vault (Production)
```bash
# Store secrets in Key Vault
az keyvault secret set --vault-name your-keyvault \
  --name "fabric-client-secret" \
  --value "$AZURE_CLIENT_SECRET"

# Reference in CI/CD
AZURE_CLIENT_SECRET=$(az keyvault secret show \
  --vault-name your-keyvault \
  --name "fabric-client-secret" \
  --query value -o tsv)
```

### 2. Rotate Credentials Regularly
- Service principal secrets: Every 90 days
- GitHub tokens: Every 12 months
- Review access permissions quarterly

### 3. Monitor Usage
- Enable Azure AD sign-in logs for service principal
- Monitor GitHub token usage in organization audit logs
- Set up alerts for unusual authentication patterns

## Troubleshooting

### Common Issues

#### "Authentication failed" 
- Verify service principal credentials are correct
- Check if service principal has required permissions
- Ensure tenant ID matches the subscription

#### "Workspace not found"
- Verify workspace names match your naming pattern
- Check if service principal has access to Fabric workspaces
- Confirm workspace exists in correct Fabric tenant

#### "GitHub API rate limit"
- Use authenticated requests with GitHub token
- Check token permissions and expiration
- Consider using GitHub App instead of personal token

### Debug Commands
```bash
# Test Azure login
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# Test Fabric workspace access  
python ops/scripts/utilities/fabric_api.py --test

# Validate all configuration
python -c "
from ops.scripts.utilities.config_manager import ConfigManager
config = ConfigManager()
config.validate_all_environments()
"
```

## Next Steps

After environment setup:

1. **Initialize project configuration**
   ```bash
   python init_project_config.py
   ```

2. **Test deployment**
   ```bash
   python ops/scripts/deploy_fabric.py --environment dev --mode standard
   ```

3. **Set up CI/CD**
   ```bash
   git add .
   git commit -m "Initial Fabric CI/CD setup"
   git push origin main
   ```

For detailed implementation guide, see: `FABRIC_CICD_IMPLEMENTATION_GUIDE.md`