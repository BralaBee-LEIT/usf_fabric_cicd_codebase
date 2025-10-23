# Data Contracts Multi-File Support Implementation

## Overview

The Microsoft Fabric CI/CD project now supports **multiple data contract YAML files** with comprehensive validation, governance, and CI/CD integration.

## Key Features

### ✅ Multi-Contract Support
- **Automatic Discovery**: Finds all `.yaml` files in `governance/data_contracts/` directory
- **Batch Validation**: Validates all contracts in a single operation
- **Individual Reporting**: Detailed validation results for each contract
- **Schema Compliance**: Enforces consistent contract structure across all files

### ✅ Data Contract Examples
The system includes sample contracts demonstrating various use cases:

1. **`incidents_contract.yaml`** - Operational incident data (original)
2. **`customer_analytics_contract.yaml`** - Customer behavior analytics  
3. **`sales_enriched_contract.yaml`** - Sales performance metrics
4. **`external_apis_contract.yaml`** - Raw API ingestion data

### ✅ Comprehensive Validation Engine
The `validate_data_contracts.py` script provides:

- **Schema Validation**: Ensures all required fields are present
- **Data Type Checking**: Validates column types and constraints  
- **SLA Compliance**: Checks freshness, completeness, and availability targets
- **Quality Rules**: Validates data quality expressions and severity levels
- **Governance Checks**: Verifies data classification and compliance settings

## Current Contract Files

```
governance/data_contracts/
├── incidents_contract.yaml          # Operational incidents
├── customer_analytics_contract.yaml # Customer behavior data
├── sales_enriched_contract.yaml     # Sales metrics 
└── external_apis_contract.yaml      # Raw API ingestion
```

## Contract Structure

Each contract follows a standardized schema with:

```yaml
dataset: bronze.incidents
owner: ${DATA_OWNER_EMAIL}
description: "Dataset description"
version: "1.0.0"

# Metadata and classification
tags: ["bronze-layer", "operational"]

# Service level agreements  
slas:
  freshness: PT4H
  completeness: 99.5%
  availability: 99.9%

# Column definitions with validation
schema:
  - name: column_name
    type: string|integer|timestamp|boolean
    nullable: true|false
    description: "Column purpose"
    valid_values: ["val1", "val2"]  # Optional

# Data quality rules
quality_rules:
  - name: rule_name
    expression: "SQL-like validation expression"
    severity: high|medium|low

# Data lineage and governance
data_lineage:
  upstream_datasets: ["source1", "source2"]
  external_sources: [...]

governance:
  data_classification: public|internal|restricted
  pii_fields: ["sensitive_column"]
  retention_policy: "retention period"
```

## Validation Features

### Schema Validation
- Required fields enforcement
- Data type consistency 
- Column constraint checking
- Valid values enumeration

### SLA Monitoring  
- Freshness requirements (ISO 8601 duration)
- Completeness thresholds (percentage)
- Availability targets (percentage)

### Quality Rules
- SQL-like expression validation
- Severity classification (high/medium/low)
- Business rule enforcement

### Governance Compliance
- Data classification levels
- PII identification and protection
- Retention policy enforcement
- Access control requirements

## CI/CD Integration

### GitHub Actions Workflow
The `fabric-cicd-pipeline.yml` includes data contract validation:

```yaml
- name: Validate data contracts
  run: |
    python ops/scripts/validate_data_contracts.py \
      --contracts-dir governance/data_contracts \
      --output-format github

- name: Upload contract validation results
  uses: actions/upload-artifact@v4
  with:
    name: data-contract-validation
    path: contract_validation_report.json
```

### Setup Script Integration
The `setup.sh` script validates all contracts during project setup:

```bash
# Validates all .yaml files in governance/data_contracts
python3 ops/scripts/validate_data_contracts.py \
  --contracts-dir governance/data_contracts --quiet
```

## Usage Examples

### Validate All Contracts
```bash
python ops/scripts/validate_data_contracts.py \
  --contracts-dir governance/data_contracts
```

### Generate JSON Report
```bash  
python ops/scripts/validate_data_contracts.py \
  --contracts-dir governance/data_contracts \
  --output-format json
```

### Validate Specific Contract
```bash
python ops/scripts/validate_data_contracts.py \
  --contracts-dir governance/data_contracts \
  --contract-filter "customer_analytics"
```

### Silent Validation (CI/CD)
```bash
python ops/scripts/validate_data_contracts.py \
  --contracts-dir governance/data_contracts \
  --quiet
```

## Validation Output Formats

