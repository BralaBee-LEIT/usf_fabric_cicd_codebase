# Data Quality Rules Multi-File Support Implementation

## Overview

The Microsoft Fabric CI/CD project now supports **multiple data quality rules YAML files** with comprehensive validation, governance, and CI/CD integration, complementing the existing data contracts system.

## Key Features

### ✅ Multi-DQ Rules File Support
- **Automatic Discovery**: Finds all `.yaml` files in `governance/dq_rules/` directory
- **Batch Validation**: Validates all DQ rules files in a single operation
- **Individual Reporting**: Detailed validation results for each rules file
- **Schema Compliance**: Enforces consistent rules structure across all files

### ✅ Data Quality Rules Examples
The system includes sample DQ rules files demonstrating various scenarios:

1. **`dq_rules.yaml`** - Original incident validation rules
2. **`customer_dq_rules.yaml`** - Customer data quality checks
3. **`sales_dq_rules.yaml`** - Sales transaction validation rules

### ✅ Comprehensive Validation Engine
The `validate_dq_rules.py` script provides:

- **Structure Validation**: Ensures proper YAML format and required sections
- **Rule Schema Checking**: Validates individual rule definitions and parameters
- **Field Type Validation**: Checks data types, thresholds, and constraint formats
- **Metadata Compliance**: Verifies metadata sections and recommended practices
- **Cross-Rule Validation**: Checks for duplicate rule names and consistency

## Current DQ Rules Files

```
governance/dq_rules/
├── dq_rules.yaml           # Original incident validation rules
├── customer_dq_rules.yaml  # Customer data quality checks  
└── sales_dq_rules.yaml     # Sales transaction validation
```

## DQ Rules File Structure

Each rules file follows a standardized schema:

```yaml
rules:
  - name: rule_name
    dataset: bronze.table_name
    check: not_null|unique|range|pattern|completeness|etc
    columns: [column1, column2]
    threshold: 100%|99.5%|0.95
    severity: low|medium|high|critical
    description: "Rule purpose and validation logic"
    owner: team@company.com

metadata:
  version: "1.0.0"
  description: "Rules description"
  owner: "team@company.com"
  last_updated: "2024-10-08"

datasets:
  - covered.dataset1
  - covered.dataset2

categories:
  - completeness
  - accuracy
  - validity
```

## Supported Check Types

The validator recognizes these standard check types:

### Core Data Quality Checks
- **`not_null`**: Completeness validation
- **`unique`**: Uniqueness constraints
- **`range`**: Numeric range validation
- **`length`**: String length constraints
- **`pattern`**: Regex pattern matching
- **`enum`**: Valid values enumeration

### Quality Dimensions
- **`completeness`**: Data completeness metrics
- **`accuracy`**: Data accuracy validation
- **`consistency`**: Cross-field consistency
- **`validity`**: Format and business rule validation
- **`timeliness`**: Temporal data validation
- **`uniqueness`**: Duplicate detection
- **`custom`**: Custom validation logic

## Validation Features

### Rule Structure Validation
- Required fields enforcement (`name`, `dataset`, `check`)
- Optional fields validation (`threshold`, `severity`, `description`)
- Field format checking (naming conventions, lengths)
- Column list validation for multi-column rules

### Threshold Validation
- **Percentage format**: `95%`, `99.5%`, `100%`
- **Decimal format**: `0.95`, `0.995`, `1.0`
- **Range validation**: 0-100% for percentages, 0-1 for decimals

### Severity Classification
- **`low`**: Minor data quality issues
- **`medium`**: Moderate impact on data quality
- **`high`**: Significant data quality concerns
- **`critical`**: Severe issues requiring immediate attention

### Metadata Validation
- **Version tracking**: Semantic versioning support
- **Ownership**: Team/individual responsibility assignment
- **Documentation**: Comprehensive rule descriptions
- **Dataset coverage**: Explicit dataset enumeration

## CI/CD Integration

### GitHub Actions Workflow
The `fabric-cicd-pipeline.yml` includes DQ rules validation:

