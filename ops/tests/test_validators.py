"""
Unit tests for data contract and DQ rules validators
"""
import pytest
import yaml
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.validate_data_contracts import DataContractValidator
from scripts.validate_dq_rules import DQRulesValidator


class TestDataContractValidator:
    """Test suite for DataContractValidator"""
    
    def test_validate_valid_contract(self, temp_dir, sample_data_contract):
        """Test validation of a valid data contract"""
        # Create contract directory and file
        contract_dir = temp_dir / "governance" / "data_contracts"
        contract_dir.mkdir(parents=True, exist_ok=True)
        contract_file = contract_dir / "test_contract.yaml"
        
        with open(contract_file, 'w') as f:
            yaml.dump(sample_data_contract, f)
        
        # Validate
        validator = DataContractValidator(str(contract_dir))
        contracts = validator.discover_contracts()
        
        assert len(contracts) == 1
        assert contracts[0].name == "test_contract.yaml"
    
    def test_missing_required_field(self, temp_dir):
        """Test validation fails for missing required fields"""
        invalid_contract = {
            "dataset": "gold.test",
            # Missing 'owner' and 'schema'
        }
        
        contract_dir = temp_dir / "governance" / "data_contracts"
        contract_dir.mkdir(parents=True, exist_ok=True)
        contract_file = contract_dir / "invalid_contract.yaml"
        
        with open(contract_file, 'w') as f:
            yaml.dump(invalid_contract, f)
        
        validator = DataContractValidator(str(contract_dir))
        result = validator.validate_contract_schema(invalid_contract)
        
        # Should have issues for missing fields
        issue_types = [issue['type'] for issue in result]
        assert 'schema' in issue_types
    
    def test_invalid_owner_email(self, temp_dir):
        """Test validation fails for invalid owner email"""
        invalid_contract = {
            "dataset": "gold.test",
            "owner": "not-an-email",  # Invalid email
            "schema": [
                {"name": "id", "type": "string", "nullable": False}
            ]
        }
        
        validator = DataContractValidator()
        result = validator.validate_contract_schema(invalid_contract)
        
        # Should have issue for invalid email
        messages = [issue['message'] for issue in result]
        assert any('email' in msg.lower() for msg in messages)
    
    def test_dataset_naming_convention(self, temp_dir):
        """Test dataset naming convention validation"""
        validator = DataContractValidator()
        
        # Valid names
        assert validator._is_valid_dataset_name("gold.incidents")
        assert validator._is_valid_dataset_name("silver.customer_data")
        
        # Invalid names
        assert not validator._is_valid_dataset_name("InvalidName")
        assert not validator._is_valid_dataset_name("gold")
    
    def test_multiple_contracts_discovery(self, temp_dir, sample_data_contract):
        """Test discovery of multiple data contract files"""
        contract_dir = temp_dir / "governance" / "data_contracts"
        contract_dir.mkdir(parents=True, exist_ok=True)
        
        # Create multiple contracts
        for i in range(3):
            contract_file = contract_dir / f"contract_{i}.yaml"
            with open(contract_file, 'w') as f:
                yaml.dump(sample_data_contract, f)
        
        validator = DataContractValidator(str(contract_dir))
        contracts = validator.discover_contracts()
        
        assert len(contracts) == 3


