#!/usr/bin/env python3
"""
Project Configuration Manager
Manages project-specific configuration and naming patterns for Microsoft Fabric CI/CD
"""

import json
import os
import re
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages project configuration and naming patterns"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager
        
        Args:
            config_path: Path to project.config.json file
        """
        if config_path is None:
            # Look for config file in current directory or parent directories
            current_dir = Path.cwd()
            config_path = self._find_config_file(current_dir)
        
        self.config_path = Path(config_path) if config_path else None
        self.config = self._load_config()
        self._validate_config()
    
    def _find_config_file(self, start_path: Path) -> Optional[str]:
        """Find project.config.json in current or parent directories"""
        for path in [start_path] + list(start_path.parents):
            config_file = path / "project.config.json"
            if config_file.exists():
                return str(config_file)
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path or not self.config_path.exists():
            raise FileNotFoundError(
                "project.config.json not found. Please create it using init_project_config.py"
            )
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Replace environment variables
            config_str = json.dumps(config)
            config_str = self._substitute_env_vars(config_str)
            config = json.loads(config_str)
            
            return config
        except (json.JSONDecodeError, IOError) as e:
            raise ValueError(f"Failed to load configuration: {e}")
    
    def _substitute_env_vars(self, text: str) -> str:
        """Replace ${VAR_NAME} patterns with environment variables"""
        def replace_env_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))  # Return original if not found
        
        return re.sub(r'\$\{([^}]+)\}', replace_env_var, text)
    
    def _validate_config(self):
        """Validate required configuration fields"""
        required_sections = ['project', 'naming_patterns', 'environments']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Required configuration section '{section}' not found")
        
        required_project_fields = ['name', 'prefix']
        for field in required_project_fields:
            if field not in self.config['project']:
                raise ValueError(f"Required project field '{field}' not found")
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information"""
        return self.config['project']
    
    def get_naming_pattern(self, resource_type: str) -> str:
        """Get naming pattern for a resource type
        
        Args:
            resource_type: Type of resource (workspace, lakehouse, etc.)
            
        Returns:
            Naming pattern string with placeholders
        """
        patterns = self.config.get('naming_patterns', {})
        if resource_type not in patterns:
            raise ValueError(f"Naming pattern for '{resource_type}' not found")
        return patterns[resource_type]
    
    def generate_name(self, resource_type: str, environment: str, **kwargs) -> str:
        """Generate a resource name based on patterns
        
        Args:
            resource_type: Type of resource
            environment: Environment (dev, test, prod)
            **kwargs: Additional variables for substitution
            
        Returns:
            Generated resource name
        """
        pattern = self.get_naming_pattern(resource_type)
        
        # Standard substitution variables
        substitutions = {
            'prefix': self.config['project']['prefix'],
            'prefix_upper': self.config['project']['prefix'].upper().replace('-', '_'),
            'prefix_clean': self.config['project']['prefix'].replace('-', ''),
            'environment': environment,
            'environment_title': environment.title(),
            'organization': self.config['project'].get('organization', ''),
            **kwargs
        }
        
        # Replace placeholders
        result = pattern
        for key, value in substitutions.items():
            result = result.replace(f'{{{key}}}', str(value))
        
        return result
    
    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get configuration for a specific environment"""
        envs = self.config.get('environments', {})
        if environment not in envs:
            raise ValueError(f"Environment '{environment}' not found in configuration")
        return envs[environment]
    
    def get_azure_config(self) -> Dict[str, Any]:
        """Get Azure configuration"""
        return self.config.get('azure', {})
    
    def get_github_config(self) -> Dict[str, Any]:
        """Get GitHub configuration"""
        return self.config.get('github', {})
    
    def get_contacts(self) -> Dict[str, Any]:
        """Get contact information"""
        return self.config.get('contacts', {})
    
    def get_purview_config(self) -> Dict[str, Any]:
        """Get Purview configuration"""
        return self.config.get('purview', {})
    
    def list_environments(self) -> list:
        """List all configured environments"""
        return list(self.config.get('environments', {}).keys())
    
    def validate_environment(self, environment: str) -> bool:
        """Validate if environment exists in configuration"""
        return environment in self.config.get('environments', {})
    
    def get_resource_group_name(self, environment: str) -> str:
        """Generate resource group name for environment"""
        pattern = self.config['azure'].get('resource_group_pattern', '{prefix}-fabric-{environment}-rg')
        return self.generate_name_from_pattern(pattern, environment)
    
    def generate_name_from_pattern(self, pattern: str, environment: str, **kwargs) -> str:
        """Generate name from a custom pattern
        
        Args:
            pattern: Custom naming pattern
            environment: Environment name
            **kwargs: Additional substitution variables
            
        Returns:
            Generated name
        """
        substitutions = {
            'prefix': self.config['project']['prefix'],
            'prefix_upper': self.config['project']['prefix'].upper().replace('-', '_'),
            'prefix_clean': self.config['project']['prefix'].replace('-', ''),
            'environment': environment,
            'environment_title': environment.title(),
            'organization': self.config['project'].get('organization', ''),
            **kwargs
        }
        
        result = pattern
        for key, value in substitutions.items():
            result = result.replace(f'{{{key}}}', str(value))
        
        return result
    
    def export_env_vars(self, environment: Optional[str] = None) -> Dict[str, str]:
        """Export configuration as environment variables
        
        Args:
            environment: Optional environment to include environment-specific vars
            
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        # Project info
        project = self.config['project']
        env_vars.update({
            'PROJECT_NAME': project['name'],
            'PROJECT_PREFIX': project['prefix'],
            'PROJECT_ORGANIZATION': project.get('organization', '')
        })
        
        # Azure config
        azure = self.config.get('azure', {})
        for key, value in azure.items():
            if key != 'resource_group_pattern':
                env_vars[f'AZURE_{key.upper()}'] = str(value)
        
        # GitHub config
        github = self.config.get('github', {})
        for key, value in github.items():
            if key != 'teams':
                env_vars[f'GITHUB_{key.upper()}'] = str(value)
        
        # Contacts
        contacts = self.config.get('contacts', {})
        for key, value in contacts.items():
            env_vars[f'CONTACT_{key.upper()}'] = str(value)
        
        # Environment-specific variables
        if environment and environment in self.config.get('environments', {}):
            env_vars['FABRIC_ENVIRONMENT'] = environment
            
            # Generate resource names for this environment
            for resource_type in self.config.get('naming_patterns', {}):
                try:
                    name = self.generate_name(resource_type, environment)
                    var_name = f'FABRIC_{resource_type.upper()}'
                    env_vars[var_name] = name
                except (KeyError, ValueError, TypeError) as e:
                    # Skip if pattern not found or invalid environment/pattern
                    logger.debug(f"Failed to generate name for {resource_type}: {type(e).__name__} - {e}")
                    continue
        
        return env_vars


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """Get a ConfigManager instance (singleton pattern)"""
    if not hasattr(get_config_manager, '_instance'):
        get_config_manager._instance = ConfigManager(config_path)
    return get_config_manager._instance


# Convenience functions
def get_project_prefix() -> str:
    """Get the project prefix"""
    return get_config_manager().config['project']['prefix']


def generate_resource_name(resource_type: str, environment: str, **kwargs) -> str:
    """Generate a resource name"""
    return get_config_manager().generate_name(resource_type, environment, **kwargs)


def get_workspace_name(environment: str) -> str:
    """Get workspace name for environment"""
    return generate_resource_name('workspace', environment)


def get_lakehouse_name(environment: str) -> str:
    """Get lakehouse name for environment"""
    return generate_resource_name('lakehouse', environment)


if __name__ == "__main__":
    # Example usage
    try:
        config = ConfigManager()
        print("Project Configuration:")
        print(f"  Name: {config.get_project_info()['name']}")
        print(f"  Prefix: {config.get_project_info()['prefix']}")
        
        print("\nEnvironments:")
        for env in config.list_environments():
            print(f"  {env}:")
            print(f"    Workspace: {config.generate_name('workspace', env)}")
            print(f"    Lakehouse: {config.generate_name('lakehouse', env)}")
            print(f"    Storage: {config.generate_name('storage_account', env)}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please run init_project_config.py to create project configuration")