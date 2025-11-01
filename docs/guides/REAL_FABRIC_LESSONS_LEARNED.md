# Real Fabric Tests - Lessons Learned

## Issues Discovered and Fixed

### 1. ❌ → ✅ Lakehouse Naming Convention

**Problem:**
```python
lakehouse_name = f"test-lakehouse-{uuid}"  # ❌ FAILS with 400 Bad Request
```

**Error Message:**
```
DisplayName is Invalid for ArtifactType. DisplayName: <pi>test-lakehouse-81fad8ed</pi>
```

**Solution:**
```python
lakehouse_name = f"test_lakehouse_{uuid}"  # ✅ WORKS - Use underscores!
```

**Lesson:** Fabric lakehouse names **cannot contain hyphens**. Use underscores instead.

---

### 2. ⏳ Resource Provisioning Delays

**Problem:** Resources created via API aren't immediately available for subsequent operations.

**Solution:** Add explicit wait times:

```python
# After workspace creation
time.sleep(10)  # Wait for workspace to be fully provisioned

# After lakehouse creation
time.sleep(5)   # Wait for lakehouse to be fully available

# Before workspace deletion (if contains lakehouses)
time.sleep(5)   # Wait for lakehouse deletion to propagate
```

**Lesson:** Always add delays when:
- Creating workspace → Wait before adding items to it
- Creating lakehouse → Wait before using it
- Deleting child resources → Wait before deleting parent

---

### 3. 🔍 Error Response Logging

**Problem:** Generic errors don't show what's wrong with the request.

**Solution:** Catch and display full API response:

```python
try:
    lakehouse_response = fabric_client.create_lakehouse(...)
except requests.exceptions.HTTPError as e:
    print(f"⚠️  Lakehouse creation failed: {e}")
    print(f"   Response: {e.response.text}")  # ✅ Shows actual error!
```

**Lesson:** Always log `e.response.text` to see detailed API error messages.

---

### 4. 🔄 Circuit Breaker Integration

**Problem:** Circuit breaker doesn't automatically register failures from decorated functions.

**Solution:** Use `breaker.call()` explicitly:

```python
# ❌ This doesn't register with circuit breaker
fabric_client.get_workspace(fake_id)

# ✅ This properly registers failures
breaker.call(fabric_client.get_workspace, fake_id)
```

**Lesson:** Circuit breaker needs explicit `.call()` to track failures, not just the decorator.

---

## Working Test Configuration

### Test 1: Workspace Creation (6 seconds)
```python
✅ Create workspace with retry protection
✅ Validate immediately (no wait needed)
✅ Delete workspace
```

### Test 2: Workspace + Lakehouse (31 seconds)
```python
✅ Create workspace
⏳ Wait 10 seconds for provisioning
✅ Create lakehouse (with underscores in name)
⏳ Wait 5 seconds for provisioning
✅ Validate both resources
✅ Delete lakehouse
⏳ Wait 5 seconds for deletion propagation
✅ Delete workspace
```

### Test 3: Circuit Breaker (varies)
```python
✅ Get circuit breaker instance
✅ Use breaker.call() for 6 failed attempts
✅ Validate failure protection
✅ Reset breaker
```

---

## API Resource Name Rules

### ✅ Valid Characters for Fabric Resources

| Resource Type | Valid Name Examples | Invalid Examples |
|---------------|-------------------|------------------|
| **Workspace** | `test-cicd-20251024-112025-abc` | (Most names work) |
| **Lakehouse** | `test_lakehouse_abc123` | `test-lakehouse-abc` ❌ |
| **Lakehouse** | `MyLakehouse2024` | `my-lakehouse` ❌ |
| **Lakehouse** | `data_warehouse_prod` | `data-warehouse-prod` ❌ |

**General Rule:** 
- Workspaces: More permissive (hyphens OK)
- Lakehouses: **NO HYPHENS** - use underscores or camelCase

---

## Timing Guidelines

### Recommended Wait Times

```python
# After creating workspace
time.sleep(10)  # Conservative - ensures workspace is ready

# After creating lakehouse
time.sleep(5)   # Enough for most cases

# After deleting child resource
time.sleep(5)   # Let deletion propagate before deleting parent

# After creating notebook/pipeline
time.sleep(3)   # Usually faster than lakehouse

# General rule: Better to wait too long than fail intermittently
```

### Production Recommendations

For production deployments:
- Use **polling** instead of fixed waits
- Check resource status in loop with timeout
- Implement exponential backoff
- Add retry logic for status checks

```python
# Better approach for production:
def wait_for_resource_ready(workspace_id, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        status = get_workspace_status(workspace_id)
        if status == "Ready":
            return True
        time.sleep(2)
    raise TimeoutError("Resource not ready")
```

---

## Final Test Results

```
╔══════════════════════════════════════════════════════════╗
║         Real Fabric Integration Test Results            ║
╠══════════════════════════════════════════════════════════╣
║ ✅ test_create_workspace_with_production_features (6s)  ║
║ ✅ test_create_workspace_and_lakehouse (31s)            ║
║ ✅ test_circuit_breaker_with_real_api                   ║
╠══════════════════════════════════════════════════════════╣
║ Total: 3 PASSED, 0 FAILED                               ║
║ Duration: ~37 seconds                                    ║
║ Resources: All created and cleaned up successfully      ║
╚══════════════════════════════════════════════════════════╝
```

---

## Key Takeaways

1. **Naming matters** - Lakehouse names can't have hyphens
2. **Wait for provisioning** - 10s for workspace, 5s for lakehouse
3. **Log API responses** - Always show `e.response.text` for debugging
4. **Circuit breakers** - Use `breaker.call()` for explicit tracking
5. **Cleanup is critical** - Use try/finally blocks always
6. **Real tests are valuable** - Caught issues that mocked tests couldn't

---

## Cost Analysis

**Total test run:**
- 3 workspaces created (deleted in <30s each)
- 1 lakehouse created (deleted in <10s)
- Total API calls: ~12
- Total duration: 37 seconds
- **Estimated cost: < $0.01**

**Safe for:**
- Daily development testing
- Pre-deployment validation
- API integration verification

**Not for:**
- CI/CD automation (too slow, real resources)
- Load testing (would be expensive)
- Continuous testing (use mocked tests instead)
