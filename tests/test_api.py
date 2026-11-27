"""Offline unit tests for ChesscomAPI. HTTP is mocked with aioresponses."""

import asyncio
from datetime import datetime, timezone

import aiohttp
import pytest
from aioresponses import aioresponses
from yarl import URL

from chess_guru import ChesscomAPI
from chess_guru.api import _terminal_error
from pgn_fixtures import NO_CLOCKS, WHITE_MATE_WITH_CLOCKS

BASE = "https://api.chess.com/pub"
USER = "alice"
ARCHIVES_URL = f"{BASE}/player/{USER}/games/archives"


def month_url(year: int, month: int) -> str:
    return f"{BASE}/player/{USER}/games/{year}/{month:02d}"


def ts(*args) -> int:
    return int(datetime(*args, tzinfo=timezone.utc).timestamp())


def calls(m: aioresponses, url: str) -> int:
    return len(m.requests.get(("GET", URL(url)), []))


@pytest.fixture
def mocked():
    with aioresponses() as m:
        yield m


@pytest.fixture
async def api():
    async with aiohttp.ClientSession() as session:
        yield ChesscomAPI(session)


@pytest.fixture(autouse=True)
def no_backoff_sleep(monkeypatch):
    """Make backoff's exponential waits instant."""
    real_sleep = asyncio.sleep

    async def fast_sleep(_delay, *args, **kwargs):
        await real_sleep(0)

    monkeypatch.setattr(asyncio, "sleep", fast_sleep)


# --- _request url / endpoint validation ---------------------------------------


async def test_request_requires_exactly_one_of_url_or_endpoint(api, mocked):
    with pytest.raises(ValueError):
        await api._request()
    with pytest.raises(ValueError):
        await api._request(url=f"{BASE}/player/{USER}", endpoint=f"player/{USER}")
    assert not mocked.requests


@pytest.mark.parametrize(
    "bad_url",
    [
        "https://evil.example.com/pub/player/alice",
        "https://api.chess.com/pubx/player/alice",
        "http://api.chess.com/pub/player/alice",
    ],
)
async def test_request_rejects_url_outside_base(api, mocked, bad_url):
    with pytest.raises(ValueError, match="not a valid chess.com url"):
        await api._request(url=bad_url)
    assert not mocked.requests


async def test_request_endpoint_joins_base_url(api, mocked):
    mocked.get(f"{BASE}/player/{USER}", payload={"username": USER})
    assert await api._request(endpoint=f"/player/{USER}") == {"username": USER}
    assert calls(mocked, f"{BASE}/player/{USER}") == 1


async def test_custom_base_url_trailing_slash_is_normalised(mocked):
    mocked.get("https://proxy.local/pub/player/alice", payload={"ok": True})
    async with aiohttp.ClientSession() as session:
        api = ChesscomAPI(session, base_url="https://proxy.local/pub/")
        assert api.base_url == "https://proxy.local/pub/"
        assert await api.get_player("alice") == {"ok": True}


async def test_headers_are_sent_and_overridable(mocked):
    mocked.get(f"{BASE}/player/{USER}", payload={})
    async with aiohttp.ClientSession() as session:
        api = ChesscomAPI(session, headers={"User-Agent": "my-app/1.0", "X-Extra": "1"})
        await api.get_player(USER)
    sent = mocked.requests[("GET", URL(f"{BASE}/player/{USER}"))][0].kwargs["headers"]
    assert sent == {
        "User-Agent": "my-app/1.0",
        "Accept": "application/json",
        "X-Extra": "1",
    }


@pytest.mark.parametrize(
    "method, path",
    [
        ("get_player", f"player/{USER}"),
        ("get_player_stats", f"player/{USER}/stats"),
        ("get_games_to_move", f"player/{USER}/games/to-move"),
        ("get_tournaments", f"player/{USER}/tournaments"),
        ("get_archives", f"player/{USER}/games/archives"),
    ],
)
async def test_simple_endpoints(api, mocked, method, path):
    mocked.get(f"{BASE}/{path}", payload={"path": path})
    assert await getattr(api, method)(USER) == {"path": path}


# --- retry / giveup -----------------------------------------------------------


