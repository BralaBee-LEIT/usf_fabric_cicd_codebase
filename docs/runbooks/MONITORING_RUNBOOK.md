# Monitoring and Observability Runbook

## 📋 Overview

This runbook provides procedures for monitoring the Microsoft Fabric CI/CD framework using Azure Application Insights, custom metrics, and structured logging.

**Target Audience:** DevOps Engineers, SREs, Support Engineers

**Prerequisites:**
- Azure Application Insights configured
- Access to Azure Portal
- Azure CLI installed
- Kusto Query Language (KQL) knowledge (basic)

---

## 📊 Monitoring Architecture

### Components

```
┌─────────────────────────────────────────────────────┐
│                  Application                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐│
│  │   Metrics    │  │    Traces    │  │   Events   ││
│  └──────┬───────┘  └──────┬───────┘  └──────┬─────┘│
│         │                 │                  │      │
│         └─────────────────┴──────────────────┘      │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
         ┌────────────────────────────────────┐
         │   Application Insights              │
         │  ┌──────────────────────────────┐  │
         │  │  Telemetry Processing        │  │
         │  └──────────────────────────────┘  │
         │  ┌──────────────────────────────┐  │
         │  │  Data Storage (90 days)      │  │
         │  └──────────────────────────────┘  │
         └────────────────┬───────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
  ┌───────────────┐              ┌───────────────┐
  │   Dashboards  │              │    Alerts     │
  └───────────────┘              └───────────────┘
```

### Telemetry Types

| Type | Purpose | Retention | Volume |
|------|---------|-----------|--------|
| **Traces** | Structured logs with context | 90 days | High |
| **Requests** | API call tracking | 90 days | Medium |
| **Dependencies** | External service calls | 90 days | Medium |
| **Exceptions** | Error tracking | 90 days | Low |
| **Custom Metrics** | Business metrics | 90 days | Medium |
| **Custom Events** | Business events | 90 days | Low |

---

## 🎯 Key Metrics

### Application Performance

**API Call Latency:**
```kusto
// P50, P95, P99 latency
requests
| where timestamp > ago(1h)
| summarize 
    p50 = percentile(duration, 50),
    p95 = percentile(duration, 95),
    p99 = percentile(duration, 99)
| project 
    p50_ms = p50,
    p95_ms = p95,
    p99_ms = p99
```

**Success Rate:**
```kusto
// Success rate over time
requests
| where timestamp > ago(24h)
| summarize 
    total = count(),
    successful = countif(success == true),
    failed = countif(success == false)
| extend success_rate = (successful * 100.0) / total
| project success_rate, total, successful, failed
```

**Requests Per Minute:**
```kusto
// Request throughput
requests
| where timestamp > ago(1h)
| summarize count() by bin(timestamp, 1m)
| render timechart
```

### Production Hardening Features

**Retry Logic Effectiveness:**
```kusto
// Retry attempts distribution
traces
| where timestamp > ago(1h)
| where message contains "Retry attempt"
| extend attempt = toint(customDimensions.attempt)
| summarize count() by attempt
| render columnchart
```

```kusto
// Retry success rate
traces
| where timestamp > ago(1h)
| where message contains "Retry"
| extend 
    operation_id = tostring(customDimensions.correlation_id),
    is_success = message contains "succeeded"
| summarize 
    total_retries = count(),
    successful_retries = countif(is_success)
  by operation_id
| extend retry_success_rate = (successful_retries * 100.0) / total_retries
| summarize avg(retry_success_rate)
```

**Circuit Breaker Status:**
```kusto
// Circuit breaker state over time
traces
| where timestamp > ago(1h)
| where message contains "Circuit breaker"
| extend state = tostring(customDimensions.circuit_state)
| summarize count() by state, bin(timestamp, 5m)
| render timechart
```

```kusto
// Circuit breaker trips
traces
| where timestamp > ago(24h)
| where message contains "Circuit breaker opened"
| extend service = tostring(customDimensions.service_name)
| summarize 
    trip_count = count(),
    last_trip = max(timestamp)
  by service
| order by trip_count desc
```

