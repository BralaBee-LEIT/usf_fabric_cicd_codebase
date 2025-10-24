#!/usr/bin/env python3
"""
Data Contract Validator for Microsoft Fabric CI/CD
Validates multiple data contract YAML files and enforces standards
"""

import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of data contract validation"""

    valid: bool
    contract_path: str
    issues: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]


class DataContractValidator:
    """Validates data contracts for compliance and standards"""

    def __init__(self, contracts_dir: str = "governance/data_contracts"):
        self.contracts_dir = Path(contracts_dir)
        self.validation_results: List[ValidationResult] = []

    def discover_contracts(self) -> List[Path]:
        """Discover all data contract YAML files"""
        if not self.contracts_dir.exists():
            logger.warning(
                f"Data contracts directory {self.contracts_dir} does not exist"
            )
            return []

        patterns = ["*.yaml", "*.yml", "*_contract.yaml", "*_contract.yml"]
        contract_files = []

        for pattern in patterns:
            contract_files.extend(self.contracts_dir.rglob(pattern))

        # Remove duplicates and sort
        contract_files = sorted(list(set(contract_files)))
        logger.info(f"Discovered {len(contract_files)} data contract files")

        return contract_files

    def validate_contract_schema(
        self, contract_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Validate contract against required schema"""
        issues = []

        # Required top-level fields
        required_fields = ["dataset", "owner", "schema"]
        for field in required_fields:
            if field not in contract_data:
                issues.append(
                    {
                        "type": "schema",
                        "severity": "high",
                        "message": f"Missing required field: {field}",
                    }
                )

        # Validate dataset naming convention
        if "dataset" in contract_data:
            dataset = contract_data["dataset"]
            if not isinstance(dataset, str) or not dataset:
                issues.append(
                    {
                        "type": "schema",
                        "severity": "high",
                        "message": "Dataset field must be a non-empty string",
                    }
                )
            elif not self._is_valid_dataset_name(dataset):
                issues.append(
                    {
                        "type": "naming",
                        "severity": "medium",
                        "message": f"Dataset name '{dataset}' should follow naming convention: layer.domain_entity",
                    }
                )

        # Validate owner email format
        if "owner" in contract_data:
            owner = contract_data["owner"]
            if not isinstance(owner, str) or "@" not in owner:
                issues.append(
                    {
                        "type": "schema",
                        "severity": "medium",
                        "message": "Owner should be a valid email address",
                    }
                )

        # Validate schema structure
        if "schema" in contract_data:
            schema_issues = self._validate_schema_definition(contract_data["schema"])
            issues.extend(schema_issues)

        # Validate SLAs if present
        if "slas" in contract_data:
            sla_issues = self._validate_slas(contract_data["slas"])
            issues.extend(sla_issues)

        return issues

    def _is_valid_dataset_name(self, dataset: str) -> bool:
        """Check if dataset follows naming convention"""
        # Expected format: layer.domain_entity (e.g., gold.servicenow_incidents)
        parts = dataset.split(".")
        if len(parts) < 2:
            return False

        layer = parts[0]
        entity = ".".join(parts[1:])

        # Valid layers
        valid_layers = ["bronze", "silver", "gold", "raw", "processed", "curated"]
        if layer not in valid_layers:
            return False

        # Entity should be snake_case
        import re

        if not re.match(r"^[a-z][a-z0-9_]*[a-z0-9]$", entity):
            return False

        return True

    def _validate_schema_definition(self, schema: Any) -> List[Dict[str, Any]]:
        """Validate schema field definitions"""
        issues = []

        if not isinstance(schema, list):
            issues.append(
                {
                    "type": "schema",
                    "severity": "high",
                    "message": "Schema must be a list of field definitions",
                }
            )
            return issues

        if len(schema) == 0:
            issues.append(
                {
                    "type": "schema",
                    "severity": "high",
                    "message": "Schema cannot be empty",
                }
            )
            return issues

        field_names = set()
        for i, field in enumerate(schema):
            if not isinstance(field, dict):
                issues.append(
                    {
                        "type": "schema",
                        "severity": "high",
                        "message": f"Schema field {i+1} must be an object",
                    }
                )
                continue

            # Required field properties
            if "name" not in field:
                issues.append(
                    {
                        "type": "schema",
                        "severity": "high",
                        "message": f"Schema field {i+1} missing 'name'",
                    }
                )
            else:
                name = field["name"]
                if name in field_names:
                    issues.append(
                        {
                            "type": "schema",
                            "severity": "high",
                            "message": f"Duplicate field name: {name}",
                        }
                    )
                field_names.add(name)

            if "type" not in field:
                issues.append(
                    {
                        "type": "schema",
                        "severity": "high",
                        "message": f"Schema field '{field.get('name', i+1)}' missing 'type'",
                    }
                )
            else:
                # Validate data type
                valid_types = [
                    "string",
                    "integer",
                    "float",
                    "boolean",
                    "timestamp",
                    "date",
                    "decimal",
                    "binary",
                ]
                if field["type"] not in valid_types:
                    issues.append(
                        {
                            "type": "schema",
                            "severity": "medium",
                            "message": f"Field '{field.get('name')}' has unknown type: {field['type']}",
                        }
                    )

            # Nullable should be boolean
            if "nullable" in field and not isinstance(field["nullable"], bool):
                issues.append(
                    {
                        "type": "schema",
                        "severity": "low",
                        "message": f"Field '{field.get('name')}' nullable should be true/false",
                    }
                )

        return issues

    def _validate_slas(self, slas: Any) -> List[Dict[str, Any]]:
        """Validate SLA definitions"""
        issues = []

        if not isinstance(slas, dict):
            issues.append(
                {
                    "type": "slas",
                    "severity": "medium",
                    "message": "SLAs must be an object",
                }
            )
            return issues

        # Validate freshness if present
        if "freshness" in slas:
            freshness = slas["freshness"]
            if not isinstance(freshness, str):
                issues.append(
                    {
                        "type": "slas",
                        "severity": "medium",
                        "message": "Freshness must be a string (ISO 8601 duration)",
                    }
                )
            elif not freshness.startswith("PT"):
                issues.append(
                    {
                        "type": "slas",
                        "severity": "low",
                        "message": "Freshness should be ISO 8601 duration (e.g., PT2H, PT30M)",
                    }
                )

        # Validate completeness if present
        if "completeness" in slas:
            completeness = slas["completeness"]
            if isinstance(completeness, str) and completeness.endswith("%"):
                try:
                    value = float(completeness.rstrip("%"))
                    if value < 0 or value > 100:
                        issues.append(
                            {
                                "type": "slas",
                                "severity": "medium",
                                "message": "Completeness percentage must be between 0% and 100%",
                            }
                        )
                except ValueError:
                    issues.append(
                        {
                            "type": "slas",
                            "severity": "medium",
                            "message": "Completeness must be a valid percentage (e.g., 99.9%)",
                        }
                    )
            else:
                issues.append(
                    {
                        "type": "slas",
                        "severity": "medium",
                        "message": "Completeness must be a percentage string (e.g., 99.9%)",
                    }
                )

        return issues

    def validate_contract_file(self, contract_path: Path) -> ValidationResult:
        """Validate a single contract file"""
        issues = []
        warnings = []

        try:
            # Load YAML
            with open(contract_path, "r", encoding="utf-8") as f:
                contract_data = yaml.safe_load(f)

            if contract_data is None:
                issues.append(
                    {
                        "type": "format",
                        "severity": "high",
                        "message": "Contract file is empty",
                    }
                )
                return ValidationResult(False, str(contract_path), issues, warnings)

            if not isinstance(contract_data, dict):
                issues.append(
                    {
                        "type": "format",
                        "severity": "high",
                        "message": "Contract must be a YAML object",
                    }
                )
                return ValidationResult(False, str(contract_path), issues, warnings)

            # Validate schema
            schema_issues = self.validate_contract_schema(contract_data)
            issues.extend(schema_issues)

            # Additional validations
            self._validate_contract_completeness(contract_data, warnings)

        except yaml.YAMLError as e:
            issues.append(
                {
                    "type": "format",
                    "severity": "high",
                    "message": f"Invalid YAML format: {str(e)}",
                }
            )
        except Exception as e:
            issues.append(
                {
                    "type": "error",
                    "severity": "high",
                    "message": f"Validation failed: {str(e)}",
                }
            )

        # Determine if valid
        high_severity_issues = [i for i in issues if i.get("severity") == "high"]
        is_valid = len(high_severity_issues) == 0

        return ValidationResult(is_valid, str(contract_path), issues, warnings)

    def _validate_contract_completeness(
        self, contract_data: Dict[str, Any], warnings: List[Dict[str, Any]]
    ):
        """Check for recommended but not required fields"""

        # Recommended fields
        if "description" not in contract_data:
            warnings.append(
                {
                    "type": "completeness",
                    "message": "Consider adding a 'description' field",
                }
            )

        if "tags" not in contract_data:
            warnings.append(
                {
                    "type": "completeness",
                    "message": "Consider adding 'tags' for better discoverability",
                }
            )

        if "slas" not in contract_data:
            warnings.append(
                {
                    "type": "completeness",
                    "message": "Consider defining SLAs (freshness, completeness)",
                }
            )

        if "breaking_changes" not in contract_data:
            warnings.append(
                {
                    "type": "completeness",
                    "message": "Consider defining what constitutes breaking changes",
                }
            )

    def validate_all_contracts(self) -> Dict[str, Any]:
        """Validate all discovered contracts"""
        contract_files = self.discover_contracts()

        if not contract_files:
            return {
                "summary": {"total": 0, "valid": 0, "invalid": 0},
                "results": [],
                "overall_status": "no_contracts",
            }

        self.validation_results = []

        for contract_file in contract_files:
            logger.info(f"Validating contract: {contract_file}")
            result = self.validate_contract_file(contract_file)
            self.validation_results.append(result)

        # Generate summary
        total = len(self.validation_results)
        valid = len([r for r in self.validation_results if r.valid])
        invalid = total - valid

        return {
            "summary": {"total": total, "valid": valid, "invalid": invalid},
            "results": [
                {
                    "file": r.contract_path,
                    "valid": r.valid,
                    "issues": r.issues,
                    "warnings": r.warnings,
                }
                for r in self.validation_results
            ],
            "overall_status": "valid" if invalid == 0 else "invalid",
        }

    def generate_report(
        self, results: Dict[str, Any], output_format: str = "text"
    ) -> str:
        """Generate validation report"""

        if output_format == "json":
            return json.dumps(results, indent=2)

        # Text report
        lines = []
        lines.append("# Data Contracts Validation Report")
        lines.append("")

        summary = results["summary"]
        lines.append(f"**Total Contracts:** {summary['total']}")
        lines.append(f"**Valid:** {summary['valid']}")
        lines.append(f"**Invalid:** {summary['invalid']}")
        lines.append(f"**Overall Status:** {results['overall_status'].upper()}")
        lines.append("")

        if summary["total"] == 0:
            lines.append("No data contract files found.")
            return "\n".join(lines)

        # Individual results
        for result in results["results"]:
            contract_name = Path(result["file"]).name
            status = "✅ VALID" if result["valid"] else "❌ INVALID"
            lines.append(f"## {contract_name} - {status}")

            if result["issues"]:
                lines.append("### Issues:")
                for issue in result["issues"]:
                    severity_icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(
                        issue.get("severity", "low"), "⚪"
                    )
                    lines.append(
                        f"- {severity_icon} **{issue.get('type', 'unknown')}**: {issue.get('message', 'No message')}"
                    )
                lines.append("")

            if result["warnings"]:
                lines.append("### Warnings:")
                for warning in result["warnings"]:
                    lines.append(
                        f"- ⚠️ **{warning.get('type', 'warning')}**: {warning.get('message', 'No message')}"
                    )
                lines.append("")

        return "\n".join(lines)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Validate data contract YAML files")
    parser.add_argument(
        "--contracts-dir",
        default="governance/data_contracts",
        help="Directory containing data contract files",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format for validation report",
    )
    parser.add_argument("--output-file", help="Write report to file instead of stdout")
    parser.add_argument(
        "--fail-on-invalid",
        action="store_true",
        help="Exit with error code if any contracts are invalid",
    )

    args = parser.parse_args()

    # Validate contracts
    validator = DataContractValidator(args.contracts_dir)
    results = validator.validate_all_contracts()

    # Generate report
    report = validator.generate_report(results, args.output_format)

    # Output report
    if args.output_file:
        with open(args.output_file, "w") as f:
            f.write(report)
        logger.info(f"Report written to {args.output_file}")
    else:
        print(report)

    # Exit code
    if args.fail_on_invalid and results["overall_status"] == "invalid":
        logger.error("Some data contracts are invalid")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
