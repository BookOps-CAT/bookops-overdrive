import pytest

from bookops_overdrive import OverdriveSession
from bookops_overdrive.errors import BookopsOverdriveError


@pytest.mark.usefixtures("mock_session_response")
class TestOverdriveSession:
    def test_session(self, mock_token):
        with OverdriveSession(authorization=mock_token) as session:
            assert session.headers["Authorization"] == "Bearer foo"
            assert session.BASE_URL == "https://api.overdrive.com/v1"
            assert session.headers["User-Agent"] == "bookops-overdrive/0.0.1"

    def test_session_refresh_token(self, mock_expired_token):
        with OverdriveSession(authorization=mock_expired_token) as session:
            stale_token_expiration = session.authorization.expires_at
            assert mock_expired_token.is_expired is True
            session._request_new_access_token()
            assert session.authorization.expires_at > stale_token_expiration

    def test_get_library_account_info(self, stub_session):
        response = stub_session.get_library_account_info(library_id="1")
        assert response.status_code == 200
        assert response.reason == "OK"

    def test_get_library_account_info_refresh_token(self, mock_expired_token):
        with OverdriveSession(authorization=mock_expired_token) as session:
            response = session.get_library_account_info(library_id="1")
            assert response.status_code == 200
            assert response.reason == "OK"

    def test_get_library_account_info_connection_error(
        self, stub_session, mock_connection_error
    ):
        with pytest.raises(BookopsOverdriveError) as exc:
            stub_session.get_library_account_info(library_id="1")
        assert "Error connecting: " in str(exc.value)

    @pytest.mark.http_code(404)
    def test_get_library_account_info_404(self, stub_session):
        with pytest.raises(BookopsOverdriveError) as exc:
            stub_session.get_library_account_info(library_id="1")
        assert "404 Client Error: Not Found for url: " in str(exc.value)

    def test_get_inventory(self, stub_session):
        response = stub_session.get_inventory(collectionToken="foo")
        assert response.status_code == 200
        assert response.reason == "OK"

    @pytest.mark.parametrize("ids", ["123,456", ["123", "456"], "123"])
    def test_get_bulk_metadata(self, stub_session, ids):
        response = stub_session.get_bulk_metadata(collectionToken="foo", reserveIds=ids)
        assert response.status_code == 200
        assert response.reason == "OK"

    def test_get_metadata(self, stub_session):
        response = stub_session.get_metadata(collectionToken="foo", reserveId="123")
        assert response.status_code == 200
        assert response.reason == "OK"

    def test_search_collection(self, stub_session):
        response = stub_session.search_collection(collectionToken="foo", q="bar")
        assert response.status_code == 200
        assert response.reason == "OK"
