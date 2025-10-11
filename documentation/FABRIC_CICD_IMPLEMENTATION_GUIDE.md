# Microsoft Fabric CI/CD Architecture Implementation Guide

## Overview

This repository implements a comprehensive CI/CD solution for Microsoft Fabric using GitHub Actions, Fabric Git Integration, and the fabric-cicd Python library. The architecture supports automated deployment across Development → Test → Production environments with comprehensive validation, monitoring, and rollback capabilities.

## Architecture Components

### 1. Core Technologies
- **Microsoft Fabric Git Integration**: Direct workspace-to-Git synchronization
- **GitHub Actions**: CI/CD automation and orchestration
- **fabric-cicd Python Library**: Programmatic deployment to Fabric workspaces
- **Fabric REST APIs**: Direct workspace management and monitoring
- **Azure Key Vault**: Secure credential management

### 2. Supported Fabric Items
- ✅ **Notebooks** (Jupyter .ipynb files)
- ✅ **Data Pipelines** (JSON definitions)
- ✅ **Dataflows Gen2** (Power Query definitions)
- ✅ **Spark Job Definitions** (Python/Scala jobs)
- ✅ **Lakehouses** (Schema and metadata)
- ✅ **Power BI Reports** (via deployment pipelines)

### 3. Environment Setup

#### Prerequisites
1. Microsoft Fabric Premium capacity or trial
2. Azure AD Service Principal with Fabric permissions
3. GitHub repository with appropriate secrets configured
4. Fabric workspaces for Dev/Test/Production

#### Required GitHub Secrets
```yaml
AZURE_CLIENT_ID: "<service-principal-client-id>"
AZURE_TENANT_ID: "<azure-tenant-id>" 
AZURE_SUBSCRIPTION_ID: "<azure-subscription-id>"
AZURE_CLIENT_SECRET: "<service-principal-secret>"
FABRIC_DEPLOYMENT_PIPELINE_ID: "<fabric-deployment-pipeline-id>"
TEAMS_WEBHOOK_URI: "<microsoft-teams-webhook>" # Optional
```

#### Service Principal Permissions
Your Azure AD Service Principal needs:
- **Fabric Workspace Access**: Admin or Contributor on all target workspaces
- **Fabric API Permissions**: `https://api.fabric.microsoft.com/.default`
- **Azure Resource Access**: If using Azure resources in pipelines

## Workflows Overview

### 1. Main CI/CD Pipeline (`fabric-cicd-pipeline.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Changes to Fabric artifacts (`notebooks/`, `pipelines/`, `dataflows/`, etc.)

**Stages:**
1. **Code Quality & Linting** - Black formatting, Flake8 linting, artifact validation
2. **Unit & Integration Tests** - pytest execution with coverage reporting
3. **Data Quality Gate** - Great Expectations validation (PR only)
4. **Package Artifacts** - Bundle Fabric items for deployment
5. **Deploy to Development** - Automatic deployment on main branch
6. **Deploy to Test** - Manual approval required
7. **Deploy to Production** - Manual approval required
8. **Security Scan** - Trivy vulnerability scanning

### 2. Fabric Git Sync (`fabric-git-sync.yml`)

**Purpose:** Bidirectional synchronization between Fabric workspaces and Git

**Triggers:**
- Manual workflow dispatch
- Scheduled daily sync (2 AM UTC)

**Features:**
- Sync workspace changes to Git (creates PR)
- Sync Git changes to workspace
- Automatic conflict detection and resolution

### 3. Health Monitoring (`fabric-monitoring.yml`)

**Purpose:** Continuous monitoring of Fabric workspace health

**Triggers:**
- Scheduled checks (every 4 hours, business days)
- Manual workflow dispatch

**Monitors:**
- Workspace accessibility and performance
- Item health and execution status
- Data quality metrics
- Git integration status
- Capacity utilization

## Directory Structure