@pytest.mark.parametrize("status", [429, 500, 502, 503])
async def test_retries_on_429_and_5xx(api, mocked, status):
    url = f"{BASE}/player/{USER}"
    mocked.get(url, status=status)
    mocked.get(url, status=status)
    mocked.get(url, payload={"username": USER})

    assert await api.get_player(USER) == {"username": USER}
    assert calls(mocked, url) == 3


async def test_gives_up_after_max_tries_on_5xx(api, mocked):
    url = f"{BASE}/player/{USER}"
    mocked.get(url, status=503, repeat=True)

    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await api.get_player(USER)
    assert exc.value.status == 503
    assert calls(mocked, url) == 5


@pytest.mark.parametrize("status", [400, 401, 403, 404, 410])
async def test_gives_up_immediately_on_4xx(api, mocked, status):
    url = f"{BASE}/player/{USER}"
    mocked.get(url, status=status, repeat=True)

    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await api.get_player(USER)
    assert exc.value.status == status
    assert calls(mocked, url) == 1


async def test_retries_connection_errors(api, mocked):
    url = f"{BASE}/player/{USER}"
    mocked.get(url, exception=aiohttp.ClientConnectionError("boom"))
    mocked.get(url, exception=asyncio.TimeoutError())
    mocked.get(url, payload={"username": USER})

    assert await api.get_player(USER) == {"username": USER}
    assert calls(mocked, url) == 3


def test_terminal_error_classification():
    def err(status):
        return aiohttp.ClientResponseError(None, (), status=status)

    assert _terminal_error(err(404)) is True
    assert _terminal_error(err(400)) is True
    assert _terminal_error(err(429)) is False
    assert _terminal_error(err(500)) is False
    assert _terminal_error(aiohttp.ClientConnectionError()) is False
    # Backwards-compatible alias still works.
    assert ChesscomAPI._terminal_error(err(404)) is True


# --- get_games ----------------------------------------------------------------


def game(end_time, pgn=WHITE_MATE_WITH_CLOCKS, **extra):
    g = {"url": f"https://www.chess.com/game/live/{end_time}", "pgn": pgn, **extra}
    if end_time is not None:
        g["end_time"] = end_time
    return g


def mock_archives(m, *year_months):
    m.get(
        ARCHIVES_URL, payload={"archives": [month_url(y, mo) for y, mo in year_months]}
    )


async def test_get_games_no_filter_returns_everything(api, mocked):
    mock_archives(mocked, (2024, 5), (2024, 6))
    mocked.get(
        month_url(2024, 5), payload={"games": [game(ts(2024, 5, 1)), game(None)]}
    )
    mocked.get(
        month_url(2024, 6), payload={"games": [game(ts(2024, 6, 1), pgn=NO_CLOCKS)]}
    )

    out = await api.get_games(USER)

    assert set(out) == {"username", "archives", "months", "errors", "from_ts", "to_ts"}
    assert out["username"] == USER
    assert out["archives"] == [month_url(2024, 5), month_url(2024, 6)]
    assert out["errors"] == {}
    assert out["from_ts"] is None and out["to_ts"] is None
    assert len(out["months"][month_url(2024, 5)]["games"]) == 2
    june = out["months"][month_url(2024, 6)]["games"][0]
    assert june["parsed_pgn"]["result"] == "1-0"
    assert june["parsed_pgn"]["moves"][1]["black"]["move"] == "e5"


async def test_get_games_time_filter_across_months(api, mocked):
    mock_archives(mocked, (2024, 4), (2024, 5), (2024, 6), (2024, 7))
    mocked.get(
        month_url(2024, 5),
        payload={
            "games": [
                game(ts(2024, 5, 14, 23, 59, 59)),  # before from_ts
                game(ts(2024, 5, 15)),  # exactly from_ts -> kept
                game(ts(2024, 5, 20)),
                game(None),  # no end_time -> dropped when filtering
            ]
        },
    )
    mocked.get(
        month_url(2024, 6),
        payload={
            "games": [
                game(ts(2024, 6, 1)),
                game(ts(2024, 6, 10)),  # exactly to_ts -> kept
                game(ts(2024, 6, 10, 0, 0, 1)),  # after to_ts
            ]
        },
    )

    out = await api.get_games(
        USER,
        from_ts=datetime(2024, 5, 15, tzinfo=timezone.utc),
        to_ts=datetime(2024, 6, 10),  # naive -> treated as UTC
    )

    assert out["archives"] == [month_url(2024, 5), month_url(2024, 6)]
    assert calls(mocked, month_url(2024, 4)) == 0
    assert calls(mocked, month_url(2024, 7)) == 0
    assert out["errors"] == {}
    may = [g["end_time"] for g in out["months"][month_url(2024, 5)]["games"]]
    june = [g["end_time"] for g in out["months"][month_url(2024, 6)]["games"]]
    assert may == [ts(2024, 5, 15), ts(2024, 5, 20)]
    assert june == [ts(2024, 6, 1), ts(2024, 6, 10)]
    assert out["from_ts"] == "2024-05-15T00:00:00+00:00"
    assert out["to_ts"] == "2024-06-10T00:00:00+00:00"


