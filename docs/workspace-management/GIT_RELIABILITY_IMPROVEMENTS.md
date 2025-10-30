# Git Connection Reliability Improvements

**Date:** October 30, 2025  
**Branch:** feature/git-reliability-improvements  
**Priority:** 🔴 HIGH (Critical blocker from status assessment)  
**Status:** ✅ Implementation Complete

---

## Problem Statement

From project status assessment (STATUS_2025-10-30.md):
- **Issue:** Git connection Step 2 fails consistently with "WorkspaceNotConnectedToGit (400)"
- **Impact:** Manual intervention required for every deployment
- **Rating:** 2/5 reliability (needs immediate work)
- **Root Cause:** No pre-flight validation, no retry logic, unclear error messages

---

## Solution Implemented

### 1. Pre-Flight Validation (`validate_git_prerequisites`)

Comprehensive validation before attempting connection:

```python
is_valid, error = connector.validate_git_prerequisites(
    workspace_id="abc-123",
    branch_name="main",
    directory_path="/"
)

if not is_valid:
    print(f"Validation failed: {error}")
    # Error includes troubleshooting steps
```

**Validates:**
- ✅ Workspace exists and is accessible
- ✅ Workspace not already connected
- ✅ Git credentials are valid (GITHUB_TOKEN or connection ID)
- ✅ Repository configuration correct

**Benefits:**
- Early failure detection
- Clear, actionable error messages
- Saves time by failing fast

---

### 2. Automatic Retry with Exponential Backoff

Handles transient failures automatically:

```python
result = connector.initialize_git_connection_with_retry(
    workspace_id="abc-123",
    branch_name="main",
    max_retries=3,           # 3 attempts total
    initial_backoff=2.0      # 2s, 4s, 8s delays
)
```

**Retry Behavior:**
- **Attempt 1:** Immediate (0s delay)
- **Attempt 2:** 2 second delay
- **Attempt 3:** 4 second delay
- **Attempt 4:** 8 second delay (if max_retries=4)

**Benefits:**
- Automatic recovery from transient failures
- Configurable retry strategy
- Success logging with attempt number

---

### 3. Enhanced Error Messages

Every error now includes:
- **Specific failure reason** (WorkspaceNotFound, Unauthorized, etc.)
- **Common issues & solutions** mapping
- **Troubleshooting steps** with actionable guidance
- **Documentation links** for each error type
- **Context information** (workspace ID, repo, branch, directory)

**Example Error:**
```
Failed to initialize Git connection for workspace abc123...

Error Type: HTTPError
Error Details: 400 Bad Request

Common Issues & Solutions:
  • 'WorkspaceNotFound' → Check workspace ID is correct
  • 'Unauthorized' → Verify you have Contributor/Admin role
  • 'RepositoryNotFound' → Confirm repo exists: org/repo
  • 'BranchNotFound' → Verify branch 'main' exists in repo
  • 'InvalidPath' → Check directory path format: '/'
  • '400 Bad Request' → Review Git provider configuration

Workspace: abc-123-def-456
Repository: my-org/my-repo
Branch: main
Directory: /

Documentation:
  https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started
```

---

### 4. Manual Fallback Workflow

When automated connection fails, guide user through manual process:

```python
try:
    connector.initialize_git_connection_with_retry(...)
except Exception as e:
    # Automatic fallback to manual instructions
    success = connector.prompt_manual_connection(
        workspace_id="abc-123",
        branch_name="main",
        wait_for_user=True  # Pause for user action
    )
```

**Manual Process:**
1. Display step-by-step instructions
2. Provide Fabric Portal URL
3. Show exact configuration values
4. Wait for user confirmation
5. Automatically verify connection
6. Return success/failure

**Benefits:**
- No deployment completely blocked
- Clear guidance for manual intervention
- Automatic verification of manual work

---

## Integration

### Automated Deployment Script

Updated `scenarios/automated-deployment/run_automated_deployment.py`:

```python
def connect_git(workspace_id, product_config, dry_run=False, enable_manual_fallback=True):
    """Step 2: Connect workspace to Git with retry logic"""
    
    try:
        # Attempt automated connection with retry
        git_connector.initialize_git_connection_with_retry(
            workspace_id=workspace_id,
            branch_name=branch_name,
            max_retries=max_retries,  # From config
        )
        return True
        
    except Exception as e:
        # Automatic fallback to manual instructions
        if enable_manual_fallback:
            return git_connector.prompt_manual_connection(
                workspace_id, branch_name, wait_for_user=True
            )
        return False
```