**Metrics Collection Overhead:**
```kusto
// Time spent collecting metrics
traces
| where timestamp > ago(1h)
| where message contains "Metrics collection"
| extend duration_ms = todouble(customDimensions.duration_ms)
| summarize 
    avg_duration = avg(duration_ms),
    p95_duration = percentile(duration_ms, 95),
    total_time = sum(duration_ms)
| project avg_duration, p95_duration, total_time_seconds = total_time / 1000
```

### Business Metrics

**Workspace Operations:**
```kusto
// Workspace creation success rate
customMetrics
| where timestamp > ago(24h)
| where name == "workspace_created"
| extend status = tostring(customDimensions.status)
| summarize count() by status
| render piechart
```

**Lakehouse Operations:**
```kusto
// Lakehouse operations timeline
customEvents
| where timestamp > ago(24h)
| where name in ("lakehouse_created", "lakehouse_deleted", "file_uploaded")
| summarize count() by name, bin(timestamp, 1h)
| render timechart
```

**Deployment Duration:**
```kusto
// Average deployment time
customMetrics
| where timestamp > ago(7d)
| where name == "deployment_duration"
| extend duration_minutes = todouble(customDimensions.duration_seconds) / 60
| summarize 
    avg_duration = avg(duration_minutes),
    p95_duration = percentile(duration_minutes, 95)
  by bin(timestamp, 1d)
| render timechart
```

---

## 🔍 Log Analysis

### Structured Logging Format

**Log Entry Structure:**
```json
{
  "timestamp": "2025-10-24T10:30:00.000Z",
  "level": "INFO",
  "correlation_id": "abc123-def456-ghi789",
  "operation": "create_workspace",
  "message": "Workspace created successfully",
  "details": {
    "workspace_id": "ws-12345",
    "workspace_name": "Analytics Hub",
    "capacity_id": "cap-67890",
    "duration_ms": 1234
  },
  "user": {
    "id": "user@company.com",
    "ip": "10.0.0.1"
  },
  "tags": {
    "environment": "production",
    "version": "1.0.0"
  }
}
```

### Common Queries

**Find Errors by Operation:**
```kusto
// Errors in last hour
traces
| where timestamp > ago(1h)
| where severityLevel >= 3  // Warning or Error
| extend operation = tostring(customDimensions.operation)
| summarize 
    error_count = count(),
    sample_message = any(message)
  by operation, severityLevel
| order by error_count desc
```

**Trace Request Flow:**
```kusto
// Follow single request through system
let correlation_id = "abc123-def456-ghi789";
traces
| where timestamp > ago(1h)
| where tostring(customDimensions.correlation_id) == correlation_id
| project 
    timestamp,
    level = severityLevel,
    operation = tostring(customDimensions.operation),
    message
| order by timestamp asc
```

**Performance Bottlenecks:**
```kusto
// Slowest operations
traces
| where timestamp > ago(1h)
| where customDimensions contains "duration_ms"
| extend 
    operation = tostring(customDimensions.operation),
    duration_ms = todouble(customDimensions.duration_ms)
| summarize 
    avg_duration = avg(duration_ms),
    p95_duration = percentile(duration_ms, 95),
    max_duration = max(duration_ms),
    count = count()
  by operation
| where avg_duration > 1000  // Over 1 second
| order by avg_duration desc
```

**User Activity:**
```kusto
// Active users in last 24 hours
traces
| where timestamp > ago(24h)
| extend user_id = tostring(customDimensions.user_id)
| where isnotempty(user_id)
| summarize 
    operation_count = count(),
    operations = make_set(tostring(customDimensions.operation))
  by user_id
| order by operation_count desc
```

---

## 🚨 Alerting

### Critical Alerts

**High Error Rate:**
```bash
az monitor metrics alert create \
  --name "high-error-rate" \
  --resource-group $RG_NAME \
  --scopes $APPINSIGHTS_ID \
  --condition "avg requests/failed > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 1 \
  --description "Error rate exceeded 10 per minute" \
  --action $ACTION_GROUP_ID
```

