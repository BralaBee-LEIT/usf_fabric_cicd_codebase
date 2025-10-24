# Feature Flags Management Runbook

## 📋 Overview

This runbook provides procedures for managing feature flags in the Microsoft Fabric CI/CD framework. Feature flags enable controlled rollout of production hardening features without code changes.

**Target Audience:** DevOps Engineers, Release Managers, Development Team

---

## 🚩 Available Feature Flags

### Production Hardening Features

| Flag Name | Default | Purpose | Impact | Dependencies |
|-----------|---------|---------|--------|--------------|
| `FEATURE_USE_RETRY_LOGIC` | `true` | Automatic retry with exponential backoff | +10% latency, +95% success rate | None |
| `FEATURE_ENABLE_CIRCUIT_BREAKER` | `true` | Circuit breaker for API stability | Prevents cascade failures | None |
| `FEATURE_COLLECT_METRICS` | `true` | Comprehensive metrics collection | +5% overhead, full observability | Application Insights |
| `FEATURE_USE_STRUCTURED_LOGGING` | `true` | JSON logging with correlation IDs | Better debugging, log analytics | None |
| `FEATURE_VALIDATE_CONFIGS` | `true` | Configuration validation on startup | Fail-fast on invalid config | None |

### Feature Flag States

```python
# Environment variable format
FEATURE_<NAME>=true|false

# Supported values
true, True, TRUE, 1, yes, Yes, YES    → Enabled
false, False, FALSE, 0, no, No, NO    → Disabled
<not set>                              → Use default
```

---

## 🔧 Managing Feature Flags

### Method 1: Environment Variables (Recommended)

**Local Development:**
```bash
# Enable all features
export FEATURE_USE_RETRY_LOGIC=true
export FEATURE_ENABLE_CIRCUIT_BREAKER=true
export FEATURE_COLLECT_METRICS=true
export FEATURE_USE_STRUCTURED_LOGGING=true

# Disable specific feature
export FEATURE_USE_RETRY_LOGIC=false

# Run application
python ops/scripts/deploy_fabric.py
```

**Docker:**
```dockerfile
# Dockerfile
ENV FEATURE_USE_RETRY_LOGIC=true
ENV FEATURE_ENABLE_CIRCUIT_BREAKER=true
ENV FEATURE_COLLECT_METRICS=true
ENV FEATURE_USE_STRUCTURED_LOGGING=true
```

```bash
# docker-compose.yml
services:
  fabric-cicd:
    environment:
      - FEATURE_USE_RETRY_LOGIC=true
      - FEATURE_ENABLE_CIRCUIT_BREAKER=true
      - FEATURE_COLLECT_METRICS=true
      - FEATURE_USE_STRUCTURED_LOGGING=true
```

### Method 2: GitHub Actions

**In Workflow:**
```yaml
# .github/workflows/deploy.yml
env:
  FEATURE_USE_RETRY_LOGIC: ${{ inputs.enable_features }}
  FEATURE_ENABLE_CIRCUIT_BREAKER: ${{ inputs.enable_features }}
  FEATURE_COLLECT_METRICS: ${{ inputs.enable_features }}
  FEATURE_USE_STRUCTURED_LOGGING: ${{ inputs.enable_features }}
```

**Manual Deployment:**
```bash
# Enable all features
gh workflow run deploy.yml \
  -f environment=production \
  -f enable_features=true

# Disable all features
gh workflow run deploy.yml \
  -f environment=production \
  -f enable_features=false
```

### Method 3: Azure App Service

**Via Azure CLI:**
```bash
# Set feature flags
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --settings \
    FEATURE_USE_RETRY_LOGIC=true \
    FEATURE_ENABLE_CIRCUIT_BREAKER=true \
    FEATURE_COLLECT_METRICS=true \
    FEATURE_USE_STRUCTURED_LOGGING=true

# Restart to apply
az webapp restart --name $APP_NAME --resource-group $RG_NAME
```

