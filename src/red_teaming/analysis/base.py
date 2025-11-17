# SPDX-License-Identifier: MPL-2.0

"""Base class for analysis modules.

This module provides a standard interface and common functionality for all
analysis modules in the red-teaming platform. All analysis modules should
inherit from AnalysisModule and implement the required abstract methods.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel

from red_teaming.errors import AnalysisModuleError, AnalysisValidationError


class AnalysisResult(BaseModel):
    """Base class for analysis results.

    All analysis modules should return results that conform to this schema
    to ensure consistency across the platform.

    Attributes:
        module_name: Name of the analysis module
        module_version: Version of the analysis module
        timestamp: ISO 8601 timestamp of analysis execution
        status: Status of analysis (success, failure, partial)
        findings: List of findings/vulnerabilities detected
        metrics: Dictionary of computed metrics
        errors: List of errors encountered (if any)
        execution_time_seconds: Total execution time in seconds
    """

    module_name: str
    module_version: str
    timestamp: str
    status: str  # 'success', 'failure', 'partial'
    findings: list[Dict[str, Any]] = []
    metrics: Dict[str, Any] = {}
    errors: list[str] = []
    execution_time_seconds: float


class AnalysisModule(ABC):
    """Abstract base class for all analysis modules.

    Analysis modules analyze model outputs for specific vulnerability classes.
    Each module should:

    1. Validate input data on initialization
    2. Execute analysis in the run() method
    3. Return standardized results via AnalysisResult
    4. Handle errors gracefully with proper logging
    5. Support configuration via YAML/Pydantic models
    """

    # Class attributes (override in subclasses)
    MODULE_NAME = "analysis_module"
    MODULE_VERSION = "1.0.0"
    DESCRIPTION = "Base analysis module"

    def __init__(
        self,
        module_name: str | None = None,
        logger: logging.Logger | None = None,
        config: BaseModel | None = None,
    ) -> None:
        """Initialize the analysis module.

        Args:
            module_name: Human-readable module name (overrides CLASS attribute)
            logger: Logger instance (default: module logger)
            config: Configuration object (subclass-specific)

        Raises:
            AnalysisModuleError: If initialization fails
        """
        self.module_name = module_name or self.MODULE_NAME
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.config = config

        try:
            self._validate_initialization()
        except Exception as e:
            msg = f"Analysis module initialization failed: {e}"
            raise AnalysisModuleError(msg) from e

    def _validate_initialization(self) -> None:
        """Validate module initialization.

        Override this method in subclasses to add custom validation logic.

        Raises:
            AnalysisValidationError: If validation fails
        """
        pass

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> AnalysisResult:
        """Execute the analysis module.

        Subclasses must implement this method to perform the actual analysis.

        Args:
            input_data: Dictionary containing input data for analysis.
                       Keys and values are module-specific.

        Returns:
            AnalysisResult object containing analysis findings and metrics

        Raises:
            AnalysisValidationError: If input validation fails
            AnalysisModuleError: If analysis execution fails
        """
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data.

        Override this method in subclasses to add custom input validation.

        Args:
            input_data: Input data to validate

        Raises:
            AnalysisValidationError: If validation fails
        """
        if not isinstance(input_data, dict):
            msg = "Input data must be a dictionary"
            raise AnalysisValidationError(msg)

    def validate_output(self, result: AnalysisResult) -> None:
        """Validate output data.

        Override this method in subclasses to add custom output validation.

        Args:
            result: Analysis result to validate

        Raises:
            AnalysisValidationError: If validation fails
        """
        if not isinstance(result, AnalysisResult):
            msg = "Result must be an AnalysisResult instance"
            raise AnalysisValidationError(msg)

        if result.module_name != self.module_name:
            msg = f"Module name mismatch: {result.module_name} != {self.module_name}"
            raise AnalysisValidationError(msg)

        if result.status not in ("success", "failure", "partial"):
            msg = f"Invalid status: {result.status}"
            raise AnalysisValidationError(msg)

    def _log_execution(
        self, status: str, duration: float, error: Optional[Exception] = None
    ) -> None:
        """Log module execution.

        Args:
            status: Execution status
            duration: Execution duration in seconds
            error: Optional exception that was raised
        """
        if error:
            self.logger.error(
                f"Module execution failed: {self.module_name}",
                extra={"duration": duration, "error": str(error)},
            )
        else:
            self.logger.info(
                f"Module execution completed: {self.module_name}",
                extra={"duration": duration, "status": status},
            )

    def export_result(
        self, result: AnalysisResult, output_path: str | Path
    ) -> None:
        """Export analysis result to file.

        Args:
            result: Analysis result to export
            output_path: Path to write the result

        Raises:
            IOError: If file write fails
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(result.model_dump(), f, indent=2, default=str)

        self.logger.info(f"Result exported to {output_path}")

    def get_metadata(self) -> Dict[str, Any]:
        """Get module metadata.

        Returns:
            Dictionary containing module metadata
        """
        return {
            "module_name": self.module_name,
            "module_version": self.MODULE_VERSION,
            "description": self.DESCRIPTION,
            "has_config": self.config is not None,
        }

    def __repr__(self) -> str:
        """Return string representation of module."""
        return f"{self.__class__.__name__}(name={self.module_name!r})"
