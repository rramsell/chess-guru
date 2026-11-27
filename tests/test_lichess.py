"""Offline unit tests for LichessAPI, using an in-repo fake aiohttp session."""

import asyncio
import json
from datetime import datetime, timedelta, timezone

import aiohttp
import pytest

import lichess_pgn_fixtures as li
import raw_game_fixtures as fx
from chess_guru import GameCollection, LichessAPI
from fake_session import FakeSession

BASE = "https://lichess.org"
USER = "alice"
GAMES_URL = f"{BASE}/api/games/user/{USER}"


def ms(*args) -> int:
    return int(datetime(*args, tzinfo=timezone.utc).timestamp() * 1000)


def game(last_move_at, pgn=li.CLOCKS_ONLY, **extra) -> dict:
    g = {"id": f"g{last_move_at}", "createdAt": 0, "pgn": pgn, **extra}
    if last_move_at is not None:
        g["lastMoveAt"] = last_move_at
    return g


def ndjson(*games) -> bytes:
    return b"".join(json.dumps(g).encode() + b"\n" for g in games)


@pytest.fixture
def mocked():
    return FakeSession()


@pytest.fixture
def api(mocked):
    return LichessAPI(mocked)


@pytest.fixture(autouse=True)
def sleeps(monkeypatch):
    real_sleep = asyncio.sleep
    delays = []

    async def fast_sleep(delay, *args, **kwargs):
        delays.append(delay)
        await real_sleep(0)

    monkeypatch.setattr(asyncio, "sleep", fast_sleep)
    return delays


# --- simple endpoints ---------------------------------------------------------


@pytest.mark.parametrize(
    "method, args, path",
    [
        ("get_user", (USER,), f"api/user/{USER}"),
        ("get_rating_history", (USER,), f"api/user/{USER}/rating-history"),
        ("get_perf", (USER, "blitz"), f"api/user/{USER}/perf/blitz"),
    ],
)
async def test_simple_endpoints(api, mocked, method, args, path):
    mocked.add(f"{BASE}/{path}", payload={"path": path})
    assert await getattr(api, method)(*args) == {"path": path}
    assert mocked.headers(f"{BASE}/{path}")["Accept"] == "application/json"


async def test_token_sets_authorization_header(mocked):
    url = f"{BASE}/api/user/{USER}"
    mocked.add(url, payload={})
    mocked.add(GAMES_URL, chunks=[])
    api = LichessAPI(mocked, token="lip_secret")

    await api.get_user(USER)
    await api.get_games(USER)

    assert mocked.headers(url)["Authorization"] == "Bearer lip_secret"
    assert mocked.headers(GAMES_URL)["Authorization"] == "Bearer lip_secret"


async def test_no_authorization_header_without_token(api, mocked):
    url = f"{BASE}/api/user/{USER}"
    mocked.add(url, payload={})
    await api.get_user(USER)
    assert "Authorization" not in mocked.headers(url)


# --- game export request --------------------------------------------------------


async def test_default_games_params_and_headers(api, mocked):
    mocked.add(GAMES_URL, chunks=[])
    await api.get_games(USER)

    assert mocked.params(GAMES_URL) == {
        "pgnInJson": "true",
        "clocks": "true",
        "evals": "true",
        "opening": "true",
        "lastFen": "true",
    }
    headers = mocked.headers(GAMES_URL)
    assert headers["Accept"] == "application/x-ndjson"
    assert headers["User-Agent"].startswith("chess-guru/")


async def test_games_params_with_filters(api, mocked):
    mocked.add(GAMES_URL, chunks=[])
    await api.get_games(
        USER,
        from_ts=datetime(2024, 6, 1, tzinfo=timezone.utc),
        to_ts=datetime(2024, 6, 30),  # naive -> UTC
        max_games=50,
        perf_type=["blitz", "rapid"],
        rated=False,
        color="black",
        vs="bob",
    )

    params = mocked.params(GAMES_URL)
    assert params["since"] == str(ms(2024, 5, 31))  # default 1 day lookback
    assert params["until"] == str(ms(2024, 6, 30))
    assert params["max"] == "50"
    assert params["perfType"] == "blitz,rapid"
    assert params["rated"] == "false"
    assert params["color"] == "black"
    assert params["vs"] == "bob"


