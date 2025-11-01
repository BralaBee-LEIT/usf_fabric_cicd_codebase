# Action Plan: Separation of Concerns
## Your Immediate Next Steps

**Created:** October 25, 2025  
**Status:** Ready to Execute  
**Effort:** Quick Start (2-3 weeks) or Full Architecture (14 weeks)

---

## 🎯 Decision Point: Which Path?

### Option A: Quick Start (RECOMMENDED)
**Timeline:** 2-3 weeks  
**Effort:** Low  
**Impact:** 60% of benefits  
**Risk:** Low

Extract only the **Platform Toolkit** and keep everything else as-is.

**✅ Choose this if:**
- You want to test the concept first
- You have limited resources now
- You need quick wins
- Other teams are already asking to reuse your utilities

### Option B: Full Enterprise Architecture
**Timeline:** 14 weeks  
**Effort:** High  
**Impact:** 100% of benefits  
**Risk:** Medium

Full 5-layer separation as described in the architecture guide.

**✅ Choose this if:**
- You have executive buy-in
- Multiple teams will use this
- Planning for 2+ years of growth
- You have resources for 3-month project

---

## 📋 Quick Start Implementation (Option A)

### Week 1: Planning & Setup

#### Monday - Review & Approval
- [ ] Review `ENTERPRISE_ARCHITECTURE_GUIDE.md` with team leads
- [ ] Get approval from Platform/DevOps leadership
- [ ] Identify internal package registry (Azure Artifacts, internal PyPI, etc.)
- [ ] Assign 1-2 engineers to this effort

#### Tuesday - Repository Setup
```bash
# Create new repository
mkdir fabric-platform-toolkit
cd fabric-platform-toolkit
git init
git remote add origin https://github.com/BralaBee-LEIT/fabric-platform-toolkit.git

# Create initial structure
mkdir -p src/fabric_platform_toolkit/{core,resilience,observability,security,utils}
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs
touch README.md
```

#### Wednesday - Package Configuration
Create these files:

**setup.py:**
```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fabric-platform-toolkit",
    version="1.0.0",
    author="Your Team",
    author_email="team@company.com",
    description="Microsoft Fabric Platform SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BralaBee-LEIT/fabric-platform-toolkit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
        "azure-identity>=1.12.0",
        "azure-keyvault-secrets>=4.7.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.0.292",
            "mypy>=1.5.0",
        ],
    },
)
```

**pyproject.toml:**
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fabric-platform-toolkit"
version = "1.0.0"
description = "Microsoft Fabric Platform SDK"
readme = "README.md"
requires-python = ">=3.9"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "real_fabric: marks tests that require real Fabric connection",
]
pythonpath = ["."]

[tool.ruff]
line-length = 100
target-version = "py39"
```

#### Thursday - Copy Files from Current Repo

```bash
# From usf-fabric-cicd, copy utilities to new repo
cd /path/to/usf-fabric-cicd

# Copy core utilities
cp ops/scripts/utilities/fabric_api.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/core/

cp ops/scripts/utilities/fabric_git_connector.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/core/

cp ops/scripts/utilities/workspace_manager.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/core/

cp ops/scripts/utilities/constants.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/core/

# Copy resilience features
cp ops/scripts/utilities/retry_handler.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/resilience/

cp ops/scripts/utilities/circuit_breaker.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/resilience/

cp ops/scripts/utilities/health_check.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/resilience/

# Copy observability
cp ops/scripts/utilities/telemetry.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/observability/

# Copy security
cp ops/scripts/utilities/secret_manager.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/security/

# Copy utilities
cp ops/scripts/utilities/feature_flags.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/utils/

cp ops/scripts/utilities/output.py \
   ../fabric-platform-toolkit/src/fabric_platform_toolkit/utils/

# Copy tests
cp tests/unit/test_retry_handler.py \
   ../fabric-platform-toolkit/tests/unit/

cp tests/unit/test_circuit_breaker.py \
   ../fabric-platform-toolkit/tests/unit/

# ... copy all relevant test files
```

#### Friday - Create Package Exports

**src/fabric_platform_toolkit/__init__.py:**
```python
"""
Microsoft Fabric Platform Toolkit
==================================

Official SDK for Microsoft Fabric operations.

Usage:
    from fabric_platform_toolkit.core import FabricAPI, WorkspaceManager
    from fabric_platform_toolkit.resilience import RetryHandler
    from fabric_platform_toolkit.security import SecretManager
"""

__version__ = "1.0.0"

