"""
Global constants for Microsoft Fabric CI/CD solution

This module centralizes all configuration constants, URLs, and magic numbers
to improve maintainability and allow environment-specific configuration.
"""

import os

# ============================================================================
# Azure Authentication & API Endpoints
# ============================================================================

# Azure Active Directory
AZURE_LOGIN_BASE_URL = os.getenv(
    "AZURE_LOGIN_BASE_URL", "https://login.microsoftonline.com"
)

# Microsoft Fabric API
FABRIC_API_BASE_URL = os.getenv(
    "FABRIC_API_BASE_URL", "https://api.fabric.microsoft.com/v1"
)

FABRIC_API_SCOPE = os.getenv(
    "FABRIC_API_SCOPE", "https://api.fabric.microsoft.com/.default"
)

# Power BI API
POWERBI_API_BASE_URL = os.getenv(
    "POWERBI_API_BASE_URL", "https://api.powerbi.com/v1.0/myorg"
)

POWERBI_API_SCOPE = os.getenv(
    "POWERBI_API_SCOPE", "https://analysis.windows.net/powerbi/api/.default"
)

# ============================================================================
# Azure Service Suffixes
# ============================================================================

AZURE_SQL_SUFFIX = ".database.windows.net"
AZURE_COSMOS_SUFFIX = ".documents.azure.com"
AZURE_STORAGE_SUFFIX = ".blob.core.windows.net"
AZURE_PURVIEW_SUFFIX = ".purview.azure.com"

# ============================================================================
# Purview Configuration
# ============================================================================

PURVIEW_ENDPOINT = os.getenv("PURVIEW_ENDPOINT", "https://usfpurview.purview.azure.com")

PURVIEW_API_VERSION = os.getenv("PURVIEW_API_VERSION", "2022-07-01-preview")

# ============================================================================
# Polling & Retry Configuration
# ============================================================================

# Deployment polling settings
DEFAULT_POLLING_INTERVAL_SECONDS = int(os.getenv("POLLING_INTERVAL", "30"))
MAX_POLLING_ATTEMPTS = int(os.getenv("MAX_POLLING_ATTEMPTS", "60"))
DEPLOYMENT_TIMEOUT_SECONDS = int(os.getenv("DEPLOYMENT_TIMEOUT", "1800"))  # 30 minutes

# API retry settings
MAX_API_RETRIES = int(os.getenv("MAX_API_RETRIES", "3"))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))
RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", "1"))

# ============================================================================
# HTTP Configuration
# ============================================================================

# Timeouts (in seconds)
HTTP_CONNECT_TIMEOUT = int(os.getenv("HTTP_CONNECT_TIMEOUT", "10"))
HTTP_READ_TIMEOUT = int(os.getenv("HTTP_READ_TIMEOUT", "30"))
HTTP_DEFAULT_TIMEOUT = (HTTP_CONNECT_TIMEOUT, HTTP_READ_TIMEOUT)

# Status codes
HTTP_STATUS_OK = 200
HTTP_STATUS_CREATED = 201
HTTP_STATUS_ACCEPTED = 202
HTTP_STATUS_NO_CONTENT = 204
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_CONFLICT = 409
HTTP_STATUS_TOO_MANY_REQUESTS = 429
HTTP_STATUS_SERVER_ERROR = 500

# ============================================================================
# File System Configuration
# ============================================================================

# Default directories
DEFAULT_CONFIG_DIR = "config"
DEFAULT_GOVERNANCE_DIR = "governance"
DEFAULT_DATA_CONTRACTS_DIR = "governance/data_contracts"
DEFAULT_DQ_RULES_DIR = "governance/dq_rules"
DEFAULT_OPS_DIR = "ops"
DEFAULT_SCRIPTS_DIR = "ops/scripts"

# File extensions
YAML_EXTENSIONS = [".yaml", ".yml"]
JSON_EXTENSIONS = [".json"]
PYTHON_EXTENSIONS = [".py"]
NOTEBOOK_EXTENSIONS = [".ipynb"]
SQL_EXTENSIONS = [".sql"]

# ============================================================================
# Validation Configuration
# ============================================================================

# Email validation pattern
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Dataset naming pattern
DATASET_NAME_PATTERN = r"^[a-z]+\.[a-z_]+$"

