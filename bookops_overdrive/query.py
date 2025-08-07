"""Wrapper class to handle access token refresh and manage queries sent to web service."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import requests

from bookops_overdrive.errors import BookopsOverdriveError

if TYPE_CHECKING:
    from .session import OverdriveSession  # pragma: no cover


class Query:
    """
    The `Query` class handles access token refresh and sends requests
    to the Overdrive API.

    Args:
        session: An `OverdriveSession` object
        prepared_request: the request that will be sent to the web service
    """

    def __init__(
        self, session: OverdriveSession, prepared_request: requests.PreparedRequest
    ) -> None:
        if session.authorization.is_expired:
            session._request_new_access_token()
        try:
            self.response = session.send(prepared_request)
            self.response.raise_for_status()
        except (requests.Timeout, requests.ConnectionError):
            raise BookopsOverdriveError(f"Error connecting: {sys.exc_info()[0]}")
        except requests.HTTPError as exc:
            raise BookopsOverdriveError(
                f"{exc}. Server response: {self.response.content.decode('utf-8')}"
            )
