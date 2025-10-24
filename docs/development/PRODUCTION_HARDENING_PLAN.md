# Production Hardening Implementation Plan

**Date:** October 24, 2025  
**Branch:** `feature/production-hardening`  
**Target:** Production-ready Microsoft Fabric CI/CD Framework  
**Duration:** 4 weeks (20 working days)

---

## 🎯 **Objectives**

Transform the current framework from development-ready to production-ready by addressing:
1. **Security** - Secrets management, RBAC, encryption
2. **Reliability** - Error handling, retry logic, rollback
3. **Observability** - Monitoring, health checks, alerting
4. **Testing** - Integration, E2E, performance tests
5. **Configuration** - Schema validation, environment overrides

**Success Criteria:**
- ✅ All secrets moved to Azure Key Vault
- ✅ 100% of Fabric API calls have retry logic
- ✅ Transaction rollback implemented for all operations
- ✅ Application Insights integrated with dashboards
- ✅ Integration test coverage >80%
- ✅ Zero breaking changes to existing scenarios

---

## 📋 **Implementation Strategy**

### **Principle 1: Non-Breaking Changes**
- All new features must be **backward compatible**
- Existing scenarios continue to work without modification
- New features opt-in via configuration flags
- Deprecation warnings before any removals

### **Principle 2: Incremental Implementation**
- Work in small, testable increments
- Each commit is independently deployable
- Feature flags control new functionality
- CI/CD validates after every change

### **Principle 3: Test-First Approach**
- Write tests before implementation
- Each feature has unit + integration tests
- E2E tests validate complete workflows
- Performance benchmarks establish baselines

### **Principle 4: Documentation-Driven**
- Document design before coding
- Update docs with implementation
- Migration guides for any changes
- Operational runbooks for new features

---

## 🗓️ **Phase-by-Phase Implementation Plan**

### **Phase 1: Security Hardening (Week 1 - Days 1-5)**

#### **Day 1: Setup & Foundation**

**Task 1.1: Create Feature Branch**
```bash
git checkout main
git pull origin main
git checkout -b feature/production-hardening
git push -u origin feature/production-hardening
```

**Task 1.2: Add Dependencies**
```python
# requirements.txt additions
azure-keyvault-secrets>=4.7.0
azure-identity>=1.15.0
tenacity>=8.2.3
applicationinsights>=0.11.10
jsonschema>=4.20.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-benchmark>=4.0.0
```

**Task 1.3: Create Feature Flag System**
```python
# ops/scripts/utilities/feature_flags.py
class FeatureFlags:
    """Control rollout of new features"""
    
    USE_KEY_VAULT = os.getenv("FEATURE_USE_KEY_VAULT", "false").lower() == "true"
    USE_RETRY_LOGIC = os.getenv("FEATURE_USE_RETRY_LOGIC", "false").lower() == "true"
    USE_TELEMETRY = os.getenv("FEATURE_USE_TELEMETRY", "false").lower() == "true"
    USE_ROLLBACK = os.getenv("FEATURE_USE_ROLLBACK", "false").lower() == "true"
```

