#!/usr/bin/env python3
"""
Check that Jupyter notebook outputs are cleared for version control
This ensures notebooks don't contain large outputs or sensitive data
"""
import argparse
import json
import logging
import os
from pathlib import Path
from typing import List, Dict, Any
import nbformat

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NotebookOutputChecker:
    """Check and optionally clear notebook outputs"""

    def __init__(self, notebooks_path: str):
        self.notebooks_path = Path(notebooks_path)
        self.results = {
            "total_notebooks": 0,
            "notebooks_with_outputs": 0,
            "notebooks_cleared": 0,
            "errors": [],
            "details": [],
        }

    def check_all_notebooks(self, auto_clear: bool = False) -> Dict[str, Any]:
        """Check all notebooks for outputs"""
        logger.info(f"Checking notebooks in {self.notebooks_path}")

        notebook_files = list(self.notebooks_path.rglob("*.ipynb"))
        self.results["total_notebooks"] = len(notebook_files)

        if not notebook_files:
            logger.warning("No notebook files found")
            return self.results

        for notebook_path in notebook_files:
            self._check_notebook(notebook_path, auto_clear)

        return self.results

    def _check_notebook(self, notebook_path: Path, auto_clear: bool = False) -> None:
        """Check a single notebook for outputs"""
        try:
            with open(notebook_path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)

            has_outputs = False
            cell_outputs_count = 0

            # Check each cell for outputs
            for i, cell in enumerate(nb.cells):
                if hasattr(cell, "outputs") and cell.outputs:
                    has_outputs = True
                    cell_outputs_count += len(cell.outputs)

                    if auto_clear:
                        cell.outputs = []

                # Also check execution_count
                if (
                    hasattr(cell, "execution_count")
                    and cell.execution_count is not None
                ):
                    has_outputs = True

                    if auto_clear:
                        cell.execution_count = None

            # Record results
            notebook_info = {
                "path": str(notebook_path),
                "has_outputs": has_outputs,
                "cell_outputs_count": cell_outputs_count,
                "total_cells": len(nb.cells),
                "cleared": False,
            }

            if has_outputs:
                self.results["notebooks_with_outputs"] += 1

                if auto_clear:
                    # Save the cleared notebook
                    with open(notebook_path, "w", encoding="utf-8") as f:
                        nbformat.write(nb, f)
                    notebook_info["cleared"] = True
                    self.results["notebooks_cleared"] += 1
                    logger.info(f"Cleared outputs from {notebook_path.name}")
                else:
                    logger.warning(
                        f"Found outputs in {notebook_path.name} ({cell_outputs_count} outputs)"
                    )
            else:
                logger.info(f"No outputs found in {notebook_path.name}")

            self.results["details"].append(notebook_info)

        except Exception as e:
            error_msg = f"Failed to process {notebook_path}: {str(e)}"
            logger.error(error_msg)
            self.results["errors"].append({"path": str(notebook_path), "error": str(e)})

    def generate_report(self, format: str = "text") -> str:
        """Generate a report of the check results"""
        if format == "json":
            return json.dumps(self.results, indent=2)

        # Text format
        lines = []
        lines.append("# Notebook Output Check Report")
        lines.append(f"Total notebooks checked: {self.results['total_notebooks']}")
        lines.append(
            f"Notebooks with outputs: {self.results['notebooks_with_outputs']}"
        )
        lines.append(f"Notebooks cleared: {self.results['notebooks_cleared']}")
        lines.append(f"Errors encountered: {len(self.results['errors'])}")
        lines.append("")

        if self.results["notebooks_with_outputs"] > 0:
            lines.append("## Notebooks with Outputs:")
            for notebook in self.results["details"]:
                if notebook["has_outputs"]:
                    status = "✅ CLEARED" if notebook["cleared"] else "❌ HAS OUTPUTS"
                    lines.append(
                        f"- {notebook['path']} - {status} ({notebook['cell_outputs_count']} outputs)"
                    )
            lines.append("")

        if self.results["errors"]:
            lines.append("## Errors:")
            for error in self.results["errors"]:
                lines.append(f"- {error['path']}: {error['error']}")
            lines.append("")

        if self.results["notebooks_with_outputs"] == 0:
            lines.append("✅ All notebooks have clean outputs!")

        return "\n".join(lines)

    def has_violations(self) -> bool:
        """Check if there are any notebooks with outputs (violations)"""
        return self.results["notebooks_with_outputs"] > 0


def main():
    parser = argparse.ArgumentParser(
        description="Check and optionally clear Jupyter notebook outputs"
    )
    parser.add_argument("--path", required=True, help="Path to notebooks directory")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Automatically clear outputs from notebooks",
    )
    parser.add_argument(
        "--fail-on-outputs",
        action="store_true",
        help="Exit with error code if notebooks have outputs",
    )
    parser.add_argument("--output-format", choices=["text", "json"], default="text")
    parser.add_argument("--output-file", help="Output file for report")

    args = parser.parse_args()

    try:
        checker = NotebookOutputChecker(args.path)
        results = checker.check_all_notebooks(auto_clear=args.clear)
        report = checker.generate_report(args.output_format)

        # Output report
        if args.output_file:
            with open(args.output_file, "w") as f:
                f.write(report)
            logger.info(f"Report written to {args.output_file}")
        else:
            print(report)

        # Check exit conditions
        if args.fail_on_outputs and checker.has_violations():
            if not args.clear:
                logger.error(
                    f"Found {results['notebooks_with_outputs']} notebooks with outputs"
                )
                return 1

        if results["errors"]:
            logger.error(
                f"Encountered {len(results['errors'])} errors during processing"
            )
            return 1

        return 0

    except Exception as e:
        logger.error(f"Check failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
