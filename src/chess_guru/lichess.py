from __future__ import annotations

import json
import random
from datetime import datetime, timedelta
from typing import Any, AsyncIterator, Generator, Optional, Sequence, Union

import aiohttp

from ._http import DEFAULT_USER_AGENT, BaseAPIClient, logger
from .models import Game
from .normalize import game_from_lichess
from .utils import attach_parsed_pgn, game_in_range, to_utc_dt

# Lichess asks clients to wait a full minute after a 429.
RATE_LIMIT_WAIT_SEC = 60.0

# Lowest `since` value the games export accepts (ms).
_MIN_SINCE_MS = 1356998400070


def _lichess_wait_gen() -> Generator[Any, Any, None]:
    # backoff sends in the exception that caused each retry
    exc = yield
    n = 0
    while True:
        if isinstance(exc, aiohttp.ClientResponseError) and exc.status == 429:
            exc = yield RATE_LIMIT_WAIT_SEC
        else:
            exc = yield random.uniform(0, 2**n)
            n += 1


def _to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def _bool_param(value: bool) -> str:
    return "true" if value else "false"


class LichessAPI(BaseAPIClient):
    provider_name = "lichess"
    provider_key = "lichess"
    retry_jitter = None
    _retry_wait_gen = staticmethod(_lichess_wait_gen)

    def __init__(
        self,
        session: aiohttp.ClientSession,
        token: Optional[str] = None,
        base_url: str = "https://lichess.org",
        timeout_sec: float = 20,
        user_agent: str = DEFAULT_USER_AGENT,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Creates a Lichess API client using an existing aiohttp session

        Args:
            session:
                An already-created aiohttp.ClientSession. The caller owns the session
                lifecycle
            token:
                Optional personal API token, sent as ``Authorization: Bearer``.
                Not needed for public data, but gives higher rate limits
            base_url:
                Base URL for the Lichess API
            timeout_sec:
                Total timeout for JSON requests. For the game export stream it is
                applied per read instead, since a long export can take minutes
            user_agent:
                User-Agent header value. Lichess asks for something that
                identifies your app or a way to contact you
            headers:
                Optional extra headers merged over the defaults (including
                "Authorization")
        """
        auth = {"Authorization": f"Bearer {token}"} if token else {}
        super().__init__(
            session,
            base_url=base_url,
            timeout_sec=timeout_sec,
            user_agent=user_agent,
            headers={**auth, **(headers or {})},
        )
        self.stream_timeout = aiohttp.ClientTimeout(
            total=None, sock_connect=timeout_sec, sock_read=timeout_sec
        )

    async def get_user(self, username: str) -> dict:
        """Public profile data for a Lichess user."""
        return await self._request_json(endpoint=f"api/user/{username}")

    async def get_rating_history(self, username: str) -> list:
        """Rating history per perf; points are ``[year, month0, day, rating]``."""
        return await self._request_json(endpoint=f"api/user/{username}/rating-history")

    async def get_perf(self, username: str, perf: str) -> dict:
        """Detailed stats for one perf type, e.g. "blitz" or "correspondence"."""
        return await self._request_json(endpoint=f"api/user/{username}/perf/{perf}")

    def _games_params(
        self,
        from_dt: Optional[datetime],
        to_dt: Optional[datetime],
        max_games: Optional[int],
        perf_type: Optional[Union[str, Sequence[str]]],
        rated: Optional[bool],
        color: Optional[str],
        vs: Optional[str],
        created_lookback: timedelta,
    ) -> dict[str, str]:
        params = {
            "pgnInJson": "true",
            "clocks": "true",
            "evals": "true",
            "opening": "true",
        }
        # since/until filter on creation time; games are matched on end time
        # afterwards, so reach back far enough to catch games that started early.
        if from_dt is not None:
            since = _to_ms(from_dt - created_lookback)
            params["since"] = str(max(since, _MIN_SINCE_MS))
        if to_dt is not None:
            params["until"] = str(_to_ms(to_dt))
        if max_games is not None:
            params["max"] = str(max_games)
        if perf_type:
            if not isinstance(perf_type, str):
                perf_type = ",".join(perf_type)
            params["perfType"] = perf_type
        if rated is not None:
            params["rated"] = _bool_param(rated)
        if color is not None:
            params["color"] = color
        if vs is not None:
            params["vs"] = vs
        return params

    async def _open_stream(self, url: str, **kwargs: Any) -> tuple[Any, Any]:
        ctx = self.session.get(url, **kwargs)
        response = await ctx.__aenter__()
        try:
            self._raise_for_status(response, url)
        except BaseException as e:
            await ctx.__aexit__(type(e), e, e.__traceback__)
            raise
        return ctx, response

    async def iter_games(
        self,
        username: str,
        *,
        from_ts: Optional[datetime] = None,
        to_ts: Optional[datetime] = None,
        max_games: Optional[int] = None,
        perf_type: Optional[Union[str, Sequence[str]]] = None,
        rated: Optional[bool] = None,
        color: Optional[str] = None,
        vs: Optional[str] = None,
        created_lookback: timedelta = timedelta(days=1),
    ) -> AsyncIterator[dict]:
        """
        Streams a user's games, newest first, as raw Lichess game dicts with
        ``parsed_pgn`` attached.

        Args:
            username: lichess username
            from_ts / to_ts:
                Keep games that *ended* (``lastMoveAt``) within the range,
                inclusive. Naive datetimes are treated as UTC
            max_games:
                Passed to Lichess as ``max``. It's applied before the end-time
                filter, so you can get back fewer games than this
            perf_type: e.g. "blitz" or ["blitz", "rapid"]
            rated: True for rated only, False for casual only
            color: "white" or "black"
            vs: only games against this opponent
            created_lookback:
                How far before ``from_ts`` to ask Lichess for games, since its
                filter works on start time. Raise it for long games such as
                correspondence

        Only the initial request is retried. An error mid-stream is raised
        rather than restarting the export, which would repeat games.
        """
        from_dt = to_utc_dt(from_ts)
        to_dt = to_utc_dt(to_ts)
        if from_dt and to_dt and from_dt > to_dt:
            raise ValueError("from_ts must be <= to_ts")

        url = self._resolve_url(endpoint=f"api/games/user/{username}")
        params = self._games_params(
            from_dt, to_dt, max_games, perf_type, rated, color, vs, created_lookback
        )
        headers = {**self.headers, "Accept": "application/x-ndjson"}

        ctx, response = await self._with_retry(self._open_stream)(
            url, params=params, headers=headers, timeout=self.stream_timeout
        )
        try:
            buffer = b""
            async for chunk in response.content.iter_any():
                buffer += chunk
                *lines, buffer = buffer.split(b"\n")
                for line in lines:
                    game = await self._handle_line(line, from_dt, to_dt)
                    if game is not None:
                        yield game
            game = await self._handle_line(buffer, from_dt, to_dt)
            if game is not None:
                yield game
        finally:
            await ctx.__aexit__(None, None, None)

    @staticmethod
    async def _handle_line(
        line: bytes, from_dt: Optional[datetime], to_dt: Optional[datetime]
    ) -> Optional[dict]:
        line = line.strip()
        if not line:
            return None
        game = json.loads(line)
        if not game_in_range(game, "lastMoveAt", from_dt, to_dt, unit="ms"):
            return None
        return await attach_parsed_pgn(game)

    async def get_games(
        self,
        username: str,
        *,
        from_ts: Optional[datetime] = None,
        to_ts: Optional[datetime] = None,
        max_games: Optional[int] = None,
        perf_type: Optional[Union[str, Sequence[str]]] = None,
        rated: Optional[bool] = None,
        color: Optional[str] = None,
        vs: Optional[str] = None,
        created_lookback: timedelta = timedelta(days=1),
    ) -> dict:
        """
        Same as ``iter_games`` but collects everything into one dict:

            {
              "username": <username>,
              "games": [ ...lichess game dicts with "parsed_pgn"... ],
              "from_ts": "<utc isoformat>" | None,
              "to_ts": "<utc isoformat>" | None,
            }
        """
        from_dt = to_utc_dt(from_ts)
        to_dt = to_utc_dt(to_ts)
        if from_dt and to_dt and from_dt > to_dt:
            raise ValueError("from_ts must be <= to_ts")

        games = [
            g
            async for g in self.iter_games(
                username,
                from_ts=from_dt,
                to_ts=to_dt,
                max_games=max_games,
                perf_type=perf_type,
                rated=rated,
                color=color,
                vs=vs,
                created_lookback=created_lookback,
            )
        ]
        logger.debug("Fetched %d lichess games for %s", len(games), username)
        return {
            "username": username,
            "games": games,
            "from_ts": from_dt.isoformat() if from_dt else None,
            "to_ts": to_dt.isoformat() if to_dt else None,
        }

    async def _raw_unified_games(
        self,
        username: str,
        from_dt: Optional[datetime],
        to_dt: Optional[datetime],
        errors: dict[str, str],
        **provider_kwargs: Any,
    ) -> AsyncIterator[dict]:
        async for g in self.iter_games(
            username, from_ts=from_dt, to_ts=to_dt, **provider_kwargs
        ):
            yield g

    @staticmethod
    def _to_game(raw: dict, include_raw: bool) -> Game:
        return game_from_lichess(raw, include_raw=include_raw)

    @staticmethod
    def _game_key(raw: dict) -> str:
        return str(raw.get("id") or "<unknown game>")
