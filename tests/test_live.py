import os

import pytest

from bookops_overdrive.authorize import OverdriveAccessToken
from bookops_overdrive.session import OverdriveSession


@pytest.fixture
def live_token(live_creds):
    return OverdriveAccessToken(
        key=os.environ["CLIENT_KEY"],
        secret=os.environ["CLIENT_SECRET"],
    )


@pytest.mark.livetest
class TestLiveOverdriveSession:
    def test_get_library_account_info(self, live_token):
        with OverdriveSession(authorization=live_token) as session:
            response = session.get_library_account_info(os.environ["LIBRARY_ID"])
            assert response.status_code == 200
            assert sorted(list(response.json().keys())) == [
                "collectionToken",
                "enabledPlatforms",
                "formats",
                "id",
                "links",
                "name",
                "type",
            ]
            assert response.json() == {}

    def test_get_inventory(self, live_token):
        with OverdriveSession(authorization=live_token) as session:
            token_response = session.get_library_account_info(os.environ["LIBRARY_ID"])
            collectionToken = token_response.json()["collectionToken"]
            inventory_response = session.get_inventory(collectionToken=collectionToken)
            assert sorted(list(inventory_response.json().keys())) == [
                "files",
                "links",
                "totalItems",
            ]
