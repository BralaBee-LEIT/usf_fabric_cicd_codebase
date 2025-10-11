"""
Pytest configuration and fixtures for Fabric CI/CD tests
"""
import os
import sys
import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_project_config():
    """Sample project configuration"""
    return {
        "project": {
            "name": "test-fabric-cicd",
            "prefix": "test",
            "description": "Test Fabric CI/CD",
            "organization": "test-org"
        },
        "naming_patterns": {
            "workspace": "{prefix}-fabric-{environment}",
            "lakehouse": "{prefix_upper}_Lakehouse_{environment_title}",
            "storage_account": "{prefix_clean}data{environment}"
        },
        "azure": {
            "tenant_id": "test-tenant-id",
            "subscription_id": "test-subscription-id",
            "client_id": "test-client-id",
            "resource_group_pattern": "{prefix}-fabric-{environment}-rg"
        },
        "environments": {
            "dev": {
                "description": "Development environment",
                "requires_approval": False,
                "auto_deploy": True
            },
            "test": {
                "description": "Test environment",
                "requires_approval": True,
                "auto_deploy": False
            },
            "prod": {
                "description": "Production environment",
                "requires_approval": True,
                "auto_deploy": False
            }
        },
        "github": {
            "organization": "test-org",
            "repository": "test-repo"
        },
        "contacts": {
            "data_owner": "data@test.com",
            "technical_lead": "tech@test.com"
        }
    }


@pytest.fixture
def sample_data_contract():
    """Sample data contract for testing"""
    return {
        "dataset": "gold.test_incidents",
        "owner": "data-owner@example.com",
        "description": "Test incidents dataset",
        "slas": {
            "freshness": "PT2H",
            "completeness": "99.9%"
        },
        "schema": [
            {
                "name": "incident_id",
                "type": "string",
                "nullable": False,
                "description": "Unique incident identifier"
            },
            {
                "name": "opened_at",
                "type": "timestamp",
                "nullable": False,
                "description": "Incident open timestamp"
            },
            {
                "name": "priority",
                "type": "string",
                "nullable": True,
                "description": "Incident priority level"
            }
        ],
        "breaking_changes": [
            "removing columns",
            "changing types"
        ]
    }


@pytest.fixture
def sample_dq_rules():
    """Sample DQ rules for testing"""
    return {
        "rules": [
            {
                "name": "test_not_null",
                "dataset": "silver.test_table",
                "check": "not_null",
                "columns": ["id", "name"],
                "threshold": "100%"
            },
            {
                "name": "test_unique",
                "dataset": "silver.test_table",
                "check": "unique",
                "columns": ["id"],
                "threshold": "100%"
            },
            {
                "name": "test_range",
                "dataset": "silver.test_table",
                "check": "range",
                "columns": ["age"],
                "min": 0,
                "max": 120,
                "threshold": "95%"
            }
        ]
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set mock environment variables"""
    env_vars = {
        "AZURE_TENANT_ID": "test-tenant-id",
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_CLIENT_SECRET": "test-secret",
        "AZURE_SUBSCRIPTION_ID": "test-subscription-id",
        "DATA_OWNER_EMAIL": "owner@test.com",
        "TECHNICAL_LEAD_EMAIL": "lead@test.com"
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars


@pytest.fixture
def project_config_file(temp_dir, sample_project_config):
    """Create a temporary project.config.json file"""
    config_path = temp_dir / "project.config.json"
    with open(config_path, 'w') as f:
        json.dump(sample_project_config, f, indent=2)
    return config_path


@pytest.fixture
def data_contract_file(temp_dir, sample_data_contract):
    """Create a temporary data contract YAML file"""
    import yaml
    contract_dir = temp_dir / "governance" / "data_contracts"
    contract_dir.mkdir(parents=True, exist_ok=True)
    contract_path = contract_dir / "test_contract.yaml"
    
    with open(contract_path, 'w') as f:
        yaml.dump(sample_data_contract, f)
    
    return contract_path


@pytest.fixture
def dq_rules_file(temp_dir, sample_dq_rules):
    """Create a temporary DQ rules YAML file"""
    import yaml
    rules_dir = temp_dir / "governance" / "dq_rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    rules_path = rules_dir / "test_rules.yaml"
    
    with open(rules_path, 'w') as f:
        yaml.dump(sample_dq_rules, f)
    
    return rules_path
