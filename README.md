# Microsoft Fabric CI/CD Enterprise Solution

**The most robust CI/CD setup for Microsoft Fabric with GitHub** - A production-ready, configurable, and reusable CI/CD framework for Microsoft Fabric with comprehensive data governance, quality validation, and multi-environment deployment capabilities.

## 🚀 Quick Start

**See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions**

### 5-Minute Setup
```bash
# 1. Create virtual environment
python -m venv fabric-env && source fabric-env/bin/activate

# 2. Install dependencies
pip install -r ops/requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your Azure/GitHub credentials

# 4. Initialize project
python init_project_config.py

# 5. Test validation
python ops/scripts/validate_data_contracts.py --contracts-dir governance/data_contracts
python ops/scripts/validate_dq_rules.py --rules-dir governance/dq_rules

# 5. Initialize project configuration
python init_project_config.py

# 6. Test deployment
python ops/scripts/deploy_fabric.py --environment dev --mode standard
```

### Alternative Setup (Python venv)
```bash
# Create virtual environment
python3 -m venv fabric-cicd-env
source fabric-cicd-env/bin/activate

# Continue with steps 3-6 above
cp .env.example .env
# ... rest of setup
```

## Notes
- Scripts under `ops/scripts/utilities/*` are placeholders: integrate with real Fabric, Purview, and Power BI REST APIs.
- Add your notebooks, SQL, and dataflows under `data/` and BI assets under `bi/`.
