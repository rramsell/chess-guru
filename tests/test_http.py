"""Behaviour shared by every client through BaseAPIClient."""

import asyncio
from typing import Any, Callable, NamedTuple

import aiohttp
import pytest

from chess_guru import ChesscomAPI, LichessAPI
from chess_guru._http import DEFAULT_USER_AGENT, _terminal_error
from fake_session import FakeSession

USER = "alice"


class Client(NamedTuple):
    api: Any
    base: str
    url: str  # what `call` hits
    call: Callable[[Any], Any]
    name: str


def make_client(kind: str, session: FakeSession, **kwargs: Any) -> Client:
    if kind == "chesscom":
        api = ChesscomAPI(session, **kwargs)
        base = api.base_url.rstrip("/")
        return Client(
            api, base, f"{base}/player/{USER}", lambda a: a.get_player(USER), kind
        )
    api = LichessAPI(session, **kwargs)
    base = api.base_url.rstrip("/")
    return Client(
        api, base, f"{base}/api/user/{USER}", lambda a: a.get_user(USER), kind
    )


@pytest.fixture
def mocked():
    return FakeSession()


@pytest.fixture(params=["chesscom", "lichess"])
def kind(request):
    return request.param


@pytest.fixture
def client(kind, mocked):
    return make_client(kind, mocked)


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    """Make backoff waits instant and record how long they would have been."""
    real_sleep = asyncio.sleep
    delays = []

    async def fast_sleep(delay, *args, **kwargs):
        delays.append(delay)
        await real_sleep(0)

    monkeypatch.setattr(asyncio, "sleep", fast_sleep)
    return delays


# --- url / endpoint handling ---------------------------------------------------


async def test_request_requires_exactly_one_of_url_or_endpoint(client, mocked):
    with pytest.raises(ValueError):
        await client.api._request_json()
    with pytest.raises(ValueError):
        await client.api._request_json(url=client.url, endpoint="x")
    assert not mocked.requests


@pytest.mark.parametrize(
    "kind, bad_url, provider",
    [
        ("chesscom", "https://evil.example.com/pub/player/alice", "chess.com"),
        ("chesscom", "https://api.chess.com/pubx/player/alice", "chess.com"),
        ("chesscom", "http://api.chess.com/pub/player/alice", "chess.com"),
        ("lichess", "https://lichess.org.evil.com/api/user/alice", "lichess"),
        ("lichess", "http://lichess.org/api/user/alice", "lichess"),
    ],
)
async def test_request_rejects_url_outside_base(client, mocked, bad_url, provider):
    with pytest.raises(ValueError, match=f"not a valid {provider} url"):
        await client.api._request_json(url=bad_url)
    assert not mocked.requests


async def test_request_url_inside_base_is_allowed(client, mocked):
    mocked.add(client.url, payload={"ok": True})
    assert await client.api._request_json(url=client.url) == {"ok": True}


@pytest.mark.parametrize(
    "kind, base_url",
    [("chesscom", "https://proxy.local/pub/"), ("lichess", "https://proxy.local/")],
)
async def test_custom_base_url_trailing_slash_is_normalised(kind, mocked, base_url):
    client = make_client(kind, mocked, base_url=base_url + "/")
    assert client.api.base_url == base_url
    mocked.add(client.url, payload={"ok": True})
    assert await client.call(client.api) == {"ok": True}


async def test_headers_are_sent_and_overridable(kind, mocked):
    client = make_client(
        kind, mocked, headers={"User-Agent": "my-app/1.0", "X-Extra": "1"}
    )
    mocked.add(client.url, payload={})
    await client.call(client.api)
    assert mocked.headers(client.url) == {
        "User-Agent": "my-app/1.0",
        "Accept": "application/json",
        "X-Extra": "1",
    }


def test_default_user_agent(kind, mocked):
    from importlib.metadata import version

    import chess_guru

    assert chess_guru.__version__ == version("chess-guru")
    assert DEFAULT_USER_AGENT == f"chess-guru/{chess_guru.__version__}"
    assert make_client(kind, mocked).api.headers["User-Agent"] == DEFAULT_USER_AGENT


# --- retry / giveup -------------------------------------------------------------


@pytest.mark.parametrize("status", [429, 500, 502, 503])
async def test_retries_on_429_and_5xx(client, mocked, status):
    mocked.add(client.url, status=status)
    mocked.add(client.url, status=status)
    mocked.add(client.url, payload={"username": USER})

    assert await client.call(client.api) == {"username": USER}
    assert mocked.calls(client.url) == 3


async def test_gives_up_after_max_tries_on_5xx(client, mocked):
    mocked.add(client.url, status=503, repeat=True)

    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await client.call(client.api)
    assert exc.value.status == 503
    assert mocked.calls(client.url) == 5


@pytest.mark.parametrize("status", [400, 401, 403, 404, 410])
async def test_gives_up_immediately_on_4xx(client, mocked, status):
    mocked.add(client.url, status=status, repeat=True)

    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await client.call(client.api)
    assert exc.value.status == status
    assert mocked.calls(client.url) == 1


async def test_retries_connection_errors(client, mocked):
    mocked.add(client.url, exception=aiohttp.ClientConnectionError("boom"))
    mocked.add(client.url, exception=asyncio.TimeoutError())
    mocked.add(client.url, payload={"username": USER})

    assert await client.call(client.api) == {"username": USER}
    assert mocked.calls(client.url) == 3


async def test_lichess_waits_a_minute_after_429(mocked, sleeps):
    client = make_client("lichess", mocked)
    mocked.add(client.url, status=429)
    mocked.add(client.url, status=500)
    mocked.add(client.url, payload={})

    await client.call(client.api)

    assert sleeps[0] == 60
    assert 0 <= sleeps[1] <= 2  # 5xx falls back to exponential


def test_terminal_error_classification():
    def err(status):
        return aiohttp.ClientResponseError(None, (), status=status)

    assert _terminal_error(err(404)) is True
    assert _terminal_error(err(400)) is True
    assert _terminal_error(err(429)) is False
    assert _terminal_error(err(500)) is False
    assert _terminal_error(aiohttp.ClientConnectionError()) is False
    # Backwards-compatible aliases still work.
    assert ChesscomAPI._terminal_error(err(404)) is True
    assert LichessAPI._terminal_error(err(404)) is True


def test_api_module_reexports():
    from chess_guru import api

    assert api.ChesscomAPI is ChesscomAPI
    assert api._terminal_error is _terminal_error
    assert api.DEFAULT_USER_AGENT == DEFAULT_USER_AGENT
