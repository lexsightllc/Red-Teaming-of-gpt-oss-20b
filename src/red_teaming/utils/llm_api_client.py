# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations

import os

from typing import Any, Mapping, MutableMapping
from uuid import uuid4

import requests

from red_teaming.utils.logging import get_logger, tracing_context


class LLMAPIClient:
    """Unified client for interacting with various LLM APIs."""

    def __init__(self, model_config: Mapping[str, Any]) -> None:
        self.model_name = model_config.get("name", "unknown_model")
        self.api_endpoint = model_config.get("api_endpoint")
        self.api_key = model_config.get("api_key") or os.getenv("LLM_API_KEY")
        self.logger = get_logger(__name__).bind(client_model=self.model_name)

        if not self.api_key:
            error_msg = (
                "API key not set. Provide 'api_key' in model config or set LLM_API_KEY env var."
            )
            self.logger.error("llm_api_client.initialisation_failed", reason="missing_api_key")
            raise ValueError(error_msg)

        self.headers: MutableMapping[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.logger.info(
            "llm_api_client.initialised",
            api_endpoint=self.api_endpoint,
            has_api_endpoint=bool(self.api_endpoint),
        )

    def query(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 150,
        *,
        trace_id: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Send a query to the LLM API and return the raw text response."""
        if not self.api_endpoint:
            self.logger.error("llm_api_client.query.misconfigured", reason="missing_endpoint")
            raise ValueError("API endpoint not set.")

        payload: dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        request_trace = trace_id or uuid4().hex
        with tracing_context(request_trace, prompt_preview=prompt[:64]):
            self.logger.info(
                "llm_api_client.query.started",
                temperature=temperature,
                max_tokens=max_tokens,
            )
            try:
                response = requests.post(self.api_endpoint, headers=self.headers, json=payload)
                response.raise_for_status()
            except requests.exceptions.HTTPError as exc:
                status = getattr(exc.response, "status_code", None)
                text = getattr(exc.response, "text", "")
                if status is not None and text:
                    message = f"Error: {status} Server Error: {text}"
                else:
                    message = f"Error: {exc}"
                self.logger.error(
                    "llm_api_client.query.http_error",
                    status=status,
                    response_text=text,
                )
                return message
            except requests.exceptions.RequestException as exc:
                self.logger.error("llm_api_client.query.request_error", error=str(exc))
                return f"Error: {exc}"
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.exception("llm_api_client.query.unexpected_error")
                return f"Error: {exc}"

            result = response.json().get("choices", [{}])[0].get("text", "").strip()
            self.logger.info(
                "llm_api_client.query.completed",
                response_length=len(result),
            )
            return result

    def get_internal_activations(self, prompt: str) -> dict[str, Any]:
        """Placeholder for retrieving internal model activations."""
        self.logger.warning("llm_api_client.internal_activations.unsupported")
        return {}
