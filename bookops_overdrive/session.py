"""Overdrive Discovery API wrapper session"""

from __future__ import annotations

import requests

from . import __title__, __version__
from .authorize import OverdriveAccessToken
from .query import Query


class OverdriveSession(requests.Session):
    """
    The `OverdriveSession` class supports interactions with the Overdrive
    Discovery APIs. Inherits all `requests.Session` methods.

    This class includes methods that support endpoints within four of the
    Overdrive Discovery APIs: Library Account, Search, Metadata, and Digital
    Inventory.

    """

    BASE_URL = "https://api.overdrive.com/v1"

    def __init__(
        self,
        authorization: OverdriveAccessToken,
        agent: str = f"{__title__}/{__version__}",
        timeout: int | float | tuple[int | float, int | float] | None = (5, 5),
    ) -> None:
        """Initializes `OverdriveSession` class instance.

        Args:
            authorization:
                an `OverdriveAccessToken` object.
            agent:
                `User-agent` parameter to be passed in request header.
                Default is 'bookops-overdrive/{version}'.
            timeout:
                How many seconds to wait for the server to respond. Accepts a single
                value to be applied to both connect and read timeouts or two separate
                values. Default is 5 seconds for connect and read timeouts.

        """

        super().__init__()
        self.authorization = authorization
        self.timeout = timeout

        self.headers.update({"User-Agent": agent})
        self.headers.update({"Authorization": f"Bearer {self.authorization.token_str}"})

    def _request_new_access_token(self) -> None:
        """Requests a new token and updates headers."""
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

    def _verify_reserve_ids(self, reserveIds: str | list[str]) -> str:
        if isinstance(reserveIds, list):
            return ",".join([str(i) for i in reserveIds])
        else:
            return ",".join([str(i.strip()) for i in reserveIds.split(",")])

    def get_library_account_info(self, library_id: int) -> requests.Response:
        """
        Given an Overdrive ID, retrieve information for the specified library.

        Uses `/libraries/{libraryID}` endpoint.

        Args:
            library_id:
                the Overdrive Library ID for an institution.

        Returns:
            `requests.Response` instance
        """
        url = self._url_library_account(library_id)
        header = {"Accept": "application/json"}
        req = requests.Request("GET", url=url, headers=header)
        prepared_request = self.prepare_request(req)
        query = Query(self, prepared_request=prepared_request)
        return query.response

    def get_collection_inventory(self, collectionToken: str) -> requests.Response:
        """
        Given an institution's `collectionToken`, retrieve an inventory of the
        library's entire digital collection. An institution's `collectionToken`
        can be retrieved using the `/libraries/{libraryID}` endpoint (or the
        `get_library_account_info` method of this class).

        Uses `/collections/{collectionToken}/digitalinventory` endpoint.

        Args:
            collectionToken:
                a token which identifies the the requesting institution.

        Returns:
            `requests.Response` instance
        """
        url = self._url_collections_digital_inventory(collectionToken)
        header = {"Accept": "application/json"}
        req = requests.Request("GET", url=url, headers=header)
        prepared_request = self.prepare_request(req)
        query = Query(self, prepared_request=prepared_request)
        return query.response

    def get_bulk_metadata(
        self, collectionToken: str, reserveIds: str | list[str]
    ) -> requests.Response:
        """
        Retrieve metadata for up to 50 titles by `reserveId` or `crossRefId`.

        Uses `/collections/{collectionToken}/bulkmetadata` endpoint.

        Args:
            collectionToken:
                a token which identifies the the requesting institution.
            reserveIds:
                string or list containing one or more reserveIds or crossRefIds.
                If str, the ids must be separated by a comma.

        Returns:
            `requests.Response` instance

        """
        url = self._url_collections_bulk_metadata(collectionToken)
        header = {"Accept": "application/json"}
        payload = {"reserveIds": self._verify_reserve_ids(reserveIds=reserveIds)}
        req = requests.Request("GET", url=url, headers=header, params=payload)
        prepared_request = self.prepare_request(req)
        query = Query(self, prepared_request=prepared_request)
        return query.response

    def get_title_metadata(
        self, collectionToken: str, reserveId: str
    ) -> requests.Response:
        """
        Retrieve metadata for a single title by `reserveId` or `crossRefId`.

        Uses `/collections/{collectionToken}/products/{reserveId}/metadata` endpoint.

        Args:
            collectionToken:
                a token which identifies the the requesting institution.
            reserveId:
                the reserveId or crossRefId for the title

        Returns:
            `requests.Response` instance

        """
        url = self._url_collections_metadata(collectionToken, reserveId=reserveId)
        header = {"Accept": "application/json"}
        req = requests.Request("GET", url=url, headers=header)
        prepared_request = self.prepare_request(req)
        query = Query(self, prepared_request=prepared_request)
        return query.response

    def search_title_metadata(
        self,
        collectionToken: str,
        q: str,
        availability: bool = True,
        formats: str | list[str] | None = None,
        identifier: str | None = None,
        crossRefId: str | None = None,
        daysSinceAdded: str | None = None,
        lastTitleUpdateTime: str | None = None,
        lastUpdateTime: str | None = None,
        limit: str | int = 25,
        minimum: bool = False,
        offset: str | None = None,
        series: str | None = None,
        sort: str | None = None,
    ) -> requests.Response:
        """
        Search for titles within an institution's digital collection using
        query parameters.

        Uses `/collections/{collectionToken}/products` endpoint.

        Args:
            collectionToken:
                A token which identifies the the requesting institution.
            q:
                Terms to include in search query. Terms will search on title,
                author, and/or keyword. Exact phrases can be included in quotes.
            availability:
                Whether or not titles are currently available to borrow. Default
                is `True`.
            formats:
                String or list containing formats to be included in search. If str,
                the formats must be separated by a comma.
            identifier:
                Unique identifiers such as ISBN and ASIN to search by. While a
                title's print ISBN may be included in a search response under
                'otherFormatIdentifiers', print ISBNs cannot be used within search.
            crossRefId:
                A title's crossRefId (also known as titleId).
            daysSinceAdded:
                Search for titles that were added to the collection within a certain
                number of days. Maximum is 90.
            lastTitleUpdateTime:
                Search for titles updated after this date. Date should be formatted
                as YYYY-MM-DD.
            lastUpdateTime:
                Search for records updated after this date. Date should be formatted
                as YYYY-MM-DD.
            limit:
                The maximum number of records to be displayed per page.
                Default is 25 and maxiumum is 2000.
            minimum:
                When true, only the title's reserveId will be included in the search
                results. Default is False.
            offset:
                Start position of records to return.
            series:
                Search by series name.
            sort:
                Sort results based on author, availability, dateAdded, gradeLevel,
                imprint, popularity, popularitySite, publisher, relevancy, saleDate,
                or title. Include either ':asc' or ':dsc' to sort the results in
                either ascending or descending order.

        Returns:
            `requests.Response` instance

        """
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
