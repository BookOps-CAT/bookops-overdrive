"""Provides client authentication for Overdrive APIs"""

import datetime

import requests

from . import __title__, __version__


class OverdriveAccessToken:
    """
    Requests an access token from Overdrive oauth2 server.

    Args:
        key: API key as a string
        secret: API secret as a string
        resource_url: url for oauth server
        agent: `User-agent` parameter to be passed in request header

    """

    def __init__(
        self,
        key: str,
        secret: str,
        resource_url: str,
        agent: str = f"{__title__}/{__version__}",
    ) -> None:
        self.agent = agent
        self.key = key
        self.resource_url = resource_url
        self.secret = secret
        self.expires_at: datetime.datetime | None = None
        self.server_response: requests.Response | None = None
        self.token_str: str | None = None
        self.token_type: str | None = None

        self._request_token()

    def _calculate_expiration_time(self, expires_in: int) -> datetime.datetime:
        """
        Calculates expiration time of access token based on 'expires_in'
        timedelta from token response.

        Args:
            expires_in: number of seconds until the access token expires as an int
        """
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=expires_in - 1
        )
        return expires_at

    def _parse_server_response(self, response: requests.Response) -> None:
        """Parse response from authorization server."""
        self.server_response = response
        if response.status_code == requests.codes.ok:
            json_response = response.json()
            self.token_str = json_response["access_token"]
            self.expires_at = self._calculate_expiration_time(
                json_response["expires_in"]
            )
            self.scope = json_response["scope"]
            self.token_type = json_response["token_type"]

    def _post_token_request(self) -> requests.Response:
        """Sends a POST request for an access token"""
        try:
            response = requests.post(
                self.resource_url,
                auth=(self.key, self.secret),
                headers={"User-Agent": self.agent, "Accept": "application/json"},
                data={"grant_type": "client_credentials"},
            )
            return response

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise

    def _request_token(self):
        """Requests access token and parses response."""
        response = self._post_token_request()
        self._parse_server_response(response)

    def is_expired(self) -> bool:
        """Checks if the access token is expired."""
        if self.expires_at and self.expires_at < datetime.datetime.now(
            datetime.timezone.utc
        ):
            return True
        else:
            return False

    def __repr__(self):
        return (
            f"access_token: '{self.token_str}', "
            f"expires_at: '{self.expires_at:%Y-%m-%d %H:%M:%SZ}'"
        )
