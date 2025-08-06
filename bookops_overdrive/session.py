"""Overdrive Discovery API wrapper session"""

import requests

from . import __title__, __version__
from .authorize import OverdriveAccessToken


class OverdriveSession(requests.Session):
    """"""

    BASE_URL = "https://api.overdrive.com/v1"

    def __init__(
        self, authorization: OverdriveAccessToken, agent: str | None = None
    ) -> None:
        super().__init__()
        self.authorization = authorization

        if not agent:
            self.headers.update({"User-Agent": f"{__title__}/{__version__}"})
        else:
            self.headers.update({"User-Agent": agent})

        self._update_auth()

    def _request_new_access_token(self) -> None:
        self.authorization._request_token()
        self._update_auth()

    def _update_auth(self) -> None:
        self.headers.update({"Authorization": f"Bearer {self.authorization.token_str}"})

    def _url_digital_inventory(self, collection_token: str) -> str:
        return f"{self.BASE_URL}/collections/{collection_token}/digitalinventory"

    def _url_library_account(self, library_id: int) -> str:
        return f"{self.BASE_URL}/libraries/{library_id}"

    def get_collection_token(self, library_id: int) -> requests.Response:
        url = self._url_library_account(library_id=library_id)
        header = {"Accept": "application/json"}
        req = requests.Request("GET", url=url, headers=header)
        prepped_request = self.prepare_request(req)
        return self.send(prepped_request)

    def get_inventory(self, collection_token: str) -> requests.Response:
        url = self._url_digital_inventory(collection_token=collection_token)
        header = {"Accept": "application/json"}
        req = requests.Request("GET", url=url, headers=header)
        prepped_request = self.prepare_request(req)
        return self.send(prepped_request)
