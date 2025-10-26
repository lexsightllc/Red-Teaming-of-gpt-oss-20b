import pytest
import requests
import requests_mock as _req_mock


@pytest.fixture
def requests_mock():
    with _req_mock.Mocker() as m:
        # Provide compatibility attribute expected by tests
        try:
            setattr(m, "exceptions", requests.exceptions)
        except Exception:
            pass
        yield m
