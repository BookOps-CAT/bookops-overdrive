"""Overdrive Discovery API wrapper session"""

from __future__ import annotations

import requests

from . import __title__, __version__
from .authorize import OverdriveAccessToken
from .query import Query


class OverdriveSession(requests.Session):
    """
    The `OverdriveSession` class supports interactions with the Overdrive Discovery API.
    Inherits all `requests.Session` methods.

    Args:
        authorization:
            an `OverdriveAccessToken` object
        agent:
            `User-agent` parameter to be passed in request header.
            Default is 'bookops-overdrive/{version}'

    """

    BASE_URL = "https://api.overdrive.com/v1"

    def __init__(
        self,
        authorization: OverdriveAccessToken,
        agent: str = f"{__title__}/{__version__}",
    ) -> None:
        super().__init__()
        self.authorization = authorization

        self.headers.update({"User-Agent": agent})
        self.headers.update({"Authorization": f"Bearer {self.authorization.token_str}"})

    def _request_new_access_token(self) -> None:
        self.authorization._request_token()
        self.headers.update({"Authorization": f"Bearer {self.authorization.token_str}"})

    def _url_collections_digital_inventory(self, collectionToken: str) -> str:
        return f"{self.BASE_URL}/collections/{collectionToken}/digitalinventory"

    def _url_collections_bulk_metadata(self, collectionToken: str) -> str:
        return f"{self.BASE_URL}/collections/{collectionToken}/bulkmetadata"

    def _url_collections_metadata(self, collectionToken: str, reserveId: str) -> str:
        return f"{self.BASE_URL}/collections/{collectionToken}/products/{reserveId}/metadata"

    def _url_collections_search(self, collectionToken: str) -> str:
        return f"{self.BASE_URL}/collections/{collectionToken}/products"

    def _url_library_account(self, library_id: int) -> str:
        return f"{self.BASE_URL}/libraries/{library_id}"

    def get_library_account_info(self, library_id: int) -> requests.Response:
        url = self._url_library_account(library_id)
        header = {"Accept": "application/json"}
        req = requests.Request("GET", url=url, headers=header)
        prepared_request = self.prepare_request(req)
        query = Query(self, prepared_request=prepared_request)
        return query.response

    def get_inventory(self, collectionToken: str) -> requests.Response:
        url = self._url_collections_digital_inventory(collectionToken)
        header = {"Accept": "application/json"}
        req = requests.Request("GET", url=url, headers=header)
        prepared_request = self.prepare_request(req)
        query = Query(self, prepared_request=prepared_request)
        return query.response

    def get_bulk_metadata(
        self, collectionToken: str, reserveIds: str | list[str]
    ) -> requests.Response:
        url = self._url_collections_bulk_metadata(collectionToken)
        header = {"Accept": "application/json"}
        payload = {"reserveIds": reserveIds}
        req = requests.Request("GET", url=url, headers=header, params=payload)
        prepared_request = self.prepare_request(req)
        query = Query(self, prepared_request=prepared_request)
        return query.response

    def get_metadata(self, collectionToken: str, reserveId: str) -> requests.Response:
        url = self._url_collections_metadata(collectionToken, reserveId=reserveId)
        header = {"Accept": "application/json"}
        req = requests.Request("GET", url=url, headers=header)
        prepared_request = self.prepare_request(req)
        query = Query(self, prepared_request=prepared_request)
        return query.response

    def search_collection(
        self,
        collectionToken: str,
        q: str,
        availability: bool | None = None,
        formats: str | list[str] | None = None,
        identifier: str | None = None,
        crossRefId: str | None = None,
        daysSinceAdded: str | None = None,
        lastTitleUpdateTime: str | None = None,
        lastUpdateTime: str | None = None,
        limit: str | None = None,
        minimum: str | None = None,
        offset: str | None = None,
        series: str | None = None,
        sort: str | None = None,
    ) -> requests.Response:
        url = self._url_collections_search(collectionToken)
        header = {"Accept": "application/json"}
        payload = {
            "availability": availability,
            "formats": formats,
            "identifier": identifier,
            "crossRefId": crossRefId,
            "daysSinceAdded": daysSinceAdded,
            "lastTitleUpdateTime": lastTitleUpdateTime,
            "lastUpdateTime": lastUpdateTime,
            "limit": limit,
            "minimum": minimum,
            "offset": offset,
            "q": q,
            "series": series,
            "sort": sort,
        }
        req = requests.Request("GET", url=url, headers=header, params=payload)
        prepared_request = self.prepare_request(req)
        query = Query(self, prepared_request=prepared_request)
        return query.response