**API Latency Spike:**
```bash
az monitor metrics alert create \
  --name "high-latency" \
  --resource-group $RG_NAME \
  --scopes $APPINSIGHTS_ID \
  --condition "avg requests/duration > 5000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2 \
  --description "API latency exceeded 5 seconds" \
  --action $ACTION_GROUP_ID
```

**Circuit Breaker Open:**
```bash
# Custom log alert
az monitor scheduled-query create \
  --name "circuit-breaker-open" \
  --resource-group $RG_NAME \
  --scopes $APPINSIGHTS_ID \
  --condition "count > 5" \
  --condition-query "traces | where message contains 'Circuit breaker opened' | summarize count()" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2 \
  --description "Circuit breaker opened 5+ times" \
  --action-groups $ACTION_GROUP_ID
```

### Warning Alerts

**Increased Retry Attempts:**
```bash
az monitor scheduled-query create \
  --name "increased-retries" \
  --resource-group $RG_NAME \
  --scopes $APPINSIGHTS_ID \
  --condition "count > 50" \
  --condition-query "traces | where message contains 'Retry attempt' | summarize count()" \
  --window-size 15m \
  --evaluation-frequency 5m \
  --severity 3 \
  --description "Retry attempts increased significantly" \
  --action-groups $ACTION_GROUP_ID
```

**Slow Workspace Creation:**
```bash
az monitor scheduled-query create \
  --name "slow-workspace-creation" \
  --resource-group $RG_NAME \
  --scopes $APPINSIGHTS_ID \
  --condition "avg_duration > 60000" \
  --condition-query "traces | where customDimensions.operation == 'create_workspace' | extend duration = todouble(customDimensions.duration_ms) | summarize avg_duration = avg(duration)" \
  --window-size 15m \
  --evaluation-frequency 5m \
  --severity 3 \
  --description "Workspace creation taking over 1 minute" \
  --action-groups $ACTION_GROUP_ID
```

### Alert Response

**When Alert Fires:**

1. **Acknowledge**
   ```bash
   # Check current status
   az monitor metrics alert show \
     --name high-error-rate \
     --resource-group $RG_NAME
   ```

2. **Investigate**
   ```kusto
   // Check recent errors
   traces
   | where timestamp > ago(15m)
   | where severityLevel >= 3
   | order by timestamp desc
   | take 50
   ```

3. **Mitigate**
   - If feature flag related: Disable feature
   - If API issue: Check Fabric service status
   - If capacity: Scale up or out

4. **Document**
   ```bash
   # Add to incident log
   echo "$(date -u): $ALERT_NAME fired - $RESOLUTION" >> incidents.log
   ```

---

## 📈 Dashboards

### Main Operations Dashboard

**Create Dashboard:**
```bash
# Dashboard JSON
cat > dashboard.json <<'EOF'
{
  "name": "Fabric CI/CD Operations",
  "tiles": [
    {
      "type": "metrics",
      "title": "Request Rate",
      "query": "requests | summarize count() by bin(timestamp, 1m)"
    },
    {
      "type": "metrics",
      "title": "Success Rate",
      "query": "requests | summarize success_rate = (countif(success) * 100.0) / count()"
    },
    {
      "type": "metrics",
      "title": "P95 Latency",
      "query": "requests | summarize p95 = percentile(duration, 95) by bin(timestamp, 5m)"
    },
    {
      "type": "logs",
      "title": "Recent Errors",
      "query": "traces | where severityLevel >= 3 | order by timestamp desc | take 10"
    }
  ]
}
EOF

# Deploy dashboard
az portal dashboard create \
  --name "fabric-cicd-ops" \
  --resource-group $RG_NAME \
  --input-path dashboard.json
```

### Production Hardening Dashboard

**Key Panels:**

1. **Retry Logic**
   ```kusto
   // Retry attempts over time
   traces
   | where message contains "Retry attempt"
   | summarize count() by bin(timestamp, 5m)
   | render timechart
   ```

2. **Circuit Breaker**
   ```kusto
   // Circuit breaker state
   traces
   | where message contains "Circuit breaker"
   | extend state = tostring(customDimensions.circuit_state)
   | summarize count() by state, bin(timestamp, 5m)
   | render areachart
   ```

