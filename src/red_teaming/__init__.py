# SPDX-License-Identifier: MPL-2.0

"""Core package initialisation for the red-teaming harness."""

from red_teaming.errors import (
    AnalysisError,
    APIError,
    ComplianceError,
    ConfigurationError,
    ControlError,
    DataError,
    DisclosureError,
    ExecutionError,
    PrivacyError,
    RedTeamingError,
    ReportingError,
    ReproducibilityError,
)
from red_teaming.utils.logging import setup_logging

setup_logging()

__all__ = [
    "setup_logging",
    "RedTeamingError",
    "ConfigurationError",
    "AnalysisError",
    "APIError",
    "ReproducibilityError",
    "ReportingError",
    "DataError",
    "ControlError",
    "DisclosureError",
    "PrivacyError",
    "ComplianceError",
    "ExecutionError",
]