```yaml
- name: Validate data quality rules
  run: |
    python ops/scripts/validate_dq_rules.py \
      --rules-dir governance/dq_rules \
      --output-format github

- name: Upload DQ rules validation results
  uses: actions/upload-artifact@v4
  with:
    name: dq-rules-validation
    path: dq_rules_validation_report.json
```

### Setup Script Integration
The `setup.sh` script validates all DQ rules during project setup:

```bash
# Validates all .yaml files in governance/dq_rules
python3 ops/scripts/validate_dq_rules.py \
  --rules-dir governance/dq_rules --quiet
```

## Usage Examples

### Validate All DQ Rules Files
```bash
python ops/scripts/validate_dq_rules.py \
  --rules-dir governance/dq_rules
```

### Generate JSON Report
```bash  
python ops/scripts/validate_dq_rules.py \
  --rules-dir governance/dq_rules \
  --output-format json
```

### Validate Specific Rules File
```bash
python ops/scripts/validate_dq_rules.py \
  --rules-dir governance/dq_rules \
  --rule-filter "customer"
```

### Silent Validation (CI/CD)
```bash
python ops/scripts/validate_dq_rules.py \
  --rules-dir governance/dq_rules \
  --quiet
```

## Validation Output Formats

### Console Output (Default)
```
📊 Data Quality Rules Validation Report
========================================

📁 Files processed: 3
📋 Total rules: 12
✅ Valid files: 3
❌ Invalid files: 0

✅ dq_rules.yaml
   Rules: 2
   Datasets: 1

✅ customer_dq_rules.yaml
   Rules: 3
   Datasets: 2

✅ sales_dq_rules.yaml
   Rules: 5
   Datasets: 2

🎉 All DQ rules files are valid!
```

### GitHub Actions Format
```
::notice title=DQ Rules Validation::Found and validated 12 rule(s) in 3 file(s)
::notice title=dq_rules.yaml::✅ 2 rules validated successfully
::notice title=customer_dq_rules.yaml::✅ 3 rules validated successfully
::notice title=sales_dq_rules.yaml::✅ 5 rules validated successfully
::notice title=Validation Complete::🎉 All DQ rules files are valid!
```

### JSON Report Format
```json
{
  "summary": {
    "total_files": 3,
    "valid_files": 3,
    "invalid_files": 0,
    "total_rules": 12,
    "dataset_coverage": [
      "bronze.customer_data",
      "silver.servicenow_incidents",
      "silver.sales_transactions"
    ]
  },
  "files": [
    {
      "file": "dq_rules.yaml", 
      "valid": true,
      "rule_count": 2,
      "dataset_coverage": ["silver.servicenow_incidents"]
    }
  ]
}
```

## Adding New DQ Rules Files

### 1. Create Rules File
```bash
touch governance/dq_rules/product_dq_rules.yaml
```

### 2. Define Rules Structure
```yaml
rules:
  - name: product_sku_unique
    dataset: bronze.products
    check: unique
    columns: [sku]
    threshold: 100%
    severity: critical
    description: "Product SKU must be unique"
    owner: inventory-team@company.com

metadata:
  version: "1.0.0"
  description: "Product data quality rules"
  owner: "inventory-team@company.com"
  last_updated: "2024-10-08"

datasets:
  - bronze.products
  - silver.product_catalog

categories:
  - uniqueness
  - completeness
```

### 3. Validate Rules
```bash
python ops/scripts/validate_dq_rules.py \
  --rules-dir governance/dq_rules
```

### 4. Commit Changes
```bash
git add governance/dq_rules/product_dq_rules.yaml
git commit -m "Add product data quality rules"
git push
```

## Integration with Great Expectations

The DQ rules system is designed for future Great Expectations integration:

```python
# Future integration capability
def convert_dq_rules_to_gx_expectations(rules_file):
    """Convert DQ rules to Great Expectations suite"""
    # Implementation planned for future enhancement
    pass
```

## Best Practices

### Rules Organization
- **One rules file per domain** (customer, sales, product, etc.)
- **Consistent naming**: `{domain}_dq_rules.yaml`
- **Version control**: Update `version` in metadata for changes
- **Documentation**: Clear descriptions for each rule