async def test_created_lookback_and_single_perf_type(api, mocked):
    mocked.add(GAMES_URL, chunks=[])
    await api.get_games(
        USER,
        from_ts=datetime(2024, 6, 1, tzinfo=timezone.utc),
        created_lookback=timedelta(days=14),
        perf_type="correspondence",
        rated=True,
    )

    params = mocked.params(GAMES_URL)
    assert params["since"] == str(ms(2024, 5, 18))
    assert "until" not in params
    assert params["perfType"] == "correspondence"
    assert params["rated"] == "true"


async def test_since_is_clamped_to_lichess_minimum(api, mocked):
    mocked.add(GAMES_URL, chunks=[])
    await api.get_games(USER, from_ts=datetime(2010, 1, 1, tzinfo=timezone.utc))
    assert mocked.params(GAMES_URL)["since"] == "1356998400070"


async def test_get_games_rejects_inverted_range_without_network(api, mocked):
    with pytest.raises(ValueError, match="from_ts must be <= to_ts"):
        await api.get_games(
            USER,
            from_ts=datetime(2024, 2, 1, tzinfo=timezone.utc),
            to_ts=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
    with pytest.raises(ValueError, match="from_ts must be <= to_ts"):
        async for _ in api.iter_games(
            USER,
            from_ts=datetime(2024, 2, 1, tzinfo=timezone.utc),
            to_ts=datetime(2024, 1, 1, tzinfo=timezone.utc),
        ):
            pass
    assert not mocked.requests


# --- NDJSON parsing ---------------------------------------------------------------


async def test_get_games_return_shape(api, mocked):
    mocked.add(GAMES_URL, chunks=[ndjson(game(1), game(2, pgn=li.CLOCKS_AND_EVALS))])

    out = await api.get_games(USER)

    assert set(out) == {"username", "games", "from_ts", "to_ts"}
    assert out["username"] == USER
    assert out["from_ts"] is None and out["to_ts"] is None
    assert [g["id"] for g in out["games"]] == ["g1", "g2"]
    assert out["games"][0]["parsed_pgn"]["result"] == "1-0"
    first = out["games"][1]["parsed_pgn"]["moves"][1]["white"]
    assert first == {"move": "e4", "clock": "0:03:00", "eval": "0.17"}


async def test_ndjson_split_across_chunks_with_blank_lines(api, mocked):
    body = b"\n" + ndjson(game(1)) + b"\n\n" + ndjson(game(2)) + b"  \n"
    body += json.dumps(game(3)).encode()  # no trailing newline
    chunks = [body[i : i + 7] for i in range(0, len(body), 7)]
    mocked.add(GAMES_URL, chunks=chunks)

    out = await api.get_games(USER)

    assert [g["id"] for g in out["games"]] == ["g1", "g2", "g3"]
    assert mocked.closed == 1


async def test_bad_pgn_keeps_game(api, mocked):
    mocked.add(GAMES_URL, chunks=[ndjson(game(1, pgn="garbage"), game(2, pgn=None))])

    out = await api.get_games(USER)

    assert [g["id"] for g in out["games"]] == ["g1", "g2"]
    assert all("parsed_pgn" not in g for g in out["games"])


async def test_iter_games_matches_get_games(api, mocked):
    body = [ndjson(game(1), game(2), game(3, pgn=li.DRAW))]
    mocked.add(GAMES_URL, chunks=body)
    mocked.add(GAMES_URL, chunks=body)

    streamed = [g async for g in api.iter_games(USER)]
    collected = await api.get_games(USER)

    assert streamed == collected["games"]
    assert len(streamed) == 3


async def test_closing_iter_games_early_releases_response(api, mocked):
    mocked.add(GAMES_URL, chunks=[ndjson(game(1)), ndjson(game(2))])

    gen = api.iter_games(USER)
    assert (await gen.__anext__())["id"] == "g1"
    assert mocked.closed == 0
    await gen.aclose()

    assert mocked.closed == 1


# --- lastMoveAt filter ------------------------------------------------------------


async def test_last_move_at_filter_is_inclusive(api, mocked):
    lo, hi = ms(2024, 6, 1), ms(2024, 6, 30)
    games = [
        game(hi + 1),
        game(hi),
        game(ms(2024, 6, 15)),
        game(lo),
        game(lo - 1),
        game(None),
    ]
    mocked.add(GAMES_URL, chunks=[ndjson(*games)])

    out = await api.get_games(
        USER,
        from_ts=datetime(2024, 6, 1, tzinfo=timezone.utc),
        to_ts=datetime(2024, 6, 30, tzinfo=timezone.utc),
    )

    assert [g["lastMoveAt"] for g in out["games"]] == [hi, ms(2024, 6, 15), lo]
    assert out["from_ts"] == "2024-06-01T00:00:00+00:00"
    assert out["to_ts"] == "2024-06-30T00:00:00+00:00"


async def test_missing_last_move_at_kept_without_filter(api, mocked):
    mocked.add(GAMES_URL, chunks=[ndjson(game(None), game(1))])
    out = await api.get_games(USER)
    assert len(out["games"]) == 2


async def test_only_to_ts_filters_upper_bound(api, mocked):
    mocked.add(GAMES_URL, chunks=[ndjson(game(ms(2024, 2, 1)), game(ms(2024, 1, 1)))])
    out = await api.get_games(USER, to_ts=datetime(2024, 1, 15, tzinfo=timezone.utc))
    assert [g["lastMoveAt"] for g in out["games"]] == [ms(2024, 1, 1)]
    assert "since" not in mocked.params(GAMES_URL)


# --- retries on the stream ---------------------------------------------------------


async def test_429_waits_a_minute_then_streams(api, mocked, sleeps):
    mocked.add(GAMES_URL, status=429)
    mocked.add(GAMES_URL, chunks=[ndjson(game(1))])

    out = await api.get_games(USER)

    assert len(out["games"]) == 1
    assert sleeps == [60]
    assert mocked.calls(GAMES_URL) == 2


async def test_5xx_and_connection_errors_retried(api, mocked):
    mocked.add(GAMES_URL, status=502)
    mocked.add(GAMES_URL, exception=aiohttp.ClientConnectionError("boom"))
    mocked.add(GAMES_URL, chunks=[ndjson(game(1))])

    out = await api.get_games(USER)

    assert len(out["games"]) == 1
    assert mocked.calls(GAMES_URL) == 3


async def test_404_is_terminal(api, mocked):
    mocked.add(GAMES_URL, status=404, repeat=True)

    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await api.get_games(USER)
    assert exc.value.status == 404
    assert mocked.calls(GAMES_URL) == 1
    assert mocked.closed == 1


async def test_error_mid_stream_is_not_retried(api, mocked):
    mocked.add(
        GAMES_URL,
        chunks=[ndjson(game(1)), aiohttp.ClientPayloadError("cut off")],
        repeat=True,
    )

    seen = []
    with pytest.raises(aiohttp.ClientPayloadError):
        async for g in api.iter_games(USER):
            seen.append(g["id"])

    assert seen == ["g1"]
    assert mocked.calls(GAMES_URL) == 1
    assert mocked.closed == 1


# --- unified games -----------------------------------------------------------------


def real_game(last_move_at, game_id, base=fx.LICHESS_BLITZ_MATE, **extra) -> dict:
    return {**base, "id": game_id, "lastMoveAt": last_move_at, **extra}


async def test_get_unified_games(api, mocked):
    mocked.add(
        GAMES_URL,
        chunks=[
            ndjson(
                real_game(ms(2024, 6, 3), "g3"),
                real_game(ms(2024, 6, 2), "g2", fx.LICHESS_DRAW),
                real_game(ms(2024, 6, 1), "g1", fx.LICHESS_NO_PGN),
            )
        ],
    )

    out = await api.get_unified_games(USER)

    assert isinstance(out, GameCollection)
    assert (out.provider, out.username, out.errors) == ("lichess", USER, {})
    assert [g.id for g in out.games] == ["g3", "g2", "g1"]
    assert out.games[0].termination == "checkmate"
    assert out.games[0].moves[0].eval_cp == 18
    assert out.games[1].result == "1/2-1/2"
    assert out.games[2].pgn is None and out.games[2].moves
    assert out.games[0].raw is None


async def test_get_unified_games_time_filter(api, mocked):
    mocked.add(
        GAMES_URL,
        chunks=[
            ndjson(
                real_game(ms(2024, 6, 10, 0, 0, 1), "late"),
                real_game(ms(2024, 6, 10), "edge"),
                real_game(ms(2024, 5, 15), "start"),
                real_game(ms(2024, 5, 14, 23, 59, 59), "early"),
            )
        ],
    )

    out = await api.get_unified_games(
        USER,
        from_ts=datetime(2024, 5, 15, tzinfo=timezone.utc),
        to_ts=datetime(2024, 6, 10),
    )

    assert [g.id for g in out.games] == ["edge", "start"]
    assert out.to_ts == datetime(2024, 6, 10, tzinfo=timezone.utc)
    assert mocked.params(GAMES_URL)["until"] == str(ms(2024, 6, 10))


async def test_get_unified_games_collects_conversion_errors(api, mocked):
    broken = real_game(ms(2024, 6, 1), "bad", players={"white": "oops"})
    mocked.add(GAMES_URL, chunks=[ndjson(real_game(ms(2024, 6, 2), "good"), broken)])

    out = await api.get_unified_games(USER)

    assert [g.id for g in out.games] == ["good"]
    assert list(out.errors) == ["bad"]
    assert "AttributeError" in out.errors["bad"]


async def test_iter_unified_games_streams_and_skips_bad_games(api, mocked):
    broken = real_game(ms(2024, 6, 1), "bad", players={"black": 1})
    mocked.add(
        GAMES_URL,
        chunks=[ndjson(real_game(ms(2024, 6, 2), "good")), ndjson(broken)],
    )

    gen = api.iter_unified_games(USER)
    first = await gen.__anext__()
    assert first.id == "good"
    assert [g async for g in gen] == []
    assert mocked.closed == 1


async def test_get_unified_games_include_raw(api, mocked):
    raw = real_game(ms(2024, 6, 1), "g1")
    mocked.add(GAMES_URL, chunks=[ndjson(raw)])

    out = await api.get_unified_games(USER, include_raw=True)

    assert out.games[0].raw == raw
    assert "parsed_pgn" not in out.games[0].raw


async def test_get_unified_games_passes_provider_kwargs(api, mocked):
    mocked.add(GAMES_URL, chunks=[])

    await api.get_unified_games(
        USER,
        from_ts=datetime(2024, 5, 15, tzinfo=timezone.utc),
        max_games=10,
        perf_type=["blitz", "rapid"],
        rated=True,
        color="white",
        vs="bob",
        created_lookback=timedelta(days=3),
    )

    params = mocked.params(GAMES_URL)
    assert params["max"] == "10"
    assert params["perfType"] == "blitz,rapid"
    assert (params["rated"], params["color"], params["vs"]) == ("true", "white", "bob")
    assert params["since"] == str(ms(2024, 5, 12))


async def test_get_unified_games_rejects_unknown_kwargs(api, mocked):
    with pytest.raises(TypeError):
        await api.get_unified_games(USER, max_concurrency=4)


async def test_get_unified_games_rejects_inverted_range(api, mocked):
    with pytest.raises(ValueError, match="from_ts must be <= to_ts"):
        await api.get_unified_games(
            USER,
            from_ts=datetime(2024, 2, 1, tzinfo=timezone.utc),
            to_ts=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
    assert not mocked.requests