# Core exports
from .core.fabric_api import FabricAPI
from .core.workspace_manager import WorkspaceManager
from .core.constants import (
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    FABRIC_API_BASE_URL,
)

# Resilience exports
from .resilience.retry_handler import RetryHandler
from .resilience.circuit_breaker import CircuitBreaker
from .resilience.health_check import HealthCheck

# Security exports
from .security.secret_manager import SecretManager

# Utility exports
from .utils.feature_flags import FeatureFlags
from .utils.output import Output

__all__ = [
    # Version
    "__version__",
    # Core
    "FabricAPI",
    "WorkspaceManager",
    "DEFAULT_TIMEOUT",
    "MAX_RETRIES",
    "FABRIC_API_BASE_URL",
    # Resilience
    "RetryHandler",
    "CircuitBreaker",
    "HealthCheck",
    # Security
    "SecretManager",
    # Utils
    "FeatureFlags",
    "Output",
]
```

### Week 2: Testing & Publishing

#### Monday-Wednesday - Fix Tests

```bash
cd fabric-platform-toolkit

# Install in development mode
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Fix any import issues
# Update imports in test files to use new package structure
```

**Example test file update:**
```python
# OLD (in usf-fabric-cicd)
from ops.scripts.utilities.retry_handler import RetryHandler

# NEW (in fabric-platform-toolkit)
from fabric_platform_toolkit.resilience import RetryHandler
```

#### Thursday - Documentation

Create `README.md`:
```markdown
# Fabric Platform Toolkit

Official SDK for Microsoft Fabric operations.

## Installation

```bash
pip install fabric-platform-toolkit
```

## Quick Start

```python
from fabric_platform_toolkit.core import FabricAPI, WorkspaceManager
from fabric_platform_toolkit.resilience import RetryHandler
from fabric_platform_toolkit.security import SecretManager

# Initialize API
api = FabricAPI(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-secret"
)

# Create workspace manager
workspace_mgr = WorkspaceManager(api)

# List workspaces with automatic retry
retry_handler = RetryHandler(max_retries=3)
workspaces = retry_handler.execute(workspace_mgr.list_workspaces)
```

## Features

- ✅ Complete Fabric REST API wrapper
- ✅ Automatic retry with exponential backoff
- ✅ Circuit breaker pattern
- ✅ Health checks
- ✅ Azure Key Vault integration
- ✅ Telemetry and observability
- ✅ Feature flags
- ✅ Type hints and validation

## Documentation

See [docs/](docs/) for detailed documentation.

## Testing

```bash
pytest tests/
```

## License

Internal use only.
```

#### Friday - Publish v1.0.0

```bash
# Build package
python -m build

