# Microsoft Fabric CI/CD - Deployment Prerequisites & Requirements

**Project Replication Guide for New Organizations**  
**Version**: 2.0.0  
**Last Updated**: October 16, 2025

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Microsoft Azure Requirements](#microsoft-azure-requirements)
3. [Microsoft Fabric Requirements](#microsoft-fabric-requirements)
4. [GitHub Requirements](#github-requirements)
5. [Local Development Environment](#local-development-environment)
6. [Service Principal Setup](#service-principal-setup)
7. [Permissions & Access Control](#permissions--access-control)
8. [Network & Security Requirements](#network--security-requirements)
9. [Team Requirements](#team-requirements)
10. [Cost Considerations](#cost-considerations)
11. [Step-by-Step Setup Checklist](#step-by-step-setup-checklist)
12. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## 📊 Executive Summary

This document outlines all prerequisites needed to replicate the Microsoft Fabric CI/CD solution in a new organization.

### **What This Solution Provides:**
- ✅ Multi-environment workspace management (Dev/Test/Prod)
- ✅ Automated CI/CD pipeline with GitHub Actions
- ✅ Data governance with contracts and quality rules
- ✅ User and permission management
- ✅ Deployment automation and rollback capabilities

### **Timeline Estimate:**
- **Azure Setup**: 2-4 hours
- **Service Principal Configuration**: 1-2 hours
- **GitHub Configuration**: 1 hour
- **Local Setup (per developer)**: 30 minutes
- **Testing & Validation**: 2-3 hours
- **Total**: 6-12 hours for complete setup

---

## 🔷 Microsoft Azure Requirements

### **1. Azure Subscription**

| Requirement | Details |
|------------|---------|
| **Active Azure Subscription** | Required |
| **Subscription Type** | Pay-As-You-Go, Enterprise Agreement, or MSDN |
| **Minimum Role** | Contributor or Owner on subscription |
| **Region Availability** | Microsoft Fabric available in region |

**Available Regions** (as of Oct 2025):
- North Europe
- West Europe
- East US
- West US
- UK South
- Australia East
- [Check latest availability](https://learn.microsoft.com/fabric/admin/region-availability)

### **2. Azure Active Directory (Entra ID)**

| Requirement | Details |
|------------|---------|
| **Azure AD Tenant** | Required |
| **Tenant Admin Access** | Required for initial setup |
| **User Accounts** | Team members need Azure AD accounts |
| **MFA Enabled** | Recommended for security |

### **3. Azure Resources (Optional but Recommended)**

| Resource | Purpose | Required? |
|----------|---------|-----------|
| **Azure Storage Account** | Data lake, GX validation store | Optional |
| **Azure Key Vault** | Secure secrets management | Recommended |
| **Azure Purview** | Data governance and cataloging | Optional |
| **Application Insights** | Monitoring and logging | Recommended |
| **Log Analytics Workspace** | Centralized logging | Recommended |

---

## 🎯 Microsoft Fabric Requirements

### **1. Microsoft Fabric License**

| Requirement | Details |
|------------|---------|
| **Fabric Capacity** | F2 minimum (F8+ for production) |
| **License Type** | Fabric capacity license OR Power BI Premium |
| **Trial Available** | 60-day free trial for testing |
| **Cost** | Starting at ~$200/month (F2) |

**Capacity Sizing Guide:**
- **Dev/Test**: F2-F4 (sufficient for testing)
- **Production**: F8+ (based on workload)
- **Trial**: Use for initial setup and testing

### **2. Fabric Admin Portal Access**

| Requirement | Details |
|------------|---------|
| **Fabric Admin** | Required for tenant settings |
| **Admin Portal Access** | admin.fabric.microsoft.com |
| **Tenant Settings** | Must enable service principal API access |

**Required Tenant Settings:**
1. ✅ Enable "Service principals can use Fabric APIs"
2. ✅ Enable "Users can create workspaces"
3. ✅ Enable "Deployment pipelines" (if using)
4. ✅ Enable "Git integration" (optional)

### **3. Fabric Workspaces**

| Item | Details |
|------|---------|
| **Number of Workspaces** | 3 minimum (dev, test, prod) |
| **Naming Convention** | `{org-prefix}-fabric-{environment}` |
| **Capacity Assignment** | Assign to Fabric capacity or use Trial |

---

## 🐙 GitHub Requirements

### **1. GitHub Account & Organization**

| Requirement | Details |
|------------|---------|
| **GitHub Account** | Team or Enterprise plan recommended |
| **Organization** | Create dedicated org or use existing |
| **Admin Access** | Required for repository setup |
| **Team Permissions** | Configure team-based access |

### **2. GitHub Repository**

| Item | Details |
|------|---------|
| **Repository Type** | Private (recommended) |
| **Branching Strategy** | main, develop, feature/* |
| **Branch Protection** | Enable for main and develop |
| **Required Reviews** | Minimum 1 reviewer for main branch |

### **3. GitHub Secrets (Required)**

Must be configured in repository settings:

```yaml
# Azure Authentication
AZURE_CLIENT_ID          # Service principal application ID
AZURE_CLIENT_SECRET      # Service principal secret
AZURE_TENANT_ID          # Azure AD tenant ID
AZURE_SUBSCRIPTION_ID    # Azure subscription ID

# GitHub Token
GITHUB_TOKEN             # Personal access token (repo + workflow scopes)

# Optional but Recommended
TEAMS_WEBHOOK_URL        # For deployment notifications
```

### **4. GitHub Actions**

| Requirement | Details |
|------------|---------|
| **GitHub Actions Enabled** | Required |
| **Workflow Permissions** | Read and write permissions |
| **Self-hosted Runners** | Optional (use GitHub-hosted by default) |
| **Concurrent Jobs** | 20+ recommended for Enterprise |

---

## 💻 Local Development Environment

### **1. Operating System**

| OS | Status | Notes |
|----|--------|-------|
| **Linux** | ✅ Fully Supported | Ubuntu 20.04+, RHEL 8+ |
| **macOS** | ✅ Fully Supported | macOS 11+ |
| **Windows** | ✅ Supported | Windows 10/11, WSL2 recommended |

### **2. Required Software**

| Software | Version | Installation |
|----------|---------|--------------|
| **Python** | 3.11.x | Required (not 3.12+) |
| **Conda/Miniconda** | Latest | Recommended for env management |
| **Git** | 2.30+ | Version control |
| **VS Code** | Latest | Recommended IDE |
| **Azure CLI** | 2.50+ | Optional but helpful |

### **3. Python Dependencies**

Installed via `environment.yml` and `ops/requirements.txt`:

```yaml
Core:
- python==3.11
- pyyaml==6.0.2
- requests==2.32.3

Azure:
- azure-identity==1.17.1
- azure-mgmt-resource==23.1.1
- msal==1.24.1

Data Quality:
- great-expectations==1.2.5

Testing:
- pytest==8.3.3
- pytest-cov==6.0.0

Code Quality:
- black==24.8.0
- flake8==7.1.1
- yamllint==1.35.1

Security:
- pip-audit==2.7.3
```

### **4. Development Tools (Recommended)**

| Tool | Purpose |
|------|---------|
| **VS Code Extensions** | Python, YAML, GitHub Copilot |
| **Postman/Thunder Client** | API testing |
| **Azure Storage Explorer** | Blob storage management |
| **Power BI Desktop** | Report development |

---

## 🔐 Service Principal Setup

### **1. Create Service Principal**

**Via Azure Portal:**
1. Navigate to Azure Active Directory
2. Go to "App registrations" → "New registration"
3. Name: `fabric-cicd-service-principal`
4. Account type: "Single tenant"
5. Redirect URI: (leave blank)
6. Click "Register"

**Via Azure CLI:**
```bash
az ad sp create-for-rbac \
  --name fabric-cicd-sp \
  --role Contributor \
  --scopes /subscriptions/{subscription-id}
```

### **2. Service Principal Configuration**

| Setting | Value |
|---------|-------|
| **Application Type** | Web (not Native/Mobile) |
| **Supported Account Types** | Single tenant |
| **Redirect URIs** | Not required |
| **Client Secret** | Create and save securely (expires in 6-24 months) |

### **3. Required Values to Capture**

After creation, save these values:

```bash
AZURE_CLIENT_ID=<Application (client) ID>
AZURE_TENANT_ID=<Directory (tenant) ID>
AZURE_CLIENT_SECRET=<Client secret value>
AZURE_SUBSCRIPTION_ID=<Your subscription ID>
```

⚠️ **IMPORTANT**: Client secret is only shown once - save it immediately!

---

## 🔒 Permissions & Access Control

### **1. Azure AD Application Permissions**

**Required API Permissions:**

| API | Permission | Type | Admin Consent |
|-----|------------|------|---------------|
| **Microsoft Fabric** | Workspace.ReadWrite.All | Application | Required |
| **Microsoft Fabric** | Item.ReadWrite.All | Application | Required |
| **Microsoft Graph** | User.Read.All | Application | Required (for user mgmt) |

**How to Add:**
1. Go to App registration → API permissions
2. Click "Add a permission"
3. Select "APIs my organization uses"
4. Search for "Power BI Service" (Fabric uses this)
5. Select "Application permissions" (NOT Delegated)
6. Add required permissions
7. Click "Grant admin consent" ✅ **CRITICAL STEP**

### **2. Fabric Tenant Settings**

**Required Configuration:**

Navigate to: `admin.fabric.microsoft.com` → Tenant settings

Enable these settings:

```
✅ Developer settings:
   - Service principals can use Fabric APIs

✅ Workspace settings:
   - Users can create workspaces

✅ Content sharing:
   - Allow service principals to use read-only admin APIs
   
✅ (Optional) Git integration:
   - Users can synchronize workspace items with Git repos
```

**Apply to**: Specific security group containing your service principal

⏱️ **Wait 15-30 minutes** after enabling for propagation

### **3. Azure RBAC Roles**

| Role | Scope | Required For |
|------|-------|--------------|
| **Contributor** | Subscription | Resource management |
| **Key Vault Secrets User** | Key Vault | Reading secrets |
| **Storage Blob Data Contributor** | Storage Account | Data access |

### **4. Fabric Workspace Roles**

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | Full control | Service principal, DevOps team |
| **Member** | Create & edit content | Developers |
| **Contributor** | Edit existing content | Data analysts |
| **Viewer** | Read-only access | Business users |

---

## 🌐 Network & Security Requirements

### **1. Network Access**

| Endpoint | Purpose | Required |
|----------|---------|----------|
| `api.fabric.microsoft.com` | Fabric REST API | Yes |
| `api.powerbi.com` | Power BI API | Yes |
| `login.microsoftonline.com` | Azure AD authentication | Yes |
| `github.com` | Version control | Yes |
| `api.github.com` | GitHub API | Yes |

**Firewall Rules:**
- Allow HTTPS (443) outbound to above endpoints
- No inbound connections required

### **2. Security Requirements**

| Item | Requirement |
|------|-------------|
| **Client Secret Expiry** | 6-24 months (set calendar reminder) |
| **MFA** | Required for all user accounts |
| **Conditional Access** | Recommended for service principals |
| **IP Restrictions** | Optional (consider for production) |
| **Key Vault** | Store secrets (not in .env files) |

### **3. Data Classification**

| Classification | Description | Examples |
|----------------|-------------|----------|
| **Public** | No restrictions | Marketing data |
| **Internal** | Internal use only | Financial reports |
| **Confidential** | Restricted access | Customer PII |
| **Restricted** | Highly sensitive | Health records |

---

## 👥 Team Requirements

### **1. Required Roles**

| Role | Responsibilities | Time Commitment |
|------|------------------|-----------------|
| **Fabric Admin** | Tenant settings, capacity management | 2-4 hours initial |
| **Azure Admin** | Subscription, service principal, RBAC | 4-6 hours initial |
| **DevOps Lead** | GitHub, CI/CD pipeline, automation | 8-12 hours initial |
| **Data Engineer** | Workspace setup, content deployment | 4-8 hours initial |
| **Security Admin** | Permissions, compliance, auditing | 2-4 hours initial |

### **2. Team Skills (Recommended)**

| Skill | Importance | Training Available |
|-------|------------|-------------------|
| **Azure Fundamentals** | High | Microsoft Learn (free) |
| **Git/GitHub** | High | GitHub Skills (free) |
| **Python Basics** | Medium | Various online courses |
| **Fabric Concepts** | High | Fabric documentation |
| **CI/CD Principles** | Medium | DevOps courses |

### **3. Team Permissions Matrix**

| Team Member | Azure Role | Fabric Role | GitHub Role |
|-------------|-----------|-------------|-------------|
| **Fabric Admin** | Reader | Workspace Admin | Read |
| **DevOps Lead** | Contributor | Workspace Admin | Admin |
| **Data Engineer** | Reader | Workspace Member | Write |
| **Data Analyst** | Reader | Workspace Contributor | Read |
| **Business User** | - | Workspace Viewer | - |

---

## 💰 Cost Considerations

### **1. Microsoft Fabric Costs**

| Item | Monthly Cost (USD) | Notes |
|------|-------------------|-------|
| **F2 Capacity** | ~$262 | Dev/Test minimum |
| **F4 Capacity** | ~$524 | Small production |
| **F8 Capacity** | ~$1,048 | Medium production |
| **F64 Capacity** | ~$8,384 | Enterprise scale |
| **Trial** | $0 | 60 days free |

**Cost Optimization:**
- Use trial for initial setup
- Start with F2 for dev/test
- Pause capacity when not in use
- Scale up only for production

### **2. Azure Costs**

| Service | Monthly Cost (USD) | Required? |
|---------|-------------------|-----------|
| **Storage Account** | $5-20 | Optional |
| **Key Vault** | $1-5 | Recommended |
| **Application Insights** | $5-50 | Recommended |
| **Purview** | $0-100+ | Optional |

### **3. GitHub Costs**

| Plan | Cost/User/Month | Features |
|------|----------------|----------|
| **Free** | $0 | 2,000 Actions minutes/month |
| **Team** | $4 | 3,000 Actions minutes/month |
| **Enterprise** | $21 | 50,000 Actions minutes/month |

**Recommendation**: Team plan minimum for private repos

### **4. Estimated Total Monthly Cost**

| Scenario | Cost Range |
|----------|------------|
| **Minimal (Trial + Free GitHub)** | $0-10 |
| **Dev/Test (F2 + Storage + Team)** | $280-350 |
| **Production (F8 + Full Stack)** | $1,100-1,500 |

---

## ✅ Step-by-Step Setup Checklist

### **Phase 1: Azure Setup (2-4 hours)**

- [ ] **1.1** Verify Azure subscription is active
- [ ] **1.2** Check Microsoft Fabric is available in region
- [ ] **1.3** Create service principal
  - [ ] Save Client ID
  - [ ] Save Tenant ID
  - [ ] Save Client Secret (immediately!)
  - [ ] Save Subscription ID
- [ ] **1.4** Add API permissions to service principal
  - [ ] Microsoft Fabric permissions
  - [ ] Microsoft Graph permissions
  - [ ] Grant admin consent ✅
- [ ] **1.5** Assign RBAC roles
  - [ ] Contributor on subscription
  - [ ] Additional roles as needed
- [ ] **1.6** Wait 15-30 minutes for propagation

### **Phase 2: Microsoft Fabric Setup (1-2 hours)**

- [ ] **2.1** Create or verify Fabric capacity
  - [ ] Region matches Azure subscription
  - [ ] Size appropriate for workload (F2+ for dev)
- [ ] **2.2** Configure Fabric tenant settings
  - [ ] Enable service principal API access
  - [ ] Enable workspace creation
  - [ ] Enable deployment pipelines (optional)
  - [ ] Apply to security group
- [ ] **2.3** Wait 15-30 minutes for settings to apply
- [ ] **2.4** Test service principal access
  ```bash
  # Use test script to verify API access
  python3 ops/scripts/test_fabric_connection.py
  ```

### **Phase 3: GitHub Setup (1 hour)**

- [ ] **3.1** Create GitHub organization (or use existing)
- [ ] **3.2** Create private repository
- [ ] **3.3** Clone this repository to new repo
  ```bash
  git clone https://github.com/BralaBee-LEIT/usf_fabric_cicd_codebase.git
  cd usf_fabric_cicd_codebase
  git remote set-url origin https://github.com/YOUR-ORG/YOUR-REPO.git
  git push -u origin main
  ```
- [ ] **3.4** Configure repository secrets
  - [ ] AZURE_CLIENT_ID
  - [ ] AZURE_CLIENT_SECRET
  - [ ] AZURE_TENANT_ID
  - [ ] AZURE_SUBSCRIPTION_ID
  - [ ] GITHUB_TOKEN
- [ ] **3.5** Set up branch protection rules
  - [ ] Require pull request reviews
  - [ ] Require status checks
- [ ] **3.6** Create GitHub teams
  - [ ] Data team
  - [ ] DevOps team
  - [ ] (Other teams as needed)

### **Phase 4: Local Development Setup (30 minutes per developer)**

- [ ] **4.1** Install required software
  - [ ] Python 3.11
  - [ ] Conda/Miniconda
  - [ ] Git
  - [ ] VS Code (recommended)
- [ ] **4.2** Clone repository
  ```bash
  git clone https://github.com/YOUR-ORG/YOUR-REPO.git
  cd YOUR-REPO
  ```
- [ ] **4.3** Create conda environment
  ```bash
  conda env create -f environment.yml
  conda activate fabric-cicd
  ```
- [ ] **4.4** Copy and configure .env file
  ```bash
  cp .env.example .env
  # Edit .env with your credentials
  ```
- [ ] **4.5** Initialize project configuration
  ```bash
  python init_project_config.py
  # Answer prompts with your organization details
  ```
- [ ] **4.6** Run setup validation
  ```bash
  ./quick_setup.sh
  ```

### **Phase 5: Workspace Creation (30 minutes)**

- [ ] **5.1** Verify environment variables
  ```bash
  cat .env | grep AZURE
  ```
- [ ] **5.2** Create dev/test/prod workspaces
  ```bash
  ./tools/fabric-cli.sh create-set your-project-name
  ```
- [ ] **5.3** Verify workspaces created
  ```bash
  ./tools/fabric-cli.sh lsd
  ```
- [ ] **5.4** Add team members to workspaces
  ```bash
  # For each workspace and user
  ./tools/fabric-cli.sh add-user WORKSPACE_ID user@domain.com --role Member
  ```

### **Phase 6: Testing & Validation (2-3 hours)**

- [ ] **6.1** Test data contract validation
  ```bash
  python ops/scripts/validate_data_contracts.py \
    --contracts-dir governance/data_contracts
  ```
- [ ] **6.2** Test DQ rules validation
  ```bash
  python ops/scripts/validate_dq_rules.py \
    --rules-dir governance/dq_rules
  ```
- [ ] **6.3** Test workspace operations
  ```bash
  # List, create test workspace, delete test workspace
  ./tools/fabric-cli.sh ls
  ./tools/fabric-cli.sh create test-workspace -e dev
  ./tools/fabric-cli.sh delete WORKSPACE_ID
  ```
- [ ] **6.4** Test CI/CD pipeline
  - [ ] Create feature branch
  - [ ] Make small change
  - [ ] Create pull request
  - [ ] Verify GitHub Actions run
  - [ ] Merge to main
  - [ ] Verify deployment
- [ ] **6.5** Run full test suite
  ```bash
  pytest ops/tests/ -v --cov
  ```

### **Phase 7: Documentation & Handoff (1-2 hours)**

- [ ] **7.1** Update project.config.json with org details
- [ ] **7.2** Document organization-specific settings
- [ ] **7.3** Create team onboarding guide
- [ ] **7.4** Schedule knowledge transfer session
- [ ] **7.5** Set up support channels (Teams, Slack, etc.)

---

## 🔧 Troubleshooting Common Issues

### **Issue 1: 401 Unauthorized Errors**

**Symptoms:**
```
Failed to list workspaces: 401 Unauthorized
```

**Solution:**
1. ✅ Verify service principal API permissions granted
2. ✅ Check admin consent was given
3. ✅ Enable "Service principals can use Fabric APIs" in tenant settings
4. ✅ Wait 15-30 minutes for propagation
5. ✅ Verify credentials in .env are correct

### **Issue 2: 404 Not Found Errors**

**Symptoms:**
```
Failed to create workspace: 404 Not Found
```

**Solution:**
1. ✅ Check Fabric capacity is created and active
2. ✅ Verify Fabric is available in your region
3. ✅ Ensure API endpoints are correct (no /v1/v1/ duplication)

### **Issue 3: Environment Not Activated**

**Symptoms:**
```
ModuleNotFoundError: No module named 'azure'
```

**Solution:**
```bash
# Activate correct environment
conda activate fabric-cicd

# Verify
python --version  # Should show 3.11.x
conda env list    # fabric-cicd should have *
```

### **Issue 4: Permission Denied on Scripts**

**Symptoms:**
```
bash: ./fabric-cli.sh: Permission denied
```

**Solution:**
```bash
chmod +x fabric-cli.sh
chmod +x quick_setup.sh
```

### **Issue 5: GitHub Actions Failing**

**Symptoms:**
- Workflow runs fail
- Secret access errors

**Solution:**
1. ✅ Verify all secrets are set in repository settings
2. ✅ Check secret names match exactly
3. ✅ Ensure no trailing spaces in secret values
4. ✅ Verify GitHub Actions is enabled for repository

---

## 📞 Support & Resources

### **Official Documentation**

| Resource | URL |
|----------|-----|
| **Microsoft Fabric Docs** | https://learn.microsoft.com/fabric/ |
| **Fabric REST API** | https://learn.microsoft.com/rest/api/fabric/ |
| **Azure AD App Registration** | https://learn.microsoft.com/azure/active-directory/ |
| **GitHub Actions** | https://docs.github.com/actions |

### **This Project Documentation**

| Document | Purpose |
|----------|---------|
| **README.md** | Project overview |
| **QUICKSTART.md** | Fast setup guide |
| **FABRIC_CLI_QUICKREF.md** | CLI command reference |
| **WORKSPACE_MANAGEMENT_GUIDE.md** | Complete workspace guide |
| **DEVELOPER_JOURNEY_GUIDE.md** | Detailed setup walkthrough |
| **SETUP_IMPROVEMENTS.md** | Environment setup details |

### **Getting Help**

1. **Check documentation** in this repository
2. **Review troubleshooting section** above
3. **Microsoft Fabric community** forums
4. **GitHub issues** in your organization's repository
5. **Microsoft support** (with active Fabric subscription)

---

## 📝 Quick Reference Card

### **Essential Information to Collect**

```bash
# Azure
AZURE_TENANT_ID=________________________________________
AZURE_SUBSCRIPTION_ID=__________________________________
AZURE_CLIENT_ID=________________________________________
AZURE_CLIENT_SECRET=____________________________________

# GitHub
GITHUB_ORG=_____________________________________________
GITHUB_REPO=____________________________________________
GITHUB_TOKEN=___________________________________________

# Organization
ORG_PREFIX=_____________________________________________
DATA_OWNER_EMAIL=_______________________________________
TECHNICAL_LEAD_EMAIL=___________________________________
```

### **First Commands to Run**

```bash
# 1. Setup environment
conda env create -f environment.yml
conda activate fabric-cicd

# 2. Configure
cp .env.example .env
# Edit .env with your values

# 3. Initialize
python init_project_config.py
./quick_setup.sh

# 4. Create workspaces
./tools/fabric-cli.sh create-set your-project

# 5. Verify
./tools/fabric-cli.sh lsd
```

---

## ✅ Pre-Deployment Checklist Summary

**Before starting deployment, confirm:**

- [ ] Azure subscription is active and accessible
- [ ] Microsoft Fabric is available in target region
- [ ] Service principal created with all permissions
- [ ] Admin consent granted for API permissions
- [ ] Fabric tenant settings configured correctly
- [ ] GitHub repository created and configured
- [ ] All secrets added to GitHub
- [ ] Local development environment set up
- [ ] Team members have necessary access
- [ ] Budget approved for Fabric capacity costs
- [ ] Security requirements understood and documented
- [ ] Support plan in place

---

**Document Version**: 1.0  
**Last Updated**: October 16, 2025  
**Maintained By**: DevOps Team  
**Review Cycle**: Quarterly

**Next Review Date**: January 16, 2026
