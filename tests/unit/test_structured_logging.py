# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

from structlog.testing import capture_logs

from red_teaming.utils import logging as structured_logging


def test_structured_logging_binds_trace_context() -> None:
    structured_logging.clear_context()
    with capture_logs() as logs:
        with structured_logging.tracing_context("trace-123", request_id="req-456"):
            logger = structured_logging.get_logger(__name__)
            logger.info("unit-test-event", extra_field="value")
    assert logs
    record = logs[0]
    assert record["trace_id"] == "trace-123"
    assert record["request_id"] == "req-456"
    assert record["event"] == "unit-test-event"
    assert record["extra_field"] == "value"


def test_clear_context_removes_previous_bindings() -> None:
    structured_logging.bind_context(trace_id="abc")
    structured_logging.clear_context()
    with capture_logs() as logs:
        structured_logging.get_logger(__name__).info("after-clear")
    assert logs
    assert "trace_id" not in logs[0]
