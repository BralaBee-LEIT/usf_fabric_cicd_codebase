#!/usr/bin/env python3
"""
Validate Microsoft Fabric artifacts for deployment readiness
Performs comprehensive validation of notebooks, pipelines, dataflows, and other Fabric items
"""
import argparse
import json
import logging
import re
from pathlib import Path
from typing import Dict, Any
import nbformat

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FabricArtifactValidator:
    """Validate Fabric artifacts for deployment readiness"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.validation_results = {
            "notebooks": {"passed": 0, "failed": 0, "issues": []},
            "pipelines": {"passed": 0, "failed": 0, "issues": []},
            "dataflows": {"passed": 0, "failed": 0, "issues": []},
            "spark_jobs": {"passed": 0, "failed": 0, "issues": []},
            "overall": {"status": "unknown", "total_issues": 0},
        }

    def validate_all(self) -> Dict[str, Any]:
        """Validate all Fabric artifacts in the repository"""
        logger.info(f"Starting validation of Fabric artifacts in {self.base_path}")

        # Validate notebooks
        notebook_files = list(self.base_path.rglob("*.ipynb"))
        for notebook_file in notebook_files:
            self._validate_notebook(notebook_file)

        # Validate pipelines
        pipeline_files = list(self.base_path.rglob("*.pipeline.json"))
        for pipeline_file in pipeline_files:
            self._validate_pipeline(pipeline_file)

        # Validate dataflows
        dataflow_files = list(self.base_path.rglob("*.dataflow.json"))
        for dataflow_file in dataflow_files:
            self._validate_dataflow(dataflow_file)

        # Validate Spark job definitions
        spark_dirs = list(self.base_path.rglob("**/sparkjobdefinitions/**"))
        for spark_dir in spark_dirs:
            if spark_dir.is_dir():
                self._validate_spark_job_dir(spark_dir)

        # Calculate overall status
        self._calculate_overall_status()

        return self.validation_results

    def _validate_notebook(self, notebook_path: Path) -> None:
        """Validate a Jupyter notebook file"""
        try:
            # Read and parse notebook
            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)

            issues = []

            # Check for outputs in cells (should be cleared for version control)
            for i, cell in enumerate(nb.cells):
                if hasattr(cell, "outputs") and cell.outputs:
                    issues.append(
                        {
                            "type": "warning",
                            "message": f"Cell {i+1} contains outputs that should be cleared",
                            "severity": "medium",
                        }
                    )

            # Check for sensitive information patterns
            notebook_content = json.dumps(nb, default=str)
            sensitive_patterns = [
                (
                    r'(?i)(password|pwd)\s*[=:]\s*["\'][^"\']+["\']',
                    "Potential password in notebook",
                ),
                (
                    r'(?i)(secret|key)\s*[=:]\s*["\'][^"\']+["\']',
                    "Potential secret/key in notebook",
                ),
                (
                    r'(?i)connectionstring\s*[=:]\s*["\'][^"\']+["\']',
                    "Potential connection string in notebook",
                ),
                (
                    r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
                    "Potential IP address in notebook",
                ),
            ]

            for pattern, message in sensitive_patterns:
                if re.search(pattern, notebook_content):
                    issues.append(
                        {"type": "security", "message": message, "severity": "high"}
                    )

            # Check for best practices
            if len(nb.cells) == 0:
                issues.append(
                    {
                        "type": "structure",
                        "message": "Notebook is empty",
                        "severity": "medium",
                    }
                )

            # Check for markdown documentation
            has_markdown = any(cell.cell_type == "markdown" for cell in nb.cells)
            if not has_markdown and len(nb.cells) > 3:
                issues.append(
                    {
                        "type": "documentation",
                        "message": "Notebook lacks markdown documentation cells",
                        "severity": "low",
                    }
                )

            # Record results
            if issues:
                self.validation_results["notebooks"]["failed"] += 1
                self.validation_results["notebooks"]["issues"].extend(
                    [{"file": str(notebook_path), **issue} for issue in issues]
                )
            else:
                self.validation_results["notebooks"]["passed"] += 1

            logger.info(
                f"Validated notebook: {notebook_path.name} ({len(issues)} issues)"
            )

        except Exception as e:
            logger.error(f"Failed to validate notebook {notebook_path}: {e}")
            self.validation_results["notebooks"]["failed"] += 1
            self.validation_results["notebooks"]["issues"].append(
                {
                    "file": str(notebook_path),
                    "type": "error",
                    "message": f"Validation failed: {str(e)}",
                    "severity": "high",
                }
            )

    def _validate_pipeline(self, pipeline_path: Path) -> None:
        """Validate a data pipeline JSON file"""
        try:
            with open(pipeline_path, "r", encoding="utf-8") as f:
                pipeline_def = json.load(f)

            issues = []

            # Check required pipeline structure
            required_fields = ["name", "properties"]
            for field in required_fields:
                if field not in pipeline_def:
                    issues.append(
                        {
                            "type": "structure",
                            "message": f"Missing required field: {field}",
                            "severity": "high",
                        }
                    )

            # Check for activities
            if (
                "properties" in pipeline_def
                and "activities" in pipeline_def["properties"]
            ):
                activities = pipeline_def["properties"]["activities"]
                if not activities:
                    issues.append(
                        {
                            "type": "structure",
                            "message": "Pipeline has no activities defined",
                            "severity": "high",
                        }
                    )
                else:
                    # Validate individual activities
                    for i, activity in enumerate(activities):
                        if "name" not in activity:
                            issues.append(
                                {
                                    "type": "structure",
                                    "message": f"Activity {i+1} missing name",
                                    "severity": "medium",
                                }
                            )
                        if "type" not in activity:
                            issues.append(
                                {
                                    "type": "structure",
                                    "message": f"Activity '{activity.get('name', i+1)}' missing type",
                                    "severity": "medium",
                                }
                            )

            # Check for hardcoded connection strings or secrets
            pipeline_content = json.dumps(pipeline_def)
            if re.search(
                r'(?i)(password|secret|key)\s*["\']:\s*["\'][^"\']+["\']',
                pipeline_content,
            ):
                issues.append(
                    {
                        "type": "security",
                        "message": "Potential hardcoded secrets in pipeline",
                        "severity": "high",
                    }
                )

            # Record results
            if issues:
                self.validation_results["pipelines"]["failed"] += 1
                self.validation_results["pipelines"]["issues"].extend(
                    [{"file": str(pipeline_path), **issue} for issue in issues]
                )
            else:
                self.validation_results["pipelines"]["passed"] += 1

            logger.info(
                f"Validated pipeline: {pipeline_path.name} ({len(issues)} issues)"
            )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in pipeline {pipeline_path}: {e}")
            self.validation_results["pipelines"]["failed"] += 1
            self.validation_results["pipelines"]["issues"].append(
                {
                    "file": str(pipeline_path),
                    "type": "format",
                    "message": f"Invalid JSON format: {str(e)}",
                    "severity": "high",
                }
            )
        except Exception as e:
            logger.error(f"Failed to validate pipeline {pipeline_path}: {e}")
            self.validation_results["pipelines"]["failed"] += 1
            self.validation_results["pipelines"]["issues"].append(
                {
                    "file": str(pipeline_path),
                    "type": "error",
                    "message": f"Validation failed: {str(e)}",
                    "severity": "high",
                }
            )

    def _validate_dataflow(self, dataflow_path: Path) -> None:
        """Validate a dataflow JSON file"""
        try:
            with open(dataflow_path, "r", encoding="utf-8") as f:
                dataflow_def = json.load(f)

            issues = []

            # Check basic structure
            if "name" not in dataflow_def:
                issues.append(
                    {
                        "type": "structure",
                        "message": "Missing dataflow name",
                        "severity": "high",
                    }
                )

            # Check for queries/transformations
            if "queries" in dataflow_def:
                queries = dataflow_def["queries"]
                if not queries:
                    issues.append(
                        {
                            "type": "structure",
                            "message": "Dataflow has no queries defined",
                            "severity": "medium",
                        }
                    )

            # Record results
            if issues:
                self.validation_results["dataflows"]["failed"] += 1
                self.validation_results["dataflows"]["issues"].extend(
                    [{"file": str(dataflow_path), **issue} for issue in issues]
                )
            else:
                self.validation_results["dataflows"]["passed"] += 1

            logger.info(
                f"Validated dataflow: {dataflow_path.name} ({len(issues)} issues)"
            )

        except Exception as e:
            logger.error(f"Failed to validate dataflow {dataflow_path}: {e}")
            self.validation_results["dataflows"]["failed"] += 1
            self.validation_results["dataflows"]["issues"].append(
                {
                    "file": str(dataflow_path),
                    "type": "error",
                    "message": f"Validation failed: {str(e)}",
                    "severity": "high",
                }
            )

    def _validate_spark_job_dir(self, spark_dir: Path) -> None:
        """Validate Spark job definition directory"""
        try:
            issues = []

            # Look for main script files
            python_files = list(spark_dir.rglob("*.py"))
            scala_files = list(spark_dir.rglob("*.scala"))
            jar_files = list(spark_dir.rglob("*.jar"))

            if not (python_files or scala_files or jar_files):
                issues.append(
                    {
                        "type": "structure",
                        "message": "No Spark job files found (*.py, *.scala, *.jar)",
                        "severity": "high",
                    }
                )

            # Check for Spark job definition file
            job_def_files = list(spark_dir.rglob("*.sparkjob.json"))
            if not job_def_files:
                issues.append(
                    {
                        "type": "structure",
                        "message": "Missing Spark job definition file (*.sparkjob.json)",
                        "severity": "medium",
                    }
                )

            # Record results
            if issues:
                self.validation_results["spark_jobs"]["failed"] += 1
                self.validation_results["spark_jobs"]["issues"].extend(
                    [{"file": str(spark_dir), **issue} for issue in issues]
                )
            else:
                self.validation_results["spark_jobs"]["passed"] += 1

            logger.info(f"Validated Spark job: {spark_dir.name} ({len(issues)} issues)")

        except Exception as e:
            logger.error(f"Failed to validate Spark job {spark_dir}: {e}")
            self.validation_results["spark_jobs"]["failed"] += 1
            self.validation_results["spark_jobs"]["issues"].append(
                {
                    "file": str(spark_dir),
                    "type": "error",
                    "message": f"Validation failed: {str(e)}",
                    "severity": "high",
                }
            )

    def _calculate_overall_status(self) -> None:
        """Calculate overall validation status"""
        total_issues = sum(
            len(category["issues"])
            for category in self.validation_results.values()
            if isinstance(category, dict) and "issues" in category
        )

        high_severity_issues = sum(
            1
            for category in self.validation_results.values()
            if isinstance(category, dict) and "issues" in category
            for issue in category["issues"]
            if issue.get("severity") == "high"
        )

        self.validation_results["overall"]["total_issues"] = total_issues
        self.validation_results["overall"][
            "high_severity_issues"
        ] = high_severity_issues

        if high_severity_issues > 0:
            self.validation_results["overall"]["status"] = "failed"
        elif total_issues > 0:
            self.validation_results["overall"]["status"] = "warning"
        else:
            self.validation_results["overall"]["status"] = "passed"

    def generate_report(self, output_format: str = "text") -> str:
        """Generate validation report"""
        if output_format == "json":
            return json.dumps(self.validation_results, indent=2)

        # Text format report
        report_lines = []
        report_lines.append("# Fabric Artifacts Validation Report")
        report_lines.append(
            f"**Overall Status:** {self.validation_results['overall']['status'].upper()}"
        )
        report_lines.append(
            f"**Total Issues:** {self.validation_results['overall']['total_issues']}"
        )
        report_lines.append("")

        # Summary by artifact type
        for artifact_type in ["notebooks", "pipelines", "dataflows", "spark_jobs"]:
            results = self.validation_results[artifact_type]
            total = results["passed"] + results["failed"]
            if total > 0:
                report_lines.append(f"## {artifact_type.title()}")
                report_lines.append(f"- Passed: {results['passed']}")
                report_lines.append(f"- Failed: {results['failed']}")
                report_lines.append(f"- Issues: {len(results['issues'])}")
                report_lines.append("")

        # Detailed issues
        if self.validation_results["overall"]["total_issues"] > 0:
            report_lines.append("## Issues Found")

            for artifact_type in ["notebooks", "pipelines", "dataflows", "spark_jobs"]:
                issues = self.validation_results[artifact_type]["issues"]
                if issues:
                    report_lines.append(f"### {artifact_type.title()}")
                    for issue in issues:
                        severity_emoji = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🔵",
                        }.get(issue["severity"], "⚪")
                        report_lines.append(
                            f"{severity_emoji} **{issue['file']}** - {issue['message']}"
                        )
                    report_lines.append("")

        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description="Validate Microsoft Fabric artifacts")
    parser.add_argument("--path", required=True, help="Path to repository root")
    parser.add_argument("--output-format", choices=["text", "json"], default="text")
    parser.add_argument("--output-file", help="Output file path (optional)")
    parser.add_argument(
        "--fail-on-high",
        action="store_true",
        help="Exit with error code if high-severity issues found",
    )

    args = parser.parse_args()

    try:
        validator = FabricArtifactValidator(args.path)
        results = validator.validate_all()
        report = validator.generate_report(args.output_format)

        # Output report
        if args.output_file:
            with open(args.output_file, "w") as f:
                f.write(report)
            logger.info(f"Validation report written to {args.output_file}")
        else:
            print(report)

        # Check exit code
        if args.fail_on_high and results["overall"].get("high_severity_issues", 0) > 0:
            logger.error(
                f"Found {results['overall']['high_severity_issues']} high-severity issues"
            )
            return 1

        if results["overall"]["status"] == "failed":
            return 1

        return 0

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
