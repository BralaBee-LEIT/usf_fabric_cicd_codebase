# Fabric CI/CD - Quick Prerequisites Checklist

**Use this for stakeholder presentations and requirement gathering**

---

## 🎯 1. Microsoft Azure (REQUIRED)

### What You Need:
- [ ] **Active Azure Subscription** with Contributor or Owner role
- [ ] **Azure AD Tenant** with admin access
- [ ] **Region** where Microsoft Fabric is available

### What We'll Create:
- [ ] **Service Principal** (automated deployment account)
- [ ] **Resource Group** (optional, for organizing resources)

### Costs:
- **Azure Resources**: $5-50/month (storage, monitoring - optional)

---

## 🎯 2. Microsoft Fabric (REQUIRED)

### What You Need:
- [ ] **Fabric Capacity License** OR 60-day free trial
- [ ] **Fabric Admin** access to tenant settings
- [ ] **Capacity Size**: F2 minimum for dev/test, F8+ for production

### What We'll Configure:
- [ ] Enable "Service principals can use Fabric APIs"
- [ ] Enable workspace creation
- [ ] Create 3 workspaces (dev, test, prod)

### Costs:
- **F2 Capacity**: ~$262/month (dev/test)
- **F8 Capacity**: ~$1,048/month (production)
- **Trial**: $0 for 60 days

---

## 🎯 3. GitHub (REQUIRED for CI/CD)

### What You Need:
- [ ] **GitHub Account** (Team plan recommended, $4/user/month)
- [ ] **Organization** or existing org with admin access
- [ ] **Private Repository** access

### What We'll Configure:
- [ ] Repository with branch protection
- [ ] GitHub Actions enabled
- [ ] Repository secrets for Azure credentials
- [ ] Team access permissions

### Costs:
- **Team Plan**: $4/user/month (recommended)
- **Free Plan**: Works but limited Actions minutes

---

## 🎯 4. Local Development Tools (Per Developer)

### Required Software:
- [ ] **Python 3.11** (specific version required)
- [ ] **Conda or Miniconda** (environment management)
- [ ] **Git** (version control)
- [ ] **VS Code** or similar IDE (recommended)

### Optional Tools:
- [ ] Azure CLI (helpful for troubleshooting)
- [ ] Power BI Desktop (for report development)

### Time to Setup:
- **30 minutes per developer**

---

## 🎯 5. Credentials & Access (CRITICAL)

### Information You Must Collect:

```
Azure Service Principal:
├─ Client ID (Application ID)
├─ Client Secret (keep secure!)
├─ Tenant ID
└─ Subscription ID

GitHub:
├─ Organization name
├─ Repository name
└─ Personal Access Token (with repo + workflow permissions)

Organization:
├─ Project prefix (e.g., "acme-corp")
├─ Team email addresses
└─ Region preference
```

---

## 🎯 6. Permissions Required

### Azure AD:
- [ ] **Global Admin** (one-time, for initial setup)
- [ ] **Application Administrator** (to create service principal)
- [ ] **Grant admin consent** (for API permissions)

### Fabric:
- [ ] **Fabric Admin** (to configure tenant settings)
- [ ] **Capacity Admin** (to manage capacity)

### GitHub:
- [ ] **Organization Owner or Admin** (to create repos and manage secrets)

---

## 🎯 7. Team Roles Needed

### For Initial Setup (6-12 hours total):
| Role | Time Needed | Responsibility |
|------|-------------|----------------|
| **Azure Admin** | 4-6 hours | Service principal, permissions |
| **Fabric Admin** | 2-4 hours | Tenant settings, capacity |
| **DevOps Lead** | 8-12 hours | GitHub, CI/CD setup |
| **Data Engineer** | 4-8 hours | Workspace setup, testing |

### Ongoing:
| Role | Time Needed | Responsibility |
|------|-------------|----------------|
| **Workspace Admin** | 1-2 hours/week | User management, monitoring |
| **Developer** | As needed | Content development |

