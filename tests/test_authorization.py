import datetime
import os

import pytest

from bookops_overdrive.authorize import OverdriveAccessToken
from bookops_overdrive.errors import BookopsOverdriveError


class TestOverdriveAccessToken:
    def test_successful_token_request(self, post_token_response_success):
        token = OverdriveAccessToken(key="foo", secret="bar")
        assert token.server_response.status_code == 200
        assert sorted(list(token.server_response.json().keys())) == [
            "access_token",
            "expires_in",
            "scope",
            "token_type",
        ]
        assert "access_token: 'foo', expires_at: " in str(token)

    def test_invalid_token_request(self, post_token_response_failure):
        with pytest.raises(BookopsOverdriveError) as exc:
            OverdriveAccessToken(key="foo", secret="bar")
        assert "401 Client Error: Unauthorized for url: " in str(exc.value)

    def test_token_request_connection_error(self, mock_connection_error):
        with pytest.raises(BookopsOverdriveError) as exc:
            OverdriveAccessToken(key="foo", secret="bar")
        assert "Error connecting: " in str(exc.value)


@pytest.mark.livetest
@pytest.mark.usefixtures("live_creds")
class TestOverdriveAccessTokenLive:
    def test_authorization(self):
        token = OverdriveAccessToken(
            key=os.environ["CLIENT_KEY"],
            secret=os.environ["CLIENT_SECRET"],
        )
        json_response = token.server_response.json()
        assert token.server_response.status_code == 200
        assert token.agent == "bookops-overdrive/0.0.1"
        assert token.expires_at > datetime.datetime.now(datetime.timezone.utc)
        assert isinstance(token.token_str, str)
        assert token.token_str is not None
        assert json_response["scope"] == "LIB META AVAIL SRCH ENABLEODAPPDOWNLOADS"
        assert sorted(list(json_response.keys())) == [
            "access_token",
            "expires_in",
            "scope",
            "token_type",
        ]

    def test_authorization_failure(self):
        with pytest.raises(BookopsOverdriveError) as exc:
            OverdriveAccessToken(key="key", secret="secret")
        assert (
            str(exc.value)
            == '401 Client Error: Unauthorized for url: https://oauth.overdrive.com/token. Server response: {"error":"invalid_client","error_description":"The client secret was incorrect."}'
        )