**Via Azure Portal:**
```
1. Navigate to: App Service → Configuration → Application settings
2. Add/Edit settings:
   - Name: FEATURE_USE_RETRY_LOGIC
   - Value: true
3. Click: Save
4. Confirm restart
```

### Method 4: Configuration File

**config/features.json:**
```json
{
  "features": {
    "use_retry_logic": true,
    "enable_circuit_breaker": true,
    "collect_metrics": true,
    "use_structured_logging": true,
    "validate_configs": true
  },
  "retry_config": {
    "max_attempts": 3,
    "initial_delay": 1.0,
    "max_delay": 10.0,
    "backoff_factor": 2.0
  },
  "circuit_breaker_config": {
    "failure_threshold": 5,
    "timeout": 60,
    "expected_exception": "requests.exceptions.RequestException"
  }
}
```

**Load in code:**
```python
import json
import os

def load_feature_flags():
    """Load feature flags from environment or config file."""
    config_file = os.getenv('FEATURE_CONFIG_FILE', 'config/features.json')
    
    if os.path.exists(config_file):
        with open(config_file) as f:
            config = json.load(f)
            return config.get('features', {})
    
    # Fallback to environment variables
    return {
        'use_retry_logic': os.getenv('FEATURE_USE_RETRY_LOGIC', 'true').lower() == 'true',
        'enable_circuit_breaker': os.getenv('FEATURE_ENABLE_CIRCUIT_BREAKER', 'true').lower() == 'true',
        # ... etc
    }
```

---

## 📊 Feature Flag Rollout Strategy

### Progressive Rollout

#### Phase 1: Development (Day 1)
```bash
# Enable all features in development
az webapp config appsettings set \
  --name fabric-cicd-dev \
  --resource-group rg-fabric-dev \
  --settings \
    FEATURE_USE_RETRY_LOGIC=true \
    FEATURE_ENABLE_CIRCUIT_BREAKER=true \
    FEATURE_COLLECT_METRICS=true \
    FEATURE_USE_STRUCTURED_LOGGING=true

# Monitor for 24 hours
# Check Application Insights for errors
```

#### Phase 2: Staging (Day 2)
```bash
# Enable in staging
az webapp config appsettings set \
  --name fabric-cicd-staging \
  --resource-group rg-fabric-staging \
  --settings \
    FEATURE_USE_RETRY_LOGIC=true \
    FEATURE_ENABLE_CIRCUIT_BREAKER=true \
    FEATURE_COLLECT_METRICS=true \
    FEATURE_USE_STRUCTURED_LOGGING=true

# Run full integration tests
pytest tests/integration/ -v

# Monitor for 48 hours
```

#### Phase 3: Production Canary (Day 4)
```bash
# Enable for 10% of production traffic
# (requires load balancer with weighted routing)

# Option A: Time-based canary
# Enable during low-traffic hours (2am-6am UTC)
FEATURE_USE_RETRY_LOGIC=true

# Monitor metrics:
# - Request latency
# - Error rate
# - Success rate
```

#### Phase 4: Production Full Rollout (Day 7)
```bash
# Enable all features in production
az webapp config appsettings set \
  --name fabric-cicd-prod \
  --resource-group rg-fabric-prod \
  --settings \
    FEATURE_USE_RETRY_LOGIC=true \
    FEATURE_ENABLE_CIRCUIT_BREAKER=true \
    FEATURE_COLLECT_METRICS=true \
    FEATURE_USE_STRUCTURED_LOGGING=true

# Monitor closely for 24 hours
```

### Rollback Strategy

**Immediate Rollback (Emergency):**
```bash
# Disable all features
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --settings \
    FEATURE_USE_RETRY_LOGIC=false \
    FEATURE_ENABLE_CIRCUIT_BREAKER=false \
    FEATURE_COLLECT_METRICS=false \
    FEATURE_USE_STRUCTURED_LOGGING=false

# Restart application
az webapp restart --name $APP_NAME --resource-group $RG_NAME

# Verify rollback
curl https://$APP_NAME.azurewebsites.net/health
```

