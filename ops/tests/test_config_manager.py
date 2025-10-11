"""
Unit tests for ConfigManager
"""
import pytest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utilities.config_manager import ConfigManager, get_config_manager


class TestConfigManager:
    """Test suite for ConfigManager"""
    
    def test_load_valid_config(self, project_config_file):
        """Test loading a valid configuration file"""
        config = ConfigManager(str(project_config_file))
        
        assert config.config is not None
        assert config.config['project']['name'] == 'test-fabric-cicd'
        assert config.config['project']['prefix'] == 'test'
    
    def test_missing_config_file(self, temp_dir):
        """Test handling of missing configuration file"""
        with pytest.raises(FileNotFoundError):
            ConfigManager(str(temp_dir / "nonexistent.json"))
    
    def test_get_project_info(self, project_config_file):
        """Test retrieving project information"""
        config = ConfigManager(str(project_config_file))
        project_info = config.get_project_info()
        
        assert project_info['name'] == 'test-fabric-cicd'
        assert project_info['prefix'] == 'test'
        assert project_info['organization'] == 'test-org'
    
    def test_generate_workspace_name(self, project_config_file):
        """Test workspace name generation"""
        config = ConfigManager(str(project_config_file))
        
        dev_workspace = config.generate_name('workspace', 'dev')
        assert dev_workspace == 'test-fabric-dev'
        
        prod_workspace = config.generate_name('workspace', 'prod')
        assert prod_workspace == 'test-fabric-prod'
    
    def test_generate_lakehouse_name(self, project_config_file):
        """Test lakehouse name generation"""
        config = ConfigManager(str(project_config_file))
        
        lakehouse = config.generate_name('lakehouse', 'dev')
        assert lakehouse == 'TEST_Lakehouse_Dev'
    
    def test_generate_storage_account_name(self, project_config_file):
        """Test storage account name generation"""
        config = ConfigManager(str(project_config_file))
        
        storage = config.generate_name('storage_account', 'dev')
        assert storage == 'testdatadev'
    
    def test_list_environments(self, project_config_file):
        """Test listing all environments"""
        config = ConfigManager(str(project_config_file))
        environments = config.list_environments()
        
        assert 'dev' in environments
        assert 'test' in environments
        assert 'prod' in environments
        assert len(environments) == 3
    
    def test_validate_environment(self, project_config_file):
        """Test environment validation"""
        config = ConfigManager(str(project_config_file))
        
        assert config.validate_environment('dev') is True
        assert config.validate_environment('test') is True
        assert config.validate_environment('prod') is True
        assert config.validate_environment('invalid') is False
    
    def test_get_environment_config(self, project_config_file):
        """Test retrieving environment-specific configuration"""
        config = ConfigManager(str(project_config_file))
        
        dev_config = config.get_environment_config('dev')
        assert dev_config['auto_deploy'] is True
        assert dev_config['requires_approval'] is False
        
        prod_config = config.get_environment_config('prod')
        assert prod_config['auto_deploy'] is False
        assert prod_config['requires_approval'] is True
    
    def test_invalid_environment(self, project_config_file):
        """Test handling of invalid environment"""
        config = ConfigManager(str(project_config_file))
        
        with pytest.raises(ValueError):
            config.get_environment_config('invalid')
    
    def test_get_resource_group_name(self, project_config_file):
        """Test resource group name generation"""
        config = ConfigManager(str(project_config_file))
        
        rg_name = config.get_resource_group_name('dev')
        assert rg_name == 'test-fabric-dev-rg'
    
    def test_export_env_vars(self, project_config_file):
        """Test exporting configuration as environment variables"""
        config = ConfigManager(str(project_config_file))
        
        env_vars = config.export_env_vars('dev')
        
        assert 'PROJECT_NAME' in env_vars
        assert env_vars['PROJECT_NAME'] == 'test-fabric-cicd'
        assert 'PROJECT_PREFIX' in env_vars
        assert env_vars['PROJECT_PREFIX'] == 'test'
        assert 'FABRIC_ENVIRONMENT' in env_vars
        assert env_vars['FABRIC_ENVIRONMENT'] == 'dev'
    
    def test_missing_required_fields(self, temp_dir):
        """Test validation of missing required fields"""
        invalid_config = {
            "project": {
                "name": "test"
                # Missing 'prefix'
            }
        }
        
        config_path = temp_dir / "invalid_config.json"
        with open(config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        with pytest.raises(ValueError):
            ConfigManager(str(config_path))
    
    def test_naming_pattern_not_found(self, project_config_file):
        """Test handling of non-existent naming pattern"""
        config = ConfigManager(str(project_config_file))
        
        with pytest.raises(ValueError):
            config.get_naming_pattern('nonexistent_resource')
    
    def test_custom_pattern_generation(self, project_config_file):
        """Test custom pattern generation"""
        config = ConfigManager(str(project_config_file))
        
        custom_name = config.generate_name_from_pattern(
            "{prefix}-custom-{environment}",
            "dev"
        )
        assert custom_name == "test-custom-dev"
    
    def test_azure_config(self, project_config_file):
        """Test retrieving Azure configuration"""
        config = ConfigManager(str(project_config_file))
        azure_config = config.get_azure_config()
        
        assert azure_config['tenant_id'] == 'test-tenant-id'
        assert azure_config['subscription_id'] == 'test-subscription-id'
    
    def test_github_config(self, project_config_file):
        """Test retrieving GitHub configuration"""
        config = ConfigManager(str(project_config_file))
        github_config = config.get_github_config()
        
        assert github_config['organization'] == 'test-org'
        assert github_config['repository'] == 'test-repo'
    
    def test_contacts_config(self, project_config_file):
        """Test retrieving contacts configuration"""
        config = ConfigManager(str(project_config_file))
        contacts = config.get_contacts()
        
        assert contacts['data_owner'] == 'data@test.com'
        assert contacts['technical_lead'] == 'tech@test.com'
    
    def test_env_var_substitution(self, project_config_file, mock_env_vars):
        """Test environment variable substitution in config"""
        # Create config with env var references
        config_with_vars = {
            "project": {
                "name": "test-fabric-cicd",
                "prefix": "test"
            },
            "naming_patterns": {
                "workspace": "{prefix}-fabric-{environment}"
            },
            "azure": {
                "tenant_id": "${AZURE_TENANT_ID}",
                "client_id": "${AZURE_CLIENT_ID}"
            },
            "environments": {
                "dev": {
                    "description": "Dev",
                    "requires_approval": False,
                    "auto_deploy": True
                }
            }
        }
        
        config_path = project_config_file.parent / "config_with_vars.json"
        with open(config_path, 'w') as f:
            json.dump(config_with_vars, f)
        
        config = ConfigManager(str(config_path))
        azure_config = config.get_azure_config()
        
        assert azure_config['tenant_id'] == 'test-tenant-id'
        assert azure_config['client_id'] == 'test-client-id'
