# chess-guru

Async Python client for the Chess.com Public API.

Built on `aiohttp` with automatic retries for rate limits and server errors. Doesn't mess with your logging config. Supports time-based filtering and concurrent month fetching.

## Install
```bash
pip install chess-guru
```

Requires Python 3.9+.

## Quickstart
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

## Return structure

`get_games()` returns a dict with these keys:
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

## Time filtering

Pass `from_ts` and/or `to_ts` as datetime objects to filter by game end time. Both should be UTC (naive datetimes are assumed to be UTC).
```python
from datetime import datetime, timezone

from_ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
to_ts = datetime(2024, 6, 30, 23, 59, 59, tzinfo=timezone.utc)

data = await api.get_games("erik", from_ts=from_ts, to_ts=to_ts)
```

The filter works in two passes: first it skips months outside your time range, then it filters individual games by `end_time` within the months that remain.

## Concurrency control

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
    user_agent="chess-guru/0.1.0",
    headers=None
)

api.get_player(username)
api.get_archives(username)
api.get_games(username, max_concurrency=10, from_ts=None, to_ts=None)
```

## License

PolyForm Noncommercial 1.0.0 — free for noncommercial use.  
Commercial licensing: richramsell@proton.me