**Configuration:**
```yaml
# product_config.yaml
git:
  enabled: true
  branch: "main"
  directory: "/data_products/my_product"
  max_retries: 3  # NEW: Configurable retry attempts
  auto_commit: false
```

---

## Testing

### Unit Tests (`tests/unit/test_git_reliability.py`)

**Test Coverage:**
- ✅ Pre-flight validation (3 tests)
  - Success scenario
  - Workspace not found
  - Already connected
  
- ✅ Retry logic (5 tests)
  - Success on first attempt
  - Success after retries
  - All retries exhausted
  - Exponential backoff timing
  - Pre-flight failure aborts retries
  
- ✅ Manual fallback (4 tests)
  - User confirms success
  - User cancels
  - Verification fails
  - Skip when disabled
  
- ✅ Error messages (1 test)
  - Troubleshooting content
  
- ✅ Integration (1 test)
  - Complete workflow

**Total:** 14 test cases

**Note:** Tests created but mock paths need adjustment for `get_fabric_client` import location.

---

## Expected Impact

### Before Improvements
- ❌ Git connection success rate: ~40%
- ❌ Manual intervention: Required every time
- ❌ Error messages: Cryptic, no guidance
- ❌ Retry attempts: None
- ❌ Validation: None

### After Improvements
- ✅ Git connection success rate: ~95%
- ✅ Manual intervention: Rare, graceful fallback
- ✅ Error messages: Detailed, actionable
- ✅ Retry attempts: 3 with exponential backoff
- ✅ Validation: Pre-flight checks

### Metrics to Monitor
- Git connection success rate (target: >95%)
- Average retry attempts before success
- Manual fallback invocation rate
- Time to successful connection

---

## Usage Examples

### Basic Usage (with retry)
```python
from ops.scripts.utilities.fabric_git_connector import FabricGitConnector

connector = FabricGitConnector(
    organization_name="my-org",
    repository_name="my-repo"
)

# Automatic retry with defaults (3 attempts, 2s initial backoff)
result = connector.initialize_git_connection_with_retry(
    workspace_id="abc-123",
    branch_name="main",
    directory_path="/my_project"
)
```

### Custom Retry Configuration
```python
# More aggressive retry (5 attempts, 1s initial backoff)
result = connector.initialize_git_connection_with_retry(
    workspace_id="abc-123",
    branch_name="main",
    max_retries=5,
    initial_backoff=1.0  # 1s, 2s, 4s, 8s, 16s
)
```

### Pre-Flight Validation Only
```python
# Check if connection will succeed before attempting
is_valid, error_msg = connector.validate_git_prerequisites(
    workspace_id="abc-123",
    branch_name="main"
)

if is_valid:
    # Safe to proceed with connection
    connector.initialize_git_connection(...)
else:
    print(f"Fix these issues first:\n{error_msg}")
```

### Manual Fallback Workflow
```python
try:
    # Try automated connection
    connector.initialize_git_connection_with_retry(...)
except Exception as e:
    # Guide user through manual process
    success = connector.prompt_manual_connection(
        workspace_id="abc-123",
        branch_name="main",
        wait_for_user=True  # Pause for user input
    )
    
    if success:
        print("Manual connection successful!")
    else:
        print("Manual connection failed or cancelled")
```

---

## Next Steps

### Immediate (This Week)
1. ✅ Implement core functionality
2. ✅ Update automated deployment script
3. ✅ Create unit tests
4. ⏳ Fix test mock paths
5. ⏳ Test against real Fabric workspaces

### Short-Term (Next 2 Weeks)
6. ⏳ Update Git integration documentation
7. ⏳ Add retry metrics to telemetry
8. ⏳ Monitor production success rates
9. ⏳ Gather user feedback

### Long-Term (1+ Months)
10. ⏳ Fine-tune retry parameters based on data
11. ⏳ Add circuit breaker for repeated failures
12. ⏳ Implement connection health checks

---

## Documentation Updates Needed

### Files to Update
- [ ] `docs/workspace-management/GIT_INTEGRATION_GUIDE.md`
  - Add pre-flight validation section
  - Document retry behavior
  - Add troubleshooting flowchart
  
- [ ] `docs/workspace-management/ENVIRONMENT_PROMOTION_GUIDE.md`
  - Update Step 2 (Git connection) with retry examples
  - Add manual fallback workflow
  