class TestDQRulesValidator:
    """Test suite for DQRulesValidator"""
    
    def test_validate_valid_rules(self, temp_dir, sample_dq_rules):
        """Test validation of valid DQ rules"""
        rules_dir = temp_dir / "governance" / "dq_rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rules_file = rules_dir / "test_rules.yaml"
        
        with open(rules_file, 'w') as f:
            yaml.dump(sample_dq_rules, f)
        
        validator = DQRulesValidator(str(rules_dir))
        rules_files = validator.discover_dq_rules()
        
        assert len(rules_files) == 1
        assert rules_files[0].name == "test_rules.yaml"
    
    def test_missing_rules_section(self, temp_dir):
        """Test validation fails for missing rules section"""
        invalid_rules = {
            "metadata": "some data"
            # Missing 'rules' section
        }
        
        rules_dir = temp_dir / "governance" / "dq_rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rules_file = rules_dir / "invalid_rules.yaml"
        
        with open(rules_file, 'w') as f:
            yaml.dump(invalid_rules, f)
        
        validator = DQRulesValidator(str(rules_dir))
        result = validator.validate_rule_file(rules_file)
        
        assert not result.valid
        assert any('rules' in issue['message'].lower() for issue in result.issues)
    
    def test_duplicate_rule_names(self, temp_dir):
        """Test detection of duplicate rule names"""
        duplicate_rules = {
            "rules": [
                {
                    "name": "duplicate_rule",
                    "dataset": "silver.test",
                    "check": "not_null",
                    "columns": ["id"],
                    "threshold": "100%"
                },
                {
                    "name": "duplicate_rule",  # Duplicate name
                    "dataset": "silver.test",
                    "check": "unique",
                    "columns": ["id"],
                    "threshold": "100%"
                }
            ]
        }
        
        rules_dir = temp_dir / "governance" / "dq_rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rules_file = rules_dir / "duplicate_rules.yaml"
        
        with open(rules_file, 'w') as f:
            yaml.dump(duplicate_rules, f)
        
        validator = DQRulesValidator(str(rules_dir))
        result = validator.validate_rule_file(rules_file)
        
        # Should have warning about duplicates
        assert len(result.warnings) > 0 or len(result.issues) > 0
    
    def test_invalid_threshold_format(self, temp_dir):
        """Test detection of invalid threshold format"""
        invalid_rules = {
            "rules": [
                {
                    "name": "test_rule",
                    "dataset": "silver.test",
                    "check": "not_null",
                    "columns": ["id"],
                    "threshold": "invalid"  # Invalid format
                }
            ]
        }
        
        rules_dir = temp_dir / "governance" / "dq_rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rules_file = rules_dir / "invalid_threshold.yaml"
        
        with open(rules_file, 'w') as f:
            yaml.dump(invalid_rules, f)
        
        validator = DQRulesValidator(str(rules_dir))
        result = validator.validate_rule_file(rules_file)
        
        # Should have issue with threshold
        threshold_issues = [
            issue for issue in result.issues 
            if 'threshold' in issue.get('message', '').lower()
        ]
        assert len(threshold_issues) > 0
    
    def test_supported_check_types(self, temp_dir):
        """Test validation of different check types"""
        rules = {
            "rules": [
                {
                    "name": "not_null_check",
                    "dataset": "silver.test",
                    "check": "not_null",
                    "columns": ["id"],
                    "threshold": "100%"
                },
                {
                    "name": "unique_check",
                    "dataset": "silver.test",
                    "check": "unique",
                    "columns": ["id"],
                    "threshold": "100%"
                },
                {
                    "name": "range_check",
                    "dataset": "silver.test",
                    "check": "range",
                    "columns": ["age"],
                    "min": 0,
                    "max": 120,
                    "threshold": "95%"
                }
            ]
        }
        
        rules_dir = temp_dir / "governance" / "dq_rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rules_file = rules_dir / "check_types.yaml"
        
        with open(rules_file, 'w') as f:
            yaml.dump(rules, f)
        
        validator = DQRulesValidator(str(rules_dir))
        result = validator.validate_rule_file(rules_file)
        
        assert result.rule_count == 3
    
    def test_multiple_rules_files_discovery(self, temp_dir, sample_dq_rules):
        """Test discovery of multiple DQ rules files"""
        rules_dir = temp_dir / "governance" / "dq_rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Create multiple rules files
        for i in range(3):
            rules_file = rules_dir / f"rules_{i}.yaml"
            with open(rules_file, 'w') as f:
                yaml.dump(sample_dq_rules, f)
        
        validator = DQRulesValidator(str(rules_dir))
        rules_files = validator.discover_dq_rules()
        
        assert len(rules_files) == 3
    
    def test_dataset_coverage_tracking(self, temp_dir, sample_dq_rules):
        """Test tracking of dataset coverage across rules"""
        rules_dir = temp_dir / "governance" / "dq_rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        rules_file = rules_dir / "test_rules.yaml"
        
        with open(rules_file, 'w') as f:
            yaml.dump(sample_dq_rules, f)
        
        validator = DQRulesValidator(str(rules_dir))
        result = validator.validate_rule_file(rules_file)
        
        assert len(result.dataset_coverage) > 0
        assert "silver.test_table" in result.dataset_coverage
