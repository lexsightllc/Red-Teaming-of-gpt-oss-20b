import os
import requests
import logging

class LLMAPIClient:
    """
    A unified client for interacting with various LLM APIs.
    This abstracts away model provider specific calls.
    """
    def __init__(self, model_config):
        self.model_name = model_config.get("name", "unknown_model")
        self.api_endpoint = model_config.get("api_endpoint")
        
        # Prefer explicit api_key from model_config for testability; fall back to env
        self.api_key = model_config.get("api_key") or os.getenv("LLM_API_KEY")
        
        if not self.api_key:
            error_msg = "API key not set. Provide 'api_key' in model config or set LLM_API_KEY env var."
            logging.error(error_msg)
            raise ValueError(error_msg)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logging.info(f"Initialized LLMAPIClient for model: {self.model_name}")

    def query(self, prompt, temperature=0.7, max_tokens=150, **kwargs):
        """
        Sends a query to the LLM API and returns the response.
        Handles basic API interaction, error logging.
        """
        if not self.api_endpoint:
            logging.error("API endpoint not configured for LLMAPIClient.")
            raise ValueError("API endpoint not set.")

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        try:
            response = requests.post(self.api_endpoint, headers=self.headers, json=payload)
            response.raise_for_status() # Raise an exception for HTTP errors
            return response.json().get('choices', [{}])[0].get('text', '').strip()
        except requests.exceptions.HTTPError as e:
            # Preserve error message semantics for unit tests expecting HTTP error text
            status = getattr(e.response, "status_code", None)
            text = getattr(e.response, "text", "")
            if status is not None and text:
                msg = f"Error: {status} Server Error: {text}"
            else:
                msg = f"Error: {e}"
            logging.error(f"HTTP error querying LLM API ({self.model_name}): {msg}")
            return msg
        except requests.exceptions.RequestException as e:
            # Non-HTTP issues (e.g., connection errors): return explicit error string (unit tests expect this)
            logging.error(f"Request error querying LLM API ({self.model_name}): {e}")
            return f"Error: {e}"
        except Exception as e:
            logging.error(f"Unexpected error in LLMAPIClient: {e}")
            return f"Error: {e}"

    def get_internal_activations(self, prompt):
        """
        Placeholder for retrieving internal model activations.
        This would require specific API support or direct model access. (Point 1, Point 5)
        """
        logging.warning("Internal activations retrieval not implemented for generic client. Requires specific model API support.")
        return {}