**Task 1.4: Create Secret Manager (Azure Key Vault)**
```python
# ops/scripts/utilities/secret_manager.py
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from typing import Optional
import os
from .feature_flags import FeatureFlags

class SecretManager:
    """Unified secret management with Key Vault + .env fallback"""
    
    def __init__(self):
        self.use_keyvault = FeatureFlags.USE_KEY_VAULT
        
        if self.use_keyvault:
            vault_url = os.getenv("KEY_VAULT_URL")
            if not vault_url:
                raise ValueError("KEY_VAULT_URL required when using Key Vault")
            
            # Support both DefaultAzureCredential and ClientSecretCredential
            tenant_id = os.getenv("AZURE_TENANT_ID")
            client_id = os.getenv("AZURE_CLIENT_ID")
            client_secret = os.getenv("AZURE_CLIENT_SECRET")
            
            if tenant_id and client_id and client_secret:
                credential = ClientSecretCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret
                )
            else:
                credential = DefaultAzureCredential()
            
            self.kv_client = SecretClient(
                vault_url=vault_url,
                credential=credential
            )
            self._cache = {}
            self._cache_ttl = 3600  # 1 hour
        else:
            self.kv_client = None
    
    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from Key Vault with .env fallback"""
        if self.use_keyvault:
            try:
                # Check cache first
                if name in self._cache:
                    return self._cache[name]
                
                # Fetch from Key Vault
                secret = self.kv_client.get_secret(name)
                self._cache[name] = secret.value
                return secret.value
            except Exception as e:
                logger.warning(f"Failed to get secret '{name}' from Key Vault: {e}")
                # Fallback to environment variable
        
        # Fallback to .env
        value = os.getenv(name.upper().replace("-", "_"), default)
        return value
    
    def set_secret(self, name: str, value: str):
        """Set secret in Key Vault (production only)"""
        if not self.use_keyvault:
            raise ValueError("Cannot set secrets when Key Vault is disabled")
        
        self.kv_client.set_secret(name, value)
        # Invalidate cache
        if name in self._cache:
            del self._cache[name]
    
    def refresh_cache(self):
        """Clear cache to force reload"""
        self._cache = {}

# Global instance
_secret_manager = None

def get_secret_manager() -> SecretManager:
    """Get singleton SecretManager instance"""
    global _secret_manager
    if _secret_manager is None:
        _secret_manager = SecretManager()
    return _secret_manager
```

**Files to Update:**
- `ops/scripts/utilities/fabric_api.py` - Use SecretManager
- `ops/scripts/utilities/workspace_manager.py` - Use SecretManager
- `ops/scripts/utilities/git_connector.py` - Use SecretManager

**Test Coverage:**
```python
# tests/unit/test_secret_manager.py
def test_secret_manager_env_fallback():
    """Test .env fallback when Key Vault disabled"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "false"
    os.environ["TEST_SECRET"] = "test-value"
    
    manager = SecretManager()
    assert manager.get_secret("TEST_SECRET") == "test-value"

def test_secret_manager_keyvault(mock_keyvault):
    """Test Key Vault integration"""
    os.environ["FEATURE_USE_KEY_VAULT"] = "true"
    os.environ["KEY_VAULT_URL"] = "https://test.vault.azure.net"
    
    manager = SecretManager()
    assert manager.get_secret("fabric-api-key") == "mock-value"
```

**Documentation:**
- `docs/security/KEY_VAULT_SETUP.md` - Setup guide
- `docs/security/SECRET_MANAGEMENT.md` - Usage guide
- `docs/migration/ENV_TO_KEYVAULT.md` - Migration guide

**Acceptance Criteria:**
- ✅ SecretManager works with Key Vault enabled
- ✅ SecretManager falls back to .env when disabled
- ✅ All existing scenarios work without changes
- ✅ Unit tests pass (>90% coverage)
- ✅ Documentation complete

---

#### **Day 2-3: Retry Logic & Circuit Breaker**

**Task 1.5: Create Retry Decorator**
```python
# ops/scripts/utilities/retry_handler.py
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)
import requests
import logging
from .feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

def create_fabric_retry_decorator():
    """Create retry decorator for Fabric API calls"""
    if not FeatureFlags.USE_RETRY_LOGIC:
        # No-op decorator when feature disabled
        def no_retry(func):
            return func
        return no_retry
    
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True
    )

# Decorator instance
fabric_retry = create_fabric_retry_decorator()

def is_retryable_error(response: requests.Response) -> bool:
    """Check if HTTP error is retryable"""
    if response.status_code in [408, 429, 500, 502, 503, 504]:
        return True
    return False

def get_retry_after(response: requests.Response) -> int:
    """Get Retry-After header value"""
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return int(retry_after)
        except ValueError:
            pass
    return 5  # Default 5 seconds
```

**Task 1.6: Update FabricClient with Retry Logic**
```python
# ops/scripts/utilities/fabric_api.py
from .retry_handler import fabric_retry, is_retryable_error, get_retry_after
import time

class FabricClient:
    @fabric_retry
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """Make authenticated request to Fabric API with retry logic"""
        # ... existing code ...
        
        response = requests.request(method, url, headers=headers, **kwargs)
        
        # Check for rate limiting
        if response.status_code == 429:
            retry_after = get_retry_after(response)
            logger.warning(f"Rate limited. Retrying after {retry_after} seconds")
            time.sleep(retry_after)
            raise requests.exceptions.HTTPError(
                f"429 Rate Limit Exceeded", 
                response=response
            )
        
        # Check for retryable errors
        if is_retryable_error(response):
            logger.warning(f"Retryable error {response.status_code}")
            response.raise_for_status()
        
        # Non-retryable errors
        if not response.ok:
            logger.error(f"Fabric API error: {response.status_code} - {response.text}")
            response.raise_for_status()
        
        return response
```