```
usf-fabric-cicd/
├── .github/
│   └── workflows/
│       ├── fabric-cicd-pipeline.yml     # Main CI/CD workflow
│       ├── fabric-git-sync.yml          # Git integration sync
│       ├── fabric-monitoring.yml        # Health monitoring
│       ├── build.yml                    # Legacy build workflow
│       └── reusable-*.yml              # Reusable workflow components
├── notebooks/                           # Jupyter notebooks
├── pipelines/                          # Data pipeline definitions
├── dataflows/                          # Dataflow Gen2 definitions
├── sparkjobdefinitions/                # Spark job definitions
├── data/
│   ├── bronze/                         # Raw data schemas
│   ├── silver/                         # Processed data schemas
│   └── gold/                           # Business-ready data schemas
├── governance/
│   ├── data_contracts/                 # Data contract definitions
│   ├── dq_rules/                       # Data quality rules
│   └── purview/                        # Purview configurations
├── ops/
│   ├── scripts/
│   │   ├── deploy_fabric.py           # Enhanced deployment script
│   │   ├── sync_fabric_git.py         # Git synchronization
│   │   ├── validate_fabric_artifacts.py # Artifact validation
│   │   ├── health_check_fabric.py     # Health monitoring
│   │   └── utilities/
│   │       ├── fabric_api.py          # Enhanced Fabric API client
│   │       └── fabric_deployment_pipeline.py # Deployment pipeline management
│   └── requirements.txt               # Python dependencies
└── platform/
    └── containers/                     # Container definitions
```

## Getting Started

### 1. Initial Setup

1. **Clone and Configure Repository:**
   ```bash
   git clone <your-repo>
   cd usf-fabric-cicd
   ```

2. **Configure GitHub Secrets:**
   - Navigate to Repository Settings → Secrets and variables → Actions
   - Add all required secrets listed above

3. **Create Fabric Workspaces:**
   ```
   usf-fabric-dev     # Development workspace
   usf-fabric-test    # Testing workspace  
   usf-fabric-prod    # Production workspace
   ```

4. **Create Fabric Deployment Pipeline:**
   - Use Fabric portal to create deployment pipeline
   - Connect workspaces to stages (Dev → Test → Prod)
   - Note the pipeline ID for GitHub secrets

### 2. Initialize Git Integration

Run the Git integration setup for your development workspace:

```bash
# Initialize Git connection
python ops/scripts/sync_fabric_git.py \
  --workspace "usf-fabric-dev" \
  --action init-git \
  --git-provider "GitHub" \
  --organization "your-org" \
  --repository "usf-fabric-cicd" \
  --branch "main"
```

### 3. First Deployment

1. **Create your first Fabric artifacts:**
   ```bash
   mkdir -p notebooks pipelines dataflows
   # Add your .ipynb, .pipeline.json, .dataflow.json files
   ```

2. **Validate artifacts:**
   ```bash
   python ops/scripts/validate_fabric_artifacts.py --path .
   ```

3. **Commit and push:**
   ```bash
   git add .
   git commit -m "Initial Fabric artifacts"
   git push origin main
   ```

4. **Monitor deployment:**
   - Check GitHub Actions for pipeline execution
   - Review deployment in Fabric workspaces

## Usage Examples

### Manual Deployment

Deploy specific bundle to workspace:
```bash
python ops/scripts/deploy_fabric.py \
  --workspace "usf-fabric-test" \
  --bundle "./artifacts/fabric_bundle.zip" \
  --mode standard
```

### Promote via Deployment Pipeline

Promote from Test to Production:
```bash
python ops/scripts/deploy_fabric.py \
  --workspace "usf-fabric-prod" \
  --deployment-pipeline-id "your-pipeline-id" \
  --source-stage 1 \
  --target-stage 2 \
  --mode promote
```

### Git Synchronization

Sync workspace changes to Git:
```bash
python ops/scripts/sync_fabric_git.py \
  --workspace "usf-fabric-dev" \
  --action sync-to-git \
  --commit-message "Updated data pipeline definitions"
```

