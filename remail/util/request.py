from __future__ import annotations

import io
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, field, replace
from typing import Any

import requests

JSONType = dict | list | str | int | float | bool | None
TimeoutType = float | tuple[float, float]
HeadersType = Mapping[str, str]
ParamsType = Mapping[str, str | int | float | bool]
CookiesType = Mapping[str, str]
type AuthType = requests.auth.AuthBase | tuple[str, str]


@dataclass(frozen=True)
class RequestBuilder:
    _method: str = "GET"
    _url: str | None = None
    _headers: dict[str, str] = field(default_factory=dict)
    _params: dict[str, Any] = field(default_factory=dict)
    _data: bytes | str | MutableMapping[str, Any] | None = None
    _json: JSONType | None = None
    _files: dict[str, Any] | None = None
    _cookies: dict[str, str] = field(default_factory=dict)
    _timeout: TimeoutType | None = (5, 15)
    _auth: AuthType | None = None

    def method(self, method: str) -> RequestBuilder:
        return replace(self, _method=method.upper())

    def get(self) -> RequestBuilder:
        return self.method("GET")

    def post(self) -> RequestBuilder:
        return self.method("POST")

    def put(self) -> RequestBuilder:
        return self.method("PUT")

    def patch(self) -> RequestBuilder:
        return self.method("PATCH")

    def delete(self) -> RequestBuilder:
        return self.method("DELETE")

    def url(self, url: str) -> RequestBuilder:
        return replace(self, _url=url)

    def header(self, name: str, value: str) -> RequestBuilder:
        new_headers = dict(self._headers)
        new_headers[name] = value

        return replace(self, _headers=new_headers)

    def headers(self, headers: HeadersType) -> RequestBuilder:
        b = self

        for k, v in headers.items():
            b = b.header(k, v)

        return b

    def accept(self, mime: str) -> RequestBuilder:
        return self.header("Accept", mime)

    def content_type(self, mime: str) -> RequestBuilder:
        return self.header("Content-Type", mime)

    def bearer(self, token: str) -> RequestBuilder:
        return self.header("Authorization", f"Bearer {token}")

    def param(self, name: str, value: Any) -> RequestBuilder:
        new_params = dict(self._params)
        new_params[name] = value

        return replace(self, _params=new_params)

    def params(self, params: ParamsType) -> RequestBuilder:
        new_params = dict(self._params)
        new_params.update(params)

        return replace(self, _params=new_params)

    def cookie(self, name: str, value: str) -> RequestBuilder:
        new_cookies = dict(self._cookies)
        new_cookies[name] = value

        return replace(self, _cookies=new_cookies)

    def cookies(self, cookies: CookiesType) -> RequestBuilder:
        new_cookies = dict(self._cookies)
        new_cookies.update(cookies)

        return replace(self, _cookies=new_cookies)

    def data(self, data: bytes | str | MutableMapping[str, Any]) -> RequestBuilder:
        return replace(self, _data=data, _json=None)

    def json(self, obj: JSONType) -> RequestBuilder:
        return replace(self, _json=obj, _data=None)

    def file(
        self,
        field_name: str,
        file_obj: io.IOBase | bytes,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> RequestBuilder:
        """
        Adds a single multipart file. Creates/merges into _files dict.
        file_obj can be a file-like object or raw bytes.
        """

        if self._files is None:
            files = {}

        else:
            files = dict(self._files)

        if isinstance(file_obj, (bytes, bytearray)):
            file_obj = io.BytesIO(file_obj)

        files[field_name] = (filename or "upload.bin", file_obj, content_type)

        return replace(self, _files=files)

    def timeout(self, seconds: TimeoutType) -> RequestBuilder:
        return replace(self, _timeout=seconds)

    def auth(self, auth: AuthType) -> RequestBuilder:
        return replace(self, _auth=auth)

    def basic_auth(self, username: str, password: str) -> RequestBuilder:
        return replace(self, _auth=(username, password))

    def build(self) -> requests.PreparedRequest:
        if not self._url:
            raise ValueError("URL is required. Call .url('https://...') before build().")

        req = requests.Request(
            method=self._method,
            url=self._url,
            headers=self._headers or None,
            params=self._params or None,
            data=self._data,
            json=self._json,
            files=self._files,
            cookies=self._cookies or None,
            auth=self._auth,
        )

        return req.prepare()

    def send(
        self,
        session: requests.Session | None = None,
        *,
        raise_for_status: bool = False,
        stream: bool = False,
        allow_redirects: bool = True,
        proxies: dict[str, str] | None = None,
        verify: bool | str | None = None,
    ) -> requests.Response:
        """
        Builds and sends the request. If no session is provided, a one-off Session is used.
        """

        prepared = self.build()
        sess = session or requests.Session()

        if self._cookies:
            jar = requests.cookies.cookiejar_from_dict(self._cookies)
            sess.cookies.update(jar)

        resp = sess.send(
            prepared,
            timeout=self._timeout,
            stream=stream,
            allow_redirects=allow_redirects,
            proxies=proxies,
            verify=verify,
        )

        if raise_for_status:
            resp.raise_for_status()

        return resp

    def clone(self) -> RequestBuilder:
        """Create a deep-ish copy suitable for branching variants."""

        return replace(
            self,
            _headers=dict(self._headers),
            _params=dict(self._params),
            _cookies=dict(self._cookies),
            _files=dict(self._files) if self._files else None,
        )
