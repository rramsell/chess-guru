import json

import raw_game_fixtures as fx
from chess_guru import fetch_all_games
from fake_session import FakeSession

CHESSCOM_ARCHIVES = "https://api.chess.com/pub/player/alice/games/archives"
CHESSCOM_MONTH = "https://api.chess.com/pub/player/alice/games/2024/01"
LICHESS_GAMES = "https://lichess.org/api/games/user/bob"


async def test_fetch_all_games_queries_both_providers():
    session = FakeSession()
    session.add(CHESSCOM_ARCHIVES, payload={"archives": [CHESSCOM_MONTH]})
    session.add(CHESSCOM_MONTH, payload={"games": [fx.CHESSCOM_BLITZ_MATE]})
    session.add(LICHESS_GAMES, chunks=[json.dumps(fx.LICHESS_RESIGN).encode()])

    chesscom, lichess = await fetch_all_games(
        session, chesscom="alice", lichess="bob", user_agent="test/1.0"
    )

    assert (chesscom.provider, chesscom.username) == ("chesscom", "alice")
    assert (lichess.provider, lichess.username) == ("lichess", "bob")
    assert len(chesscom.games) == len(lichess.games) == 1
    assert session.headers(LICHESS_GAMES)["User-Agent"] == "test/1.0"


async def test_fetch_all_games_skips_providers_without_username():
    session = FakeSession()
    session.add(LICHESS_GAMES, chunks=[])

    out = await fetch_all_games(session, lichess="bob")

    assert [c.provider for c in out] == ["lichess"]
    assert not session.requests.get(CHESSCOM_ARCHIVES)