### Health Check

Check workspace health:
```bash
python ops/scripts/health_check_fabric.py \
  --workspace "usf-fabric-prod" \
  --environment prod \
  --output-format json
```

## Advanced Configuration

### Custom Validation Rules

Edit `ops/scripts/validate_fabric_artifacts.py` to add custom validation:
```python
# Add custom notebook validation
def _validate_custom_notebook_standards(self, notebook_path):
    # Your custom validation logic
    pass
```

### Environment-Specific Settings

Create environment-specific configurations:
```yaml
# .github/environments/production.yml
protection_rules:
  required_reviewers: 2
  prevent_self_review: true
```

### Integration with External Tools

- **Power BI**: Automatic report deployment via deployment pipelines
- **Purview**: Data lineage and governance integration
- **Azure Monitor**: Extended monitoring and alerting
- **Great Expectations**: Data quality validation gates

## Monitoring and Alerting

### Health Dashboard

Access the automatically generated health dashboard:
- Run the monitoring workflow
- Download the `health-dashboard.html` artifact
- Open in browser for visual health status

### Microsoft Teams Integration

Configure Teams notifications for critical issues:
1. Create Teams webhook URL
2. Add `TEAMS_WEBHOOK_URI` secret
3. Receive alerts for deployment failures and health issues

### Custom Metrics

The health check script provides these metrics:
- Workspace response times
- Item execution success rates
- Data quality scores
- Git sync status
- Capacity utilization

## Troubleshooting

### Common Issues

1. **Authentication Failures:**
   ```bash
   # Verify service principal permissions
   az ad sp show --id $AZURE_CLIENT_ID
   ```

2. **Deployment Timeouts:**
   ```bash
   # Check workspace capacity and activity
   python ops/scripts/health_check_fabric.py --workspace "workspace-name" --environment dev
   ```

3. **Git Sync Conflicts:**
   ```bash
   # Check sync status
   python ops/scripts/sync_fabric_git.py --workspace "workspace-name" --action status
   ```

### Debug Mode

Enable detailed logging:
```bash
export FABRIC_DEBUG=true
python ops/scripts/deploy_fabric.py --workspace "workspace-name" --bundle "bundle.zip"
```

## Security Best Practices

### Credential Management
- ✅ Use Azure Key Vault for secrets
- ✅ Rotate service principal secrets regularly
- ✅ Use managed identity where possible
- ✅ Implement least-privilege access

### Data Protection
- ✅ Clear notebook outputs before commit
- ✅ Scan for sensitive data in artifacts
- ✅ Encrypt data in transit and at rest
- ✅ Audit access and changes

### Network Security
- ✅ Use private endpoints for Fabric access
- ✅ Implement network restrictions
- ✅ Monitor for unusual access patterns

## Contributing

### Development Workflow
1. Create feature branch from `develop`
2. Make changes and add tests
3. Validate with `validate_fabric_artifacts.py`
4. Create pull request to `develop`
5. After review, merge to `main` for deployment

### Testing Guidelines
- Add unit tests for all utility functions
- Include integration tests for deployment scenarios
- Test with sample Fabric artifacts
- Validate against multiple workspace configurations

## Support and Documentation

### Additional Resources
- [Microsoft Fabric Documentation](https://docs.microsoft.com/fabric/)
- [Fabric REST API Reference](https://docs.microsoft.com/rest/api/fabric/)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [fabric-cicd Library](https://pypi.org/project/fabric-cicd/)

### Getting Help
- Review GitHub Issues for common problems
- Check workflow logs in GitHub Actions
- Use health check scripts for diagnostics
- Contact your Fabric administrator for workspace issues

---

**Note:** This implementation provides enterprise-grade CI/CD capabilities for Microsoft Fabric. Customize the workflows and scripts according to your organization's specific requirements and governance policies.