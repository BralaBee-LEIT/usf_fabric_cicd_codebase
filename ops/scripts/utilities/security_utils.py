"""
Security utilities for Microsoft Fabric CI/CD
Includes path traversal protection, SQL sanitization, and input validation
"""
import os
import re
import logging
from pathlib import Path
from typing import Union, List

# Configure logging
logger = logging.getLogger(__name__)


class SecurityValidator:
    """Security validation utilities"""
    
    # SQL keywords that could indicate injection attempts
    SQL_INJECTION_PATTERNS = [
        r';\s*DROP\s+TABLE',
        r';\s*DELETE\s+FROM',
        r';\s*UPDATE\s+.*\s+SET',
        r'--',
        r'/\*.*\*/',
        r'\bUNION\b.*\bSELECT\b',
        r'\bEXEC\b.*\(',
        r'\bEXECUTE\b.*\(',
        r'xp_cmdshell'
    ]
    
    @staticmethod
    def validate_path_traversal(file_path: Union[str, Path], base_dir: Union[str, Path]) -> bool:
        """
        Validate that file_path is within base_dir (prevent path traversal attacks)
        
        Args:
            file_path: Path to validate
            base_dir: Base directory that paths should be within
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            # Resolve both paths to absolute paths
            base_path = Path(base_dir).resolve()
            target_path = Path(file_path).resolve()
            
            # Check if target_path is within base_path
            try:
                target_path.relative_to(base_path)
                return True
            except ValueError:
                # Path is outside base directory
                logger.debug(f"Path traversal detected: {file_path} is outside {base_dir}")
                return False
        except (OSError, RuntimeError, TypeError) as e:
            # Specific errors: permission issues, symlink loops, invalid types
            logger.warning(f"Path resolution failed for {file_path}: {type(e).__name__} - {e}")
            return False
    
    @staticmethod
    def sanitize_sql_query(query: str, allow_comments: bool = False) -> str:
        """
        Sanitize SQL query to prevent SQL injection
        
        Args:
            query: SQL query string to sanitize
            allow_comments: Whether to allow SQL comments
            
        Returns:
            Sanitized query string
            
        Raises:
            ValueError: If potentially malicious patterns detected
        """
        # Check for dangerous patterns
        for pattern in SecurityValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError(f"Potentially malicious SQL pattern detected: {pattern}")
        
        # Remove SQL comments if not allowed
        if not allow_comments:
            # Remove single-line comments
            query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
            # Remove multi-line comments
            query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        return query.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid email format, False otherwise
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    @staticmethod
    def validate_dataset_name(dataset_name: str) -> bool:
        """
        Validate dataset name follows expected patterns
        
        Args:
            dataset_name: Dataset name to validate (e.g., 'gold.incidents')
            
        Returns:
            True if valid format, False otherwise
        """
        # Expected format: layer.entity_name
        pattern = r'^(bronze|silver|gold|external)\.[a-z_][a-z0-9_]*$'
        return bool(re.match(pattern, dataset_name))
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to remove potentially dangerous characters
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        # Remove path separators and special characters
        filename = os.path.basename(filename)
        # Allow only alphanumeric, dash, underscore, and period
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return filename
    
    @staticmethod
    def validate_workspace_name(workspace_name: str) -> bool:
        """
        Validate workspace name format
        
        Args:
            workspace_name: Workspace name to validate
            
        Returns:
            True if valid format, False otherwise
        """
        # Workspace names should be alphanumeric with hyphens/underscores
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]{2,62}[a-zA-Z0-9]$'
        return bool(re.match(pattern, workspace_name))
    
    @staticmethod
    def validate_column_name(column_name: str) -> bool:
        """
        Validate column name follows safe naming patterns
        
        Args:
            column_name: Column name to validate
            
        Returns:
            True if valid format, False otherwise
        """
        # Column names should be alphanumeric with underscores, starting with letter
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]{0,127}$'
        return bool(re.match(pattern, column_name))
    
    @staticmethod
    def check_secrets_exposure(content: str) -> List[str]:
        """
        Check content for potential secrets or sensitive data
        
        Args:
            content: Content to check
            
        Returns:
            List of potential issues found
        """
        issues = []
        
        # Check for common secret patterns
        patterns = {
            'Azure Connection String': r'DefaultEndpointsProtocol=https;AccountName=',
            'Private Key': r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----',
            'AWS Access Key': r'AKIA[0-9A-Z]{16}',
            'Password in URL': r'://[^:]+:[^@]+@',
            'Generic Secret': r'(secret|password|key|token)\s*[:=]\s*["\'][^"\']+["\']',
        }
        
        for issue_name, pattern in patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"Potential {issue_name} detected")
        
        return issues


def validate_deployment_artifact(artifact_path: str, base_dir: str) -> bool:
    """
    Validate a deployment artifact for security issues
    
    Args:
        artifact_path: Path to artifact
        base_dir: Base directory for path validation
        
    Returns:
        True if artifact passes security checks
        
    Raises:
        ValueError: If security issues are detected
    """
    validator = SecurityValidator()
    
    # Check path traversal
    if not validator.validate_path_traversal(artifact_path, base_dir):
        raise ValueError(f"Path traversal detected: {artifact_path}")
    
    # Sanitize filename
    sanitized_name = validator.sanitize_filename(os.path.basename(artifact_path))
    if sanitized_name != os.path.basename(artifact_path):
        raise ValueError(f"Invalid filename characters detected: {artifact_path}")
    
    # Check for secrets if it's a text file
    if artifact_path.endswith(('.py', '.sql', '.json', '.yaml', '.yml', '.txt')):
        try:
            with open(artifact_path, 'r') as f:
                content = f.read()
                issues = validator.check_secrets_exposure(content)
                if issues:
                    raise ValueError(f"Potential secrets detected: {', '.join(issues)}")
        except UnicodeDecodeError:
            # Binary file, skip content check
            pass
    
    return True