**Gradual Rollback:**
```bash
# Step 1: Disable non-critical features first
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --settings FEATURE_COLLECT_METRICS=false

# Wait 5 minutes, check impact

# Step 2: Disable retry logic if still problematic
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --settings FEATURE_USE_RETRY_LOGIC=false
```

---

## 🔍 Feature Flag Monitoring

### Metrics to Track

**Per Feature:**
- Adoption rate (% of requests with feature enabled)
- Error rate (before vs. after)
- Latency (p50, p95, p99)
- Success rate
- User impact (# affected users)

### Application Insights Queries

**Check Feature Flag Usage:**
```kusto
// Count requests by feature flag state
traces
| where timestamp > ago(1h)
| where message contains "FEATURE_USE_RETRY_LOGIC"
| extend flag_value = tostring(customDimensions.feature_flag_value)
| summarize count() by flag_value
| render piechart
```

**Monitor Feature Impact:**
```kusto
// Compare latency with/without retry logic
requests
| where timestamp > ago(24h)
| extend has_retry = tobool(customDimensions.retry_enabled)
| summarize 
    avg_duration = avg(duration),
    p95_duration = percentile(duration, 95),
    error_rate = countif(success == false) * 100.0 / count()
  by has_retry
```

**Circuit Breaker Status:**
```kusto
// Monitor circuit breaker state changes
traces
| where timestamp > ago(1h)
| where message contains "Circuit breaker"
| extend state = tostring(customDimensions.circuit_state)
| summarize count() by state, bin(timestamp, 5m)
| render timechart
```

### Alerting Rules

**Create Alerts:**
```bash
# Alert on high error rate after feature enable
az monitor metrics alert create \
  --name "feature-high-error-rate" \
  --resource-group $RG_NAME \
  --scopes $APPINSIGHTS_ID \
  --condition "avg requests/failed > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action $ACTION_GROUP_ID \
  --description "Error rate increased after feature flag change"

# Alert on performance degradation
az monitor metrics alert create \
  --name "feature-high-latency" \
  --resource-group $RG_NAME \
  --scopes $APPINSIGHTS_ID \
  --condition "avg requests/duration > 1000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action $ACTION_GROUP_ID \
  --description "Latency increased after feature flag change"
```

---

## 🧪 Testing Feature Flags

### Unit Tests

**Test Feature Toggle:**
```python
# tests/unit/test_feature_flags.py
import os
import pytest
from ops.scripts.utilities.feature_flags import FeatureFlags

def test_feature_flag_enabled():
    """Test feature flag when enabled."""
    os.environ['FEATURE_USE_RETRY_LOGIC'] = 'true'
    flags = FeatureFlags()
    assert flags.use_retry_logic is True

def test_feature_flag_disabled():
    """Test feature flag when disabled."""
    os.environ['FEATURE_USE_RETRY_LOGIC'] = 'false'
    flags = FeatureFlags()
    assert flags.use_retry_logic is False

def test_feature_flag_default():
    """Test feature flag default value."""
    if 'FEATURE_USE_RETRY_LOGIC' in os.environ:
        del os.environ['FEATURE_USE_RETRY_LOGIC']
    flags = FeatureFlags()
    assert flags.use_retry_logic is True  # Default is True
```

### Integration Tests

**Test With/Without Feature:**
```python
# tests/integration/test_retry_with_flag.py
import pytest
import os

@pytest.mark.parametrize("flag_enabled", [True, False])
def test_api_call_with_retry_flag(flag_enabled):
    """Test API call with retry flag enabled/disabled."""
    os.environ['FEATURE_USE_RETRY_LOGIC'] = str(flag_enabled).lower()
    
    from ops.scripts.utilities.fabric_api import FabricAPIClient
    client = FabricAPIClient()
    
    # Make API call that might fail
    result = client.list_workspaces()
    
    # Verify behavior based on flag
    if flag_enabled:
        # Should retry on failure
        assert result is not None
    else:
        # May fail without retry
        pass  # Just verify no crash
```

### E2E Tests

**Test Feature Combinations:**
```python
# tests/e2e/test_feature_combinations.py
import pytest
import itertools

FEATURE_FLAGS = [
    'FEATURE_USE_RETRY_LOGIC',
    'FEATURE_ENABLE_CIRCUIT_BREAKER',
    'FEATURE_COLLECT_METRICS',
    'FEATURE_USE_STRUCTURED_LOGGING',
]

@pytest.mark.e2e
@pytest.mark.parametrize("flags", [
    # Test with all combinations
    dict(zip(FEATURE_FLAGS, combo))
    for combo in itertools.product([True, False], repeat=len(FEATURE_FLAGS))
])
def test_feature_combination(flags):
    """Test all feature flag combinations work together."""
    # Set flags
    for flag, value in flags.items():
        os.environ[flag] = str(value).lower()
    
    # Run critical path
    from ops.scripts.deploy_fabric import main
    result = main(['--workspace', 'test-workspace'])
    
    # Verify success regardless of flag combination
    assert result == 0
```

---

## 🚨 Incident Response

### Feature Flag Caused Incident

**Immediate Actions:**
```bash
# 1. Identify problematic feature
# Check Application Insights for correlation

# 2. Disable feature immediately
az webapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG_NAME \
  --settings FEATURE_<NAME>=false

# 3. Restart application
az webapp restart --name $APP_NAME --resource-group $RG_NAME

# 4. Verify service restored
curl https://$APP_NAME.azurewebsites.net/health

# 5. Notify stakeholders
```

**Post-Incident:**
```bash
# 1. Create incident report
cat > incidents/incident_$(date +%Y%m%d).md <<EOF
# Incident: Feature Flag Rollback

**Date:** $(date -u +"%Y-%m-%d %H:%M UTC")
**Feature:** FEATURE_<NAME>
**Impact:** <Describe impact>

## Timeline
- HH:MM: Feature enabled
- HH:MM: Issue detected
- HH:MM: Feature disabled
- HH:MM: Service restored

## Root Cause
<Analysis>

## Resolution
- Disabled feature flag
- Service restored
- No data loss

## Prevention
- Add test coverage
- Improve monitoring
- Update runbook
EOF

# 2. Review feature implementation
# Identify bug and fix

# 3. Add regression tests
# Prevent similar issues

# 4. Update documentation
# Document known issues
```

---

## 📋 Feature Flag Checklist

### Before Enabling Feature

```bash
□ Feature tested in development
□ Integration tests passing
□ Performance benchmarks reviewed
□ Monitoring configured
□ Alerts configured
□ Rollback procedure documented
□ Team notified
□ Change ticket created
```

### After Enabling Feature

```bash
□ Feature confirmed active
□ No errors in logs
□ Performance within SLA
□ Metrics collecting properly
□ User feedback positive
□ Documentation updated
□ Stakeholders notified
```

### Before Removing Feature Flag

```bash
□ Feature stable for 30+ days
□ No rollback in last 30 days
□ 100% adoption in all environments
□ Code cleanup plan created
□ Tests updated
□ Documentation updated
```

---

## 📚 Additional Resources

- [Deployment Runbook](./DEPLOYMENT_RUNBOOK.md)
- [Monitoring Runbook](./MONITORING_RUNBOOK.md)
- [Feature Flag Best Practices](https://martinfowler.com/articles/feature-toggles.html)
- [Azure App Configuration](https://docs.microsoft.com/en-us/azure/azure-app-configuration/)

---

**Document Owner:** DevOps Team  
**Last Updated:** 2025-10-24  
**Version:** 1.0.0  
**Review Cycle:** Quarterly
