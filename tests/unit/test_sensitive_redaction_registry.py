# SPDX-License-Identifier: MPL-2.0

"""Unit tests for sensitive data redaction functionality."""

import logging

import pytest

from red_teaming.reproducibility.redaction_registry import (
    RedactionPattern,
    RedactionPatternError,
    SensitivePatternRegistry,
    get_global_registry,
    redact_dict,
    redact_text,
)


class TestRedactionPattern:
    """Test RedactionPattern class."""

    def test_create_valid_pattern(self) -> None:
        """Test creating a valid redaction pattern."""
        pattern = RedactionPattern(
            name="test_api_key",
            pattern=r"api_key=\w+",
            replacement="[REDACTED]",
            severity="critical",
            description="Test API key",
        )

        assert pattern.name == "test_api_key"
        assert pattern.severity == "critical"
        assert pattern.compiled_pattern is not None

    def test_invalid_regex_pattern(self) -> None:
        """Test that invalid regex raises error."""
        with pytest.raises(RedactionPatternError, match="Invalid regex pattern"):
            RedactionPattern(
                name="bad_pattern",
                pattern="[invalid(regex",  # Invalid regex
            )

    def test_redact_with_pattern(self) -> None:
        """Test redacting text with a pattern."""
        pattern = RedactionPattern(
            name="api_key",
            pattern=r"api_key=\w+",
        )

        text = "api_key=secret123 and api_key=secret456"
        redacted, count = pattern.redact(text)

        assert "[REDACTED]" in redacted
        assert count == 2
        assert "secret123" not in redacted

    def test_redact_no_matches(self) -> None:
        """Test redacting text with no matches."""
        pattern = RedactionPattern(
            name="api_key",
            pattern=r"api_key=\w+",
        )

        text = "no secrets here"
        redacted, count = pattern.redact(text)

        assert redacted == text
        assert count == 0

    def test_case_insensitive_redaction(self) -> None:
        """Test that redaction is case-insensitive."""
        pattern = RedactionPattern(
            name="password",
            pattern=r"(?i)password\s*=\s*[^\s,;]+",
        )

        text = "PASSWORD=secret123 and password=secret456"
        redacted, count = pattern.redact(text)

        assert count == 2
        assert "[REDACTED]" in redacted


