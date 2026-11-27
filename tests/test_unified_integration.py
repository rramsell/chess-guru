import os
from datetime import datetime, timedelta, timezone

import aiohttp
import pytest

from chess_guru import ChesscomAPI, GameCollection, LichessAPI

CHESSCOM_USERNAME = os.environ.get("CHESSCOM_TEST_USERNAME") or "JobandJethro"
LICHESS_USERNAME = os.environ.get("LICHESS_TEST_USERNAME") or "Zhigalko_Sergei"
LICHESS_TOKEN = os.environ.get("LICHESS_TOKEN") or None

pytestmark = pytest.mark.integration


def last_30_days():
    to_ts = datetime.now(timezone.utc)
    return to_ts - timedelta(days=30), to_ts


def check_collection(out: GameCollection, from_ts, to_ts) -> None:
    for game in out.games:
        assert from_ts <= game.end_time <= to_ts
        if game.variant == "standard" and game.termination not in (
            "aborted",
            "abandoned",
        ):
            assert game.moves, game.url
    ends = [g.end_time for g in out.games]
    assert ends == sorted(ends, reverse=True)
    assert GameCollection.model_validate_json(out.model_dump_json()) == out


@pytest.mark.chesscom
async def test_chesscom_unified_last_30_days():
    from_ts, to_ts = last_30_days()
    async with aiohttp.ClientSession() as session:
        api = ChesscomAPI(session)
        out = await api.get_unified_games(
            CHESSCOM_USERNAME, from_ts=from_ts, to_ts=to_ts, max_concurrency=2
        )

    assert out.provider == "chesscom"
    assert out.errors == {}
    check_collection(out, from_ts, to_ts)


@pytest.mark.lichess
async def test_lichess_unified_last_30_days():
    from_ts, to_ts = last_30_days()
    async with aiohttp.ClientSession() as session:
        api = LichessAPI(session, token=LICHESS_TOKEN)
        out = await api.get_unified_games(
            LICHESS_USERNAME,
            from_ts=from_ts,
            to_ts=to_ts,
            max_games=100,
            include_raw=True,
        )

    assert out.provider == "lichess"
    assert out.errors == {}
    assert out.games
    assert all(g.raw and g.raw["id"] == g.id for g in out.games)
    check_collection(out, from_ts, to_ts)
