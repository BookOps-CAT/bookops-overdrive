from __future__ import annotations

import datetime
import json
import os

import pytest
from requests import Response
from requests.exceptions import ConnectionError

from bookops_overdrive import OverdriveAccessToken, OverdriveSession


@pytest.fixture(scope="module")
def live_creds() -> None:
    with open(
        os.path.join(
            os.environ["USERPROFILE"], ".cred/.overdrive/overdrive_creds.json"
        ),
        "r",
    ) as fh:
        creds = json.load(fh)
        for k, v in creds.items():
            os.environ[k] = v


class FakeUtcNow(datetime.datetime):
    @classmethod
    def now(cls, tzinfo=datetime.timezone.utc) -> FakeUtcNow:
        return cls(2025, 1, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)


@pytest.fixture
def mock_now(monkeypatch) -> None:
    monkeypatch.setattr(datetime, "datetime", FakeUtcNow)


class MockHTTPResponse(Response):
    REASON = {"200": "OK", "401": "Unauthorized", "404": "Not Found"}

    def __init__(self, http_code: int, content: bytes | None = None) -> None:
        self.status_code = http_code
        self.reason = self.REASON[str(self.status_code)]
        self.url = "https://foo.bar?query"
        self._content = content if content else b""
        self.encoding = "utf-8"


@pytest.fixture
def post_token_response_success(monkeypatch):
    def oauth_200_response(*args, **kwargs):
        value = b'{"access_token": "foo","expires_in": 3600,"scope": "LIB META AVAIL SRCH ENABLEODAPPDOWNLOADS","token_type": "bearer"}'
        return MockHTTPResponse(http_code=200, content=value)

    monkeypatch.setattr("requests.post", oauth_200_response)


@pytest.fixture
def post_token_response_failure(monkeypatch):
    def oauth_401_response(*args, **kwargs):
        value = b'{"error": "invalid_client","error_description": "The client secret was incorrect."}'
        return MockHTTPResponse(http_code=401, content=value)

    monkeypatch.setattr("requests.post", oauth_401_response)


@pytest.fixture
def mock_token(post_token_response_success, mock_now) -> OverdriveAccessToken:
    return OverdriveAccessToken(key="foo", secret="bar")


@pytest.fixture
def mock_expired_token(post_token_response_success, mock_now) -> OverdriveAccessToken:
    token = OverdriveAccessToken(key="foo", secret="bar")
    token.expires_at = datetime.datetime.now(
        datetime.timezone.utc
    ) - datetime.timedelta(seconds=1)
    return token


@pytest.fixture
def mock_session_response(request, monkeypatch) -> None:
    marker = request.node.get_closest_marker("http_code")
    if marker is None:
        http_code = 200
    else:
        http_code = marker.args[0]

    def mock_api_response(*args, http_code=http_code, **kwargs):
        return MockHTTPResponse(http_code=http_code)

    monkeypatch.setattr("requests.Session.send", mock_api_response)


@pytest.fixture
def mock_connection_error(monkeypatch) -> None:
    def connection_error(*args, **kwargs):
        raise ConnectionError

    monkeypatch.setattr("requests.post", connection_error)
    monkeypatch.setattr("requests.get", connection_error)
    monkeypatch.setattr("requests.Session.send", connection_error)


@pytest.fixture
def stub_session(mock_token):
    yield OverdriveSession(authorization=mock_token)
