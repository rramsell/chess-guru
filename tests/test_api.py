"""Offline unit tests for ChesscomAPI, using an in-repo fake aiohttp session.

Retry, header and URL handling shared with LichessAPI is covered in test_http.py.
"""

import asyncio
from datetime import datetime, timezone

import pytest

import raw_game_fixtures as fx
from chess_guru import ChesscomAPI, Game, GameCollection
from fake_session import FakeSession
from pgn_fixtures import NO_CLOCKS, WHITE_MATE_WITH_CLOCKS

BASE = "https://api.chess.com/pub"
USER = "alice"
ARCHIVES_URL = f"{BASE}/player/{USER}/games/archives"


def month_url(year: int, month: int) -> str:
    return f"{BASE}/player/{USER}/games/{year}/{month:02d}"


def ts(*args) -> int:
    return int(datetime(*args, tzinfo=timezone.utc).timestamp())


@pytest.fixture
def mocked():
    return FakeSession()


@pytest.fixture
def api(mocked):
    return ChesscomAPI(mocked)


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


async def test_request_endpoint_joins_base_url(api, mocked):
    mocked.add(f"{BASE}/player/{USER}", payload={"username": USER})
    assert await api._request(endpoint=f"/player/{USER}") == {"username": USER}
    assert mocked.calls(f"{BASE}/player/{USER}") == 1


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
    mocked.add(f"{BASE}/{path}", payload={"path": path})
    assert await getattr(api, method)(USER) == {"path": path}


# --- get_games ----------------------------------------------------------------


def game(end_time, pgn=WHITE_MATE_WITH_CLOCKS, **extra):
    g = {"url": f"https://www.chess.com/game/live/{end_time}", "pgn": pgn, **extra}
    if end_time is not None:
        g["end_time"] = end_time
    return g


def mock_archives(m, *year_months):
    m.add(
        ARCHIVES_URL, payload={"archives": [month_url(y, mo) for y, mo in year_months]}
    )


