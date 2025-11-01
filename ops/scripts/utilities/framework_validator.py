#!/usr/bin/env python3
"""
Framework Prerequisites Validator

Enforces core framework requirements before any operation:
1. project.config.json - Organization naming standards (MANDATORY)
2. .env - Azure credentials (MANDATORY)
3. naming_standards.yaml - Naming validation rules (MANDATORY)

This ensures:
- Governance and naming consistency across all operations
- Infrastructure-as-code principles are followed
- No ad-hoc resource creation without proper configuration
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class FrameworkValidationError(Exception):
    """Raised when framework prerequisites are not met"""
    pass


class FrameworkValidator:
    """
    Validates framework prerequisites before any operation
    
    Core Principles Enforced:
    1. Standardized naming via project.config.json
    2. Proper authentication via .env
    3. Naming validation rules via naming_standards.yaml
    """
    
    # Required files for framework operation
    REQUIRED_FILES = {
        'project.config.json': {
            'description': 'Organization naming standards and governance',
            'template': 'project.config.template.json',
            'purpose': 'Ensures consistent naming across all workspaces and items'
        },
        '.env': {
            'description': 'Azure credentials and Fabric configuration',
            'template': '.env.example',
            'purpose': 'Required for authentication to Azure and Fabric APIs'
        },
        'naming_standards.yaml': {
            'description': 'Naming validation rules and patterns',
            'template': None,
            'purpose': 'Enforces naming conventions and validates resource names',
            'alternatives': ['config/naming_standards.yaml']  # Check alternate locations
        }
    }
    
    def __init__(self, repo_root: Optional[Path] = None, strict_mode: bool = True):
        """
        Initialize framework validator
        
        Args:
            repo_root: Repository root path (auto-detected if None)
            strict_mode: If True, fail on missing files. If False, warn only.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.strict_mode = strict_mode
        self.validation_results: List[Tuple[str, bool, str]] = []
        
    def _find_repo_root(self) -> Path:
        """
        Find repository root by looking for .git directory or key files
        """
        current = Path.cwd()
        
        # Check current directory and parents
        for path in [current, *current.parents]:
            # Check for .git directory
            if (path / '.git').exists():
                return path
            # Check for project marker files
            if (path / 'project.config.template.json').exists():
                return path
                
        # Default to current directory
        return current
    
    def validate_all(self) -> Tuple[bool, List[str]]:
        """
        Validate all framework prerequisites
        
        Returns:
            Tuple of (all_valid: bool, error_messages: List[str])
        """
        self.validation_results = []
        errors = []
        
        # Check each required file
        for file_path, metadata in self.REQUIRED_FILES.items():
            full_path = self.repo_root / file_path
            
            # Check primary location
            if full_path.exists():
                self.validation_results.append((file_path, True, "Found"))
            else:
                # Check alternative locations if specified
                found_alternative = False
                alternatives = metadata.get('alternatives', [])
                for alt_path in alternatives:
                    alt_full_path = self.repo_root / alt_path
                    if alt_full_path.exists():
                        self.validation_results.append((file_path, True, f"Found (at {alt_path})"))
                        found_alternative = True
                        break
                
                if not found_alternative:
                    error_msg = self._format_missing_file_error(file_path, metadata)
                    self.validation_results.append((file_path, False, error_msg))
                    errors.append(error_msg)
        
        all_valid = len(errors) == 0
        return all_valid, errors
    
    def _format_missing_file_error(self, file_path: str, metadata: dict) -> str:
        """Format error message for missing file"""
        template = metadata.get('template')
        purpose = metadata.get('purpose', '')
        
        error = f"Missing required file: {file_path}\n"
        error += f"  Purpose: {purpose}\n"
        
        if template:
            error += f"  Create it: cp {template} {file_path}"
        
        return error
    
    def validate_or_exit(self, operation_name: str = "operation"):
        """
        Validate prerequisites and exit with error if validation fails (strict mode)
        
        Args:
            operation_name: Name of operation being performed (for error message)
        """
        all_valid, errors = self.validate_all()
        
        if not all_valid:
            self._print_validation_error(operation_name, errors)
            if self.strict_mode:
                sys.exit(1)
            else:
                print("\n⚠️  WARNING: Continuing without required files (non-strict mode)")
    
    def _print_validation_error(self, operation_name: str, errors: List[str]):
        """Print formatted validation error"""
        print("\n" + "="*80)
        print("❌ FRAMEWORK PREREQUISITES NOT MET")
        print("="*80)
        print(f"\nCannot perform {operation_name} without required configuration files.")
        print("\nCore Framework Principles:")
        print("  1. Standardized naming via project.config.json")
        print("  2. Proper authentication via .env")
        print("  3. Naming validation via naming_standards.yaml")
        print("\nMissing Files:")
        print("-" * 80)
        
        for error in errors:
            print(f"\n{error}")
        
        print("\n" + "="*80)
        print("Quick Setup:")
        print("="*80)
        print("\n# 1. Copy templates:")
        if not (self.repo_root / 'project.config.json').exists():
            print("   cp project.config.template.json project.config.json")
        if not (self.repo_root / '.env').exists():
            print("   cp .env.example .env")
        
        print("\n# 2. Edit with your values:")
        if not (self.repo_root / 'project.config.json').exists():
            print("   nano project.config.json  # Set organization prefix and naming patterns")
        if not (self.repo_root / '.env').exists():
            print("   nano .env  # Set Azure credentials and Fabric capacity")
        
        print("\n# 3. Re-run your command")
        print("\nFor more information, see: docs/getting-started/")
        print("="*80 + "\n")
    
    def get_validation_summary(self) -> str:
        """Get formatted validation summary"""
        if not self.validation_results:
            return "No validation performed yet"
        
        summary = "\nFramework Prerequisites Status:\n"
        summary += "-" * 50 + "\n"
        
        for file_path, is_valid, message in self.validation_results:
            status = "✅" if is_valid else "❌"
            summary += f"{status} {file_path}: {message}\n"
        
        return summary
    
    def validate_file_exists(self, file_path: str) -> bool:
        """
        Check if a specific file exists
        
        Args:
            file_path: Relative path from repo root
            
        Returns:
            True if file exists, False otherwise
        """
        full_path = self.repo_root / file_path
        return full_path.exists()
    
    def get_missing_files(self) -> List[str]:
        """Get list of missing required files"""
        missing = []
        for file_path in self.REQUIRED_FILES.keys():
            if not self.validate_file_exists(file_path):
                missing.append(file_path)
        return missing


def validate_framework_prerequisites(operation_name: str = "operation", strict_mode: bool = True):
    """
    Convenience function to validate framework prerequisites
    
    Args:
        operation_name: Name of operation being performed
        strict_mode: If True, exit on validation failure. If False, warn only.
    """
    validator = FrameworkValidator(strict_mode=strict_mode)
    validator.validate_or_exit(operation_name)


def quick_check() -> bool:
    """
    Quick check if all prerequisites are met (no error messages)
    
    Returns:
        True if all prerequisites met, False otherwise
    """
    validator = FrameworkValidator(strict_mode=False)
    all_valid, _ = validator.validate_all()
    return all_valid


if __name__ == "__main__":
    """
    Command-line usage for validation
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate framework prerequisites",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--non-strict',
        action='store_true',
        help='Warn instead of failing on missing files'
    )
    
    args = parser.parse_args()
    
    validator = FrameworkValidator(strict_mode=not args.non_strict)
    all_valid, errors = validator.validate_all()
    
    print(validator.get_validation_summary())
    
    if not all_valid:
        validator._print_validation_error("validation check", errors)
        sys.exit(1 if validator.strict_mode else 0)
    else:
        print("\n✅ All framework prerequisites are satisfied!\n")
        sys.exit(0)