---

## 🎯 8. Network & Security

### Required Access:
- [ ] **api.fabric.microsoft.com** (HTTPS/443)
- [ ] **api.powerbi.com** (HTTPS/443)
- [ ] **login.microsoftonline.com** (HTTPS/443)
- [ ] **github.com** (HTTPS/443)

### Security Requirements:
- [ ] **MFA enabled** for all user accounts
- [ ] **Client secret rotation** every 6-24 months
- [ ] **Audit logging** enabled
- [ ] **IP restrictions** (optional, for production)

---

## 💰 Total Cost Estimate

### Minimal Setup (Dev/Test Only):
```
Fabric F2 Capacity:     $262/month
Azure Storage:          $10/month
GitHub Team:            $4/user/month
─────────────────────────────────
Total:                  ~$280-350/month
```

### Production Setup:
```
Fabric F8 Capacity:     $1,048/month
Azure Resources:        $50-100/month
GitHub Team:            $4/user/month
─────────────────────────────────
Total:                  ~$1,100-1,500/month
```

### Trial/POC (60 days):
```
Fabric Trial:           $0
GitHub Free:            $0
Azure Free Tier:        $0
─────────────────────────────────
Total:                  $0 (for 60 days)
```

---

## ⏱️ Timeline Estimate

### Phase 1: Azure Setup
- **Duration**: 2-4 hours
- **Tasks**: Service principal, permissions, RBAC

### Phase 2: Fabric Setup
- **Duration**: 1-2 hours
- **Tasks**: Capacity, tenant settings, wait for propagation

### Phase 3: GitHub Setup
- **Duration**: 1 hour
- **Tasks**: Repository, secrets, teams

### Phase 4: Local Setup
- **Duration**: 30 minutes per developer
- **Tasks**: Software, environment, configuration

### Phase 5: Testing
- **Duration**: 2-3 hours
- **Tasks**: Workspace creation, CI/CD validation

### **Total Time: 6-12 hours** (spread over 1-2 days for propagation delays)

---

## ✅ Pre-Approval Questions

### Budget:
- [ ] Is there budget for Fabric capacity? (~$262-1,048/month)
- [ ] Can we start with a 60-day trial?
- [ ] Who approves ongoing Azure costs?

### Access:
- [ ] Do we have a Fabric Admin available?
- [ ] Can we create a service principal?
- [ ] Do we have Azure subscription admin access?

### Team:
- [ ] Do we have DevOps/Data Engineering resources?
- [ ] What is the expected timeline?
- [ ] Who will maintain this after setup?

### Security:
- [ ] Are there specific security requirements?
- [ ] Is MFA mandatory? (recommended: yes)
- [ ] Any data residency requirements?

---

## 🚀 Quick Start After Approval

Once you have all prerequisites:

```bash
# 1. Create conda environment (2 minutes)
conda env create -f environment.yml
conda activate fabric-cicd

# 2. Configure credentials (5 minutes)
cp .env.example .env
# Edit .env with your Azure/GitHub credentials

# 3. Initialize project (3 minutes)
python init_project_config.py

# 4. Create workspaces (2 minutes)
./tools/fabric-cli.sh create-set your-project-name

# 5. Verify (1 minute)
./tools/fabric-cli.sh lsd

Total: ~15 minutes after prerequisites are ready!
```

---

## 📞 Questions?

Before starting, ensure you can answer:

1. ✅ Do we have an active Azure subscription?
2. ✅ Do we have Fabric licensing or can we use trial?
3. ✅ Do we have GitHub access?
4. ✅ Who will be the Fabric Admin?
5. ✅ Who will be the Azure Admin?
6. ✅ What is our project timeline?
7. ✅ What is our budget approval process?

---

**Print this checklist and use it in stakeholder meetings!**

**For detailed information, see: DEPLOYMENT_PREREQUISITES.md**
