# chess-guru

[![tests](https://github.com/rramsell/chess-guru/actions/workflows/tests.yml/badge.svg)](https://github.com/rramsell/chess-guru/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/chess-guru.svg)](https://pypi.org/project/chess-guru/)

Async Python clients for the [Chess.com Public API](https://www.chess.com/news/view/published-data-api) and the [Lichess API](https://lichess.org/api).

Built on `aiohttp` with automatic retries for rate limits and server errors. Doesn't mess with your logging config. Supports time-based filtering, concurrent month fetching for Chess.com and streamed game exports for Lichess. Games come back with a `parsed_pgn` (headers, result, and each move's SAN, clock and engine eval when present).

The two clients return provider-specific shapes; see the sections below.

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
