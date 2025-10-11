"""
Environment-specific configuration management for Fabric deployments
Handles parameter substitution and environment overrides using ConfigManager
"""
import json
import re
from typing import Dict, Any, Optional
from pathlib import Path

from .constants import (
    get_sql_server_url,
    get_cosmos_db_url,
    is_valid_environment,
    VALID_ENVIRONMENTS
)

try:
    from .config_manager import ConfigManager, get_config_manager
except ImportError:
    # Fallback if config_manager is not available
    def get_config_manager():
        return None

class EnvironmentConfigManager:
    """Manage environment-specific configurations for Fabric deployments"""
    
    def __init__(self, environment: str, config_path: Optional[str] = None):
        self.environment = environment.lower()
        self.config_path = Path(config_path) if config_path else Path("./ops/config")
        
        # Try to use ConfigManager if available
        self.config_manager = get_config_manager()
        if self.config_manager and not self.config_manager.validate_environment(self.environment):
            available_envs = self.config_manager.list_environments()
            raise ValueError(
                f"Environment '{self.environment}' not found in project configuration. "
                f"Available environments: {available_envs}"
            )
        
        self.env_config = self._load_environment_config()
    
    def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration"""
        config_file = self.config_path / f"{self.environment}.json"
        
        if not config_file.exists():
            # Create default config if it doesn't exist
            default_config = self._get_default_config()
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration template using ConfigManager if available"""
        if self.config_manager:
            # Use ConfigManager for dynamic naming
            env_config = self.config_manager.get_environment_config(self.environment)
            return {
                "workspace": {
                    "name": self.config_manager.generate_name("workspace", self.environment),
                    "capacity": "Premium_P1" if self.environment == "prod" else "Trial"
                },
                "data_sources": {
                    "lakehouse_name": self.config_manager.generate_name("lakehouse", self.environment),
                    "storage_account": self.config_manager.generate_name("storage_account", self.environment),
                    "key_vault": self.config_manager.generate_name("key_vault", self.environment),
                    "data_gateway": self.config_manager.generate_name("data_gateway", self.environment)
                },
                "connection_strings": {
                    "sql_server": f"Server={self.config_manager.generate_name('sql_server', self.environment)}",
                    "cosmos_db": self.config_manager.generate_name("cosmos_db", self.environment),
                    "event_hub": self.config_manager.generate_name("event_hub", self.environment),
                    "service_bus": self.config_manager.generate_name("service_bus", self.environment)
                },
                "deployment": {
                    "mode": "standard" if self.environment != "prod" else "promote",
                    "validation_level": "strict" if self.environment == "prod" else "standard",
                    "approval_required": env_config.get("requires_approval", self.environment in ["test", "prod"]),
                    "auto_deploy": env_config.get("auto_deploy", self.environment == "dev")
                },
                "monitoring": {
                    "health_check_interval": "4h" if self.environment == "prod" else "8h",
                    "alert_threshold": {
                        "response_time_ms": 2000 if self.environment == "prod" else 5000,
                        "error_rate_percent": 1 if self.environment == "prod" else 5
                    }
                }
            }
        else:
            # Fallback to legacy behavior if ConfigManager not available
            return {
                "workspace": {
                    "name": f"fabric-cicd-{self.environment}",
                    "capacity": "Premium_P1" if self.environment == "prod" else "Trial"
                },
                "data_sources": {
                    "lakehouse_name": f"Lakehouse_{self.environment.title()}",
                    "storage_account": f"data{self.environment}",
                    "key_vault": f"kv-{self.environment}"
                },
                "connection_strings": {
                    "sql_server": get_sql_server_url(self.environment),
                    "cosmos_db": get_cosmos_db_url(self.environment)
                },
                "deployment": {
                    "mode": "standard" if self.environment != "prod" else "promote",
                    "validation_level": "strict" if self.environment == "prod" else "standard",
                    "approval_required": self.environment in ["test", "prod"]
                },
                "monitoring": {
                    "health_check_interval": "4h" if self.environment == "prod" else "8h",
                    "alert_threshold": {
                        "response_time_ms": 2000 if self.environment == "prod" else 5000,
                        "error_rate_percent": 1 if self.environment == "prod" else 5
                    }
                }
            }
    
    def substitute_parameters(self, content: str) -> str:
        """Substitute environment-specific parameters in content"""
        
        # Define parameter substitution patterns
        substitutions = {
            # Workspace parameters
            r'\$\{WORKSPACE_NAME\}': self.env_config["workspace"]["name"],
            r'\$\{ENVIRONMENT\}': self.environment.upper(),
            
            # Data source parameters
            r'\$\{LAKEHOUSE_NAME\}': self.env_config["data_sources"]["lakehouse_name"],
            r'\$\{STORAGE_ACCOUNT\}': self.env_config["data_sources"]["storage_account"],
            r'\$\{KEY_VAULT\}': self.env_config["data_sources"]["key_vault"],
            
            # Connection string parameters
            r'\$\{SQL_SERVER\}': self.env_config["connection_strings"]["sql_server"],
            r'\$\{COSMOS_DB\}': self.env_config["connection_strings"]["cosmos_db"],
        }
        
        # Apply substitutions
        result = content
        for pattern, replacement in substitutions.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def substitute_pipeline_parameters(self, pipeline_json: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute parameters in pipeline JSON definition"""
        
        # Convert to string, substitute, then back to dict
        pipeline_str = json.dumps(pipeline_json)
        substituted_str = self.substitute_parameters(pipeline_str)
        
        try:
            return json.loads(substituted_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON after parameter substitution: {e}")
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment-specific configuration"""
        return self.env_config.get("deployment", {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring-specific configuration"""
        return self.env_config.get("monitoring", {})
    
    def validate_environment_config(self) -> Dict[str, Any]:
        """Validate environment configuration"""
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        required_sections = ["workspace", "data_sources", "deployment"]
        for section in required_sections:
            if section not in self.env_config:
                validation_results["errors"].append(f"Missing required section: {section}")
                validation_results["valid"] = False
        
        # Validate workspace name format
        workspace_name = self.env_config.get("workspace", {}).get("name", "")
        if not re.match(r'^[a-zA-Z0-9-_]+$', workspace_name):
            validation_results["warnings"].append(f"Workspace name '{workspace_name}' contains invalid characters")
        
        return validation_results

# Example environment configurations
ENVIRONMENT_CONFIGS = {
    "dev": {
        "workspace_suffix": "-dev",
        "data_retention_days": 30,
        "auto_scale": False,
        "monitoring_level": "basic"
    },
    "test": {
        "workspace_suffix": "-test", 
        "data_retention_days": 90,
        "auto_scale": True,
        "monitoring_level": "standard"
    },
    "prod": {
        "workspace_suffix": "-prod",
        "data_retention_days": 365,
        "auto_scale": True,
        "monitoring_level": "comprehensive"
    }
}