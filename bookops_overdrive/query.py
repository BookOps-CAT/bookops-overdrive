"""Wrapper class to manage access token refresh and requests sent to web service."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import requests

from bookops_overdrive.errors import BookopsOverdriveError

if TYPE_CHECKING:
    from .session import OverdriveSession  # pragma: no cover


class Query:
    """
    The `Query` class handles requests sent to the Overdrive API. The class checks
    if the session's associated access token has expired before sending the request.
    This ensures that requests will always be sent with an unexpired token.

    """

    def __init__(
        self,
        session: OverdriveSession,
        prepared_request: requests.PreparedRequest,
        timeout: int | float | tuple[int | float, int | float] | None = (5, 5),
    ) -> None:
        """Initializes `Query` class instance.

        Args:
            session:
                An `OverdriveSession` object.
            prepared_request:
                The request that will be sent to the web service as a
                `requests.PreparedRequest` object.
            timeout:
                How many seconds to wait for the server to respond. Accepts a single
                value to be applied to both connect and read timeouts or two separate
                values. Default is 5 seconds for connect and read timeouts.

        Raises:
            BookopsOverdriveError: If the request encounters any errors.

        """

        if session.authorization.is_expired:
            session._request_new_access_token()
        try:
            self.response = session.send(prepared_request, timeout=timeout)
            self.response.raise_for_status()
        except (requests.Timeout, requests.ConnectionError):
            raise BookopsOverdriveError(f"Error connecting: {sys.exc_info()[0]}")
        except requests.HTTPError as exc:
            raise BookopsOverdriveError(
                f"{exc}. Server response: {self.response.content.decode('utf-8')}"
            )
