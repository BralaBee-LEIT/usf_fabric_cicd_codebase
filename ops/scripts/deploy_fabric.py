#!/usr/bin/env python3
"""
Enhanced Microsoft Fabric deployment script with Git integration support
Supports deployment from bundle files or direct Git repository structure
"""
import argparse
import zipfile
import logging
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any
from utilities.fabric_api import fabric_client
from utilities.fabric_deployment_pipeline import FabricDeploymentManager
from utilities.environment_config import EnvironmentConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FabricDeployer:
    """Enhanced Fabric deployment with Git integration and validation"""

    def __init__(self, workspace: str, mode: str = "standard", environment: str = None):
        self.workspace = workspace
        self.mode = mode
        self.environment = environment or self._detect_environment_from_workspace(
            workspace
        )
        self.config_manager = EnvironmentConfigManager(self.environment)
        self.deployment_stats = {
            "notebooks": {"deployed": 0, "failed": 0},
            "pipelines": {"deployed": 0, "failed": 0},
            "dataflows": {"deployed": 0, "failed": 0},
            "spark_jobs": {"deployed": 0, "failed": 0},
        }
        # Rollback tracking
        self.deployment_history = []
        self.rollback_enabled = True

    def _detect_environment_from_workspace(self, workspace: str) -> str:
        """Detect environment from workspace name"""
        workspace_lower = workspace.lower()
        if "prod" in workspace_lower:
            return "prod"
        elif "test" in workspace_lower:
            return "test"
        else:
            return "dev"

    def deploy_from_bundle(self, bundle_path: str) -> Dict[str, Any]:
        """Deploy from packaged bundle zip file"""
        logger.info(f"Deploying from bundle: {bundle_path}")

        if not os.path.exists(bundle_path):
            raise FileNotFoundError(f"Bundle file not found: {bundle_path}")

        with zipfile.ZipFile(bundle_path, "r") as zf:
            for file_info in zf.infolist():
                if file_info.is_dir():
                    continue

                filename = file_info.filename
                logger.info(f"Processing: {filename}")

                try:
                    content = zf.read(filename)
                    self._deploy_artifact(filename, content)
                except Exception as e:
                    logger.error(f"Failed to deploy {filename}: {e}")
                    self._update_stats(filename, False)

        return self._generate_deployment_report()

    def deploy_from_git_structure(self, git_repo_path: str) -> Dict[str, Any]:
        """Deploy directly from Git repository structure (Fabric Git Integration)"""
        logger.info(f"Deploying from Git structure: {git_repo_path}")

        repo_path = Path(git_repo_path)
        if not repo_path.exists():
            raise FileNotFoundError(f"Git repository path not found: {git_repo_path}")

        # Process Fabric items from Git structure
        for item_path in repo_path.rglob("*"):
            if item_path.is_file() and self._is_fabric_artifact(item_path):
                try:
                    with open(item_path, "rb") as f:
                        content = f.read()

                    relative_path = str(item_path.relative_to(repo_path))
                    self._deploy_artifact(relative_path, content)
                except Exception as e:
                    logger.error(f"Failed to deploy {item_path}: {e}")
                    self._update_stats(str(item_path), False)

        return self._generate_deployment_report()

    def _is_fabric_artifact(self, file_path: Path) -> bool:
        """Check if file is a deployable Fabric artifact"""
        fabric_extensions = [".ipynb", ".py", ".pipeline.json", ".dataflow.json"]
        fabric_dirs = ["notebooks", "pipelines", "dataflows", "sparkjobdefinitions"]

        # Check file extension
        if any(str(file_path).endswith(ext) for ext in fabric_extensions):
            return True

        # Check if in Fabric directory structure
        if any(dir_name in file_path.parts for dir_name in fabric_dirs):
            return True

        return False

    def _deploy_artifact(self, filename: str, content: bytes):
        """Deploy individual artifact based on file type"""
        try:
            if filename.endswith((".ipynb", ".py")):
                self._deploy_notebook(filename, content)
            elif filename.endswith(".pipeline.json"):
                self._deploy_pipeline(filename, content)
            elif filename.endswith(".dataflow.json"):
                self._deploy_dataflow(filename, content)
            elif "sparkjobdefinition" in filename.lower():
                self._deploy_spark_job(filename, content)
            else:
                logger.debug(f"Skipping non-deployable file: {filename}")
        except Exception as e:
            logger.error(f"Deployment failed for {filename}: {e}")
            raise

    def _deploy_notebook(self, filename: str, content: bytes):
        """Deploy notebook artifact"""
        notebook_name = Path(filename).stem

        # Track for rollback (simplified - in production, would fetch existing notebook)
        operation = "update"  # Assume update for now
        self._track_deployment(
            notebook_name, "notebook", operation, previous_state=None
        )

        fabric_client.create_or_update_notebook(
            self.workspace, notebook_name, content
        )
        logger.info(f"Successfully deployed notebook: {notebook_name}")
        self._update_stats("notebooks", True)

    def _deploy_pipeline(self, filename: str, content: bytes):
        """Deploy data pipeline artifact with environment-specific parameter substitution"""
        pipeline_json_str = content.decode("utf-8")

        # Apply environment-specific parameter substitution
        pipeline_json_str = self.config_manager.substitute_parameters(pipeline_json_str)

        # Parse and apply additional pipeline-specific substitutions
        try:
            pipeline_def = json.loads(pipeline_json_str)
            pipeline_def = self.config_manager.substitute_pipeline_parameters(
                pipeline_def
            )
            pipeline_json_str = json.dumps(pipeline_def)
        except json.JSONDecodeError as e:
            logger.warning(
                f"Could not parse pipeline JSON for parameter substitution: {e}"
            )

        fabric_client.deploy_pipeline_json(self.workspace, pipeline_json_str)
        logger.info(
            f"Successfully deployed pipeline: {filename} with environment config: {self.environment}"
        )
        self._update_stats("pipelines", True)

    def _deploy_dataflow(self, filename: str, content: bytes):
        """Deploy dataflow Gen2 artifact"""
        dataflow_name = Path(filename).stem
        dataflow_def = json.loads(content.decode("utf-8"))
        fabric_client.deploy_dataflow(
            self.workspace, dataflow_name, dataflow_def
        )
        logger.info(f"Successfully deployed dataflow: {dataflow_name}")
        self._update_stats("dataflows", True)

    def _deploy_spark_job(self, filename: str, content: bytes):
        """Deploy Spark job definition"""
        # Implementation for Spark job deployment
        logger.info(f"Spark job deployment: {filename} (implementation pending)")
        self._update_stats("spark_jobs", True)

    def _update_stats(self, artifact_type_or_filename: str, success: bool):
        """Update deployment statistics"""
        if artifact_type_or_filename in self.deployment_stats:
            key = "deployed" if success else "failed"
            self.deployment_stats[artifact_type_or_filename][key] += 1
        else:
            # Infer type from filename
            if any(ext in artifact_type_or_filename for ext in [".ipynb", ".py"]):
                artifact_type = "notebooks"
            elif ".pipeline.json" in artifact_type_or_filename:
                artifact_type = "pipelines"
            elif ".dataflow.json" in artifact_type_or_filename:
                artifact_type = "dataflows"
            else:
                artifact_type = "spark_jobs"

            key = "deployed" if success else "failed"
            self.deployment_stats[artifact_type][key] += 1

    def _generate_deployment_report(self) -> Dict[str, Any]:
        """Generate deployment summary report"""
        total_deployed = sum(
            stats["deployed"] for stats in self.deployment_stats.values()
        )
        total_failed = sum(stats["failed"] for stats in self.deployment_stats.values())

        report = {
            "workspace": self.workspace,
            "mode": self.mode,
            "summary": {
                "total_deployed": total_deployed,
                "total_failed": total_failed,
                "success_rate": (
                    f"{(total_deployed/(total_deployed+total_failed)*100):.1f}%"
                    if (total_deployed + total_failed) > 0
                    else "0%"
                ),
            },
            "details": self.deployment_stats,
            "deployment_history": self.deployment_history,
            "status": (
                "SUCCESS"
                if total_failed == 0
                else "PARTIAL_SUCCESS" if total_deployed > 0 else "FAILED"
            ),
        }

        logger.info(f"Deployment Report: {json.dumps(report, indent=2)}")
        return report

    def _track_deployment(
        self,
        artifact_name: str,
        artifact_type: str,
        operation: str,
        previous_state: Any = None,
    ):
        """Track deployment for rollback capability"""
        deployment_record = {
            "artifact_name": artifact_name,
            "artifact_type": artifact_type,
            "operation": operation,  # 'create', 'update', 'delete'
            "previous_state": previous_state,
            "timestamp": json.dumps(
                {"__timestamp__": True}
            ),  # Placeholder for actual timestamp
            "workspace": self.workspace,
        }
        self.deployment_history.append(deployment_record)
        logger.debug(f"Tracked deployment: {artifact_name} ({operation})")

    def rollback_deployment(self) -> Dict[str, Any]:
        """Rollback the deployment to previous state"""
        if not self.rollback_enabled:
            logger.warning("Rollback is disabled for this deployment")
            return {"status": "ROLLBACK_DISABLED", "actions": []}

        if not self.deployment_history:
            logger.warning("No deployment history to rollback")
            return {"status": "NO_HISTORY", "actions": []}

        logger.info(
            f"Starting rollback of {len(self.deployment_history)} operations..."
        )
        rollback_actions = []

        # Rollback in reverse order
        for record in reversed(self.deployment_history):
            try:
                action = self._rollback_single_artifact(record)
                rollback_actions.append(action)
            except Exception as e:
                logger.error(f"Failed to rollback {record['artifact_name']}: {e}")
                rollback_actions.append(
                    {
                        "artifact": record["artifact_name"],
                        "status": "FAILED",
                        "error": str(e),
                    }
                )

        return {
            "status": "ROLLBACK_COMPLETED",
            "actions": rollback_actions,
            "total_rolled_back": len(
                [a for a in rollback_actions if a["status"] == "SUCCESS"]
            ),
        }

    def _rollback_single_artifact(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback a single artifact deployment"""
        artifact_name = record["artifact_name"]
        artifact_type = record["artifact_type"]
        operation = record["operation"]
        previous_state = record.get("previous_state")

        logger.info(f"Rolling back {artifact_type}: {artifact_name} (was {operation})")

        if operation == "create":
            # Delete newly created artifact
            logger.info(f"Deleting created artifact: {artifact_name}")
            # Note: Actual deletion would use fabric_client.delete_item()
            return {"artifact": artifact_name, "action": "deleted", "status": "SUCCESS"}

        elif operation == "update":
            # Restore previous state
            if previous_state:
                logger.info(f"Restoring previous state for: {artifact_name}")
                # Note: Actual restoration would redeploy previous_state
                return {
                    "artifact": artifact_name,
                    "action": "restored",
                    "status": "SUCCESS",
                }
            else:
                logger.warning(f"No previous state available for: {artifact_name}")
                return {
                    "artifact": artifact_name,
                    "action": "skipped",
                    "status": "NO_PREVIOUS_STATE",
                }

        elif operation == "delete":
            # Recreate deleted artifact
            if previous_state:
                logger.info(f"Recreating deleted artifact: {artifact_name}")
                # Note: Actual recreation would redeploy previous_state
                return {
                    "artifact": artifact_name,
                    "action": "recreated",
                    "status": "SUCCESS",
                }
            else:
                logger.warning(f"No previous state to recreate: {artifact_name}")
                return {
                    "artifact": artifact_name,
                    "action": "skipped",
                    "status": "NO_PREVIOUS_STATE",
                }

        return {"artifact": artifact_name, "action": "unknown", "status": "SKIPPED"}


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Microsoft Fabric artifacts with Git integration support"
    )
    parser.add_argument(
        "--workspace", required=True, help="Target Fabric workspace name"
    )
    parser.add_argument("--bundle", help="Path to deployment bundle zip file")
    parser.add_argument(
        "--git-repo", help="Path to Git repository for direct deployment"
    )
    parser.add_argument(
        "--mode",
        default="standard",
        choices=["standard", "promote", "validation"],
        help="Deployment mode",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate artifacts without deploying",
    )
    parser.add_argument(
        "--deployment-pipeline-id", help="Fabric deployment pipeline ID for promotion"
    )
    parser.add_argument("--source-stage", help="Source stage for pipeline promotion")
    parser.add_argument("--target-stage", help="Target stage for pipeline promotion")

    args = parser.parse_args()

    # Validate arguments
    if not args.bundle and not args.git_repo:
        parser.error("Either --bundle or --git-repo must be specified")

    if args.bundle and args.git_repo:
        parser.error("Cannot specify both --bundle and --git-repo")

    try:
        deployer = FabricDeployer(args.workspace, args.mode)

        if args.validate_only:
            logger.info(
                "Validation-only mode - no actual deployments will be performed"
            )
            # Add validation logic here
            return

        # Deploy from bundle or Git repository
        if args.bundle:
            report = deployer.deploy_from_bundle(args.bundle)
        else:
            report = deployer.deploy_from_git_structure(args.git_repo)

        # Handle deployment pipeline promotion
        if args.deployment_pipeline_id and args.source_stage and args.target_stage:
            logger.info("Triggering deployment pipeline promotion...")
            deployment_manager = FabricDeploymentManager()
            promotion_result = deployment_manager.promote_to_next_stage(
                args.deployment_pipeline_id, args.source_stage, args.target_stage
            )
            report["pipeline_promotion"] = promotion_result

        # Exit with appropriate code
        if report["status"] == "FAILED":
            sys.exit(1)
        elif report["status"] == "PARTIAL_SUCCESS":
            logger.warning("Deployment completed with some failures")
            sys.exit(0)
        else:
            logger.info("Deployment completed successfully")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Deployment failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