# Valid data quality check types
VALID_DQ_CHECK_TYPES = [
    "not_null",
    "unique",
    "valid_values",
    "range",
    "pattern",
    "completeness",
    "freshness",
    "volume",
    "distribution",
    "referential_integrity",
]

# Valid severity levels
VALID_SEVERITY_LEVELS = ["critical", "high", "medium", "low"]

# ============================================================================
# Security Configuration
# ============================================================================

# Secret patterns to detect
SECRET_PATTERNS = [
    r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?[\w\-\.@]+["\']?',
    r'(?i)(api[_\-]?key|apikey)\s*[=:]\s*["\']?[\w\-]+["\']?',
    r'(?i)(secret|token)\s*[=:]\s*["\']?[\w\-]+["\']?',
    r'(?i)(connection[_\-]?string)\s*[=:]\s*["\']?.+["\']?',
    r'["\'][a-zA-Z0-9]{32,}["\']',  # Generic long strings in quotes
]

# SQL injection patterns
SQL_INJECTION_PATTERNS = [
    r"(\bDROP\b|\bDELETE\b|\bTRUNCATE\b)",
    r"(--|\#|\/\*)",
    r"(\bOR\b\s+[\w\d]+\s*=\s*[\w\d]+)",
    r"(\bUNION\b.*\bSELECT\b)",
    r"(\bEXEC\b|\bEXECUTE\b)",
]

# Maximum allowed path traversal levels
MAX_PATH_TRAVERSAL_LEVELS = 3

# ============================================================================
# Logging Configuration
# ============================================================================

# Log levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"

DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", LOG_LEVEL_INFO)

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# Data Quality Thresholds
# ============================================================================

# Default thresholds (can be overridden in DQ rules)
DEFAULT_COMPLETENESS_THRESHOLD = 0.95  # 95%
DEFAULT_UNIQUENESS_THRESHOLD = 0.99  # 99%
DEFAULT_VALIDITY_THRESHOLD = 0.98  # 98%

# ============================================================================
# Deployment Configuration
# ============================================================================

# Valid deployment modes
DEPLOYMENT_MODE_VALIDATE = "validate"
DEPLOYMENT_MODE_DEPLOY = "deploy"
DEPLOYMENT_MODE_ROLLBACK = "rollback"
VALID_DEPLOYMENT_MODES = [
    DEPLOYMENT_MODE_VALIDATE,
    DEPLOYMENT_MODE_DEPLOY,
    DEPLOYMENT_MODE_ROLLBACK,
]

# Valid environments
ENVIRONMENT_DEV = "dev"
ENVIRONMENT_TEST = "test"
ENVIRONMENT_PROD = "prod"
VALID_ENVIRONMENTS = [ENVIRONMENT_DEV, ENVIRONMENT_TEST, ENVIRONMENT_PROD]

# Artifact types
ARTIFACT_TYPE_NOTEBOOK = "notebook"
ARTIFACT_TYPE_PIPELINE = "pipeline"
ARTIFACT_TYPE_DATAFLOW = "dataflow"
ARTIFACT_TYPE_LAKEHOUSE = "lakehouse"
ARTIFACT_TYPE_WAREHOUSE = "warehouse"
ARTIFACT_TYPE_REPORT = "report"

# ============================================================================
# Cache Configuration
# ============================================================================

# LRU cache sizes
WORKSPACE_CACHE_SIZE = 128
ITEM_CACHE_SIZE = 256
TOKEN_CACHE_SIZE = 1

# Cache TTL (in seconds)
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 1800  # 30 minutes
CACHE_TTL_LONG = 3600  # 1 hour

# ============================================================================
# Error Messages
# ============================================================================

ERROR_MISSING_CREDENTIALS = "Missing required Azure credentials. Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET"
ERROR_INVALID_ENVIRONMENT = "Invalid environment specified. Valid environments: {}"
ERROR_INVALID_DEPLOYMENT_MODE = "Invalid deployment mode. Valid modes: {}"
ERROR_CONFIG_NOT_FOUND = "Configuration file not found: {}"
ERROR_VALIDATION_FAILED = "Validation failed with {} errors"
ERROR_DEPLOYMENT_FAILED = "Deployment failed: {}"
ERROR_ROLLBACK_FAILED = "Rollback failed: {}"
ERROR_API_REQUEST_FAILED = "API request failed: {} - {}"
ERROR_AUTHENTICATION_FAILED = "Authentication failed: {}"

# ============================================================================
# Success Messages
# ============================================================================

SUCCESS_VALIDATION_PASSED = "✅ Validation passed successfully"
SUCCESS_DEPLOYMENT_COMPLETE = "✅ Deployment completed successfully"
SUCCESS_ROLLBACK_COMPLETE = "✅ Rollback completed successfully"
SUCCESS_CONFIG_LOADED = "✅ Configuration loaded successfully"

# ============================================================================
# Feature Flags (for gradual rollout)
# ============================================================================

ENABLE_ROLLBACK = os.getenv("ENABLE_ROLLBACK", "true").lower() == "true"
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
ENABLE_SECURITY_VALIDATION = (
    os.getenv("ENABLE_SECURITY_VALIDATION", "true").lower() == "true"
)
ENABLE_VERBOSE_LOGGING = os.getenv("ENABLE_VERBOSE_LOGGING", "false").lower() == "true"
ENABLE_DRY_RUN = os.getenv("ENABLE_DRY_RUN", "false").lower() == "true"

# ============================================================================
# Version Information
# ============================================================================

CONSTANTS_VERSION = "1.0.0"
API_VERSION = "v1"

# ============================================================================
# Helper Functions
# ============================================================================


def get_azure_authority_url(tenant_id: str) -> str:
    """
    Get the Azure AD authority URL for a given tenant.

    Args:
        tenant_id: The Azure AD tenant ID

    Returns:
        Complete authority URL

    Example:
        >>> get_azure_authority_url("12345-67890")
        'https://login.microsoftonline.com/12345-67890'
    """
    return f"{AZURE_LOGIN_BASE_URL}/{tenant_id}"


def get_sql_server_url(environment: str) -> str:
    """
    Get the Azure SQL Server URL for a given environment.

    Args:
        environment: The environment name (dev, test, prod)

    Returns:
        SQL Server connection string prefix

    Example:
        >>> get_sql_server_url("dev")
        'Server=sql-dev.database.windows.net'
    """
    return f"Server=sql-{environment}{AZURE_SQL_SUFFIX}"


def get_cosmos_db_url(environment: str) -> str:
    """
    Get the Azure Cosmos DB URL for a given environment.

    Args:
        environment: The environment name (dev, test, prod)

    Returns:
        Cosmos DB endpoint URL

    Example:
        >>> get_cosmos_db_url("prod")
        'https://cosmos-prod.documents.azure.com:443/'
    """
    return f"https://cosmos-{environment}{AZURE_COSMOS_SUFFIX}:443/"


def is_valid_environment(environment: str) -> bool:
    """
    Check if an environment name is valid.

    Args:
        environment: The environment name to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> is_valid_environment("dev")
        True
        >>> is_valid_environment("invalid")
        False
    """
    return environment in VALID_ENVIRONMENTS


def is_valid_deployment_mode(mode: str) -> bool:
    """
    Check if a deployment mode is valid.

    Args:
        mode: The deployment mode to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> is_valid_deployment_mode("deploy")
        True
        >>> is_valid_deployment_mode("invalid")
        False
    """
    return mode in VALID_DEPLOYMENT_MODES


# ============================================================================
# Module Initialization
# ============================================================================


def validate_constants():
    """
    Validate that all required constants are properly configured.
    Raises ValueError if any critical constants are missing or invalid.
    """
    errors = []

    # Validate polling configuration
    if DEFAULT_POLLING_INTERVAL_SECONDS <= 0:
        errors.append("POLLING_INTERVAL must be positive")

    if MAX_POLLING_ATTEMPTS <= 0:
        errors.append("MAX_POLLING_ATTEMPTS must be positive")

    # Validate retry configuration
    if MAX_API_RETRIES < 0:
        errors.append("MAX_API_RETRIES must be non-negative")

    if RETRY_BACKOFF_FACTOR < 1.0:
        errors.append("RETRY_BACKOFF_FACTOR must be >= 1.0")

    # Validate timeouts
    if HTTP_CONNECT_TIMEOUT <= 0:
        errors.append("HTTP_CONNECT_TIMEOUT must be positive")

    if HTTP_READ_TIMEOUT <= 0:
        errors.append("HTTP_READ_TIMEOUT must be positive")

    if errors:
        raise ValueError(f"Invalid constants configuration: {', '.join(errors)}")


# Validate on import (can be disabled with environment variable)
if os.getenv("SKIP_CONSTANTS_VALIDATION", "false").lower() != "true":
    validate_constants()
