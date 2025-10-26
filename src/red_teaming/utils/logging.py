# SPDX-License-Identifier: MPL-2.0

"""Structured logging configuration for the red-teaming harness."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Iterator

import structlog

_TRACE_ID: ContextVar[str | None] = ContextVar("trace_id", default=None)
_CONFIGURED = False

def _add_trace_id(
    _: structlog.typing.WrappedLogger,
    __: str,
    event_dict: structlog.typing.EventDict,
) -> structlog.typing.EventDict:
    trace_id = _TRACE_ID.get()
    if trace_id:
        event_dict.setdefault("trace_id", trace_id)
    return event_dict

def bind_context(*, trace_id: str | None = None, **context: Any) -> None:
    """Bind contextual information that is propagated through all log entries."""
    if trace_id is not None:
        _TRACE_ID.set(trace_id)
        context.setdefault("trace_id", trace_id)
    if context:
        structlog.contextvars.bind_contextvars(**context)

def clear_context() -> None:
    """Reset bound context for subsequent log statements."""
    structlog.contextvars.clear_contextvars()
    _TRACE_ID.set(None)

@contextmanager
def tracing_context(trace_id: str, **context: Any) -> Iterator[None]:
    """Context manager that binds and clears trace context automatically."""
    token = _TRACE_ID.set(trace_id)
    try:
        bind_context(trace_id=trace_id, **context)
        yield
    finally:
        _TRACE_ID.reset(token)
        clear_context()

def setup_logging(level: int = logging.INFO) -> None:
    """Configure structlog once for the entire process."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp")

    processor_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            _add_trace_id,
            structlog.stdlib.add_log_level,
            timestamper,
        ],
        processor=structlog.processors.JSONRenderer(),
    )

    handler = logging.StreamHandler()
    handler.setFormatter(processor_formatter)

    logging.basicConfig(level=level, handlers=[handler], force=True)

    structlog.configure(
        context_class=dict,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_trace_id,
            structlog.stdlib.add_log_level,
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.EventRenamer("message"),
            structlog.processors.JSONRenderer(),
        ],
    )

    _CONFIGURED = True

def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structured logger with optional name."""
    setup_logging()
    if name is None:
        return structlog.get_logger()
    return structlog.get_logger(name)

__all__ = [
    "bind_context",
    "clear_context",
    "get_logger",
    "setup_logging",
    "tracing_context",
]