class TestSensitivePatternRegistry:
    """Test SensitivePatternRegistry class."""

    def test_create_registry(self) -> None:
        """Test creating a new registry."""
        registry = SensitivePatternRegistry()
        assert registry is not None
        assert len(registry.list_patterns()) > 0

    def test_register_pattern(self) -> None:
        """Test registering a new pattern."""
        registry = SensitivePatternRegistry()
        initial_count = len(registry.list_patterns())

        new_pattern = RedactionPattern(
            name="custom_secret",
            pattern=r"custom_secret=\w+",
        )
        registry.register(new_pattern)

        assert len(registry.list_patterns()) == initial_count + 1
        assert "custom_secret" in registry.list_patterns()

    def test_register_duplicate_pattern(self) -> None:
        """Test that registering duplicate pattern raises error."""
        registry = SensitivePatternRegistry()

        with pytest.raises(RedactionPatternError, match="already registered"):
            # Try to register a pattern that already exists
            registry.register(registry.get_pattern("openai_api_key"))

    def test_unregister_pattern(self) -> None:
        """Test unregistering a pattern."""
        registry = SensitivePatternRegistry()
        patterns_before = len(registry.list_patterns())

        registry.unregister("openai_api_key")
        patterns_after = len(registry.list_patterns())

        assert patterns_after == patterns_before - 1
        assert "openai_api_key" not in registry.list_patterns()

    def test_unregister_nonexistent_pattern(self) -> None:
        """Test that unregistering nonexistent pattern raises error."""
        registry = SensitivePatternRegistry()

        with pytest.raises(RedactionPatternError, match="not found"):
            registry.unregister("nonexistent_pattern")

    def test_get_pattern(self) -> None:
        """Test retrieving a pattern."""
        registry = SensitivePatternRegistry()
        pattern = registry.get_pattern("openai_api_key")

        assert pattern is not None
        assert pattern.name == "openai_api_key"

    def test_get_nonexistent_pattern(self) -> None:
        """Test retrieving nonexistent pattern returns None."""
        registry = SensitivePatternRegistry()
        pattern = registry.get_pattern("nonexistent")

        assert pattern is None

    def test_list_patterns_all(self) -> None:
        """Test listing all patterns."""
        registry = SensitivePatternRegistry()
        patterns = registry.list_patterns()

        assert len(patterns) > 0
        assert isinstance(patterns, list)

    def test_list_patterns_by_severity(self) -> None:
        """Test listing patterns filtered by severity."""
        registry = SensitivePatternRegistry()
        critical = registry.list_patterns("critical")
        high = registry.list_patterns("high")

        assert len(critical) > 0
        assert len(high) > 0
        assert all(
            registry.get_pattern(p).severity == "critical" for p in critical
        )

    def test_redact_text_multiple_patterns(self) -> None:
        """Test redacting text with multiple patterns."""
        registry = SensitivePatternRegistry()

        text = "api_key=sk-abc123 and email=test@example.com"
        redacted = registry.redact(text)

        assert "[REDACTED]" in redacted
        # Note: generic patterns might match different strings

    def test_redact_dict(self) -> None:
        """Test redacting dictionary values."""
        registry = SensitivePatternRegistry()

        data = {
            "api_key": "sk-abc123",
            "user": {
                "name": "John Doe",
            },
        }

        redacted = registry.redact_dict(data)

        assert isinstance(redacted, dict)
        assert "sk-abc123" not in str(redacted)

    def test_audit_log(self) -> None:
        """Test audit log functionality."""
        registry = SensitivePatternRegistry()

        # Clear audit log
        registry.clear_audit_log()
        assert len(registry.get_audit_log()) == 0

        # Register a pattern
        new_pattern = RedactionPattern(
            name="test_pattern",
            pattern=r"test=\w+",
        )
        registry.register(new_pattern)

        # Check audit log has entries
        audit_log = registry.get_audit_log()
        assert len(audit_log) > 0

    def test_redact_openai_api_key(self) -> None:
        """Test redacting OpenAI API key."""
        registry = SensitivePatternRegistry()

        text = "My API key is sk-abcdefghijklmnopqrst1234567890"
        redacted = registry.redact(text)

        assert "[REDACTED]" in redacted
        assert "sk-abcdefghijklmnopqrst" not in redacted

    def test_redact_anthropic_api_key(self) -> None:
        """Test redacting Anthropic API key."""
        registry = SensitivePatternRegistry()

        text = "API key: sk-ant-abcdefghijklmnopqrstuvwxyz123456"
        redacted = registry.redact(text)

        assert "[REDACTED]" in redacted
        assert "sk-ant-" not in redacted

    def test_redact_email_address(self) -> None:
        """Test redacting email addresses."""
        registry = SensitivePatternRegistry()

        text = "Contact me at john.doe@example.com for details"
        redacted = registry.redact(text)

        assert "[REDACTED]" in redacted
        assert "john.doe@example.com" not in redacted

    def test_redact_jwt_token(self) -> None:
        """Test redacting JWT tokens."""
        registry = SensitivePatternRegistry()

        text = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        redacted = registry.redact(text)

        assert "[REDACTED]" in redacted
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in redacted


class TestGlobalRegistry:
    """Test global registry singleton."""

    def test_get_global_registry(self) -> None:
        """Test getting the global registry."""
        registry = get_global_registry()
        assert registry is not None
        assert isinstance(registry, SensitivePatternRegistry)

    def test_global_registry_singleton(self) -> None:
        """Test that global registry is a singleton."""
        registry1 = get_global_registry()
        registry2 = get_global_registry()

        assert registry1 is registry2

    def test_redact_text_convenience_function(self) -> None:
        """Test convenience redact_text function."""
        text = "API key: sk-abcdefghijklmnopqrst1234567890"
        redacted = redact_text(text)

        assert "[REDACTED]" in redacted
        assert "sk-abcdefghijklmnopqrst" not in redacted

    def test_redact_dict_convenience_function(self) -> None:
        """Test convenience redact_dict function."""
        data = {
            "api_key": "sk-abc123",
            "user_email": "test@example.com",
        }

        redacted = redact_dict(data)

        assert "[REDACTED]" in str(redacted)
        assert "sk-abc123" not in str(redacted)
