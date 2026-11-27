import os
from datetime import datetime, timedelta, timezone

import aiohttp
import pytest

from chess_guru import LichessAPI

USERNAME = os.environ.get("LICHESS_TEST_USERNAME") or "Zhigalko_Sergei"
TOKEN = os.environ.get("LICHESS_TOKEN") or None
pytestmark = [pytest.mark.integration, pytest.mark.lichess]


@pytest.fixture
async def api():
    async with aiohttp.ClientSession() as session:
        yield LichessAPI(session, token=TOKEN)


async def test_get_user(api):
    data = await api.get_user(USERNAME)
    assert data["username"].lower() == USERNAME.lower()
    assert "perfs" in data


async def test_get_games_with_parsed_pgn(api):
    out = await api.get_games(USERNAME, max_games=20)

    assert out["username"] == USERNAME
    assert 0 < len(out["games"]) <= 20
    for game in out["games"]:
        assert "pgn" in game
        parsed = game["parsed_pgn"]
        assert parsed["headers"]["Site"].startswith("https://lichess.org/")
        assert parsed["moves"]


async def test_get_games_last_30_days_respects_bounds(api):
    to_ts = datetime.now(timezone.utc)
    from_ts = to_ts - timedelta(days=30)

    out = await api.get_games(USERNAME, from_ts=from_ts, to_ts=to_ts, max_games=50)

    for game in out["games"]:
        ended = datetime.fromtimestamp(game["lastMoveAt"] / 1000, tz=timezone.utc)
        assert from_ts <= ended <= to_ts


async def test_nonexistent_user_returns_404(api):
    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await api.get_user("nonexistent_user_xyz123")
    assert exc.value.status == 404