**Task 1.7: Implement Circuit Breaker**
```python
# ops/scripts/utilities/circuit_breaker.py
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception(
                    f"Circuit breaker OPEN. Too many failures. "
                    f"Will retry after {self.recovery_timeout} seconds"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker OPEN after {self.failure_count} failures"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
```

**Test Coverage:**
```python
# tests/unit/test_retry_handler.py
def test_retry_on_connection_error(mock_api):
    """Test retry on connection errors"""
    mock_api.side_effect = [
        requests.exceptions.ConnectionError(),
        requests.exceptions.ConnectionError(),
        mock_response(200, {"status": "success"})
    ]
    
    client = FabricClient()
    response = client._make_request("GET", "workspaces")
    assert response.status_code == 200
    assert mock_api.call_count == 3

def test_retry_on_rate_limit(mock_api):
    """Test retry with Retry-After header"""
    mock_api.side_effect = [
        mock_response(429, {}, headers={"Retry-After": "2"}),
        mock_response(200, {"status": "success"})
    ]
    
    client = FabricClient()
    response = client._make_request("GET", "workspaces")
    assert response.status_code == 200

def test_circuit_breaker_opens_after_threshold():
    """Test circuit breaker opens after failures"""
    breaker = CircuitBreaker(failure_threshold=3)
    
    def failing_function():
        raise Exception("Always fails")
    
    # Fail 3 times
    for i in range(3):
        with pytest.raises(Exception):
            breaker.call(failing_function)
    
    # Circuit should be open
    assert breaker.state == CircuitState.OPEN
    
    # Next call should be rejected
    with pytest.raises(Exception, match="Circuit breaker OPEN"):
        breaker.call(failing_function)
```

**Acceptance Criteria:**
- ✅ Retry logic works for transient failures
- ✅ Rate limiting (429) handled with Retry-After
- ✅ Circuit breaker opens after threshold
- ✅ Feature flag allows disabling for debugging
- ✅ Unit tests pass (>95% coverage)

---

#### **Day 4-5: Transaction Rollback System**

