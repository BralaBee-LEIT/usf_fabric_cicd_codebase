# Runbook: Incidents Pipeline

## Alerts
- Failures in DevOps stages generate alerts to #usf-incidents-ops.

## Rollback
- In DevOps, select previous successful run and redeploy to target environment.
- For data issues, perform forward-fix; use Delta time travel for audit.

## Backfill
- Trigger backfill job with limited concurrency.
- Validate DQ before publishing to Gold.
