from __future__ import annotations

import io

import pytest
import requests

from remail.util.request import RequestBuilder


def _make_response(status_code: int, request: requests.PreparedRequest) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = b"ok"
    response.request = request

    return response


def test_request_builder_builds_expected_prepared_request():
    builder = (
        RequestBuilder()
        .post()
        .url("https://api.example.com/resource")
        .header("Accept", "application/json")
        .param("page", 1)
        .json({"foo": "bar"})
    )

    prepared = builder.build()

    assert prepared.method == "POST"
    assert prepared.url == "https://api.example.com/resource?page=1"
    assert prepared.headers["Accept"] == "application/json"
    assert prepared.headers["Content-Type"] == "application/json"
    assert prepared.body == b'{"foo": "bar"}'


def test_build_requires_url():
    builder = RequestBuilder()

    with pytest.raises(ValueError, match="URL is required"):
        builder.build()


def test_file_accepts_bytes_and_creates_bytesio():
    payload = b"sample"
    builder = RequestBuilder().file(
        "upload", payload, filename="payload.bin", content_type="application/octet-stream"
    )
    stored_filename, file_obj, stored_content_type = builder._files["upload"]

    assert builder._files is not None
    assert stored_filename == "payload.bin"
    assert stored_content_type == "application/octet-stream"
    assert isinstance(file_obj, io.BytesIO)
    assert file_obj.getvalue() == payload


def test_clone_returns_independent_copy():
    builder = RequestBuilder().header("X-Test", "1").param("flag", True).cookie("session", "abc")

    clone = builder.clone()

    assert clone is not builder
    assert clone._headers == builder._headers
    assert clone._params == builder._params
    assert clone._cookies == builder._cookies
    assert clone._files == builder._files

    assert clone._headers is not builder._headers
    assert clone._params is not builder._params
    assert clone._cookies is not builder._cookies


def test_send_uses_provided_session_and_updates_cookies():
    class FakeSession(requests.Session):
        def __init__(self) -> None:
            super().__init__()
            self.sent_args: tuple[requests.PreparedRequest, dict[str, object]] | None = None

        def send(self, request: requests.PreparedRequest, **kwargs: object) -> requests.Response:
            self.sent_args = (request, kwargs)

            return _make_response(200, request)

    session = FakeSession()
    builder = RequestBuilder().url("https://example.com").cookie("token", "abc")

    response = builder.send(
        session=session,
        stream=True,
        allow_redirects=False,
        proxies={"http": "http://proxy"},
        verify=False,
    )

    assert response.status_code == 200
    assert "token" in session.cookies.get_dict()

    assert session.sent_args is not None
    request, kwargs = session.sent_args
    assert request.url == "https://example.com/"
    assert kwargs["timeout"] == builder._timeout
    assert kwargs["stream"] is True
    assert kwargs["allow_redirects"] is False
    assert kwargs["proxies"] == {"http": "http://proxy"}
    assert kwargs["verify"] is False


def test_send_creates_session_if_none(monkeypatch: pytest.MonkeyPatch):
    created_sessions: list[requests.Session] = []

    class DummySession(requests.Session):
        def __init__(self) -> None:
            super().__init__()
            created_sessions.append(self)
            self.sent: tuple[requests.PreparedRequest, dict[str, object]] | None = None

        def send(self, request: requests.PreparedRequest, **kwargs: object) -> requests.Response:
            self.sent = (request, kwargs)
            return _make_response(200, request)

    monkeypatch.setattr(requests, "Session", DummySession)

    builder = RequestBuilder().url("https://example.com").get()
    response = builder.send()

    assert response.status_code == 200
    assert len(created_sessions) == 1
    sent_request, sent_kwargs = created_sessions[0].sent
    assert sent_request.method == "GET"
    assert sent_request.url == "https://example.com/"
    assert sent_kwargs["timeout"] == builder._timeout


def test_send_raise_for_status_raises_http_error():
    class ErrorSession(requests.Session):
        def send(self, request: requests.PreparedRequest, **kwargs: object) -> requests.Response:
            return _make_response(400, request)

    builder = RequestBuilder().url("https://example.com")

    with pytest.raises(requests.HTTPError):
        builder.send(session=ErrorSession(), raise_for_status=True)


def test_builder_methods_are_immutable():
    original = RequestBuilder()
    updated = original.header("X-Test", "value")

    assert original is not updated
    assert original._headers == {}
    assert updated._headers == {"X-Test": "value"}
