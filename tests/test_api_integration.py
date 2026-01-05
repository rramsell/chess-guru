import aiohttp
import pytest
from datetime import datetime, timezone, timedelta

from chesscom_guru import ChesscomAPI


USERNAME = "richardramsell"
pytestmark = pytest.mark.integration


@pytest.fixture
async def api():
    async with aiohttp.ClientSession() as session:
        yield ChesscomAPI(session)


@pytest.mark.asyncio
async def test_get_player(api):
    data = await api.get_player(USERNAME)
    assert data["username"].lower() == USERNAME.lower()
    assert "url" in data or "player_id" in data


@pytest.mark.asyncio
async def test_get_archives(api):
    data = await api.get_archives(USERNAME)
    assert "archives" in data
    assert len(data["archives"]) > 0
    assert all("/games/" in url for url in data["archives"])


@pytest.mark.asyncio
async def test_get_games_basic(api):
    out = await api.get_games(USERNAME, max_concurrency=4)
    
    assert out["username"] == USERNAME
    assert len(out["months"]) >= 1
    assert any(m.get("games") for m in out["months"].values())


@pytest.mark.asyncio
async def test_get_games_with_time_filter(api):
    to_ts = datetime.now(timezone.utc)
    from_ts = to_ts - timedelta(days=30)
    
    out = await api.get_games(USERNAME, max_concurrency=4, from_ts=from_ts, to_ts=to_ts)
    
    from_dt = datetime.fromisoformat(out["from_ts"])
    to_dt = datetime.fromisoformat(out["to_ts"])
    
    for month in out["months"].values():
        for game in month.get("games", []):
            game_dt = datetime.fromtimestamp(game["end_time"], tz=timezone.utc)
            assert from_dt <= game_dt <= to_dt


@pytest.mark.asyncio
async def test_get_games_rejects_invalid_range(api):
    # from_ts after to_ts should fail
    with pytest.raises(ValueError):
        await api.get_games(
            USERNAME,
            from_ts=datetime(2024, 2, 1, tzinfo=timezone.utc),
            to_ts=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )


@pytest.mark.asyncio
async def test_nonexistent_player_returns_404(api):
    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await api.get_player("nonexistent_user_xyz123")
    assert exc.value.status == 404
