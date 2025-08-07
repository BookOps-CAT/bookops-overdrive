import pytest
from requests import Request

from bookops_overdrive.errors import BookopsOverdriveError
from bookops_overdrive.query import Query


def test_query(stub_session, mock_session_response):
    req = Request("GET", url="https://foo", headers={"Accept": "application/json"})
    prepared_request = stub_session.prepare_request(req)
    query = Query(stub_session, prepared_request)
    assert query.response.status_code == 200


def test_query_connection_error(stub_session, mock_connection_error):
    req = Request("GET", url="https://foo", headers={"Accept": "application/json"})
    prepared_request = stub_session.prepare_request(req)
    with pytest.raises(BookopsOverdriveError) as exc:
        Query(stub_session, prepared_request)
    assert "Error connecting: " in str(exc.value)


@pytest.mark.http_code(404)
def test_query_http_error(stub_session, mock_session_response):
    req = Request("GET", url="https://foo", headers={"Accept": "application/json"})
    prepared_request = stub_session.prepare_request(req)
    with pytest.raises(BookopsOverdriveError) as exc:
        Query(stub_session, prepared_request)
    assert "404 Client Error: Not Found for url: " in str(exc.value)
