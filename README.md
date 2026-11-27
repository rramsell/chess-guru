# chess-guru

[![tests](https://github.com/rramsell/chess-guru/actions/workflows/tests.yml/badge.svg)](https://github.com/rramsell/chess-guru/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/chess-guru.svg)](https://pypi.org/project/chess-guru/)

Async Python clients for the [Chess.com Public API](https://www.chess.com/news/view/published-data-api) and the [Lichess API](https://lichess.org/api).

Built on `aiohttp` with automatic retries for rate limits and server errors. Doesn't mess with your logging config. Supports time-based filtering, concurrent month fetching for Chess.com and streamed game exports for Lichess. Games come back with a `parsed_pgn` (headers, result, and each move's SAN, clock and engine eval when present).

`get_games()` on each client returns that provider's own shape. For one shape across both, use the [unified games](#unified-games) methods, which return pydantic models.

- PyPI: [chess-guru](https://pypi.org/project/chess-guru/)
- Source: [github.com/rramsell/chess-guru](https://github.com/rramsell/chess-guru)
- Changelog: [CHANGELOG.md](https://github.com/rramsell/chess-guru/blob/main/CHANGELOG.md)

## Install
```bash
pip install chess-guru
```

Requires Python 3.9+.

## Quickstart (Chess.com)
```python
import asyncio
import aiohttp
from chess_guru import ChesscomAPI

async def main():
    async with aiohttp.ClientSession() as session:
        api = ChesscomAPI(session, user_agent="my-app/1.0")
        
        profile = await api.get_player("erik")
        print(profile.get("username"), profile.get("country"))
        
        data = await api.get_games("erik", max_concurrency=8)
        print("months fetched:", len(data["months"]))
        
        first_month = next(iter(data["months"].values()))
        print("games in first month:", len(first_month.get("games", [])))

asyncio.run(main())
```

You can also pass a custom user agent via headers:
```python
api = ChesscomAPI(session, headers={"User-Agent": "my-app/1.0"})
```

## Quickstart (Lichess)
```python
import asyncio
import aiohttp
from chess_guru import LichessAPI

async def main():
    async with aiohttp.ClientSession() as session:
        api = LichessAPI(session, user_agent="my-app/1.0 (you@example.com)")

        profile = await api.get_user("DrNykterstein")
        print(profile["username"], profile["perfs"]["blitz"]["rating"])

        data = await api.get_games("DrNykterstein", max_games=20, perf_type="blitz")
        for game in data["games"]:
            print(game["id"], game["parsed_pgn"]["result"])

        # or stream them one at a time
        async for game in api.iter_games("DrNykterstein", max_games=5):
            print(game["id"])

asyncio.run(main())
```

### Token

Public data doesn't need a token, but a [personal API token](https://lichess.org/account/oauth/token) gets you a faster game export:
```python
api = LichessAPI(session, token="lip_...")
```
It's sent as `Authorization: Bearer <token>`.

### Rate limits

Lichess asks clients to make one request at a time and to wait a minute after a `429`. `LichessAPI` waits 60 seconds on a `429` and backs off exponentially on server and connection errors. Only the initial request of a game export is retried: if the stream breaks partway through, the error is raised rather than restarting the export and repeating games. Lichess also asks for a `User-Agent` that identifies your app or gives a way to contact you.

## Unified games

`get_unified_games()` returns a `GameCollection` of `Game` models with the same fields for both providers, newest first. `iter_unified_games()` yields the same `Game` objects one at a time.
```python
import asyncio
from datetime import datetime, timedelta, timezone

import aiohttp
from chess_guru import ChesscomAPI, LichessAPI

async def main():
    to_ts = datetime.now(timezone.utc)
    from_ts = to_ts - timedelta(days=30)

    async with aiohttp.ClientSession() as session:
        chesscom = ChesscomAPI(session, user_agent="my-app/1.0")
        lichess = LichessAPI(session, user_agent="my-app/1.0 (you@example.com)")

        games = await chesscom.get_unified_games("erik", from_ts=from_ts, to_ts=to_ts)
        print(len(games.games), games.errors)

        async for game in lichess.iter_unified_games(
            "DrNykterstein", from_ts=from_ts, to_ts=to_ts, perf_type="blitz"
        ):
            print(game.end_time, game.white.username, game.result, game.termination)

asyncio.run(main())
```

`from_ts` / `to_ts` work exactly as in `get_games()`. Other keyword arguments go to the provider's `get_games()`: `max_concurrency` for Chess.com; `max_games`, `perf_type`, `rated`, `color`, `vs` and `created_lookback` for Lichess.

To fetch from both at once:
```python
from chess_guru import fetch_all_games

chesscom_games, lichess_games = await fetch_all_games(
    session, chesscom="erik", lichess="DrNykterstein", from_ts=from_ts, to_ts=to_ts
)
```

### Game fields

- `provider`: `"chesscom"` or `"lichess"`
- `id`, `url`: the Chess.com game `uuid` (or the number at the end of the URL) / the Lichess game id
- `rated`
- `variant`, `variant_raw`: `"standard"`, `"chess960"`, `"crazyhouse"`, `"king_of_the_hill"`, `"three_check"`, ... (snake_case for both providers)
- `speed`, `speed_raw`: `"ultrabullet"`, `"bullet"`, `"blitz"`, `"rapid"`, `"classical"`, `"correspondence"` or `"other"`
- `time_control`: `initial_seconds`, `increment_seconds`, `days_per_move`, `raw`
- `start_time`, `end_time`: UTC-aware datetimes
- `white`, `black`: `username`, `rating`, `rating_diff`, `title`, `ai_level`, `result_raw`
- `result`: `"1-0"`, `"0-1"`, `"1/2-1/2"` or `"*"`; `winner`: `"white"`, `"black"` or `None`
- `termination`, `termination_raw`: `"checkmate"`, `"resignation"`, `"timeout"`, `"timeout_vs_insufficient"`, `"draw_agreement"`, `"stalemate"`, `"repetition"`, `"insufficient_material"`, `"fifty_move"`, `"abandoned"`, `"aborted"`, `"variant_end"` or `"other"`
- `opening`: `eco`, `name`
- `initial_fen` (only when the game didn't start from the standard position), `final_fen`
- `pgn`, `headers` (parsed PGN headers)
- `moves`: one `Move` per ply with `ply`, `move_number`, `color`, `san`, `clock_seconds`, `eval_cp` and `eval_mate` (evals from white's side)
- `raw`: the provider's game dict, only with `include_raw=True`

Values that don't map to the lists above come through as `"other"` (or unchanged, for `variant`) with the provider's value kept in the matching `*_raw` field, so a new value from either API doesn't break validation.

### Mapping notes

- **Chess.com termination** comes from the per-player result codes. The losing side's code is used (`"win"` vs `"checkmated"` is a checkmate); for draws both sides carry the same code. Each player's code is kept in `result_raw`.
- **Chess.com daily** games have `speed="correspondence"` and `time_control.days_per_move` set. Chess.com only sends `start_time` for daily games; for live games it comes from the PGN `UTCDate`/`UTCTime` headers.
- **Chess.com opening names** come from the ECO URL with the move list dropped, e.g. `"Sicilian Defense Alapin Variation"`.
- **Lichess draws** don't say why the game was drawn: agreement, repetition and the 50-move rule are all `"draw"`, and the PGN `Termination` header just says `"Normal"`. They come through as `termination="other"`, `termination_raw="draw"`. Stalemate and running out of time against insufficient material are reported separately.
- **Lichess `timeout`** means a player left the game and the opponent claimed the win, so it maps to `"abandoned"`. Running out of clock is `outoftime`, which maps to `"timeout"`.
- **Lichess `fromPosition`** games have `variant="standard"`, `variant_raw="fromPosition"` and `initial_fen` set.
- **Lichess correspondence** time controls use the same `raw` format as Chess.com daily, e.g. `"1/259200"` for three days a move.
- Games without a usable PGN still convert: Lichess moves fall back to the plain `moves` string (no clocks or evals), Chess.com games get an empty `moves` list.

### Errors

A game that fails to convert is skipped instead of failing the whole request. `get_unified_games()` lists it in `GameCollection.errors`, keyed by game URL (Chess.com) or id (Lichess), along with any Chess.com months that failed to fetch. `iter_unified_games()` only logs them at debug level.

### JSON and raw data

The models are frozen pydantic v2 models, so the usual pydantic API works:
```python
data = games.model_dump(mode="json")  # plain dicts, ISO datetimes
text = games.model_dump_json()
again = GameCollection.model_validate_json(text)
```
Pass `include_raw=True` to keep each provider's original game dict on `Game.raw` (left out of `repr()`).

The converters are plain functions if you already have raw game dicts:
```python
from chess_guru import game_from_chesscom, game_from_lichess

game = game_from_lichess(raw_lichess_game)
```

## Return structure (Chess.com)

`ChesscomAPI.get_games()` returns a dict with these keys:
```python
{
  "username": "erik",
  "archives": ["https://api.chess.com/pub/player/erik/games/2024/06", ...],
  "months": {
    "https://api.chess.com/pub/player/erik/games/2024/06": {
      "games": [{...}, {...}, ...]
      # full month payload from chess.com
    }
  },
  "errors": {
    "https://...": "ClientError(...)"
    # month URLs that failed to fetch
  },
  "from_ts": "2024-01-01T00:00:00+00:00",  # or None
  "to_ts": "2024-06-30T23:59:59+00:00"     # or None
}
```

If a monthly archive fails to fetch, it shows up in `errors` but doesn't kill the whole request.

## Return structure (Lichess)

`LichessAPI.get_games()` returns:
```python
{
  "username": "DrNykterstein",
  "games": [{...}, {...}, ...],  # Lichess game dicts, newest first, each with "parsed_pgn"
  "from_ts": "2024-01-01T00:00:00+00:00",  # or None
  "to_ts": "2024-06-30T23:59:59+00:00"     # or None
}
```

Games are requested with `pgnInJson`, `clocks`, `evals` and `opening` turned on, so each one has a `pgn` field and moves carry clocks and evals where Lichess has them.

## Parsed PGN

Both clients add `parsed_pgn` to every game whose PGN parses (if it doesn't, the game is kept without it):
```python
{
  "headers": {"Event": "Rated blitz game", "White": "...", ...},
  "result": "1-0",  # or "0-1", "1/2-1/2", "*", None
  "moves": {
    1: {
      "white": {"move": "e4", "clock": "0:02:59", "eval": "0.17"},
      "black": {"move": "e5", "clock": "0:02:58", "eval": "0.2"},
    },
    ...
  },
}
```
`clock` and `eval` are strings as written in the PGN (`eval` can be a mate score like `"#-3"`), or `None` when absent.

## Time filtering

Pass `from_ts` and/or `to_ts` as datetime objects to keep games that **ended** within the range, inclusive. Both should be UTC (naive datetimes are assumed to be UTC). This works the same way for both clients.
```python
from datetime import datetime, timezone

from_ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
to_ts = datetime(2024, 6, 30, 23, 59, 59, tzinfo=timezone.utc)

data = await api.get_games("erik", from_ts=from_ts, to_ts=to_ts)
```

For Chess.com the filter works in two passes: first it skips months outside your time range, then it filters individual games by `end_time` within the months that remain.

For Lichess, games are matched on `lastMoveAt`. The Lichess `since`/`until` parameters filter on when a game *started*, so they're only used to narrow the request: `until` is set to `to_ts`, and `since` to `from_ts - created_lookback` (default one day) to catch games that started before `from_ts` but ended after it. Raise `created_lookback` for long games such as correspondence:
```python
from datetime import timedelta

data = await api.get_games(
    "someone", from_ts=from_ts, to_ts=to_ts, created_lookback=timedelta(days=30)
)
```
`max_games` is applied by Lichess before the end-time filter, so with a time range you can get back fewer games than `max_games`. Games without a `lastMoveAt` are dropped when a range is given.

## Concurrency control (Chess.com)

`max_concurrency` limits how many month requests run in parallel:
```python
data = await api.get_games("erik", max_concurrency=5)
```

Default is 10. If you're hitting rate limits, lower it. If you want faster fetching and the API can handle it, raise it.

## Logging

The library uses Python's standard logging but doesn't configure anything by default. If you want to see retry warnings or debug output:
```python
import logging
logging.basicConfig(level=logging.WARNING)
```

Set level to `INFO` or `DEBUG` for more detail.

## API methods
```python
ChesscomAPI(
    session,
    base_url="https://api.chess.com/pub",
    timeout_sec=20,
    user_agent="chess-guru/<installed version>",
    headers=None
)

api.get_player(username)
api.get_player_stats(username)
api.get_games_to_move(username)
api.get_tournaments(username)
api.get_archives(username)
api.get_games(username, max_concurrency=10, from_ts=None, to_ts=None)
api.get_unified_games(username, *, from_ts=None, to_ts=None, include_raw=False,
                      max_concurrency=10)
api.iter_unified_games(username, ...)  # same arguments

LichessAPI(
    session,
    token=None,
    base_url="https://lichess.org",
    timeout_sec=20,  # applied per read for the game export stream
    user_agent="chess-guru/<installed version>",
    headers=None
)

api.get_user(username)
api.get_rating_history(username)
api.get_perf(username, perf)  # e.g. "blitz", "rapid", "correspondence"
api.iter_games(username, *, from_ts=None, to_ts=None, max_games=None,
               perf_type=None, rated=None, color=None, vs=None,
               created_lookback=timedelta(days=1))
api.get_games(username, ...)  # same arguments as iter_games
api.get_unified_games(username, *, from_ts=None, to_ts=None, include_raw=False,
                      **iter_games_kwargs)
api.iter_unified_games(username, ...)  # same arguments

fetch_all_games(session, *, chesscom=None, lichess=None, from_ts=None, to_ts=None,
                include_raw=False, user_agent="chess-guru/<installed version>")
```

## Development
```bash
uv sync --group dev
uv run pytest                    # offline unit tests (default)
uv run pytest -m integration     # live tests against both APIs
uv run pytest -m "integration and chesscom"
uv run pytest -m "integration and lichess"
```

The integration tests read these optional environment variables:
- `CHESSCOM_TEST_USERNAME`: Chess.com account to test against
- `LICHESS_TEST_USERNAME`: Lichess account to test against
- `LICHESS_TOKEN`: Lichess API token (the tests pass without it)

## License

MIT. See [LICENSE](LICENSE).
