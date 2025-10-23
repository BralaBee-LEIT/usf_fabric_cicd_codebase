"""
Standardized output utilities for Microsoft Fabric CI/CD
Provides consistent console output and logging for both interactive and automated use
"""

import sys
import json
import logging
import re
from typing import Any, Dict, Optional
from datetime import datetime
from enum import Enum


class OutputLevel(Enum):
    """Output levels for console messages"""

    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


def sanitize_for_logging(value: str) -> str:
    """Redact sensitive patterns from log messages.

    Args:
        value: String that may contain sensitive information

    Returns:
        Sanitized string with sensitive data redacted
    """
    if not value:
        return value

    # Redact Bearer tokens
    value = re.sub(
        r"(Bearer\s+)[\w\-\.]+", r"\1***REDACTED***", value, flags=re.IGNORECASE
    )

    # Redact Azure connection strings
    value = re.sub(r"(AccountKey=)[\w\+/=]+", r"\1***", value, flags=re.IGNORECASE)

    # Redact passwords in connection strings
    value = re.sub(r"(password=)[^;]+", r"\1***", value, flags=re.IGNORECASE)
    value = re.sub(r"(pwd=)[^;]+", r"\1***", value, flags=re.IGNORECASE)

    # Redact client secrets
    value = re.sub(r"(client_secret=)[^&\s]+", r"\1***", value, flags=re.IGNORECASE)
    value = re.sub(
        r"(AZURE_CLIENT_SECRET=)[^\s]+", r"\1***", value, flags=re.IGNORECASE
    )

    # Redact API keys
    value = re.sub(r"(api[_-]?key[=:]\s*)[\w\-]+", r"\1***", value, flags=re.IGNORECASE)

    # Redact access tokens
    value = re.sub(
        r"(access[_-]?token[=:]\s*)[\w\-\.]+", r"\1***", value, flags=re.IGNORECASE
    )

    return value


class ConsoleOutput:
    """
    Standardized console output with consistent formatting

    Supports both plain text and JSON output for CI/CD integration
    """

    # Color codes for terminal output
    COLORS = {
        OutputLevel.DEBUG: "\033[90m",  # Gray
        OutputLevel.INFO: "\033[94m",  # Blue
        OutputLevel.SUCCESS: "\033[92m",  # Green
        OutputLevel.WARNING: "\033[93m",  # Yellow
        OutputLevel.ERROR: "\033[91m",  # Red
        OutputLevel.CRITICAL: "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    # Emoji prefixes for visual clarity
    EMOJIS = {
        OutputLevel.DEBUG: "🔍",
        OutputLevel.INFO: "ℹ️",
        OutputLevel.SUCCESS: "✅",
        OutputLevel.WARNING: "⚠️",
        OutputLevel.ERROR: "❌",
        OutputLevel.CRITICAL: "🔥",
    }

    def __init__(
        self,
        use_colors: bool = True,
        use_emojis: bool = True,
        json_output: bool = False,
    ):
        """
        Initialize console output handler

        Args:
            use_colors: Whether to use ANSI color codes
            use_emojis: Whether to use emoji prefixes
            json_output: Whether to output JSON instead of formatted text
        """
        self.use_colors = use_colors and sys.stdout.isatty()
        self.use_emojis = use_emojis
        self.json_output = json_output
        self.logger = logging.getLogger(__name__)

    def print(self, message: str, level: OutputLevel = OutputLevel.INFO, **kwargs):
        """
        Print a message with consistent formatting

        Args:
            message: The message to print
            level: The output level (info, success, warning, error, etc.)
            **kwargs: Additional context to include in JSON output
        """
        if self.json_output:
            self._print_json(message, level, **kwargs)
        else:
            self._print_formatted(message, level)

        # Also log to Python logger
        self._log_to_logger(message, level)

    def _print_formatted(self, message: str, level: OutputLevel):
        """Print formatted text output"""
        # Sanitize message to prevent credential leakage
        message = sanitize_for_logging(message)

        prefix = ""

        if self.use_emojis:
            prefix = f"{self.EMOJIS.get(level, '')} "

        if self.use_colors:
            color = self.COLORS.get(level, "")
            output = f"{color}{prefix}{message}{self.RESET}"
        else:
            output = f"{prefix}{message}"

        # Decide which stream to use
        stream = (
            sys.stderr
            if level in [OutputLevel.ERROR, OutputLevel.CRITICAL]
            else sys.stdout
        )
        print(output, file=stream)

    def _print_json(self, message: str, level: OutputLevel, **kwargs):
        """Print JSON output"""
        output = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.value,
            "message": message,
            **kwargs,
        }
        print(json.dumps(output), file=sys.stdout)

    def _log_to_logger(self, message: str, level: OutputLevel):
        """Log message to Python logger"""
        # Sanitize message before logging
        message = sanitize_for_logging(message)

        log_method = {
            OutputLevel.DEBUG: self.logger.debug,
            OutputLevel.INFO: self.logger.info,
            OutputLevel.SUCCESS: self.logger.info,
            OutputLevel.WARNING: self.logger.warning,
            OutputLevel.ERROR: self.logger.error,
            OutputLevel.CRITICAL: self.logger.critical,
        }.get(level, self.logger.info)

        log_method(message)

    def debug(self, message: str, **kwargs):
        """Print debug message"""
        self.print(message, OutputLevel.DEBUG, **kwargs)

    def info(self, message: str, **kwargs):
        """Print info message"""
        self.print(message, OutputLevel.INFO, **kwargs)

    def success(self, message: str, **kwargs):
        """Print success message"""
        self.print(message, OutputLevel.SUCCESS, **kwargs)

    def warning(self, message: str, **kwargs):
        """Print warning message"""
        self.print(message, OutputLevel.WARNING, **kwargs)

    def error(self, message: str, **kwargs):
        """Print error message"""
        self.print(message, OutputLevel.ERROR, **kwargs)

    def critical(self, message: str, **kwargs):
        """Print critical message"""
        self.print(message, OutputLevel.CRITICAL, **kwargs)

    def json(self, data: Any, indent: int = 2):
        """
        Print data as formatted JSON

        Args:
            data: Data to print as JSON
            indent: Number of spaces for indentation
        """
        if self.json_output:
            # Already in JSON mode, just print the data
            print(json.dumps(data), file=sys.stdout)
        else:
            # Pretty print JSON
            print(json.dumps(data, indent=indent), file=sys.stdout)

    def table(self, headers: list, rows: list, title: Optional[str] = None):
        """
        Print data as a formatted table

        Args:
            headers: List of column headers
            rows: List of row data (each row is a list)
            title: Optional table title
        """
        if self.json_output:
            # Output as JSON array of objects
            data = [dict(zip(headers, row)) for row in rows]
            if title:
                self.json({"title": title, "data": data})
            else:
                self.json(data)
        else:
            # Calculate column widths
            widths = [len(h) for h in headers]
            for row in rows:
                for i, cell in enumerate(row):
                    widths[i] = max(widths[i], len(str(cell)))

            # Print title if provided
            if title:
                total_width = sum(widths) + (len(headers) - 1) * 3 + 4
                self.info("=" * total_width)
                self.info(title.center(total_width))
                self.info("=" * total_width)

            # Print headers
            header_row = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
            print(header_row)
            print("-" * len(header_row))

            # Print rows
            for row in rows:
                print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, widths)))

    def section(self, title: str):
        """
        Print a section header

        Args:
            title: Section title
        """
        if not self.json_output:
            print()
            self.info("=" * 60)
            self.info(f"  {title}")
            self.info("=" * 60)

    def progress(self, current: int, total: int, message: str = ""):
        """
        Print progress indicator

        Args:
            current: Current progress value
            total: Total expected value
            message: Optional message to display
        """
        if self.json_output:
            self._print_json(
                message or "Progress",
                OutputLevel.INFO,
                current=current,
                total=total,
                percent=round(100 * current / total, 1),
            )
        else:
            percent = 100 * current / total
            bar_length = 40
            filled = int(bar_length * current / total)
            bar = "█" * filled + "░" * (bar_length - filled)
            output = f"\r{bar} {percent:.1f}% ({current}/{total})"
            if message:
                output += f" - {message}"
            print(output, end="", file=sys.stdout, flush=True)
            if current >= total:
                print()  # New line when complete