# Publish to Azure Artifacts
# (Adjust URL for your organization)
twine upload \
  --repository-url https://pkgs.dev.azure.com/YOUR_ORG/_packaging/YOUR_FEED/pypi/upload \
  dist/*

# Tag release
git tag -a v1.0.0 -m "Release v1.0.0: Initial platform toolkit"
git push origin v1.0.0
```

### Week 3: Update Original Repo

#### Monday - Update Dependencies

In `usf-fabric-cicd/pyproject.toml`:
```toml
[tool.poetry.dependencies]
python = "^3.9"
fabric-platform-toolkit = "^1.0.0"  # NEW
# ... existing dependencies
```

Or in `requirements.txt`:
```
fabric-platform-toolkit==1.0.0
```

#### Tuesday-Thursday - Update Imports

Update all files in `usf-fabric-cicd` to use the new package:

**ops/scripts/deploy_fabric.py:**
```python
# OLD
from ops.scripts.utilities.fabric_api import FabricAPI
from ops.scripts.utilities.retry_handler import RetryHandler
from ops.scripts.utilities.secret_manager import SecretManager

# NEW
from fabric_platform_toolkit.core import FabricAPI
from fabric_platform_toolkit.resilience import RetryHandler
from fabric_platform_toolkit.security import SecretManager
```

Do this for:
- `ops/scripts/deploy_fabric.py`
- `ops/scripts/deploy_fabric_bundle.py`
- `ops/scripts/promote_to_prod.py`
- `ops/scripts/bulk_delete_workspaces.py`
- All test files

#### Friday - Delete Old Utilities

```bash
cd usf-fabric-cicd

# Remove now-redundant files
rm ops/scripts/utilities/fabric_api.py
rm ops/scripts/utilities/fabric_git_connector.py
rm ops/scripts/utilities/workspace_manager.py
rm ops/scripts/utilities/retry_handler.py
rm ops/scripts/utilities/circuit_breaker.py
rm ops/scripts/utilities/telemetry.py
rm ops/scripts/utilities/health_check.py
rm ops/scripts/utilities/secret_manager.py
rm ops/scripts/utilities/feature_flags.py
# Keep any utilities NOT moved to toolkit

# Keep __init__.py files
# Keep output.py if it's specific to scripts

# Test everything still works
pytest tests/ -v
```

---

## ✅ Success Criteria

After 3 weeks, you should have:

1. **✅ New Repository Created**
   - `fabric-platform-toolkit` repository
   - All utilities extracted and organized
   - Complete test suite

2. **✅ Package Published**
   - Version 1.0.0 published to Azure Artifacts/internal PyPI
   - Accessible via `pip install fabric-platform-toolkit`

3. **✅ Original Repo Updated**
   - Uses `fabric-platform-toolkit` as dependency
   - Old utility files removed
   - All tests passing

4. **✅ Documentation Complete**
   - README with usage examples
   - API documentation
   - Migration notes

5. **✅ Team Trained**
   - Team knows how to use published package
   - Understands versioning strategy
   - Can request new features

---

## 📊 Validation

### Test Original Repo Still Works

```bash
cd usf-fabric-cicd

# Install with new dependency
pip install -e .

# Run all tests
pytest tests/unit/ tests/integration/ tests/e2e/ -v -m "not real_fabric"

# Should see: 101 passed, 1 skipped ✅

# Test a real deployment (optional)
python ops/scripts/deploy_fabric.py --env dev
```

### Test Package Can Be Reused

```bash
# In a new project
mkdir test-fabric-toolkit
cd test-fabric-toolkit
python -m venv venv
source venv/bin/activate
pip install fabric-platform-toolkit

# Create test script
cat > test.py << 'EOF'
from fabric_platform_toolkit.core import FabricAPI
from fabric_platform_toolkit.resilience import RetryHandler

print(f"Imported successfully!")
print(f"FabricAPI: {FabricAPI}")
print(f"RetryHandler: {RetryHandler}")
EOF

python test.py
# Should see imports work ✅
```

---

## 🎓 What You've Achieved

### Before (Monolith)
```
usf-fabric-cicd/
├── ops/scripts/utilities/  ← Mixed with deployment scripts
└── tests/                  ← All tests mixed together

❌ Other teams copy-paste utilities
❌ Version conflicts
❌ Hard to release updates
```

### After (Modular)
```
fabric-platform-toolkit/     ← Stable, versioned SDK
├── Published to Azure Artifacts
└── Used by usf-fabric-cicd

usf-fabric-cicd/             ← Deployment scripts only
└── Depends on fabric-platform-toolkit==1.0.0

✅ Other teams: pip install fabric-platform-toolkit
✅ Clear versioning (v1.0.0)
✅ Independent releases
```

---

## 🚀 Next Steps After Quick Start

Once this is working smoothly (2-3 months), consider:

1. **Extract Orchestration Engine** (Month 4-5)
   - If deployment patterns become complex
   - If multiple teams need orchestration

2. **Create Item Promotion Module** (Month 6-7)
   - If promotion logic grows
   - If multiple teams need different promotion rules

3. **Restructure CI/CD Pipelines** (Month 8-9)
   - Create reusable workflow templates
   - Separate environment configs

---

## 📞 Support

### Questions?

**Technical Questions:**
- How to publish to Azure Artifacts?
- How to version breaking changes?
- How to handle dependencies?

**Organizational Questions:**
- Who approves platform toolkit changes?
- How do teams request features?
- What's the support model?

**Common Issues:**
- "Tests failing after extraction" → Check imports, ensure all dependencies listed
- "Can't publish package" → Verify Azure Artifacts permissions
- "Version conflicts" → Use semantic versioning properly

---

## 📚 References

- **Main Guide:** `ENTERPRISE_ARCHITECTURE_GUIDE.md` (full enterprise architecture)
- **Current PR:** `PR_VALIDATION_REPORT.md` (what we just validated)
- **Production Status:** `PRODUCTION_HARDENING_COMPLETE.md` (current capabilities)

---

**Status:** Ready to execute  
**Estimated Effort:** 2-3 weeks with 1-2 engineers  
**Risk Level:** Low (can roll back if needed)  
**Impact:** High (enables reusability, faster releases)

**Recommendation:** Start with Quick Start, prove the value, then consider full architecture.
