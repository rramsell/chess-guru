"""A minimal stand-in for aiohttp.ClientSession used by the unit tests.

ChesscomAPI only calls ``session.get(url, **kwargs)`` as an async context
manager and uses ``status``, ``raise_for_status()`` and ``json()`` on the
response. Faking just that surface keeps the tests independent of aiohttp
internals, while errors are still real ``aiohttp`` exception types.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional

import aiohttp
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL


@dataclass
class _Route:
    status: int = 200
    payload: Any = None
    exception: Optional[BaseException] = None
    callback: Optional[Callable[..., Awaitable[None]]] = None
    repeat: bool = False


class FakeResponse:
    def __init__(self, url: str, status: int, payload: Any) -> None:
        self.url = URL(url)
        self.status = status
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status >= 400:
            request_info = aiohttp.RequestInfo(
                self.url, "GET", CIMultiDictProxy(CIMultiDict()), self.url
            )
            raise aiohttp.ClientResponseError(
                request_info, (), status=self.status, message=f"HTTP {self.status}"
            )

    async def json(self, content_type: Optional[str] = "application/json") -> Any:
        return self._payload


class _RequestContext:
    def __init__(self, session: FakeSession, url: str, kwargs: dict) -> None:
        self._session = session
        self._url = url
        self._kwargs = kwargs

    async def __aenter__(self) -> FakeResponse:
        self._session.requests[self._url].append(self._kwargs)
        queue = self._session._routes.get(self._url)
        if not queue:
            raise aiohttp.ClientConnectionError(f"No fake route for GET {self._url}")
        route = queue[0] if queue[0].repeat else queue.pop(0)
        if route.callback is not None:
            await route.callback(self._url, **self._kwargs)
        if route.exception is not None:
            raise route.exception
        return FakeResponse(self._url, route.status, route.payload)

    async def __aexit__(self, *exc_info: Any) -> None:
        return None


class FakeSession:
    """Register responses with ``add(url, ...)``; each is used once, in order,
    unless ``repeat=True``. Requests made are recorded in ``requests``."""

    def __init__(self) -> None:
        self._routes: dict[str, list[_Route]] = defaultdict(list)
        self.requests: dict[str, list[dict]] = defaultdict(list)

    def add(self, url: str, **route: Any) -> None:
        self._routes[url].append(_Route(**route))

    def calls(self, url: str) -> int:
        return len(self.requests.get(url, []))

    def get(self, url: str, **kwargs: Any) -> _RequestContext:
        return _RequestContext(self, url, kwargs)
