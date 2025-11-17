# SPDX-License-Identifier: MPL-2.0

"""Centralized sensitive data redaction pattern registry.

This module provides a single, auditable registry of patterns for redacting
sensitive information from logs, outputs, and reports. All redaction operations
in the platform should use patterns from this registry to ensure consistency
and security.
"""

import logging
import re
from typing import Optional, Set

from red_teaming.errors import RedTeamingError


class RedactionPatternError(RedTeamingError):
    """Raised when redaction pattern operations fail."""

    pass


class RedactionPattern:
    """Represents a single redaction pattern.

    Attributes:
        name: Name of the pattern (e.g., 'api_key')
        pattern: Regular expression to match sensitive data
        replacement: Replacement text (default: '[REDACTED]')
        severity: Severity level ('low', 'medium', 'high', 'critical')
        description: Description of what this pattern redacts
    """

    def __init__(
        self,
        name: str,
        pattern: str,
        replacement: str = "[REDACTED]",
        severity: str = "high",
        description: str = "",
    ) -> None:
        """Initialize a redaction pattern.

        Args:
            name: Pattern name
            pattern: Regex pattern to match
            replacement: Text to use as replacement
            severity: Severity level
            description: Pattern description

        Raises:
            RedactionPatternError: If pattern compilation fails
        """
        self.name = name
        self.pattern_str = pattern
        self.replacement = replacement
        self.severity = severity
        self.description = description

        try:
            self.compiled_pattern = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            msg = f"Invalid regex pattern '{name}': {e}"
            raise RedactionPatternError(msg) from e

    def redact(self, text: str) -> tuple[str, int]:
        """Redact sensitive data from text.

        Args:
            text: Text to redact

        Returns:
            Tuple of (redacted_text, number_of_replacements)
        """
        original_text = text
        redacted_text, count = self.compiled_pattern.subn(self.replacement, text)
        return redacted_text, count

    def __repr__(self) -> str:
        """Return string representation."""
        return f"RedactionPattern(name={self.name!r}, severity={self.severity!r})"


