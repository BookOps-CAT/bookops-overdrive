"""Provides client authentication for Overdrive APIs"""

from __future__ import annotations

import datetime
import sys

import requests

from . import __title__, __version__
from .errors import BookopsOverdriveError


class OverdriveAccessToken:
    """
    Requests an access token from Overdrive OAuth2 server.

    Args:
        key:
            API key as a string
        secret:
            API secret as a string
        oauth_url:
            url for OAuth2 server as a string
        agent:
            `User-agent` parameter to be passed in request header.
            Default is 'bookops-overdrive/{version}'

    """

    def __init__(
        self,
        key: str,
        secret: str,
        agent: str = f"{__title__}/{__version__}",
    ) -> None:
        self.agent = agent
        self.expires_at: datetime.datetime | None = None
        self.key = key
        self.oauth_url = "https://oauth.overdrive.com/token"
        self.secret = secret
        self.server_response: requests.Response | None = None
        self.token_str: str | None = None

        self._request_token()

    def _calculate_expiration_time(self, expires_in: int) -> datetime.datetime:
        """
        Calculates expiration time of access token based on 'expires_in'
        value from token response.

        Args:
            expires_in: number of seconds until the access token expires as an int

        Returns:
            expiration time of access token as `datetime.datetime` object.
        """
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=expires_in - 1
        )
        return expires_at

    def _parse_server_response(self, response: requests.Response) -> None:
        """Parse response from authorization server."""
        self.server_response = response
        if response.ok:
            json_resp = response.json()
            self.token_str = json_resp["access_token"]
            self.expires_at = self._calculate_expiration_time(json_resp["expires_in"])

    def _post_token_request(self) -> requests.Response:
        """Sends a POST request for an access token"""
        auth = (self.key, self.secret)
        headers = {"User-Agent": self.agent, "Accept": "application/json"}
        data = {"grant_type": "client_credentials"}
        try:
            response = requests.post(
                self.oauth_url, auth=auth, headers=headers, data=data
            )
            response.raise_for_status()
        except (requests.Timeout, requests.ConnectionError):
            raise BookopsOverdriveError(f"Error connecting: {sys.exc_info()[0]}")
        except requests.HTTPError as exc:
            raise BookopsOverdriveError(
                f"{exc}. Server response: {response.content.decode('utf-8')}"
            )
        else:
            return response

    def _request_token(self):
        """Requests access token and parses response."""
        response = self._post_token_request()
        self._parse_server_response(response)

    @property
    def is_expired(self) -> bool:
        """Checks if the access token has expired."""
        now = datetime.datetime.now(datetime.timezone.utc)
        if self.expires_at and self.expires_at < now:
            return True
        else:
            return False

    def __repr__(self):
        return (
            f"access_token: '{self.token_str}', "
            f"expires_at: '{self.expires_at:%Y-%m-%d %H:%M:%SZ}'"
        )