async def test_get_games_no_filter_returns_everything(api, mocked):
    mock_archives(mocked, (2024, 5), (2024, 6))
    mocked.add(
        month_url(2024, 5), payload={"games": [game(ts(2024, 5, 1)), game(None)]}
    )
    mocked.add(
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
    mocked.add(
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
    mocked.add(
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
    assert mocked.calls(month_url(2024, 4)) == 0
    assert mocked.calls(month_url(2024, 7)) == 0
    assert out["errors"] == {}
    may = [g["end_time"] for g in out["months"][month_url(2024, 5)]["games"]]
    june = [g["end_time"] for g in out["months"][month_url(2024, 6)]["games"]]
    assert may == [ts(2024, 5, 15), ts(2024, 5, 20)]
    assert june == [ts(2024, 6, 1), ts(2024, 6, 10)]
    assert out["from_ts"] == "2024-05-15T00:00:00+00:00"
    assert out["to_ts"] == "2024-06-10T00:00:00+00:00"


async def test_get_games_only_from_ts(api, mocked):
    mock_archives(mocked, (2023, 12), (2024, 1))
    mocked.add(month_url(2024, 1), payload={"games": [game(ts(2024, 1, 2))]})

    out = await api.get_games(USER, from_ts=datetime(2024, 1, 1, tzinfo=timezone.utc))

    assert out["archives"] == [month_url(2024, 1)]
    assert out["to_ts"] is None
    assert mocked.calls(month_url(2023, 12)) == 0


async def test_get_games_records_failed_month_in_errors(api, mocked):
    mock_archives(mocked, (2024, 5), (2024, 6), (2024, 7))
    mocked.add(month_url(2024, 5), payload={"games": [game(ts(2024, 5, 1))]})
    mocked.add(month_url(2024, 6), status=404)
    mocked.add(month_url(2024, 7), status=500, repeat=True)

    out = await api.get_games(USER)

    assert list(out["months"]) == [month_url(2024, 5)]
    assert set(out["errors"]) == {month_url(2024, 6), month_url(2024, 7)}
    assert "404" in out["errors"][month_url(2024, 6)]
    assert "500" in out["errors"][month_url(2024, 7)]
    assert mocked.calls(month_url(2024, 6)) == 1
    assert mocked.calls(month_url(2024, 7)) == 5
    # the archive list still reports every month that was attempted
    assert len(out["archives"]) == 3


async def test_get_games_keeps_game_when_pgn_unparseable(api, mocked):
    mock_archives(mocked, (2024, 5))
    mocked.add(
        month_url(2024, 5), payload={"games": [game(ts(2024, 5, 1), pgn="garbage")]}
    )

    out = await api.get_games(USER)

    (g,) = out["months"][month_url(2024, 5)]["games"]
    assert g["pgn"] == "garbage"
    assert "parsed_pgn" not in g


async def test_get_games_does_not_mutate_payload_extras(api, mocked):
    mock_archives(mocked, (2024, 5))
    mocked.add(
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
        mocked.add(month_url(y, mo), payload={"games": []}, callback=slow)

    out = await api.get_games(USER, max_concurrency=3)

    assert len(out["months"]) == 8
    assert peak == 3


# --- unified games ------------------------------------------------------------


def real_game(end_time, n, base=fx.CHESSCOM_BLITZ_MATE, **extra):
    url = f"https://www.chess.com/game/live/{n}"
    return {**base, "url": url, "uuid": f"uuid-{n}", "end_time": end_time, **extra}


async def test_get_unified_games_newest_first_across_months(api, mocked):
    mock_archives(mocked, (2024, 5), (2024, 6))
    mocked.add(
        month_url(2024, 5),
        payload={"games": [real_game(ts(2024, 5, 1), 1), real_game(ts(2024, 5, 9), 2)]},
    )
    mocked.add(
        month_url(2024, 6),
        payload={
            "games": [
                real_game(ts(2024, 6, 2), 3, fx.CHESSCOM_AGREED),
                real_game(ts(2024, 6, 3), 4, fx.CHESSCOM_DAILY),
            ]
        },
    )

    out = await api.get_unified_games(USER)

    assert isinstance(out, GameCollection)
    assert (out.provider, out.username, out.errors) == ("chesscom", USER, {})
    assert [g.id for g in out.games] == ["uuid-4", "uuid-3", "uuid-2", "uuid-1"]
    assert all(isinstance(g, Game) for g in out.games)
    assert out.games[1].termination == "draw_agreement"
    assert out.games[0].speed == "correspondence"
    assert out.games[0].raw is None


async def test_get_unified_games_time_filter(api, mocked):
    mock_archives(mocked, (2024, 4), (2024, 5), (2024, 6))
    mocked.add(
        month_url(2024, 5),
        payload={
            "games": [
                real_game(ts(2024, 5, 14, 23, 59, 59), 1),
                real_game(ts(2024, 5, 15), 2),
                real_game(ts(2024, 5, 31), 3),
            ]
        },
    )
    mocked.add(
        month_url(2024, 6),
        payload={
            "games": [real_game(ts(2024, 6, 10), 4), real_game(ts(2024, 6, 11), 5)]
        },
    )

    out = await api.get_unified_games(
        USER,
        from_ts=datetime(2024, 5, 15, tzinfo=timezone.utc),
        to_ts=datetime(2024, 6, 10),
    )

    assert [g.id for g in out.games] == ["uuid-4", "uuid-3", "uuid-2"]
    assert mocked.calls(month_url(2024, 4)) == 0
    assert out.from_ts == datetime(2024, 5, 15, tzinfo=timezone.utc)
    assert out.to_ts == datetime(2024, 6, 10, tzinfo=timezone.utc)


async def test_get_unified_games_collects_errors(api, mocked):
    mock_archives(mocked, (2024, 5), (2024, 6))
    broken = real_game(ts(2024, 5, 2), 2, white="not a dict")
    mocked.add(
        month_url(2024, 5), payload={"games": [real_game(ts(2024, 5, 1), 1), broken]}
    )
    mocked.add(month_url(2024, 6), status=404)

    out = await api.get_unified_games(USER)

    assert [g.id for g in out.games] == ["uuid-1"]
    assert set(out.errors) == {month_url(2024, 6), broken["url"]}
    assert "404" in out.errors[month_url(2024, 6)]
    assert "AttributeError" in out.errors[broken["url"]]


async def test_get_unified_games_include_raw(api, mocked):
    mock_archives(mocked, (2024, 5))
    raw = real_game(ts(2024, 5, 1), 1)
    mocked.add(month_url(2024, 5), payload={"games": [raw]})

    out = await api.get_unified_games(USER, include_raw=True)

    # parsed_pgn is added by the client and left out of raw
    assert out.games[0].raw == raw


async def test_iter_unified_games_skips_bad_games(api, mocked):
    mock_archives(mocked, (2024, 5))
    mocked.add(
        month_url(2024, 5),
        payload={
            "games": [
                real_game(ts(2024, 5, 1), 1),
                real_game(ts(2024, 5, 2), 2, black="oops"),
            ]
        },
    )

    games = [g async for g in api.iter_unified_games(USER)]

    assert [g.id for g in games] == ["uuid-1"]


async def test_get_unified_games_passes_max_concurrency(api, mocked):
    months = [(2024, m) for m in range(1, 5)]
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
        mocked.add(month_url(y, mo), payload={"games": []}, callback=slow)

    out = await api.get_unified_games(USER, max_concurrency=2)

    assert out.games == [] and peak == 2


async def test_get_unified_games_rejects_unknown_kwargs(api, mocked):
    with pytest.raises(TypeError):
        await api.get_unified_games(USER, max_games=5)


async def test_get_unified_games_rejects_inverted_range(api, mocked):
    with pytest.raises(ValueError, match="from_ts must be <= to_ts"):
        await api.get_unified_games(
            USER,
            from_ts=datetime(2024, 2, 1, tzinfo=timezone.utc),
            to_ts=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
    assert not mocked.requests