# Global instance for convenience
_console = None


def get_console(json_output: bool = False) -> ConsoleOutput:
    """
    Get the global console output instance

    Args:
        json_output: Whether to enable JSON output mode

    Returns:
        ConsoleOutput instance
    """
    global _console
    if _console is None:
        _console = ConsoleOutput(json_output=json_output)
    return _console


# Convenience functions
def console_print(message: str, level: str = "info", **kwargs):
    """
    Quick console print function

    Args:
        message: Message to print
        level: Output level (info, success, warning, error)
        **kwargs: Additional context
    """
    console = get_console()
    level_enum = OutputLevel(level) if isinstance(level, str) else level
    console.print(message, level_enum, **kwargs)


def console_info(message: str, **kwargs):
    """Print info message"""
    get_console().info(message, **kwargs)


def console_success(message: str, **kwargs):
    """Print success message"""
    get_console().success(message, **kwargs)


def console_warning(message: str, **kwargs):
    """Print warning message"""
    get_console().warning(message, **kwargs)


def console_error(message: str, **kwargs):
    """Print error message"""
    get_console().error(message, **kwargs)


def console_json(data: Any, indent: int = 2):
    """Print JSON data"""
    get_console().json(data, indent)


def console_table(headers: list, rows: list, title: Optional[str] = None):
    """Print table"""
    get_console().table(headers, rows, title)


def console_section(title: str):
    """Print section header"""
    get_console().section(title)


# Example usage
if __name__ == "__main__":
    # Demonstrate different output styles
    console = ConsoleOutput()

    console.section("Console Output Examples")

    console.debug("This is a debug message")
    console.info("This is an info message")
    console.success("This is a success message")
    console.warning("This is a warning message")
    console.error("This is an error message")
    console.critical("This is a critical message")

    console.section("JSON Output")
    console.json(
        {"deployment": "fabric-prod", "status": "success", "duration_seconds": 45.2}
    )

    console.section("Table Output")
    console.table(
        headers=["Environment", "Status", "Last Deploy"],
        rows=[
            ["dev", "✅ Active", "2025-10-10 10:30"],
            ["test", "✅ Active", "2025-10-10 09:15"],
            ["prod", "✅ Active", "2025-10-09 14:00"],
        ],
        title="Deployment Status",
    )

    console.section("Progress Indicator")
    import time

    for i in range(1, 11):
        console.progress(i, 10, f"Processing item {i}")
        time.sleep(0.2)