**Task 1.8: Create Deployment Transaction Manager**
```python
# ops/scripts/utilities/deployment_transaction.py
from typing import List, Callable, Dict, Any, Optional
from dataclasses import dataclass
import logging
from .feature_flags import FeatureFlags

logger = logging.getLogger(__name__)

@dataclass
class ResourceRecord:
    """Track a created resource for rollback"""
    resource_type: str  # "workspace", "item", "user", "git_connection"
    resource_id: str
    resource_name: str
    cleanup_function: Callable
    cleanup_args: Dict[str, Any]
    metadata: Dict[str, Any] = None

class DeploymentTransaction:
    """Manage deployment as a transaction with rollback capability"""
    
    def __init__(self, transaction_id: str, enable_rollback: bool = None):
        self.transaction_id = transaction_id
        self.enable_rollback = (
            enable_rollback 
            if enable_rollback is not None 
            else FeatureFlags.USE_ROLLBACK
        )
        self.resources: List[ResourceRecord] = []
        self.committed = False
        self.rolled_back = False
    
    def register_resource(
        self,
        resource_type: str,
        resource_id: str,
        resource_name: str,
        cleanup_function: Callable,
        cleanup_args: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ):
        """Register a resource for potential rollback"""
        if not self.enable_rollback:
            return
        
        record = ResourceRecord(
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            cleanup_function=cleanup_function,
            cleanup_args=cleanup_args,
            metadata=metadata or {}
        )
        
        self.resources.append(record)
        logger.info(
            f"Registered {resource_type} '{resource_name}' ({resource_id}) "
            f"for transaction {self.transaction_id}"
        )
    
    def commit(self):
        """Commit transaction - no rollback will occur"""
        self.committed = True
        logger.info(
            f"Transaction {self.transaction_id} committed. "
            f"{len(self.resources)} resources preserved."
        )
    
    def rollback(self, reason: str = "Transaction failed"):
        """Rollback all created resources"""
        if not self.enable_rollback:
            logger.warning("Rollback disabled via feature flag")
            return
        
        if self.committed:
            logger.warning(f"Cannot rollback committed transaction {self.transaction_id}")
            return
        
        if self.rolled_back:
            logger.warning(f"Transaction {self.transaction_id} already rolled back")
            return
        
        logger.warning(
            f"Rolling back transaction {self.transaction_id}. Reason: {reason}"
        )
        
        rollback_errors = []
        
        # Rollback in reverse order
        for record in reversed(self.resources):
            try:
                logger.info(
                    f"Cleaning up {record.resource_type} "
                    f"'{record.resource_name}' ({record.resource_id})"
                )
                
                record.cleanup_function(**record.cleanup_args)
                
                logger.info(
                    f"✓ Successfully cleaned up {record.resource_type} "
                    f"'{record.resource_name}'"
                )
            except Exception as e:
                error_msg = (
                    f"✗ Failed to cleanup {record.resource_type} "
                    f"'{record.resource_name}': {str(e)}"
                )
                logger.error(error_msg)
                rollback_errors.append(error_msg)
        
        self.rolled_back = True
        
        if rollback_errors:
            logger.error(
                f"Rollback completed with {len(rollback_errors)} errors. "
                f"Manual cleanup may be required."
            )
            for error in rollback_errors:
                logger.error(f"  - {error}")
        else:
            logger.info(f"✓ Transaction {self.transaction_id} fully rolled back")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - rollback on exception"""
        if exc_type is not None and not self.committed:
            self.rollback(reason=f"Exception: {exc_type.__name__}: {exc_val}")
        return False  # Don't suppress exception
```

**Task 1.9: Update Workspace Manager with Transaction Support**
```python
# ops/scripts/utilities/workspace_manager.py
from .deployment_transaction import DeploymentTransaction

class WorkspaceManager:
    def create_workspace_with_transaction(
        self,
        workspace_name: str,
        transaction: Optional[DeploymentTransaction] = None,
        **kwargs
    ) -> dict:
        """Create workspace and register for rollback"""
        workspace = self.create_workspace(workspace_name, **kwargs)
        
        if transaction:
            transaction.register_resource(
                resource_type="workspace",
                resource_id=workspace["id"],
                resource_name=workspace["displayName"],
                cleanup_function=self.delete_workspace,
                cleanup_args={
                    "workspace_id": workspace["id"],
                    "force": True
                },
                metadata={"capacity_id": kwargs.get("capacity_id")}
            )
        
        return workspace
    
    def add_user_with_transaction(
        self,
        workspace_id: str,
        principal_id: str,
        transaction: Optional[DeploymentTransaction] = None,
        **kwargs
    ):
        """Add user and register for rollback"""
        self.add_user(workspace_id, principal_id, **kwargs)
        
        if transaction:
            transaction.register_resource(
                resource_type="user_assignment",
                resource_id=f"{workspace_id}:{principal_id}",
                resource_name=f"User {principal_id} in {workspace_id}",
                cleanup_function=self.remove_user,
                cleanup_args={
                    "workspace_id": workspace_id,
                    "principal_id": principal_id
                }
            )
```

**Task 1.10: Update Automated Deployment with Transactions**
```python
# scenarios/automated-deployment/run_automated_deployment.py
from ops.scripts.utilities.deployment_transaction import DeploymentTransaction
import uuid

def run_deployment(config, dry_run=False):
    """Run deployment with transaction support"""
    transaction_id = str(uuid.uuid4())
    
    with DeploymentTransaction(transaction_id) as transaction:
        try:
            # Step 1: Create workspace
            workspace = create_workspace_with_items(config, transaction)
            
            # Step 2: Add users
            add_users(workspace["id"], config, transaction)
            
            # Step 3: Connect to Git
            connect_git(workspace["id"], config, transaction)
            
            # Step 4: Create items
            create_items(workspace["id"], config, transaction)
            
            # All succeeded - commit transaction
            transaction.commit()
            
            print_success("✓ Deployment completed successfully")
            return workspace
            
        except Exception as e:
            print_error(f"✗ Deployment failed: {str(e)}")
            print_warning("Rolling back changes...")
            # Transaction automatically rolls back on exception
            raise
```