3. **Metrics Collection**
   ```kusto
   // Custom metrics volume
   customMetrics
   | summarize count() by name, bin(timestamp, 5m)
   | render timechart
   ```

4. **Error Correlation**
   ```kusto
   // Errors by feature flag state
   traces
   | where severityLevel >= 3
   | extend 
       retry_enabled = tobool(customDimensions.retry_enabled),
       circuit_enabled = tobool(customDimensions.circuit_enabled)
   | summarize count() by retry_enabled, circuit_enabled
   | render table
   ```

---

## 🔧 Troubleshooting

### High Latency

**Diagnosis:**
```kusto
// Identify slow operations
requests
| where timestamp > ago(1h)
| where duration > 5000  // Over 5 seconds
| extend operation = tostring(customDimensions.operation)
| summarize 
    count = count(),
    avg_duration = avg(duration),
    max_duration = max(duration)
  by operation
| order by avg_duration desc
```

**Resolution:**
1. Check if retry logic adding overhead
2. Review circuit breaker status
3. Check Fabric API status
4. Scale capacity if needed

### High Error Rate

**Diagnosis:**
```kusto
// Error distribution
exceptions
| where timestamp > ago(1h)
| summarize 
    count = count(),
    sample = any(outerMessage)
  by type
| order by count desc
```

**Resolution:**
1. Check error types
2. Review recent deployments
3. Check feature flag changes
4. Verify Azure service health

### Missing Telemetry

**Diagnosis:**
```bash
# Check Application Insights ingestion
az monitor app-insights metrics show \
  --app $APPINSIGHTS_APP_NAME \
  --metric "Ingestion Lag" \
  --interval PT1M

# Verify instrumentation key
az monitor app-insights component show \
  --app $APPINSIGHTS_APP_NAME \
  --resource-group $RG_NAME \
  --query "instrumentationKey"
```

**Resolution:**
1. Verify `APPLICATIONINSIGHTS_CONNECTION_STRING` set
2. Check network connectivity
3. Review sampling configuration
4. Check ingestion quotas

---

## 📊 Performance Baselines

### Normal Operating Ranges

| Metric | Normal Range | Warning Threshold | Critical Threshold |
|--------|--------------|-------------------|-------------------|
| Request Rate | 10-100/min | <5 or >200/min | <1 or >500/min |
| Success Rate | >99% | <98% | <95% |
| P95 Latency | <1000ms | >2000ms | >5000ms |
| Error Rate | <1/min | >5/min | >10/min |
| Retry Success | >95% | <90% | <80% |
| Circuit Breaker Trips | 0-2/hour | >5/hour | >10/hour |

### Weekly Health Report

**Generate Report:**
```bash
#!/bin/bash
# weekly_health_report.sh

REPORT_FILE="health_report_$(date +%Y%m%d).md"

cat > $REPORT_FILE <<EOF
# Weekly Health Report
**Period:** $(date -d '7 days ago' +%Y-%m-%d) to $(date +%Y-%m-%d)

## Summary Metrics
EOF

# Get metrics via Azure CLI
az monitor app-insights metrics show \
  --app $APPINSIGHTS_APP_NAME \
  --metric "requests/count" \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --aggregation total \
  >> $REPORT_FILE

# Add KQL query results
az monitor app-insights query \
  --app $APPINSIGHTS_APP_NAME \
  --analytics-query "
    requests
    | where timestamp > ago(7d)
    | summarize 
        total_requests = count(),
        success_rate = (countif(success) * 100.0) / count(),
        avg_duration = avg(duration),
        p95_duration = percentile(duration, 95)
  " \
  >> $REPORT_FILE

echo "Report generated: $REPORT_FILE"
```

---

## 📚 Additional Resources

- [Application Insights Overview](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Kusto Query Language](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Azure Monitor Alerts](https://docs.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview)
- [Deployment Runbook](./DEPLOYMENT_RUNBOOK.md)
- [Feature Flags Runbook](./FEATURE_FLAGS_RUNBOOK.md)

---

**Document Owner:** DevOps Team  
**Last Updated:** 2025-10-24  
**Version:** 1.0.0  
**Review Cycle:** Monthly