async def test_get_games_only_from_ts(api, mocked):
    mock_archives(mocked, (2023, 12), (2024, 1))
    mocked.get(month_url(2024, 1), payload={"games": [game(ts(2024, 1, 2))]})

    out = await api.get_games(USER, from_ts=datetime(2024, 1, 1, tzinfo=timezone.utc))

    assert out["archives"] == [month_url(2024, 1)]
    assert out["to_ts"] is None
    assert calls(mocked, month_url(2023, 12)) == 0


async def test_get_games_records_failed_month_in_errors(api, mocked):
    mock_archives(mocked, (2024, 5), (2024, 6), (2024, 7))
    mocked.get(month_url(2024, 5), payload={"games": [game(ts(2024, 5, 1))]})
    mocked.get(month_url(2024, 6), status=404)
    mocked.get(month_url(2024, 7), status=500, repeat=True)

    out = await api.get_games(USER)

    assert list(out["months"]) == [month_url(2024, 5)]
    assert set(out["errors"]) == {month_url(2024, 6), month_url(2024, 7)}
    assert "404" in out["errors"][month_url(2024, 6)]
    assert "500" in out["errors"][month_url(2024, 7)]
    assert calls(mocked, month_url(2024, 6)) == 1
    assert calls(mocked, month_url(2024, 7)) == 5
    # the archive list still reports every month that was attempted
    assert len(out["archives"]) == 3


async def test_get_games_keeps_game_when_pgn_unparseable(api, mocked):
    mock_archives(mocked, (2024, 5))
    mocked.get(
        month_url(2024, 5), payload={"games": [game(ts(2024, 5, 1), pgn="garbage")]}
    )

    out = await api.get_games(USER)

    (g,) = out["months"][month_url(2024, 5)]["games"]
    assert g["pgn"] == "garbage"
    assert "parsed_pgn" not in g


async def test_get_games_does_not_mutate_payload_extras(api, mocked):
    mock_archives(mocked, (2024, 5))
    mocked.get(
        month_url(2024, 5), payload={"games": [game(ts(2024, 5, 1))], "extra": 1}
    )

    out = await api.get_games(USER)

    assert out["months"][month_url(2024, 5)]["extra"] == 1


async def test_get_games_rejects_inverted_range_without_network(api, mocked):
    with pytest.raises(ValueError, match="from_ts must be <= to_ts"):
        await api.get_games(
            USER,
            from_ts=datetime(2024, 2, 1, tzinfo=timezone.utc),
            to_ts=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
    assert not mocked.requests


async def test_get_games_respects_max_concurrency(api, mocked):
    months = [(2024, m) for m in range(1, 9)]
    mock_archives(mocked, *months)
    in_flight = 0
    peak = 0

    async def slow(url, **kwargs):
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        for _ in range(5):
            await asyncio.sleep(0)
        in_flight -= 1

    for y, mo in months:
        mocked.get(month_url(y, mo), payload={"games": []}, callback=slow)

    out = await api.get_games(USER, max_concurrency=3)

    assert len(out["months"]) == 8
    assert peak == 3


def test_default_user_agent_matches_package_version():
    from importlib.metadata import version

    import chess_guru
    from chess_guru.api import DEFAULT_USER_AGENT

    assert chess_guru.__version__ == version("chess-guru")
    assert DEFAULT_USER_AGENT == f"chess-guru/{chess_guru.__version__}"
    assert ChesscomAPI(session=None).headers["User-Agent"] == DEFAULT_USER_AGENT
