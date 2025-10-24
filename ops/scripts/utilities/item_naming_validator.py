"""
Fabric Item Naming Validator

Enforces naming conventions for Microsoft Fabric items based on naming_standards.yaml.
Provides validation, auto-fix suggestions, and compliance reporting.
"""

import re
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of naming validation"""

    def __init__(
        self,
        is_valid: bool,
        item_name: str,
        item_type: str,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        suggestions: Optional[List[str]] = None,
    ):
        self.is_valid = is_valid
        self.item_name = item_name
        self.item_type = item_type
        self.errors = errors or []
        self.warnings = warnings or []
        self.suggestions = suggestions or []

    def __str__(self) -> str:
        status = "✓ VALID" if self.is_valid else "✗ INVALID"
        output = [f"{status}: {self.item_type} - '{self.item_name}'"]

        if self.errors:
            output.append("  Errors:")
            for error in self.errors:
                output.append(f"    - {error}")

        if self.warnings:
            output.append("  Warnings:")
            for warning in self.warnings:
                output.append(f"    - {warning}")

        if self.suggestions:
            output.append("  Suggestions:")
            for suggestion in self.suggestions:
                output.append(f"    - {suggestion}")

        return "\n".join(output)


class ItemNamingValidator:
    """
    Validate Fabric item names against naming standards

    Usage:
        validator = ItemNamingValidator()

        # Validate name
        result = validator.validate("BRONZE_CustomerData_Lakehouse", "Lakehouse")
        if not result.is_valid:
            print(result.errors)
            print(result.suggestions)

        # Get suggested name
        suggested = validator.suggest_name("customerdata", "Lakehouse", layer="BRONZE")
        # Returns: "BRONZE_CustomerData_Lakehouse"
    """

    def __init__(self, standards_file: Optional[Path] = None):
        """
        Initialize validator with naming standards

        Args:
            standards_file: Path to naming_standards.yaml (auto-detects if None)
        """
        if standards_file is None:
            # Auto-detect standards file
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent
            standards_file = project_root / "naming_standards.yaml"

        if not standards_file.exists():
            raise FileNotFoundError(
                f"Naming standards file not found: {standards_file}\n"
                "Please create naming_standards.yaml in project root."
            )

        with open(standards_file, "r") as f:
            self.standards = yaml.safe_load(f)

        self.strict_mode = self.standards.get("validation", {}).get("strict_mode", True)
        self.warn_on_deviation = self.standards.get("validation", {}).get(
            "warn_on_deviation", True
        )
        self.auto_fix_enabled = self.standards.get("validation", {}).get(
            "auto_fix_suggestions", True
        )

        logger.info(f"Loaded naming standards from: {standards_file}")
        logger.info(f"Strict mode: {self.strict_mode}")

    def validate(
        self, item_name: str, item_type: str, ticket_id: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate item name against naming standards

        Args:
            item_name: Name to validate
            item_type: Fabric item type (Lakehouse, Notebook, etc.)
            ticket_id: Optional ticket ID for feature branch workflows

        Returns:
            ValidationResult with is_valid, errors, warnings, suggestions
        """
        errors = []
        warnings = []
        suggestions = []

        # Get item type standards
        item_standards = self.standards.get("item_types", {}).get(item_type)

        if not item_standards:
            if self.strict_mode:
                errors.append(f"Unknown item type: {item_type}")
                return ValidationResult(False, item_name, item_type, errors=errors)
            else:
                warnings.append(f"No naming standards defined for type: {item_type}")
                return ValidationResult(True, item_name, item_type, warnings=warnings)

        # Check global rules
        global_errors = self._validate_global_rules(item_name)
        errors.extend(global_errors)

        # Check item-specific pattern
        pattern = item_standards.get("pattern")
        if pattern:
            if not re.match(pattern, item_name):
                errors.append(f"Name does not match pattern: {pattern}")

                # Add examples if available
                examples = item_standards.get("examples", [])
                if examples:
                    suggestions.append(f"Valid examples: {', '.join(examples[:3])}")

                # Auto-fix suggestion
                if self.auto_fix_enabled:
                    fixed_name = self._suggest_fix(item_name, item_type, item_standards)
                    if fixed_name:
                        suggestions.append(f"Suggested fix: '{fixed_name}'")

        # Check ticket-based naming if ticket provided
        if ticket_id:
            ticket_errors, ticket_suggestions = self._validate_ticket_naming(
                item_name, item_type, ticket_id
            )
            errors.extend(ticket_errors)
            suggestions.extend(ticket_suggestions)

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            item_name=item_name,
            item_type=item_type,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
        )

    def _validate_global_rules(self, item_name: str) -> List[str]:
        """Validate against global naming rules"""
        errors = []
        global_rules = self.standards.get("global_rules", {})

        # Max length
        max_length = global_rules.get("max_length", 256)
        if len(item_name) > max_length:
            errors.append(f"Name exceeds max length of {max_length} characters")

        # Allowed characters
        allowed_chars = global_rules.get("allowed_characters", "A-Za-z0-9_-")
        if not re.match(f"^[{allowed_chars}]+$", item_name):
            errors.append(f"Name contains invalid characters. Allowed: {allowed_chars}")

        # No leading numbers
        if global_rules.get("no_leading_numbers", False):
            if item_name[0].isdigit():
                errors.append("Name cannot start with a number")

        # No special chars at start
        if global_rules.get("no_special_chars_start", True):
            if item_name[0] in "_-":
                errors.append("Name cannot start with special character")

        # Reserved words
        reserved = global_rules.get("reserved_words", [])
        if item_name.lower() in [word.lower() for word in reserved]:
            errors.append(f"'{item_name}' is a reserved word and cannot be used")

        return errors

    def _validate_ticket_naming(
        self, item_name: str, item_type: str, ticket_id: str
    ) -> Tuple[List[str], List[str]]:
        """Validate ticket-based naming convention"""
        errors = []
        suggestions = []

        ticket_standards = self.standards.get("ticket_based_naming", {})
        if not ticket_standards.get("enabled", False):
            return errors, suggestions

        # Extract ticket prefix from ID (e.g., "JIRA" from "JIRA-12345")
        ticket_parts = ticket_id.split("-")
        if len(ticket_parts) < 2:
            errors.append(f"Invalid ticket ID format: {ticket_id}")
            return errors, suggestions

        ticket_prefix = ticket_parts[0].upper()
        valid_systems = ticket_standards.get("ticket_systems", [])

        if ticket_prefix not in valid_systems:
            pass

        # Check if name starts with ticket ID
        expected_prefix = ticket_id.replace("-", "")
        if not item_name.startswith(expected_prefix):
            errors.append(f"Ticket-based item should start with: {expected_prefix}_")
            suggestions.append(f"Suggested: {expected_prefix}_{item_name}")

        return errors, suggestions

    def _suggest_fix(
        self, item_name: str, item_type: str, item_standards: Dict
    ) -> Optional[str]:
        """Suggest a corrected name based on standards"""
        # Extract meaningful parts from the name
        name_parts = re.split(r"[_\-\s]+", item_name)

        # Get the expected suffix
        suffix = self._extract_type_suffix(item_type)

        # Build suggestion based on type
        if item_type == "Lakehouse":
            # Try to identify layer
            layer = "BRONZE"
            for part in name_parts:
                if part.upper() in ["BRONZE", "SILVER", "GOLD"]:
                    layer = part.upper()
                    name_parts.remove(part)
                    break

            # Remove suffix if present
            clean_parts = [p for p in name_parts if p.lower() != "lakehouse"]
            descriptive = "_".join([self._to_camel_case(p) for p in clean_parts if p])

            return f"{layer}_{descriptive}_Lakehouse"

        elif item_type == "Notebook":
            # Try to find sequence number
            seq_num = "01"
            remaining_parts = []

            for part in name_parts:
                if part.isdigit() and len(part) <= 2:
                    seq_num = part.zfill(2)
                elif part.lower() != "notebook":
                    remaining_parts.append(part)

            descriptive = "_".join(
                [self._to_camel_case(p) for p in remaining_parts if p]
            )
            return f"{seq_num}_{descriptive}_Notebook"

        else:
            # Generic fix: clean parts + suffix
            clean_parts = [p for p in name_parts if p.lower() != suffix.lower()]
            descriptive = "_".join([self._to_camel_case(p) for p in clean_parts if p])
            return f"{descriptive}_{suffix}"

    def _extract_type_suffix(self, item_type: str) -> str:
        """Extract the suffix for an item type"""
        suffix_map = {
            "Lakehouse": "Lakehouse",
            "Warehouse": "Warehouse",
            "Notebook": "Notebook",
            "DataPipeline": "Pipeline",
            "SemanticModel": "SemanticModel",
            "Report": "Report",
            "Dashboard": "Dashboard",
            "Dataflow": "Dataflow",
            "MLModel": "Model",
            "MLExperiment": "Experiment",
        }
        return suffix_map.get(item_type, item_type)

    def _to_camel_case(self, text: str) -> str:
        """Convert text to CamelCase"""
        words = re.split(r"[_\-\s]+", text.lower())
        return "".join(word.capitalize() for word in words if word)

    def suggest_name(
        self,
        base_name: str,
        item_type: str,
        layer: Optional[str] = None,
        sequence: Optional[int] = None,
        ticket_id: Optional[str] = None,
    ) -> str:
        """
        Generate a compliant name suggestion

        Args:
            base_name: Base descriptive name (e.g., "customer data")
            item_type: Fabric item type
            layer: For lakehouses: BRONZE, SILVER, or GOLD
            sequence: For notebooks: sequence number (1-99)
            ticket_id: Optional ticket ID for feature branch naming

        Returns:
            Suggested compliant name
        """
        # Clean and format base name
        clean_base = self._to_camel_case(base_name)
        suffix = self._extract_type_suffix(item_type)

        # Build name based on type
        if item_type == "Lakehouse":
            layer = layer or "BRONZE"
            name = f"{layer.upper()}_{clean_base}_Lakehouse"

        elif item_type == "Notebook":
            seq = str(sequence or 1).zfill(2)
            name = f"{seq}_{clean_base}_Notebook"

        else:
            name = f"{clean_base}_{suffix}"

        # Add ticket prefix if provided
        if ticket_id:
            ticket_prefix = ticket_id.replace("-", "")
            name = f"{ticket_prefix}_{name}"

        return name

    def validate_batch(
        self, items: List[Tuple[str, str]], ticket_id: Optional[str] = None
    ) -> Dict[str, ValidationResult]:
        """
        Validate multiple items at once

        Args:
            items: List of (item_name, item_type) tuples
            ticket_id: Optional ticket ID for all items

        Returns:
            Dictionary mapping item names to ValidationResults
        """
        results = {}

        for item_name, item_type in items:
            result = self.validate(item_name, item_type, ticket_id)
            results[item_name] = result

        return results

    def generate_compliance_report(
        self, validation_results: Dict[str, ValidationResult]
    ) -> Dict[str, Any]:
        """
        Generate compliance report from validation results

        Args:
            validation_results: Dictionary of ValidationResults

        Returns:
            Compliance report with statistics and violations
        """
        total = len(validation_results)
        valid = sum(1 for r in validation_results.values() if r.is_valid)
        invalid = total - valid

        violations = [
            {
                "item_name": name,
                "item_type": result.item_type,
                "errors": result.errors,
                "suggestions": result.suggestions,
            }
            for name, result in validation_results.items()
            if not result.is_valid
        ]

        return {
            "total_items": total,
            "valid_items": valid,
            "invalid_items": invalid,
            "compliance_rate": f"{(valid/total*100):.1f}%" if total > 0 else "0%",
            "violations": violations,
        }


def validate_item_name(
    item_name: str,
    item_type: str,
    ticket_id: Optional[str] = None,
    raise_on_invalid: bool = False,
) -> ValidationResult:
    """
    Convenience function to validate a single item name

    Args:
        item_name: Name to validate
        item_type: Fabric item type
        ticket_id: Optional ticket ID
        raise_on_invalid: If True, raise ValueError on validation failure

    Returns:
        ValidationResult

    Raises:
        ValueError: If raise_on_invalid=True and validation fails
    """
    validator = ItemNamingValidator()
    result = validator.validate(item_name, item_type, ticket_id)

    if raise_on_invalid and not result.is_valid:
        error_msg = f"Invalid item name: {item_name}\n"
        error_msg += "\n".join(f"  - {err}" for err in result.errors)
        if result.suggestions:
            error_msg += "\n\nSuggestions:\n"
            error_msg += "\n".join(f"  - {sug}" for sug in result.suggestions)
        raise ValueError(error_msg)

    return result
