#!/usr/bin/env python3
"""
Data Quality Rules Validator for Microsoft Fabric CI/CD
Validates multiple DQ rules YAML files and enforces standards
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of DQ rules validation"""
    valid: bool
    file_path: str
    issues: List[Dict[str, Any]]
    warnings: List[str]
    rule_count: int = 0
    dataset_coverage: List[str] = None

    def __post_init__(self):
        if self.dataset_coverage is None:
            self.dataset_coverage = []

class DQRulesValidator:
    """Validates data quality rules for compliance and standards"""
    
    def __init__(self, rules_dir: str = "governance/dq_rules"):
        self.rules_dir = Path(rules_dir)
        self.validation_results: List[ValidationResult] = []
        
    def discover_dq_rules(self) -> List[Path]:
        """Discover all DQ rules YAML files"""
        if not self.rules_dir.exists():
            logger.warning(f"DQ rules directory {self.rules_dir} does not exist")
            return []
        
        patterns = ["*.yaml", "*.yml", "*_rules.yaml", "*_dq.yaml"]
        rules_files = []
        
        for pattern in patterns:
            rules_files.extend(self.rules_dir.rglob(pattern))
        
        # Remove duplicates and sort
        rules_files = sorted(list(set(rules_files)))
        logger.info(f"Discovered {len(rules_files)} DQ rules files")
        
        return rules_files
    
    def validate_rule_file(self, rules_path: Path) -> ValidationResult:
        """Validate a single DQ rules file"""
        issues = []
        warnings = []
        rule_count = 0
        dataset_coverage = []
        
        try:
            with open(rules_path, 'r') as f:
                rules_data = yaml.safe_load(f)
            
            # Validate file structure
            if not isinstance(rules_data, dict):
                issues.append({
                    "type": "structure",
                    "severity": "high",
                    "message": "DQ rules file must be a YAML dictionary"
                })
                return ValidationResult(False, str(rules_path), issues, warnings, rule_count, dataset_coverage)
            
            # Check for rules section
            if 'rules' not in rules_data:
                issues.append({
                    "type": "structure", 
                    "severity": "high",
                    "message": "Missing 'rules' section in DQ rules file"
                })
                return ValidationResult(False, str(rules_path), issues, warnings, rule_count, dataset_coverage)
            
            rules_list = rules_data.get('rules', [])
            if not isinstance(rules_list, list):
                issues.append({
                    "type": "structure",
                    "severity": "high", 
                    "message": "'rules' must be a list"
                })
                return ValidationResult(False, str(rules_path), issues, warnings, rule_count, dataset_coverage)
            
            rule_count = len(rules_list)
            
            # Validate each rule
            rule_names = []
            for i, rule in enumerate(rules_list):
                rule_issues = self._validate_individual_rule(rule, i)
                issues.extend(rule_issues)
                
                # Track rule names for uniqueness
                if isinstance(rule, dict) and 'name' in rule:
                    rule_name = rule['name']
                    if rule_name in rule_names:
                        issues.append({
                            "type": "uniqueness",
                            "severity": "medium",
                            "message": f"Duplicate rule name '{rule_name}' found"
                        })
                    else:
                        rule_names.append(rule_name)
                    
                    # Track dataset coverage
                    if 'dataset' in rule:
                        dataset = rule['dataset']
                        if dataset not in dataset_coverage:
                            dataset_coverage.append(dataset)
            
            # Validate metadata sections
            self._validate_metadata_sections(rules_data, warnings)
            
        except yaml.YAMLError as e:
            issues.append({
                "type": "format",
                "severity": "high", 
                "message": f"Invalid YAML format: {str(e)}"
            })
        except Exception as e:
            issues.append({
                "type": "error",
                "severity": "high",
                "message": f"Validation failed: {str(e)}"
            })
        
        # Determine if valid
        high_severity_issues = [i for i in issues if i.get("severity") == "high"]
        is_valid = len(high_severity_issues) == 0
        
        return ValidationResult(is_valid, str(rules_path), issues, warnings, rule_count, dataset_coverage)
    
    def _validate_individual_rule(self, rule: Dict[str, Any], index: int) -> List[Dict[str, Any]]:
        """Validate a single DQ rule"""
        issues = []
        
        if not isinstance(rule, dict):
            issues.append({
                "type": "structure",
                "severity": "high",
                "message": f"Rule {index + 1}: Must be a dictionary"
            })
            return issues
        
        # Required fields
        required_fields = ['name', 'dataset', 'check']
        for field in required_fields:
            if field not in rule:
                issues.append({
                    "type": "required_field",
                    "severity": "high", 
                    "message": f"Rule {index + 1}: Missing required field '{field}'"
                })
            elif not isinstance(rule[field], str) or not rule[field].strip():
                issues.append({
                    "type": "field_value",
                    "severity": "high",
                    "message": f"Rule {index + 1}: Field '{field}' must be a non-empty string"
                })
        
        # Validate rule name format
        if 'name' in rule:
            name = rule['name']
            if not isinstance(name, str) or len(name) < 3 or len(name) > 100:
                issues.append({
                    "type": "field_format",
                    "severity": "medium",
                    "message": f"Rule {index + 1}: Rule name should be 3-100 characters"
                })
        
        # Validate dataset format
        if 'dataset' in rule:
            dataset = rule['dataset']
            if isinstance(dataset, str) and '.' not in dataset:
                issues.append({
                    "type": "field_format",
                    "severity": "low",
                    "message": f"Rule {index + 1}: Dataset '{dataset}' should include schema (e.g., 'bronze.table')"
                })
        
        # Validate check type
        if 'check' in rule:
            check = rule['check']
            valid_checks = [
                'not_null', 'unique', 'range', 'length', 'pattern', 'enum',
                'completeness', 'accuracy', 'consistency', 'validity', 
                'timeliness', 'uniqueness', 'custom'
            ]
            if isinstance(check, str) and check not in valid_checks:
                issues.append({
                    "type": "field_value",
                    "severity": "low", 
                    "message": f"Rule {index + 1}: Check type '{check}' not in standard types: {valid_checks}"
                })
        
        # Validate threshold format
        if 'threshold' in rule:
            threshold = rule['threshold']
            if isinstance(threshold, str):
                # Check percentage format
                if threshold.endswith('%'):
                    try:
                        pct_val = float(threshold[:-1])
                        if not (0 <= pct_val <= 100):
                            issues.append({
                                "type": "field_value",
                                "severity": "medium",
                                "message": f"Rule {index + 1}: Percentage threshold must be 0-100%"
                            })
                    except ValueError:
                        issues.append({
                            "type": "field_format",
                            "severity": "medium",
                            "message": f"Rule {index + 1}: Invalid percentage format in threshold"
                        })
            elif isinstance(threshold, (int, float)):
                if not (0 <= threshold <= 1):
                    issues.append({
                        "type": "field_value", 
                        "severity": "medium",
                        "message": f"Rule {index + 1}: Numeric threshold should be 0-1 (use percentage for >1)"
                    })
        
        # Validate columns field
        if 'columns' in rule:
            columns = rule['columns']
            if not isinstance(columns, list):
                issues.append({
                    "type": "field_format",
                    "severity": "medium",
                    "message": f"Rule {index + 1}: 'columns' should be a list"
                })
            elif len(columns) == 0:
                issues.append({
                    "type": "field_value",
                    "severity": "low",
                    "message": f"Rule {index + 1}: 'columns' list is empty"
                })
        
        # Validate optional fields
        optional_str_fields = ['description', 'owner', 'severity', 'tags']
        for field in optional_str_fields:
            if field in rule and not isinstance(rule[field], str):
                issues.append({
                    "type": "field_format",
                    "severity": "low",
                    "message": f"Rule {index + 1}: '{field}' should be a string"
                })
        
        # Validate severity levels
        if 'severity' in rule:
            severity = rule['severity']
            valid_severities = ['low', 'medium', 'high', 'critical']
            if isinstance(severity, str) and severity.lower() not in valid_severities:
                issues.append({
                    "type": "field_value",
                    "severity": "low",
                    "message": f"Rule {index + 1}: Severity should be one of: {valid_severities}"
                })
        
        return issues
    
    def _validate_metadata_sections(self, rules_data: Dict[str, Any], warnings: List[str]):
        """Validate optional metadata sections"""
        
        # Check for metadata section
        if 'metadata' in rules_data:
            metadata = rules_data['metadata']
            if not isinstance(metadata, dict):
                warnings.append("'metadata' section should be a dictionary")
            else:
                # Validate metadata fields
                recommended_fields = ['version', 'description', 'owner', 'last_updated']
                for field in recommended_fields:
                    if field not in metadata:
                        warnings.append(f"Consider adding '{field}' to metadata section")
        else:
            warnings.append("Consider adding 'metadata' section with version, owner, description")
        
        # Check for datasets section (coverage documentation)
        if 'datasets' in rules_data:
            datasets = rules_data['datasets']
            if not isinstance(datasets, list):
                warnings.append("'datasets' section should be a list of covered datasets")
        
        # Check for tags/categories
        if 'categories' not in rules_data and 'tags' not in rules_data:
            warnings.append("Consider adding 'categories' or 'tags' for rule organization")
    
    def validate_all_rules(self, rules_files: Optional[List[Path]] = None) -> List[ValidationResult]:
        """Validate all DQ rules files"""
        if rules_files is None:
            rules_files = self.discover_dq_rules()
        
        self.validation_results = []
        
        for rules_file in rules_files:
            logger.info(f"Validating DQ rules file: {rules_file}")
            result = self.validate_rule_file(rules_file)
            self.validation_results.append(result)
        
        return self.validation_results
    
    def generate_report(self, output_format: str = "console") -> Optional[str]:
        """Generate validation report in specified format"""
        
        if not self.validation_results:
            logger.warning("No validation results to report")
            return None
        
        if output_format == "console":
            return self._generate_console_report()
        elif output_format == "json":
            return self._generate_json_report()
        elif output_format == "github":
            return self._generate_github_report()
        else:
            logger.error(f"Unsupported output format: {output_format}")
            return None
    
    def _generate_console_report(self) -> str:
        """Generate console-friendly validation report"""
        report = []
        report.append("📊 Data Quality Rules Validation Report")
        report.append("=" * 40)
        report.append("")
        
        total_files = len(self.validation_results)
        valid_files = len([r for r in self.validation_results if r.valid])
        total_rules = sum(r.rule_count for r in self.validation_results)
        
        # Summary
        report.append(f"📁 Files processed: {total_files}")
        report.append(f"📋 Total rules: {total_rules}")
        report.append(f"✅ Valid files: {valid_files}")
        report.append(f"❌ Invalid files: {total_files - valid_files}")
        report.append("")
        
        # Individual file results
        for result in self.validation_results:
            file_name = Path(result.file_path).name
            status_icon = "✅" if result.valid else "❌"
            report.append(f"{status_icon} {file_name}")
            report.append(f"   Rules: {result.rule_count}")
            report.append(f"   Datasets: {len(result.dataset_coverage)}")
            
            if result.issues:
                report.append(f"   Issues: {len(result.issues)}")
                for issue in result.issues[:3]:  # Show first 3 issues
                    severity_icon = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🔵"
                    report.append(f"     {severity_icon} {issue['message']}")
                if len(result.issues) > 3:
                    report.append(f"     ... and {len(result.issues) - 3} more")
            
            if result.warnings:
                report.append(f"   Warnings: {len(result.warnings)}")
                for warning in result.warnings[:2]:  # Show first 2 warnings
                    report.append(f"     ⚠️ {warning}")
                if len(result.warnings) > 2:
                    report.append(f"     ... and {len(result.warnings) - 2} more")
            
            report.append("")
        
        # Overall status
        if valid_files == total_files:
            report.append("🎉 All DQ rules files are valid!")
        else:
            report.append(f"⚠️ {total_files - valid_files} file(s) need attention")
        
        return "\n".join(report)
    
    def _generate_json_report(self) -> str:
        """Generate JSON validation report"""
        total_files = len(self.validation_results)
        valid_files = len([r for r in self.validation_results if r.valid])
        total_rules = sum(r.rule_count for r in self.validation_results)
        
        # Collect all datasets across all files
        all_datasets = set()
        for result in self.validation_results:
            all_datasets.update(result.dataset_coverage)
        
        report_data = {
            "summary": {
                "total_files": total_files,
                "valid_files": valid_files,
                "invalid_files": total_files - valid_files,
                "total_rules": total_rules,
                "dataset_coverage": list(all_datasets),
                "validation_timestamp": "N/A"
            },
            "files": []
        }
        
        for result in self.validation_results:
            file_data = {
                "file": Path(result.file_path).name,
                "valid": result.valid,
                "rule_count": result.rule_count,
                "dataset_coverage": result.dataset_coverage,
                "issues": result.issues,
                "warnings": result.warnings
            }
            report_data["files"].append(file_data)
        
        # Write JSON report to file
        report_json = json.dumps(report_data, indent=2)
        with open("dq_rules_validation_report.json", "w") as f:
            f.write(report_json)
        
        return report_json
    
    def _generate_github_report(self) -> str:
        """Generate GitHub Actions compatible output"""
        report = []
        
        total_files = len(self.validation_results)
        valid_files = len([r for r in self.validation_results if r.valid])
        total_rules = sum(r.rule_count for r in self.validation_results)
        
        # GitHub Actions annotations
        report.append(f"::notice title=DQ Rules Validation::Found and validated {total_rules} rule(s) in {total_files} file(s)")
        
        for result in self.validation_results:
            file_name = Path(result.file_path).name
            if result.valid:
                report.append(f"::notice title={file_name}::✅ {result.rule_count} rules validated successfully")
            else:
                high_issues = [i for i in result.issues if i.get('severity') == 'high']
                medium_issues = [i for i in result.issues if i.get('severity') == 'medium']
                
                if high_issues:
                    for issue in high_issues:
                        report.append(f"::error title={file_name}::{issue['message']}")
                
                if medium_issues:
                    for issue in medium_issues:
                        report.append(f"::warning title={file_name}::{issue['message']}")
        
        if valid_files == total_files:
            report.append("::notice title=Validation Complete::🎉 All DQ rules files are valid!")
        else:
            report.append(f"::warning title=Validation Issues::{total_files - valid_files} file(s) need attention")
        
        return "\n".join(report)

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Validate Data Quality Rules YAML files for Microsoft Fabric CI/CD"
    )
    
    parser.add_argument(
        "--rules-dir",
        default="governance/dq_rules",
        help="Directory containing DQ rules YAML files (default: governance/dq_rules)"
    )
    
    parser.add_argument(
        "--output-format",
        choices=["console", "json", "github"],
        default="console",
        help="Output format for validation report (default: console)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output, exit with status code only"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--rule-filter",
        help="Only validate files containing this string in filename"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Initialize validator
    validator = DQRulesValidator(args.rules_dir)
    
    # Discover rules files
    rules_files = validator.discover_dq_rules()
    
    if not rules_files:
        if not args.quiet:
            print(f"❌ No DQ rules files found in {args.rules_dir}")
        return 1
    
    # Apply filter if specified
    if args.rule_filter:
        rules_files = [f for f in rules_files if args.rule_filter.lower() in f.name.lower()]
        if not rules_files:
            if not args.quiet:
                print(f"❌ No DQ rules files match filter '{args.rule_filter}'")
            return 1
    
    # Validate all rules
    results = validator.validate_all_rules(rules_files)
    
    # Generate and output report
    if not args.quiet:
        report = validator.generate_report(args.output_format)
        if report:
            print(report)
    
    # Determine exit code
    invalid_files = [r for r in results if not r.valid]
    if invalid_files:
        if not args.quiet:
            logger.error(f"Validation failed for {len(invalid_files)} file(s)")
        return 1
    
    if not args.quiet:
        logger.info("All DQ rules files validated successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())