**Test Coverage:**
```python
# tests/unit/test_deployment_transaction.py
def test_transaction_rollback_on_failure():
    """Test transaction rolls back on exception"""
    cleanup_called = []
    
    def mock_cleanup(resource_id):
        cleanup_called.append(resource_id)
    
    with pytest.raises(Exception):
        with DeploymentTransaction("test-tx") as tx:
            tx.register_resource(
                "workspace",
                "ws-123",
                "test-workspace",
                mock_cleanup,
                {"resource_id": "ws-123"}
            )
            raise Exception("Simulated failure")
    
    assert "ws-123" in cleanup_called

def test_transaction_commit_prevents_rollback():
    """Test committed transaction doesn't rollback"""
    cleanup_called = []
    
    def mock_cleanup(resource_id):
        cleanup_called.append(resource_id)
    
    with DeploymentTransaction("test-tx") as tx:
        tx.register_resource(
            "workspace",
            "ws-456",
            "test-workspace",
            mock_cleanup,
            {"resource_id": "ws-456"}
        )
        tx.commit()
    
    assert len(cleanup_called) == 0
```

**Documentation:**
- `docs/reliability/TRANSACTION_ROLLBACK.md` - How it works
- `docs/development/DEBUGGING_ROLLBACK.md` - Disable for debugging

**Acceptance Criteria:**
- ✅ Resources cleaned up on deployment failure
- ✅ Committed transactions preserved
- ✅ Rollback works in reverse order
- ✅ Feature flag allows disabling
- ✅ Unit tests pass (>90% coverage)

---

### **Phase 2: Reliability & Automation (Week 2 - Days 6-10)**

**Day 6-7: Microsoft Graph API Integration**
**Day 8-9: Git OAuth Device Code Flow**
**Day 10: Integration Testing**

### **Phase 3: Observability (Week 3 - Days 11-15)**

**Day 11-12: Application Insights Integration**
**Day 13: Health Check Endpoints**
**Day 14-15: Monitoring Dashboards**

### **Phase 4: Testing & Validation (Week 4 - Days 16-20)**

**Day 16-17: Integration & E2E Tests**
**Day 18: Performance & Load Tests**
**Day 19: Documentation & Runbooks**
**Day 20: Final Review & Merge**

---

## 🚨 **Risk Mitigation**

### **Risk 1: Breaking Changes**
**Mitigation:**
- All new features behind feature flags
- Existing scenarios tested after each change
- Backward compatibility tests in CI/CD

### **Risk 2: Key Vault Dependency**
**Mitigation:**
- Graceful fallback to .env
- Clear error messages
- Local development works without Key Vault

### **Risk 3: Graph API Permissions**
**Mitigation:**
- Permission check on startup
- Clear error messages with remediation steps
- Fallback to manual principals file

### **Risk 4: Performance Degradation**
**Mitigation:**
- Benchmark existing performance first
- Compare after each change
- Alert if >10% degradation

---

## ✅ **Validation Checklist**

Before merging to main:

- [ ] All unit tests pass (>90% coverage)
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Performance benchmarks within 10% of baseline
- [ ] All existing scenarios work without modification
- [ ] Documentation complete and reviewed
- [ ] Migration guide tested with fresh .env
- [ ] CI/CD pipeline passes
- [ ] Code review completed (2+ approvers)
- [ ] Security review completed

---

## 📚 **References**

- [Azure Key Vault Best Practices](https://docs.microsoft.com/azure/key-vault/general/best-practices)
- [Microsoft Graph API Permissions](https://docs.microsoft.com/graph/permissions-reference)
- [Application Insights for Python](https://docs.microsoft.com/azure/azure-monitor/app/opencensus-python)
- [Tenacity Retry Library](https://tenacity.readthedocs.io/)

---

**Created by:** GitHub Copilot  
**Last Updated:** October 24, 2025  
**Status:** Ready for Implementation