class SensitivePatternRegistry:
    """Centralized registry for sensitive data redaction patterns.

    This class maintains a curated set of patterns for redacting common sensitive
    information types. Patterns are organized by severity and category.
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """Initialize the pattern registry.

        Args:
            logger: Logger for audit trail
        """
        self.logger = logger or logging.getLogger(__name__)
        self._patterns: dict[str, RedactionPattern] = {}
        self._audit_log: list[str] = []

        # Register default patterns
        self._register_default_patterns()

    def _register_default_patterns(self) -> None:
        """Register default sensitive data patterns."""
        # API Keys and Tokens
        self.register(
            RedactionPattern(
                "openai_api_key",
                r"sk-[A-Za-z0-9\-_]{20,}",
                severity="critical",
                description="OpenAI API key",
            )
        )

        self.register(
            RedactionPattern(
                "anthropic_api_key",
                r"sk-ant-[A-Za-z0-9\-_]{32,}",
                severity="critical",
                description="Anthropic API key",
            )
        )

        self.register(
            RedactionPattern(
                "generic_api_key",
                r"(?i)api[_-]?key\s*=\s*[^\s,;]+",
                severity="critical",
                description="Generic API key pattern",
            )
        )

        self.register(
            RedactionPattern(
                "bearer_token",
                r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*",
                severity="critical",
                description="Bearer token",
            )
        )

        # AWS credentials
        self.register(
            RedactionPattern(
                "aws_access_key",
                r"(?i)AKIA[0-9A-Z]{16}",
                severity="critical",
                description="AWS Access Key ID",
            )
        )

        self.register(
            RedactionPattern(
                "aws_secret_key",
                r"(?i)aws_secret_access_key\s*=\s*[^\s,;]+",
                severity="critical",
                description="AWS Secret Access Key",
            )
        )

        # Passwords and secrets
        self.register(
            RedactionPattern(
                "password_field",
                r"(?i)password\s*[:=]\s*[^\s,;]+",
                severity="critical",
                description="Password field assignments",
            )
        )

        self.register(
            RedactionPattern(
                "secret_field",
                r"(?i)secret\s*[:=]\s*[^\s,;]+",
                severity="critical",
                description="Secret field assignments",
            )
        )

        # PII - Email addresses
        self.register(
            RedactionPattern(
                "email_address",
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                severity="high",
                description="Email addresses",
            )
        )

        # PII - Phone numbers
        self.register(
            RedactionPattern(
                "phone_number",
                r"(?:\+?1[-.\s]?)?(?:\([0-9]{3}\)|[0-9]{3})[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}",
                severity="high",
                description="Phone numbers",
            )
        )

        # PII - Social Security Numbers
        self.register(
            RedactionPattern(
                "ssn",
                r"\b(?!000|666|9)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b",
                severity="critical",
                description="Social Security Numbers",
            )
        )

        # PII - Credit card numbers
        self.register(
            RedactionPattern(
                "credit_card",
                r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
                severity="critical",
                description="Credit card numbers",
            )
        )

        # URLs with credentials
        self.register(
            RedactionPattern(
                "url_with_credentials",
                r"(?:https?://)[^\s:]+:[^\s@]+@[^\s/]+",
                severity="critical",
                description="URLs containing credentials",
            )
        )

        # Database connection strings
        self.register(
            RedactionPattern(
                "db_connection_string",
                r"(?i)(?:mysql|postgresql|mongodb|sqlite)://[^\s]+",
                severity="critical",
                description="Database connection strings",
            )
        )

        # JWT tokens
        self.register(
            RedactionPattern(
                "jwt_token",
                r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
                severity="high",
                description="JWT tokens",
            )
        )

        # IPv4 addresses (medium severity - can be PII in some contexts)
        self.register(
            RedactionPattern(
                "ipv4_address",
                r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
                severity="medium",
                description="IPv4 addresses",
            )
        )

        # Authorization headers
        self.register(
            RedactionPattern(
                "authorization_header",
                r"(?i)authorization\s*[:=]\s*[^\s\r\n]+",
                severity="high",
                description="Authorization headers",
            )
        )

    def register(self, pattern: RedactionPattern) -> None:
        """Register a redaction pattern.

        Args:
            pattern: RedactionPattern instance to register

        Raises:
            RedactionPatternError: If pattern name already exists
        """
        if pattern.name in self._patterns:
            msg = f"Pattern '{pattern.name}' already registered"
            raise RedactionPatternError(msg)

        self._patterns[pattern.name] = pattern
        self._audit_log.append(f"Registered pattern: {pattern.name} ({pattern.severity})")
        self.logger.debug(f"Registered pattern: {pattern.name}")

    def unregister(self, pattern_name: str) -> None:
        """Unregister a redaction pattern.

        Args:
            pattern_name: Name of pattern to unregister

        Raises:
            RedactionPatternError: If pattern not found
        """
        if pattern_name not in self._patterns:
            msg = f"Pattern '{pattern_name}' not found"
            raise RedactionPatternError(msg)

        del self._patterns[pattern_name]
        self._audit_log.append(f"Unregistered pattern: {pattern_name}")
        self.logger.debug(f"Unregistered pattern: {pattern_name}")

    def get_pattern(self, pattern_name: str) -> Optional[RedactionPattern]:
        """Get a specific pattern by name.

        Args:
            pattern_name: Name of pattern to retrieve

        Returns:
            RedactionPattern or None if not found
        """
        return self._patterns.get(pattern_name)

    def list_patterns(self, severity: Optional[str] = None) -> list[str]:
        """List all registered patterns.

        Args:
            severity: Optional severity filter ('low', 'medium', 'high', 'critical')

        Returns:
            List of pattern names
        """
        if severity is None:
            return list(self._patterns.keys())

        return [
            name
            for name, pattern in self._patterns.items()
            if pattern.severity == severity
        ]

    def redact(self, text: str, pattern_names: Optional[Set[str]] = None) -> str:
        """Redact sensitive data using registered patterns.

        Args:
            text: Text to redact
            pattern_names: Optional set of specific patterns to apply.
                          If None, applies all patterns.

        Returns:
            Redacted text

        Raises:
            RedactionPatternError: If specified pattern not found
        """
        if not pattern_names:
            pattern_names = set(self._patterns.keys())

        redacted_text = text
        redaction_counts: dict[str, int] = {}

        for pattern_name in pattern_names:
            if pattern_name not in self._patterns:
                msg = f"Pattern '{pattern_name}' not found"
                raise RedactionPatternError(msg)

            pattern = self._patterns[pattern_name]
            redacted_text, count = pattern.redact(redacted_text)
            if count > 0:
                redaction_counts[pattern_name] = count

        # Log redactions at debug level for audit trail
        if redaction_counts:
            self.logger.debug(
                f"Redacted sensitive data",
                extra={"patterns": redaction_counts},
            )
            self._audit_log.append(f"Redacted data: {redaction_counts}")

        return redacted_text

    def redact_dict(
        self, data: dict, pattern_names: Optional[Set[str]] = None
    ) -> dict:
        """Redact sensitive data from dictionary values.

        Args:
            data: Dictionary to redact (modified in-place)
            pattern_names: Optional set of specific patterns to apply

        Returns:
            Redacted dictionary
        """
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = self.redact(value, pattern_names)
            elif isinstance(value, dict):
                data[key] = self.redact_dict(value, pattern_names)
            elif isinstance(value, list):
                data[key] = [
                    self.redact(item, pattern_names) if isinstance(item, str) else item
                    for item in value
                ]

        return data

    def get_audit_log(self) -> list[str]:
        """Get the redaction audit log.

        Returns:
            List of audit log entries
        """
        return self._audit_log.copy()

    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        self._audit_log.clear()


# Global registry instance
_global_registry: Optional[SensitivePatternRegistry] = None


def get_global_registry(
    logger: Optional[logging.Logger] = None,
) -> SensitivePatternRegistry:
    """Get the global sensitive pattern registry (lazy singleton).

    Args:
        logger: Optional logger for the registry

    Returns:
        Global SensitivePatternRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = SensitivePatternRegistry(logger)
    return _global_registry


def redact_text(text: str, pattern_names: Optional[Set[str]] = None) -> str:
    """Convenience function to redact text using the global registry.

    Args:
        text: Text to redact
        pattern_names: Optional set of specific patterns to apply

    Returns:
        Redacted text
    """
    registry = get_global_registry()
    return registry.redact(text, pattern_names)


def redact_dict(
    data: dict, pattern_names: Optional[Set[str]] = None
) -> dict:
    """Convenience function to redact dictionary using the global registry.

    Args:
        data: Dictionary to redact
        pattern_names: Optional set of specific patterns to apply

    Returns:
        Redacted dictionary
    """
    registry = get_global_registry()
    return registry.redact_dict(data, pattern_names)
