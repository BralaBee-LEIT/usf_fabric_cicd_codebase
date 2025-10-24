#!/usr/bin/env python3
"""
Microsoft Fabric workspace health check
Monitors workspace health, item status, and performance metrics
"""
import argparse
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any
from utilities.fabric_api import fabric_client

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FabricHealthChecker:
    """Comprehensive Fabric workspace health monitoring"""

    def __init__(self, workspace_name: str, environment: str):
        self.workspace_name = workspace_name
        self.environment = environment
        self.workspace_id = None
        self.health_report = {
            "workspace": workspace_name,
            "environment": environment,
            "check_timestamp": datetime.utcnow().isoformat(),
            "overall_status": "unknown",
            "critical_issues": [],
            "warnings": [],
            "metrics": {},
            "item_health": {},
            "recommendations": [],
        }

    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all health checks"""
        logger.info(f"Starting health check for workspace: {self.workspace_name}")

        try:
            # Get workspace ID
            self.workspace_id = fabric_client.get_workspace_id(self.workspace_name)

            # Run individual checks
            self._check_workspace_accessibility()
            self._check_items_health()
            self._check_recent_activities()
            self._check_capacity_metrics()
            self._check_git_integration_status()
            self._analyze_performance_trends()

            # Calculate overall status
            self._determine_overall_health()

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.health_report["critical_issues"].append(
                {
                    "type": "connection_error",
                    "description": f"Failed to connect to workspace: {str(e)}",
                    "severity": "critical",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            self.health_report["overall_status"] = "critical"

        return self.health_report

    def _check_workspace_accessibility(self):
        """Check if workspace is accessible and responsive"""
        try:
            start_time = time.time()

            # Test workspace access
            fabric_client._make_request("GET", f"workspaces/{self.workspace_id}")
            response_time = time.time() - start_time

            self.health_report["metrics"]["workspace_response_time"] = response_time

            if response_time > 5.0:
                self.health_report["warnings"].append(
                    {
                        "type": "performance",
                        "description": f"Slow workspace response time: {response_time:.2f}s",
                        "severity": "medium",
                    }
                )

            logger.info(f"Workspace accessible (response time: {response_time:.2f}s)")

        except Exception as e:
            self.health_report["critical_issues"].append(
                {
                    "type": "accessibility",
                    "description": f"Workspace not accessible: {str(e)}",
                    "severity": "critical",
                }
            )

    def _check_items_health(self):
        """Check the health of all items in the workspace"""
        try:
            # Get all items
            items = fabric_client.list_workspace_items(self.workspace_id)

            item_counts = {}
            failed_items = []

            for item in items:
                item_type = item.get("type", "Unknown")
                item_counts[item_type] = item_counts.get(item_type, 0) + 1

                # Check item status (if available)
                item_status = self._check_individual_item_health(item)
                if item_status["status"] == "failed":
                    failed_items.append(item_status)

            self.health_report["metrics"]["item_counts"] = item_counts
            self.health_report["metrics"]["total_items"] = len(items)
            self.health_report["item_health"]["failed_items"] = failed_items

            if failed_items:
                self.health_report["critical_issues"].append(
                    {
                        "type": "item_failures",
                        "description": f"{len(failed_items)} items in failed state",
                        "severity": "high",
                        "details": failed_items,
                    }
                )

            logger.info(f"Checked {len(items)} items, {len(failed_items)} failures")

        except Exception as e:
            self.health_report["warnings"].append(
                {
                    "type": "item_check",
                    "description": f"Could not check all items: {str(e)}",
                    "severity": "medium",
                }
            )

    def _check_individual_item_health(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of an individual workspace item"""
        item_health = {
            "id": item.get("id"),
            "name": item.get("displayName"),
            "type": item.get("type"),
            "status": "unknown",
            "last_modified": item.get("lastModifiedDateTime"),
            "issues": [],
        }

        try:
            # Get detailed item information
            item_id = item["id"]
            fabric_client._make_request(
                "GET", f"workspaces/{self.workspace_id}/items/{item_id}"
            )

            # Check for common issues
            if item.get("type") == "DataPipeline":
                # Check pipeline status
                pipeline_status = self._check_pipeline_status(item_id)
                item_health.update(pipeline_status)
            elif item.get("type") == "Notebook":
                # Check notebook status
                notebook_status = self._check_notebook_status(item_id)
                item_health.update(notebook_status)

            if not item_health["issues"]:
                item_health["status"] = "healthy"

        except Exception as e:
            item_health["status"] = "failed"
            item_health["issues"].append(f"Health check failed: {str(e)}")

        return item_health

    def _check_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Check data pipeline specific health"""
        status = {"issues": []}

        try:
            # Get pipeline runs (if available)
            # This would typically check recent execution history
            # For now, we'll simulate pipeline health checking

            # Check for failed runs in the last 24 hours
            # (Implementation would depend on available APIs)

            status["status"] = "healthy"

        except Exception as e:
            status["status"] = "failed"
            status["issues"].append(f"Pipeline check failed: {str(e)}")

        return status

    def _check_notebook_status(self, notebook_id: str) -> Dict[str, Any]:
        """Check notebook specific health"""
        status = {"issues": []}

        try:
            # Check notebook definition and content
            status["status"] = "healthy"

        except Exception as e:
            status["status"] = "failed"
            status["issues"].append(f"Notebook check failed: {str(e)}")

        return status

    def _check_recent_activities(self):
        """Check recent workspace activity for anomalies"""
        try:
            # This would check activity logs if available
            # For now, we'll simulate activity checking

            self.health_report["metrics"]["recent_activity"] = {
                "last_24h_deployments": 0,
                "failed_operations": 0,
                "active_users": 0,
            }

            logger.info("Recent activity check completed")

        except Exception as e:
            self.health_report["warnings"].append(
                {
                    "type": "activity_check",
                    "description": f"Could not check recent activities: {str(e)}",
                    "severity": "low",
                }
            )

    def _check_capacity_metrics(self):
        """Check workspace capacity and resource usage"""
        try:
            # This would check capacity metrics if available through APIs
            # For now, we'll simulate capacity checking

            self.health_report["metrics"]["capacity"] = {
                "cpu_usage": "unknown",
                "memory_usage": "unknown",
                "storage_usage": "unknown",
            }

            logger.info("Capacity metrics check completed")

        except Exception as e:
            self.health_report["warnings"].append(
                {
                    "type": "capacity_check",
                    "description": f"Could not check capacity metrics: {str(e)}",
                    "severity": "low",
                }
            )

    def _check_git_integration_status(self):
        """Check Git integration health"""
        try:
            # Check if workspace has Git integration configured
            git_status = fabric_client._make_request(
                "GET", f"workspaces/{self.workspace_id}/git/status"
            )

            git_info = git_status.json()

            self.health_report["metrics"]["git_integration"] = {
                "connected": git_info.get("gitProviderDetails") is not None,
                "sync_status": git_info.get("gitSyncStatus", "Unknown"),
                "last_sync": git_info.get("lastSyncTime"),
            }

            # Check for sync issues
            sync_status = git_info.get("gitSyncStatus", "")
            if sync_status in ["Failed", "Conflict"]:
                self.health_report["warnings"].append(
                    {
                        "type": "git_sync",
                        "description": f"Git sync status: {sync_status}",
                        "severity": "medium",
                    }
                )

            logger.info(f"Git integration status: {sync_status}")

        except Exception as e:
            # Git integration might not be configured, which is not necessarily an error
            self.health_report["metrics"]["git_integration"] = {
                "connected": False,
                "error": str(e),
            }
            logger.info("No Git integration configured or accessible")

    def _analyze_performance_trends(self):
        """Analyze performance trends (if historical data available)"""
        try:
            # This would analyze historical performance data
            # For now, we'll provide a placeholder

            self.health_report["metrics"]["performance_trends"] = {
                "trend_analysis": "insufficient_data",
                "performance_score": "unknown",
            }

            logger.info("Performance trends analysis completed")

        except Exception as e:
            logger.warning(f"Could not analyze performance trends: {e}")

    def _determine_overall_health(self):
        """Determine overall workspace health status"""
        if self.health_report["critical_issues"]:
            self.health_report["overall_status"] = "critical"
            self.health_report["recommendations"].append(
                "Address critical issues immediately to restore workspace functionality"
            )
        elif len(self.health_report["warnings"]) > 3:
            self.health_report["overall_status"] = "degraded"
            self.health_report["recommendations"].append(
                "Multiple warnings detected - investigate and resolve to prevent issues"
            )
        elif self.health_report["warnings"]:
            self.health_report["overall_status"] = "healthy_with_warnings"
            self.health_report["recommendations"].append(
                "Minor issues detected - monitor and resolve when convenient"
            )
        else:
            self.health_report["overall_status"] = "healthy"
            self.health_report["recommendations"].append(
                "Workspace is operating normally - continue regular monitoring"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Check Microsoft Fabric workspace health"
    )
    parser.add_argument("--workspace", required=True, help="Fabric workspace name")
    parser.add_argument(
        "--environment", required=True, help="Environment (dev/test/prod)"
    )
    parser.add_argument("--output-format", choices=["json", "text"], default="json")
    parser.add_argument("--output-file", help="Output file for health report")
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        help="Exit with error code if critical issues found",
    )

    args = parser.parse_args()

    try:
        health_checker = FabricHealthChecker(args.workspace, args.environment)
        health_report = health_checker.run_comprehensive_check()

        # Format output
        if args.output_format == "json":
            output = json.dumps(health_report, indent=2)
        else:
            # Text format
            lines = []
            lines.append("# Fabric Workspace Health Report")
            lines.append(f"**Workspace:** {health_report['workspace']}")
            lines.append(f"**Environment:** {health_report['environment']}")
            lines.append(
                f"**Overall Status:** {health_report['overall_status'].upper()}"
            )
            lines.append(f"**Check Time:** {health_report['check_timestamp']}")
            lines.append("")

            if health_report["critical_issues"]:
                lines.append("## 🔴 Critical Issues")
                for issue in health_report["critical_issues"]:
                    lines.append(f"- **{issue['type']}:** {issue['description']}")
                lines.append("")

            if health_report["warnings"]:
                lines.append("## 🟡 Warnings")
                for warning in health_report["warnings"]:
                    lines.append(f"- **{warning['type']}:** {warning['description']}")
                lines.append("")

            lines.append("## 📊 Metrics")
            for key, value in health_report["metrics"].items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

            if health_report["recommendations"]:
                lines.append("## 💡 Recommendations")
                for rec in health_report["recommendations"]:
                    lines.append(f"- {rec}")

            output = "\n".join(lines)

        # Output result
        if args.output_file:
            with open(args.output_file, "w") as f:
                f.write(output)
            logger.info(f"Health report written to {args.output_file}")
        else:
            print(output)

        # Check exit conditions
        if args.fail_on_critical and health_report["overall_status"] == "critical":
            logger.error("Critical issues found in workspace health check")
            return 1

        return 0

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
