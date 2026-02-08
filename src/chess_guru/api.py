import asyncio
import aiohttp
import backoff
import logging
from typing import Any, Optional
from datetime import datetime, timezone
from .utils import (
    parse_archive_year_month,
    to_utc_dt,
    parse_pgn,
)

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.addHandler(logging.NullHandler())


def _log_backoff(details: dict[str, Any]) -> None:
    exc = details.get("exception")
    wait = details.get("wait")
    tries = details.get("tries")
    target = getattr(details.get("target"), "__name__", str(details.get("target")))

    logger.warning(
        "Retrying %s after error (tries=%s, wait=%.2fs): %r",
        target,
        tries,
        wait if wait is not None else -1.0,
        exc,
    )


def _log_giveup(details: dict[str, Any]) -> None:
    exc = details.get("exception")
    tries = details.get("tries")
    target = getattr(details.get("target"), "__name__", str(details.get("target")))

    logger.error(
        "Giving up on %s after %s tries: %r",
        target,
        tries,
        exc,
    )

class ChesscomAPI:
    def __init__(
        self, 
        session:aiohttp.ClientSession, 
        base_url:str = 'https://api.chess.com/pub', 
        timeout_sec:int = 20,
        user_agent: str = "chess-guru/0.1.0",
        headers: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Creates a Chess.com Public API client using an existing aiohttp session

        Args:
            session:
                An already-created aiohttp.ClientSession. The caller owns the session
                lifecycle
            base_url (provided):
                Base URL for the chess.com public API
            timeout_sec (provided):
                Total request timeout in seconds (applied to each HTTP request)
            user_agent:
                User-Agent header value to send with every request. Defaults to a
                generic library identifier (recommended). You should override this to
                identify your application/version
            headers:
                Optional extra headers to merge into the default headers. If provided,
                keys in this dict override defaults (including "User-Agent" and "Accept")

        Notes:
            - Keeping the session external makes this client easy to integrate into
              larger async apps where one shared session is preferred
        """

        self.base_url = base_url.rstrip("/") + "/"
        self.session = session
        self.timeout = aiohttp.ClientTimeout(total=timeout_sec)
        
        base_headers = {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }
        if headers:
            base_headers.update(headers)
        
        self.headers = base_headers

    @staticmethod
    def _terminal_error(e: Exception) -> bool:
        if isinstance(e, aiohttp.ClientResponseError):
            return e.status is not None and e.status < 500 and e.status != 429
        return False

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=5,
        giveup=_terminal_error,
        on_backoff=_log_backoff,
        on_giveup=_log_giveup,
    )
    async def _request(
        self, 
        *,
        url:Optional[str] = None, 
        endpoint:Optional[str] = None, 
        **kwargs
    ) -> Any:
        if (url is None) == (endpoint is None):
            raise ValueError("Requires only one endpoint or url parameter.")
        elif endpoint is not None:
            url = self.base_url+endpoint.lstrip("/")
        else:
            assert url is not None
            if not url.startswith(self.base_url):
                raise ValueError(f"{url} is not a valid chess.com url.")

        async with self.session.get(url, headers=self.headers, timeout=self.timeout, **kwargs) as response:
            status = response.status

            try:
                response.raise_for_status()
            except aiohttp.ClientError as e:
                terminal = self._terminal_error(e)
                logger.debug(
                    "Request failed (status=%s, terminal=%s, url=%s): %r",
                    status,
                    terminal,
                    url,
                    e,
                )
                raise # lets backoff see it
            
            return await response.json(content_type=None)
        
    async def get_player(self, username:str) -> dict:
        """
        Fetches public profile information for a Chess.com user.
        Arg: username: chess.com username
        Returns:
            JSON dict as returned by Chess.com
        """
        return await self._request(endpoint=f"player/{username}")
    
    async def get_player_stats(self, username:str) -> dict:
        # grabs player stats as of query
        return await self._request(endpoint=f"player/{username}/stats")
    
    async def get_games_to_move(self, username:str) -> dict:
        # gets games 'to move' at time of query, provides insight into
        # vacations delaying play if ran over window
        return await self._request(endpoint=f"player/{username}/games/to-move")
    
    async def get_tournaments(self, username:str) -> dict:
        # grabs tournaments participated in by a user
        return await self._request(endpoint=f"player/{username}/tournaments")
    
    async def get_archives(self, username:str) -> dict:
        """
        Fetch the list of monthly game archive URLs for a Chess.com user.
        Arg: username: chess.com username
        Returns:
            JSON dict, example:
                { "archives": ["https://api.chess.com/pub/player/<u>/games/2024/06", ...] }
        """
        return await self._request(endpoint=f"player/{username}/games/archives")
    

    async def get_games(
        self,
        username: str,
        max_concurrency: int = 10,
        from_ts: Optional[datetime] = None,
        to_ts: Optional[datetime] = None,
    ) -> dict:
        """
        Fetches a user's games from monthly archives, optionally filtered by time range.
        
        High-level steps:
            1) Call get_archives(username) to get monthly archive URLs
            2) If from_ts/to_ts provided:
                - Convert to UTC via to_utc_dt()
                - Filter archive URLs by month bounds (year, month)
            3) Fetch each month's JSON concurrently
            4) Inside each month payload:
                - Optionally filter games by end_time (unix seconds) to match from/to range
        Args:
            username: chess.com username
            max_concurrency:
                Max number of monthly archive requests to run at once
            from_ts:
                Lower bound timestamp -- expects UTC
            to_ts:
                Upper bound timestamp -- expects UTC

        Returns:
            {
              "username": <username>,
              "archives": [<filtered month URLs>],
              "months": {
                  "<archive_url>": {
                      ...month payload...,
                      "games": [ ...filtered/annotated game dicts... ]
                  },
                  ...
              },
              "errors": { "<archive_url>": "<repr(exception)>", ... },
              "from_ts": "<utc isoformat>" | None,
              "to_ts": "<utc isoformat>" | None,
            }
        """
        archive_data = await self.get_archives(username)
        archive_urls = archive_data.get("archives", [])

        from_dt = to_utc_dt(from_ts)
        to_dt = to_utc_dt(to_ts)

        if from_dt and to_dt and from_dt > to_dt:
            raise ValueError("from_ts must be <= to_ts")

        # Filter month URLs by (year, month) bounds derived from timestamps
        if from_dt is None and to_dt is None:
            filtered_urls = archive_urls
        else:
            start_ym = (from_dt.year, from_dt.month) if from_dt else None
            end_ym = (to_dt.year, to_dt.month) if to_dt else None

            def month_in_range(u: str) -> bool:
                ym = parse_archive_year_month(u)
                if start_ym and ym < start_ym:
                    return False
                if end_ym and ym > end_ym:
                    return False
                return True

            filtered_urls = [u for u in archive_urls if month_in_range(u)]

        sem = asyncio.Semaphore(max_concurrency)

        async def fetch_month(u: str):
            async with sem:
                return await self._request(url=u)

        monthly_datas = await asyncio.gather(
            *(fetch_month(u) for u in filtered_urls),
            return_exceptions=True,
        )

        months: dict[str, Any] = {}
        errors: dict[str, str] = {}

        # Build months dict, but filter games inside each month by timestamp
        for u, r in zip(filtered_urls, monthly_datas):
            if isinstance(r, Exception):
                logger.warning("Month fetch failed: %s -> %r", u, r)
                errors[u] = repr(r)
                continue

            games = r.get("games", [])
            kept = []

            for g in games:
                # Apply time filter only if bounds exist
                if from_dt or to_dt:
                    end_time = g.get("end_time")
                    if end_time is None:
                        continue
                    g_dt = datetime.fromtimestamp(end_time, tz=timezone.utc)

                    if from_dt and g_dt < from_dt:
                        continue
                    if to_dt and g_dt > to_dt:
                        continue

                pgn = g.get("pgn")
                if pgn:
                    try:
                        headers, end_result, moves = await asyncio.to_thread(parse_pgn, pgn)
                        g = dict(g)
                        g["parsed_pgn"] = {
                            "headers": headers,
                            "result": end_result,
                            "moves": moves,
                        }
                    except Exception as exc:
                        logger.debug("PGN parse failed for game: %r", exc)

                kept.append(g)

            r = dict(r)
            r["games"] = kept
            months[u] = r

        return {
            "username": username,
            "archives": filtered_urls,
            "months": months,
            "errors": errors,
            "from_ts": from_dt.isoformat() if from_dt else None,
            "to_ts": to_dt.isoformat() if to_dt else None,
        }
    