### Console Output (Default)
```
📊 Data Contract Validation Report
================================

✅ incidents_contract.yaml - Valid
✅ customer_analytics_contract.yaml - Valid  
✅ sales_enriched_contract.yaml - Valid
✅ external_apis_contract.yaml - Valid

🎉 All 4 contracts are valid!
```

### GitHub Actions Format
```
::notice title=Data Contracts::Found and validated 4 contract(s)
::notice title=incidents_contract.yaml::✅ Contract is valid
::notice title=customer_analytics_contract.yaml::✅ Contract is valid
```

### JSON Report Format
```json
{
  "summary": {
    "total_contracts": 4,
    "valid_contracts": 4,
    "invalid_contracts": 0
  },
  "contracts": [
    {
      "file": "incidents_contract.yaml",
      "valid": true,
      "dataset": "bronze.incidents",
      "owner": "data-engineering@company.com"
    }
  ]
}
```

## Adding New Contracts

1. **Create Contract File**
   ```bash
   touch governance/data_contracts/new_dataset_contract.yaml
   ```

2. **Define Contract Structure**
   ```yaml
   dataset: bronze.new_dataset
   owner: ${DATA_OWNER_EMAIL}
   description: "New dataset description" 
   version: "1.0.0"
   # ... rest of contract definition
   ```

3. **Validate Contract**
   ```bash
   python ops/scripts/validate_data_contracts.py \
     --contracts-dir governance/data_contracts
   ```

4. **Commit Changes**
   ```bash
   git add governance/data_contracts/new_dataset_contract.yaml
   git commit -m "Add new dataset contract"
   git push
   ```

## Integration with Great Expectations

The validation system is designed to integrate with Great Expectations:

```python
# Future integration capability
def integrate_with_gx(contract_file):
    """Convert data contract to Great Expectations suite"""
    # Implementation planned for future enhancement
    pass
```

## Best Practices

### Contract Organization
- **One contract per dataset** for clarity
- **Consistent naming**: `{dataset_name}_contract.yaml`
- **Version control**: Update `version` field for changes
- **Documentation**: Comprehensive descriptions and comments

### Schema Management
- **Breaking changes**: Document in `breaking_changes` section
- **Backward compatibility**: Consider downstream consumers
- **Quality rules**: Start with essential rules, expand gradually
- **SLA targets**: Set achievable but meaningful targets

### Governance
- **Data classification**: Properly classify all datasets
- **PII handling**: Explicitly identify sensitive fields
- **Retention policies**: Align with legal and business requirements
- **Access controls**: Define appropriate access levels

## Future Enhancements

### Planned Features
- **Contract versioning**: Automatic version management
- **Dependency tracking**: Cross-contract relationship mapping  
- **GX integration**: Automatic expectation suite generation
- **Monitoring alerts**: SLA breach notifications
- **Schema evolution**: Automated compatibility checking

### Roadmap
1. **Phase 1**: Multi-contract validation ✅ **COMPLETED**
2. **Phase 2**: Great Expectations integration
3. **Phase 3**: Contract versioning and evolution tracking
4. **Phase 4**: Real-time SLA monitoring and alerting

## Configuration

### Environment Variables
```bash
export DATA_OWNER_EMAIL="data-owner@company.com"
export TECHNICAL_LEAD_EMAIL="tech-lead@company.com" 
```

### Project Configuration
The contracts system respects the `project.config.json` settings:
- Email placeholders are resolved from project configuration
- Naming patterns can be applied to contract datasets
- Environment-specific contract variations supported

## Troubleshooting

### Common Issues
1. **YAML syntax errors**: Use `yamllint` for syntax checking
2. **Missing required fields**: Check against contract schema
3. **Invalid SLA formats**: Use ISO 8601 for freshness durations
4. **Quality rule syntax**: Ensure SQL-like expressions are valid

### Validation Commands
```bash
# Check YAML syntax
yamllint governance/data_contracts/*.yaml

# Validate individual contract  
python -c "
import yaml
with open('governance/data_contracts/incidents_contract.yaml') as f:
    print(yaml.safe_load(f))
"

# Debug validation issues
python ops/scripts/validate_data_contracts.py \
  --contracts-dir governance/data_contracts \
  --verbose
```

---

## Summary

The Microsoft Fabric CI/CD project now provides **comprehensive multi-contract data validation** with:

✅ **Multiple contract file support**  
✅ **Automated discovery and validation**  
✅ **CI/CD pipeline integration**  
✅ **Multiple output formats**  
✅ **Governance and compliance checking**  
✅ **Schema and SLA validation**  

This enables teams to manage multiple datasets with proper governance, quality assurance, and automated validation across the entire data lifecycle.