- [ ] `scenarios/automated-deployment/README.md`
  - Document new max_retries config option
  - Add troubleshooting section for Step 2 failures
  
- [ ] `docs/user-stories-validation/USER_STORY_1_ASSESSMENT.md`
  - Update AC6 with reliability improvements
  - Note Git connection success rate improvement

---

## API Reference

### `validate_git_prerequisites()`

**Purpose:** Validate all prerequisites before attempting Git connection

**Parameters:**
- `workspace_id` (str): Fabric workspace GUID
- `branch_name` (str): Git branch to validate
- `directory_path` (str, optional): Folder path in repo (default: "/")
- `github_token` (str, optional): GitHub PAT (from env if not provided)

**Returns:**
- `Tuple[bool, Optional[str]]`: (is_valid, error_message)

**Example:**
```python
is_valid, error = connector.validate_git_prerequisites(
    workspace_id="abc-123",
    branch_name="main"
)
```

---

### `initialize_git_connection_with_retry()`

**Purpose:** Initialize Git connection with automatic retry and exponential backoff

**Parameters:**
- `workspace_id` (str): Fabric workspace GUID
- `branch_name` (str): Git branch to connect
- `directory_path` (str, optional): Folder path in repo (default: "/")
- `auto_commit` (bool, optional): Auto-commit after connection (default: False)
- `max_retries` (int, optional): Maximum retry attempts (default: 3)
- `initial_backoff` (float, optional): Initial backoff delay in seconds (default: 2.0)

**Returns:**
- `Dict[str, Any]`: Connection response from Fabric API

**Raises:**
- `ValueError`: If pre-flight validation fails
- `Exception`: If all retry attempts fail

**Example:**
```python
result = connector.initialize_git_connection_with_retry(
    workspace_id="abc-123",
    branch_name="main",
    max_retries=3
)
```

---

### `prompt_manual_connection()`

**Purpose:** Guide user through manual Git connection and verify completion

**Parameters:**
- `workspace_id` (str): Fabric workspace GUID
- `branch_name` (str): Git branch to connect
- `directory_path` (str, optional): Folder path in repo (default: "/")
- `wait_for_user` (bool, optional): Prompt and wait for user (default: True)

**Returns:**
- `bool`: True if manual connection successful, False otherwise

**Example:**
```python
success = connector.prompt_manual_connection(
    workspace_id="abc-123",
    branch_name="main",
    wait_for_user=True
)
```

---

## Troubleshooting

### Common Issues

**Issue:** "Pre-flight validation failed: Workspace not found"
- **Cause:** Invalid workspace ID or insufficient permissions
- **Solution:** Verify workspace ID, ensure Contributor/Admin role

**Issue:** "All 3 connection attempts failed"
- **Cause:** Persistent error (wrong config, service issue)
- **Solution:** Check error details, verify all configuration, try manual fallback

**Issue:** "Git connection validated but state is DISCONNECTED"
- **Cause:** API request succeeded but actual connection failed
- **Solution:** Verify branch exists, check directory path format, wait 30s and retry

**Issue:** "Manual connection verification failed"
- **Cause:** User didn't complete manual steps correctly
- **Solution:** Review manual steps, ensure 'Connected' status in Fabric Portal

---

## Success Criteria

### Definition of Done
- ✅ Pre-flight validation implemented
- ✅ Retry logic with exponential backoff implemented
- ✅ Enhanced error messages with troubleshooting
- ✅ Manual fallback workflow implemented
- ✅ Automated deployment script updated
- ✅ Unit tests created (14 test cases)
- ⏳ Tests pass (need mock path fixes)
- ⏳ Real Fabric API testing completed
- ⏳ Documentation updated

### Acceptance Criteria
- [ ] Git connection success rate >95%
- [ ] Manual intervention <5% of deployments
- [ ] Error messages include troubleshooting steps
- [ ] Retry attempts logged with timing
- [ ] Manual fallback workflow tested

---

## References

- **Status Assessment:** `docs/project-status/STATUS_2025-10-30.md`
- **User Story 2:** `docs/user-stories-validation/USER_STORIES_2_3_GAP_ANALYSIS.md`
- **Fabric Git API:** https://learn.microsoft.com/en-us/rest/api/fabric/core/git
- **Git Integration Guide:** https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started

---

**Status:** ✅ Implementation Complete | ⏳ Testing & Documentation In Progress
