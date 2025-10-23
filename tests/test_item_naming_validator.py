"""
Unit tests for ItemNamingValidator utility
"""
import pytest
from pathlib import Path
import sys

# Add utilities to path
UTILITIES_PATH = Path(__file__).parent.parent / "ops" / "scripts" / "utilities"
if str(UTILITIES_PATH) not in sys.path:
    sys.path.insert(0, str(UTILITIES_PATH))

from item_naming_validator import ItemNamingValidator, ValidationResult


class TestItemNamingValidator:
    """Test suite for ItemNamingValidator"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance with default config"""
        # Use the naming_standards.yaml from the repo root
        config_path = Path(__file__).parent.parent / "naming_standards.yaml"
        return ItemNamingValidator(config_path=str(config_path))
    
    def test_valid_lakehouse_name(self, validator):
        """Test validation of valid lakehouse name"""
        result = validator.validate("BRONZE_CustomerData_Lakehouse", "Lakehouse")
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_invalid_lakehouse_name(self, validator):
        """Test validation of invalid lakehouse name"""
        result = validator.validate("Invalid Name!", "Lakehouse")
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_valid_sequential_notebook(self, validator):
        """Test validation of valid sequential notebook name"""
        result = validator.validate("01_DataIngestion_Notebook", "Notebook")
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_valid_pipeline_name(self, validator):
        """Test validation of valid pipeline name"""
        result = validator.validate("CustomerETL_Pipeline", "DataPipeline")
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_ticket_based_naming(self, validator):
        """Test validation with ticket-based naming"""
        result = validator.validate(
            "JIRA12345_BRONZE_Sales_Lakehouse",
            "Lakehouse",
            ticket_id="JIRA-12345"
        )
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_suggest_name_lakehouse(self, validator):
        """Test name suggestion for lakehouse"""
        suggested = validator.suggest_name(
            base_name="CustomerData",
            item_type="Lakehouse",
            layer="BRONZE"
        )
        assert "BRONZE" in suggested
        assert "CustomerData" in suggested
        assert "Lakehouse" in suggested
    
    def test_suggest_name_notebook(self, validator):
        """Test name suggestion for notebook"""
        suggested = validator.suggest_name(
            base_name="DataIngestion",
            item_type="Notebook",
            sequence=1
        )
        assert "01" in suggested
        assert "DataIngestion" in suggested
        assert "Notebook" in suggested
    
    def test_suggest_name_with_ticket(self, validator):
        """Test name suggestion with ticket ID"""
        suggested = validator.suggest_name(
            base_name="Sales",
            item_type="Lakehouse",
            layer="SILVER",
            ticket_id="JIRA-12345"
        )
        assert "JIRA12345" in suggested
        assert "SILVER" in suggested
        assert "Sales" in suggested
    
    def test_batch_validation(self, validator):
        """Test batch validation of multiple items"""
        items = [
            ("BRONZE_Customers_Lakehouse", "Lakehouse"),
            ("Invalid Name!", "Warehouse"),
            ("01_Transform_Notebook", "Notebook")
        ]
        results = validator.validate_batch(items)
        assert len(results) == 3
        assert results[0].is_valid
        assert not results[1].is_valid
        assert results[2].is_valid
    
    def test_reserved_word_detection(self, validator):
        """Test detection of reserved words"""
        result = validator.validate("TEMP_Lakehouse", "Lakehouse")
        # Reserved words should trigger warnings or errors
        assert len(result.warnings) > 0 or len(result.errors) > 0
    
    def test_max_length_validation(self, validator):
        """Test max length validation"""
        long_name = "A" * 300 + "_Lakehouse"
        result = validator.validate(long_name, "Lakehouse")
        assert not result.is_valid
        assert any("length" in error.lower() for error in result.errors)
    
    def test_compliance_report_generation(self, validator):
        """Test compliance report generation"""
        items = [
            ("BRONZE_Valid_Lakehouse", "Lakehouse"),
            ("InvalidName!", "Warehouse")
        ]
        results = validator.validate_batch(items)
        report = validator.generate_compliance_report(results)
        
        assert "total_items" in report
        assert "valid_items" in report
        assert "invalid_items" in report
        assert report["total_items"] == 2
        assert report["valid_items"] == 1
        assert report["invalid_items"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
