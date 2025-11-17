# SPDX-License-Identifier: MPL-2.0

"""Custom exception classes and error handling utilities.

This module defines a comprehensive exception hierarchy for the red-teaming platform.
All custom exceptions inherit from RedTeamingError and are organized by domain.
"""


class RedTeamingError(Exception):
    """Base exception for all red-teaming platform errors.

    All custom exceptions in this platform inherit from this class to enable
    generic catching and handling of platform-specific errors.
    """

    def __init__(self, message: str, error_code: str | None = None) -> None:
        """Initialize RedTeamingError.

        Args:
            message: Error message
            error_code: Optional error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


# Configuration errors


class ConfigurationError(RedTeamingError):
    """Raised when configuration is invalid or missing.

    This is the base class for all configuration-related errors.
    """

    pass


class ConfigFileNotFoundError(ConfigurationError):
    """Raised when a configuration file cannot be found."""

    pass


class ConfigValidationError(ConfigurationError):
    """Raised when configuration validation fails.

    This typically occurs when YAML config doesn't match Pydantic schema.
    """

    pass


class ConfigParseError(ConfigurationError):
    """Raised when configuration file cannot be parsed.

    This occurs for invalid YAML, JSON, or other format issues.
    """

    pass


# Analysis errors


class AnalysisError(RedTeamingError):
    """Base class for analysis-related errors."""

    pass


class AnalysisModuleError(AnalysisError):
    """Raised when an analysis module fails to initialize or execute."""

    pass


class AnalysisTimeout(AnalysisError):
    """Raised when an analysis module exceeds its time limit."""

    pass


class AnalysisValidationError(AnalysisError):
    """Raised when analysis input/output validation fails."""

    pass


# API client errors


class APIError(RedTeamingError):
    """Base class for API-related errors."""

    pass


class APIConnectionError(APIError):
    """Raised when API connection fails."""

    pass


class APIAuthenticationError(APIError):
    """Raised when API authentication fails."""

    pass


class APIRateLimitError(APIError):
    """Raised when API rate limit is exceeded."""

    pass


class APITimeoutError(APIError):
    """Raised when API request times out."""

    pass


class APIUnexpectedResponseError(APIError):
    """Raised when API returns unexpected response format."""

    pass


# Reproducibility errors


class ReproducibilityError(RedTeamingError):
    """Base class for reproducibility-related errors."""

    pass


class TamperDetectionError(ReproducibilityError):
    """Raised when tamper detection identifies a discrepancy."""

    pass


class NonDeterminismError(ReproducibilityError):
    """Raised when non-determinism is detected where determinism is required."""

    pass


class RandomSeedError(ReproducibilityError):
    """Raised when random seed initialization fails."""

    pass


# Ethics and compliance errors


class EthicsError(RedTeamingError):
    """Base class for ethics and compliance related errors."""

    pass


class DisclosureError(EthicsError):
    """Raised when vulnerability disclosure fails."""

    pass


class PrivacyError(EthicsError):
    """Raised when privacy requirements are violated."""

    pass


class ComplianceError(EthicsError):
    """Raised when compliance requirements are not met."""

    pass


# Reporting errors


class ReportingError(RedTeamingError):
    """Base class for reporting-related errors."""

    pass


class ReportGenerationError(ReportingError):
    """Raised when report generation fails."""

    pass


class MetricsCalculationError(ReportingError):
    """Raised when metrics calculation fails."""

    pass


class ReportFormatError(ReportingError):
    """Raised when report format is invalid."""

    pass


# Data errors


class DataError(RedTeamingError):
    """Base class for data-related errors."""

    pass


class DataValidationError(DataError):
    """Raised when data validation fails."""

    pass


class DataLoadError(DataError):
    """Raised when data loading fails."""

    pass


class DataGenerationError(DataError):
    """Raised when synthetic data generation fails."""

    pass


# Control/Guard errors


class ControlError(RedTeamingError):
    """Base class for control/guard-related errors."""

    pass


class ComplexityGuardError(ControlError):
    """Raised when scenario complexity exceeds limits."""

    pass


class RiskGuardError(ControlError):
    """Raised when scenario risk exceeds limits."""

    pass


class ModerationGuardError(ControlError):
    """Raised when moderation requirements are violated."""

    pass


# Execution errors


class ExecutionError(RedTeamingError):
    """Base class for execution-related errors."""

    pass


class ScenarioExecutionError(ExecutionError):
    """Raised when scenario execution fails."""

    pass


class WorkflowExecutionError(ExecutionError):
    """Raised when workflow execution fails."""

    pass


class InvalidStateError(ExecutionError):
    """Raised when operation attempted in invalid state."""

    pass
