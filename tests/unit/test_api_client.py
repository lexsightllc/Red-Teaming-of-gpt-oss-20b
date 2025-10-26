# SPDX-License-Identifier: MPL-2.0

import pytest
from red_teaming.utils.llm_api_client import LLMAPIClient
import requests_mock
import logging

# Suppress logging during tests to avoid clutter
logging.getLogger().setLevel(logging.CRITICAL)

@pytest.fixture
def mock_model_config():
    return {
        "name": "test_model",
        "api_endpoint": "http://mock-api.com/v1/chat/completions",
        "api_key": "mock_api_key"
    }

def test_client_initialization(mock_model_config):
    client = LLMAPIClient(mock_model_config)
    assert client.model_name == "test_model"
    assert client.api_endpoint == "http://mock-api.com/v1/chat/completions"
    assert client.api_key == "mock_api_key"
    assert "Authorization" in client.headers
    assert "Bearer mock_api_key" == client.headers["Authorization"]

def test_query_success(mock_model_config, requests_mock):
    client = LLMAPIClient(mock_model_config)
    requests_mock.post(mock_model_config["api_endpoint"], json={
        "choices": [{"text": "Hello, world!"}]
    }, status_code=200)

    response = client.query("test prompt")
    assert response == "Hello, world!"
    assert requests_mock.called
    assert requests_mock.last_request.json() == {
        "model": "test_model",
        "prompt": "test prompt",
        "temperature": 0.7,
        "max_tokens": 150
    }

def test_query_api_error(mock_model_config, requests_mock):
    client = LLMAPIClient(mock_model_config)
    requests_mock.post(mock_model_config["api_endpoint"], status_code=500, text="Internal Server Error")

    response = client.query("test prompt")
    assert "Error: 500 Server Error: Internal Server Error" in response

def test_query_network_error(mock_model_config, requests_mock):
    client = LLMAPIClient(mock_model_config)
    requests_mock.post(mock_model_config["api_endpoint"], exc=requests_mock.exceptions.ConnectionError("Network down"))

    response = client.query("test prompt")
    assert "Error: Network down" in response

def test_get_internal_activations_not_implemented(mock_model_config, caplog):
    client = LLMAPIClient(mock_model_config)
    with caplog.at_level(logging.WARNING):
        activations = client.get_internal_activations("test prompt")
        assert activations == {}
        assert "llm_api_client.internal_activations.unsupported" in caplog.text
