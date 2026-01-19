import aiohttp
import pytest

from chess_guru import ChesscomAPI


USERNAME = "richardramsell"
pytestmark = pytest.mark.integration


@pytest.fixture
async def api():
    async with aiohttp.ClientSession() as session:
        yield ChesscomAPI(session)


@pytest.mark.asyncio
async def test_get_games_includes_parsed_pgn(api):
    out = await api.get_games(USERNAME, max_concurrency=4)

    parsed_count = 0
    for month in out["months"].values():
        for game in month.get("games", []):
            if "pgn" in game:
                assert "parsed_pgn" in game
                parsed = game["parsed_pgn"]
                assert "headers" in parsed
                assert "result" in parsed
                assert "moves" in parsed
                parsed_count += 1

    assert parsed_count > 0
