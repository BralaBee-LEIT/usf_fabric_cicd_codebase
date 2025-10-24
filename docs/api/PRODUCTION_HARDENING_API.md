# API Documentation - Production Hardening Components

**Version:** 1.0  
**Date:** 24 October 2025  
**Status:** Implementation Guide

---

## 📚 **Table of Contents**

1. [SecretManager API](#secretmanager-api)
2. [RetryHandler API](#retryhandler-api)
3. [CircuitBreaker API](#circuitbreaker-api)
4. [DeploymentTransaction API](#deploymenttransaction-api)
5. [TelemetryLogger API](#telemetrylogger-api)
6. [FeatureFlags API](#featureflags-api)
7. [Integration Examples](#integration-examples)

---

## 🔐 **SecretManager API**

### **Module:** `ops/scripts/utilities/secret_manager.py`

### **Class: SecretManager**

Unified secret management with Azure Key Vault and .env fallback.

#### **Constructor**

```python
def __init__(self):
    """
    Initialize SecretManager
    
    Environment Variables:
        FEATURE_USE_KEY_VAULT: Enable Key Vault (default: false)
        KEY_VAULT_URL: Azure Key Vault URL (required if enabled)
        AZURE_TENANT_ID: Azure AD tenant ID
        AZURE_CLIENT_ID: Service principal client ID
        AZURE_CLIENT_SECRET: Service principal secret
    
    Raises:
        ValueError: If KEY_VAULT_URL missing when Key Vault enabled
    """
```

#### **Methods**

##### `get_secret(name: str, default: Optional[str] = None) -> Optional[str]`

Get secret from Key Vault with .env fallback.

```python
manager = get_secret_manager()
fabric_api_key = manager.get_secret("FABRIC_API_KEY")
```

**Parameters:**
- `name` (str): Secret name (e.g., "fabric-api-key")
- `default` (Optional[str]): Default value if not found

**Returns:**
- Secret value or default

**Behavior:**
1. If Key Vault enabled:
   - Check cache (TTL: 1 hour)
   - Fetch from Key Vault if cache miss
   - Fallback to .env on Key Vault failure
2. If Key Vault disabled:
   - Load from .env directly

**Example:**

```python
from ops.scripts.utilities.secret_manager import get_secret_manager

manager = get_secret_manager()

# Get required secret
tenant_id = manager.get_secret("AZURE_TENANT_ID")
if not tenant_id:
    raise ValueError("Missing AZURE_TENANT_ID")

# Get optional secret with default
retry_count = manager.get_secret("MAX_RETRIES", default="3")
```

##### `set_secret(name: str, value: str)`

Set secret in Key Vault (production only).

```python
manager.set_secret("new-api-key", "sk-...")
```

**Parameters:**
- `name` (str): Secret name
- `value` (str): Secret value

**Raises:**
- `ValueError`: If Key Vault disabled

**Example:**

```python
# Rotate API key
manager.set_secret("fabric-api-key", new_key_value)
manager.refresh_cache()  # Force reload
```

##### `refresh_cache()`

Clear cache to force reload from Key Vault.

```python
manager.refresh_cache()
```

**Use Cases:**
- After secret rotation
- Before critical operations
- During troubleshooting

---

### **Function: get_secret_manager() -> SecretManager**

Get singleton SecretManager instance.

```python
from ops.scripts.utilities.secret_manager import get_secret_manager

manager = get_secret_manager()
```

**Returns:**
- Singleton SecretManager instance

**Thread Safety:**
- Safe for multi-threaded use
- Cache is thread-local

---

## 🔄 **RetryHandler API**

### **Module:** `ops/scripts/utilities/retry_handler.py`

### **Decorator: @fabric_retry**

Retry decorator for Fabric API calls with exponential backoff.

```python
from ops.scripts.utilities.retry_handler import fabric_retry

@fabric_retry
def create_workspace(name: str) -> dict:
    response = requests.post(url, json={"displayName": name})
    response.raise_for_status()
    return response.json()
```

**Configuration:**
- Max attempts: 3
- Wait strategy: Exponential backoff
  - 1st retry: 2 seconds
  - 2nd retry: 4 seconds
  - 3rd retry: 8 seconds
- Retryable errors:
  - `ConnectionError`
  - `Timeout`
  - `HTTPError` (408, 429, 500-504)

**Feature Flag:**
- `FEATURE_USE_RETRY_LOGIC`: Enable/disable (default: false)
- When disabled, decorator is a no-op

**Example:**

```python
from ops.scripts.utilities.retry_handler import fabric_retry
import requests

class FabricClient:
    @fabric_retry
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make request with automatic retry"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, **kwargs)
        
        # Handle rate limiting
        if response.status_code == 429:
            retry_after = get_retry_after(response)
            time.sleep(retry_after)
            raise requests.exceptions.HTTPError("Rate limited")
        
        response.raise_for_status()
        return response
```

---

### **Function: is_retryable_error(response: requests.Response) -> bool**

Check if HTTP error is retryable.

```python
if is_retryable_error(response):
    # Retry logic will handle this
    response.raise_for_status()
else:
    # Non-retryable error
    logger.error(f"Cannot retry: {response.status_code}")
    response.raise_for_status()
```

**Parameters:**
- `response` (requests.Response): HTTP response object

**Returns:**
- `True` if status code in [408, 429, 500, 502, 503, 504]
- `False` otherwise

---

### **Function: get_retry_after(response: requests.Response) -> int**

Get Retry-After header value.

```python
if response.status_code == 429:
    wait_time = get_retry_after(response)
    time.sleep(wait_time)
```

**Parameters:**
- `response` (requests.Response): HTTP response object

**Returns:**
- Seconds to wait (from Retry-After header or default 5)

---

## ⚡ **CircuitBreaker API**

### **Module:** `ops/scripts/utilities/circuit_breaker.py`

### **Class: CircuitBreaker**

Circuit breaker pattern for fault tolerance.

#### **Constructor**

```python
def __init__(
    self,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception
):
    """
    Initialize circuit breaker
    
    Args:
        failure_threshold: Number of failures before opening (default: 5)
        recovery_timeout: Seconds before attempting reset (default: 60)
        expected_exception: Exception type to catch (default: Exception)
    """
```

**Example:**

```python
fabric_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=requests.exceptions.RequestException
)
```

#### **Methods**

##### `call(func: Callable, *args, **kwargs)`

Execute function with circuit breaker protection.

```python
result = breaker.call(fabric_client.create_workspace, "my-workspace")
```

**States:**
- **CLOSED**: Normal operation, all requests allowed
- **OPEN**: Too many failures, requests rejected
- **HALF_OPEN**: Testing recovery, limited requests allowed

**State Transitions:**

```
CLOSED --[5 failures]--> OPEN --[60 seconds]--> HALF_OPEN --[success]--> CLOSED
                                                      |
                                                  [failure]
                                                      |
                                                      v
                                                    OPEN
```

**Example:**

```python
from ops.scripts.utilities.circuit_breaker import CircuitBreaker
import requests

# Create circuit breaker for Fabric API
fabric_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30
)

def risky_operation():
    try:
        result = fabric_breaker.call(
            fabric_client.create_workspace,
            workspace_name="test"
        )
        return result
    except Exception as e:
        if "Circuit breaker OPEN" in str(e):
            logger.error("Fabric API temporarily unavailable")
            # Use cached data or queue for later
        else:
            logger.error(f"Operation failed: {e}")
        raise
```

---

## 📦 **DeploymentTransaction API**

### **Module:** `ops/scripts/utilities/deployment_transaction.py`

### **Class: ResourceRecord**

Track a created resource for rollback.

```python
@dataclass
class ResourceRecord:
    resource_type: str       # "workspace", "item", "user"
    resource_id: str         # Unique ID
    resource_name: str       # Display name
    cleanup_function: Callable  # Function to call for cleanup
    cleanup_args: Dict[str, Any]  # Arguments for cleanup
    metadata: Dict[str, Any] = None  # Optional metadata
```

---

### **Class: DeploymentTransaction**

Manage deployment as a transaction with rollback capability.

#### **Constructor**

```python
def __init__(
    self,
    transaction_id: str,
    enable_rollback: bool = None
):
    """
    Initialize deployment transaction
    
    Args:
        transaction_id: Unique transaction identifier
        enable_rollback: Enable rollback (default: from feature flag)
    """
```

**Example:**

```python
import uuid
from ops.scripts.utilities.deployment_transaction import DeploymentTransaction

transaction_id = str(uuid.uuid4())
transaction = DeploymentTransaction(transaction_id)
```

#### **Methods**

##### `register_resource(...)`

Register a resource for potential rollback.

```python
def register_resource(
    self,
    resource_type: str,
    resource_id: str,
    resource_name: str,
    cleanup_function: Callable,
    cleanup_args: Dict[str, Any],
    metadata: Dict[str, Any] = None
):
```

**Example:**

```python
# Create workspace and register for rollback
workspace = fabric_client.create_workspace(name="sales-analytics")

transaction.register_resource(
    resource_type="workspace",
    resource_id=workspace["id"],
    resource_name=workspace["displayName"],
    cleanup_function=fabric_client.delete_workspace,
    cleanup_args={"workspace_id": workspace["id"], "force": True},
    metadata={"capacity_id": "cap-123"}
)
```

##### `commit()`

Commit transaction - no rollback will occur.

```python
# All operations succeeded
transaction.commit()
logger.info("Deployment successful - no rollback needed")
```

**Behavior:**
- Marks transaction as committed
- Prevents rollback even if exception occurs
- Preserves all created resources

##### `rollback(reason: str = "Transaction failed")`

Rollback all created resources.

```python
try:
    # Some operation fails
    raise Exception("Git connection failed")
except Exception as e:
    transaction.rollback(reason=f"Exception: {str(e)}")
```

**Behavior:**
- Rolls back resources in reverse order
- Logs each cleanup attempt
- Continues rollback even if individual cleanup fails
- Reports errors for manual cleanup

**Example Output:**

```
WARNING - Rolling back transaction abc-123. Reason: Git connection failed
INFO - Cleaning up user_assignment 'User xyz in workspace-123'
INFO - ✓ Successfully cleaned up user_assignment
INFO - Cleaning up workspace 'sales-analytics-dev' (ws-456)
INFO - ✓ Successfully cleaned up workspace
INFO - ✓ Transaction abc-123 fully rolled back
```

#### **Context Manager**

Use with `with` statement for automatic rollback.

```python
with DeploymentTransaction(transaction_id) as transaction:
    # Create resources
    workspace = create_workspace(...)
    transaction.register_resource(...)
    
    # If exception occurs, automatic rollback
    add_users(...)
    transaction.register_resource(...)
    
    # All succeeded - commit
    transaction.commit()
```

**Behavior:**
- Automatic rollback on exception
- No rollback if committed
- Exception propagates after rollback

---

## 📊 **TelemetryLogger API**

### **Module:** `ops/scripts/utilities/telemetry_logger.py`

### **Class: TelemetryLogger**

Application Insights integration for telemetry.

#### **Constructor**

```python
def __init__(self, instrumentation_key: Optional[str] = None):
    """
    Initialize telemetry logger
    
    Args:
        instrumentation_key: App Insights key (from env if not provided)
    
    Environment Variables:
        FEATURE_USE_TELEMETRY: Enable telemetry (default: false)
        APPINSIGHTS_INSTRUMENTATION_KEY: App Insights key
    """
```

#### **Methods**

##### `track_event(name: str, properties: Dict[str, Any] = None)`

Track custom event.

```python
telemetry.track_event(
    "WorkspaceCreated",
    properties={
        "workspace_id": "ws-123",
        "workspace_name": "sales-analytics",
        "environment": "dev",
        "capacity_id": "cap-456"
    }
)
```

##### `track_metric(name: str, value: float, properties: Dict[str, Any] = None)`

Track custom metric.

```python
telemetry.track_metric(
    "DeploymentDuration",
    value=45.2,  # seconds
    properties={"scenario": "automated-deployment"}
)
```

##### `track_exception(exception: Exception, properties: Dict[str, Any] = None)`

Track exception.

```python
try:
    create_workspace(...)
except Exception as e:
    telemetry.track_exception(
        e,
        properties={
            "operation": "create_workspace",
            "workspace_name": name
        }
    )
    raise
```

##### `operation(name: str, properties: Dict[str, Any] = None)`

Context manager for tracking operations.

```python
with telemetry.operation("CreateWorkspace", {"name": "sales-analytics"}):
    workspace = fabric_client.create_workspace(name)
    # Automatically tracks duration, success/failure
```

**Captured Automatically:**
- Operation duration
- Success/failure status
- Exception details (if raised)
- Custom properties

---

## 🚩 **FeatureFlags API**

### **Module:** `ops/scripts/utilities/feature_flags.py`

### **Class: FeatureFlags**

Control rollout of new features.

```python
class FeatureFlags:
    """Feature flags for production hardening"""
    
    USE_KEY_VAULT = os.getenv("FEATURE_USE_KEY_VAULT", "false").lower() == "true"
    USE_RETRY_LOGIC = os.getenv("FEATURE_USE_RETRY_LOGIC", "false").lower() == "true"
    USE_TELEMETRY = os.getenv("FEATURE_USE_TELEMETRY", "false").lower() == "true"
    USE_ROLLBACK = os.getenv("FEATURE_USE_ROLLBACK", "false").lower() == "true"
    USE_CIRCUIT_BREAKER = os.getenv("FEATURE_USE_CIRCUIT_BREAKER", "false").lower() == "true"
```

**Usage:**

```python
from ops.scripts.utilities.feature_flags import FeatureFlags

if FeatureFlags.USE_KEY_VAULT:
    # Use Key Vault for secrets
    manager = get_secret_manager()
    secret = manager.get_secret("api-key")
else:
    # Use .env
    secret = os.getenv("API_KEY")
```

**Environment Variables:**

```bash
# Enable all features
export FEATURE_USE_KEY_VAULT=true
export FEATURE_USE_RETRY_LOGIC=true
export FEATURE_USE_TELEMETRY=true
export FEATURE_USE_ROLLBACK=true
export FEATURE_USE_CIRCUIT_BREAKER=true
```

---

## 🎯 **Integration Examples**

### **Example 1: Enhanced Workspace Creation**

```python
from ops.scripts.utilities.secret_manager import get_secret_manager
from ops.scripts.utilities.retry_handler import fabric_retry
from ops.scripts.utilities.deployment_transaction import DeploymentTransaction
from ops.scripts.utilities.telemetry_logger import get_telemetry_logger
import uuid

# Get dependencies
secret_manager = get_secret_manager()
telemetry = get_telemetry_logger()

# Get credentials from Key Vault (with .env fallback)
tenant_id = secret_manager.get_secret("AZURE_TENANT_ID")
client_id = secret_manager.get_secret("AZURE_CLIENT_ID")
client_secret = secret_manager.get_secret("AZURE_CLIENT_SECRET")

class EnhancedFabricClient:
    """Fabric client with all production hardening features"""
    
    @fabric_retry  # Automatic retry with exponential backoff
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make request with retry logic"""
        # Implementation...
        pass
    
    def create_workspace_with_transaction(
        self,
        name: str,
        transaction: DeploymentTransaction
    ) -> dict:
        """Create workspace with telemetry and transaction support"""
        
        with telemetry.operation("CreateWorkspace", {"name": name}):
            # Create workspace
            workspace = self._make_request(
                "POST",
                "workspaces",
                json={"displayName": name}
            )
            
            # Register for rollback
            transaction.register_resource(
                resource_type="workspace",
                resource_id=workspace["id"],
                resource_name=workspace["displayName"],
                cleanup_function=self.delete_workspace,
                cleanup_args={"workspace_id": workspace["id"]}
            )
            
            # Track success
            telemetry.track_event(
                "WorkspaceCreated",
                properties={
                    "workspace_id": workspace["id"],
                    "workspace_name": name
                }
            )
            
            return workspace

# Usage
def deploy_workspace(config: dict):
    """Deploy workspace with full production hardening"""
    
    transaction_id = str(uuid.uuid4())
    
    with DeploymentTransaction(transaction_id) as transaction:
        try:
            client = EnhancedFabricClient()
            
            # Create workspace (with retry, telemetry, rollback)
            workspace = client.create_workspace_with_transaction(
                name=config["workspace_name"],
                transaction=transaction
            )
            
            # Additional operations...
            # All registered for rollback
            
            # Success - commit transaction
            transaction.commit()
            
            return workspace
            
        except Exception as e:
            # Automatic rollback via context manager
            logger.error(f"Deployment failed: {e}")
            raise
```

### **Example 2: Gradual Feature Rollout**

```python
from ops.scripts.utilities.feature_flags import FeatureFlags
from ops.scripts.utilities.secret_manager import get_secret_manager
import os

def get_api_credentials():
    """Get credentials with gradual Key Vault adoption"""
    
    if FeatureFlags.USE_KEY_VAULT:
        # Production: Use Key Vault
        manager = get_secret_manager()
        return {
            "tenant_id": manager.get_secret("AZURE_TENANT_ID"),
            "client_id": manager.get_secret("AZURE_CLIENT_ID"),
            "client_secret": manager.get_secret("AZURE_CLIENT_SECRET")
        }
    else:
        # Development: Use .env
        return {
            "tenant_id": os.getenv("AZURE_TENANT_ID"),
            "client_id": os.getenv("AZURE_CLIENT_ID"),
            "client_secret": os.getenv("AZURE_CLIENT_SECRET")
        }
```

### **Example 3: Complete Deployment with All Features**

```python
import uuid
from ops.scripts.utilities.secret_manager import get_secret_manager
from ops.scripts.utilities.deployment_transaction import DeploymentTransaction
from ops.scripts.utilities.telemetry_logger import get_telemetry_logger
from ops.scripts.utilities.feature_flags import FeatureFlags

def run_complete_deployment(config: dict):
    """
    Complete deployment with all production hardening features:
    - Secret management (Key Vault)
    - Retry logic (exponential backoff)
    - Transaction rollback
    - Telemetry (Application Insights)
    - Circuit breaker
    """
    
    # Initialize services
    secret_manager = get_secret_manager()
    telemetry = get_telemetry_logger()
    transaction_id = str(uuid.uuid4())
    
    # Track deployment
    with telemetry.operation("CompleteDeployment", {"config": config}):
        with DeploymentTransaction(transaction_id) as transaction:
            try:
                # Step 1: Create workspace
                workspace = create_workspace_with_features(
                    config["workspace_name"],
                    transaction
                )
                
                # Step 2: Add users
                for user in config["users"]:
                    add_user_with_features(
                        workspace["id"],
                        user,
                        transaction
                    )
                
                # Step 3: Connect Git
                connect_git_with_features(
                    workspace["id"],
                    config["git"],
                    transaction
                )
                
                # Step 4: Create items
                for item in config["items"]:
                    create_item_with_features(
                        workspace["id"],
                        item,
                        transaction
                    )
                
                # All succeeded - commit
                transaction.commit()
                
                telemetry.track_event(
                    "DeploymentSuccess",
                    properties={
                        "transaction_id": transaction_id,
                        "workspace_id": workspace["id"]
                    }
                )
                
                return workspace
                
            except Exception as e:
                # Automatic rollback via context manager
                telemetry.track_exception(
                    e,
                    properties={
                        "transaction_id": transaction_id,
                        "operation": "deployment"
                    }
                )
                logger.error(f"Deployment failed, rolled back: {e}")
                raise
```

---

## 📋 **Configuration Reference**

### **Environment Variables**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FEATURE_USE_KEY_VAULT` | No | `false` | Enable Azure Key Vault |
| `FEATURE_USE_RETRY_LOGIC` | No | `false` | Enable retry logic |
| `FEATURE_USE_TELEMETRY` | No | `false` | Enable Application Insights |
| `FEATURE_USE_ROLLBACK` | No | `false` | Enable transaction rollback |
| `FEATURE_USE_CIRCUIT_BREAKER` | No | `false` | Enable circuit breaker |
| `KEY_VAULT_URL` | If KV enabled | - | Key Vault URL |
| `APPINSIGHTS_INSTRUMENTATION_KEY` | If telemetry enabled | - | App Insights key |
| `AZURE_TENANT_ID` | Yes | - | Azure AD tenant ID |
| `AZURE_CLIENT_ID` | Yes | - | Service principal client ID |
| `AZURE_CLIENT_SECRET` | Yes | - | Service principal secret |

### **Feature Flag Combinations**

#### **Local Development**
```bash
# Minimal features for local dev
FEATURE_USE_KEY_VAULT=false
FEATURE_USE_RETRY_LOGIC=true   # Helps with flaky connections
FEATURE_USE_TELEMETRY=false
FEATURE_USE_ROLLBACK=false     # Easier debugging
FEATURE_USE_CIRCUIT_BREAKER=false
```

#### **Development Environment**
```bash
# Most features enabled
FEATURE_USE_KEY_VAULT=true
FEATURE_USE_RETRY_LOGIC=true
FEATURE_USE_TELEMETRY=true
FEATURE_USE_ROLLBACK=true
FEATURE_USE_CIRCUIT_BREAKER=true
```

#### **Production Environment**
```bash
# All features mandatory
FEATURE_USE_KEY_VAULT=true
FEATURE_USE_RETRY_LOGIC=true
FEATURE_USE_TELEMETRY=true
FEATURE_USE_ROLLBACK=true
FEATURE_USE_CIRCUIT_BREAKER=true
```

---

**Document Owner:** GitHub Copilot  
**Last Updated:** 24 October 2025  
**Next Review:** Post-implementation
