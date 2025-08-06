import datetime
import os

import pytest

from bookops_overdrive.authorize import OverdriveAccessToken
from bookops_overdrive.session import OverdriveSession


@pytest.mark.livetest
def test_authorization(live_creds):
    token = OverdriveAccessToken(
        key=os.environ["CLIENT_KEY"],
        secret=os.environ["CLIENT_SECRET"],
        resource_url=os.environ["OAUTH_URL"],
    )
    assert token.server_response.status_code == 200
    assert token.token_str is not None
    assert token.expires_at > datetime.datetime.now(datetime.timezone.utc)
    assert token.scope == "LIB META AVAIL SRCH ENABLEODAPPDOWNLOADS"
    assert token.token_type == "bearer"


@pytest.mark.livetest
def test_get_collection_token(live_creds):
    token = OverdriveAccessToken(
        key=os.environ["CLIENT_KEY"],
        secret=os.environ["CLIENT_SECRET"],
        resource_url=os.environ["OAUTH_URL"],
    )
    with OverdriveSession(authorization=token) as session:
        token_response = session.get_collection_token(os.environ["LIBRARY_ID"])
        collection_token = token_response.json()["collectionToken"]
        inventory_response = session.get_inventory(collection_token=collection_token)
        file_response = session.get(inventory_response.json()["files"][0]["fileUrl"])
        title_count = len(file_response.json()["reserveIds"])
        assert token_response.status_code == 200
        assert inventory_response.status_code == 200
        assert file_response.status_code == 200
        assert title_count > 1