### Rule Definition
- **Meaningful names**: Use descriptive rule names
- **Appropriate thresholds**: Set realistic but meaningful targets
- **Severity levels**: Classify impact appropriately
- **Column specificity**: List exact columns being validated

### Metadata Management
- **Version tracking**: Use semantic versioning
- **Ownership**: Assign clear team responsibility
- **Dataset coverage**: Document all covered datasets
- **Categories**: Tag rules for easy organization

## Rule Validation Examples

### Customer Data Quality Rules
```yaml
rules:
  - name: customer_email_completeness
    dataset: bronze.customer_data
    check: not_null
    columns: [email]
    threshold: 99.5%
    severity: high
    description: "Customer email should be populated"
    owner: data-engineering@company.com
```

### Sales Transaction Rules  
```yaml
rules:
  - name: sales_amount_positive
    dataset: silver.sales_transactions
    check: range
    columns: [amount]
    threshold: 100%
    severity: critical
    description: "Sales amount must be positive"
    owner: finance-team@company.com
```

### Product Validation Rules
```yaml
rules:
  - name: product_category_enum
    dataset: bronze.products
    check: enum
    columns: [category]
    threshold: 100%
    severity: medium
    description: "Product category must be from approved list"
    owner: inventory-team@company.com
```

## Future Enhancements

### Planned Features
- **Great Expectations Integration**: Automatic expectation suite generation
- **Rule Dependencies**: Cross-rule relationship mapping
- **Dynamic Thresholds**: Context-aware threshold adjustment
- **Real-time Monitoring**: Continuous data quality monitoring
- **Rule Versioning**: Automatic version management and history

### Roadmap
1. **Phase 1**: Multi-file DQ rules validation ✅ **COMPLETED**
2. **Phase 2**: Great Expectations integration
3. **Phase 3**: Rule dependency tracking and impact analysis
4. **Phase 4**: Real-time data quality monitoring dashboard

## Configuration

### Environment Variables
```bash
export DATA_ENGINEERING_TEAM_EMAIL="data-eng@company.com"
export FINANCE_TEAM_EMAIL="finance@company.com"
export INVENTORY_TEAM_EMAIL="inventory@company.com"
```

### Project Configuration
The DQ rules system respects the `project.config.json` settings:
- Email placeholders resolved from project configuration
- Naming patterns applied to datasets in rules
- Environment-specific rule variations supported

## Troubleshooting

### Common Issues
1. **YAML syntax errors**: Use `yamllint` for syntax checking
2. **Missing required fields**: Ensure `name`, `dataset`, `check` are present
3. **Invalid threshold formats**: Use percentage (95%) or decimal (0.95)
4. **Unsupported check types**: Refer to supported check types list

### Validation Commands
```bash
# Check YAML syntax
yamllint governance/dq_rules/*.yaml

# Validate individual rules file
python -c "
import yaml
with open('governance/dq_rules/customer_dq_rules.yaml') as f:
    print(yaml.safe_load(f))
"

# Debug validation issues
python ops/scripts/validate_dq_rules.py \
  --rules-dir governance/dq_rules \
  --verbose
```

## Integration with Data Contracts

DQ rules complement data contracts by providing:

- **Operational validation** vs **schema definition**
- **Runtime checks** vs **design-time contracts**
- **Quality metrics** vs **governance metadata**
- **Threshold monitoring** vs **SLA definitions**

Both systems work together to ensure comprehensive data governance and quality assurance across the Microsoft Fabric CI/CD pipeline.

---

## Summary

The Microsoft Fabric CI/CD project now provides **comprehensive multi-file data quality rules validation** with:

✅ **Multiple DQ rules file support**  
✅ **Automated discovery and validation**  
✅ **CI/CD pipeline integration**  
✅ **Multiple output formats**  
✅ **Rule schema and metadata validation**  
✅ **Cross-file consistency checking**  

This enables teams to manage domain-specific data quality rules with proper validation, governance, and automated checking across the entire data pipeline lifecycle.