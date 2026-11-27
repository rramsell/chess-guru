from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Optional

import aiohttp

from ._http import DEFAULT_USER_AGENT, BaseAPIClient, logger
from .utils import annotate_games, parse_archive_year_month, to_utc_dt


class ChesscomAPI(BaseAPIClient):
    provider_name = "chess.com"

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str = "https://api.chess.com/pub",
        timeout_sec: int = 20,
        user_agent: str = DEFAULT_USER_AGENT,
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
                keys in this dict override defaults (including "User-Agent" and
                "Accept")

        Notes:
            - Keeping the session external makes this client easy to integrate into
              larger async apps where one shared session is preferred
        """

        super().__init__(
            session,
            base_url=base_url,
            timeout_sec=timeout_sec,
            user_agent=user_agent,
            headers=headers,
        )

    async def _request(
        self, *, url: Optional[str] = None, endpoint: Optional[str] = None, **kwargs
    ) -> Any:
        return await self._request_json(url=url, endpoint=endpoint, **kwargs)

    async def get_player(self, username: str) -> dict:
        """
        Fetches public profile information for a Chess.com user.
        Arg: username: chess.com username
        Returns:
            JSON dict as returned by Chess.com
        """
        return await self._request(endpoint=f"player/{username}")

    async def get_player_stats(self, username: str) -> dict:
        # grabs player stats as of query
        return await self._request(endpoint=f"player/{username}/stats")

    async def get_games_to_move(self, username: str) -> dict:
        # gets games 'to move' at time of query, provides insight into
        # vacations delaying play if ran over window
        return await self._request(endpoint=f"player/{username}/games/to-move")

    async def get_tournaments(self, username: str) -> dict:
        # grabs tournaments participated in by a user
        return await self._request(endpoint=f"player/{username}/tournaments")

    async def get_archives(self, username: str) -> dict:
        """
        Fetch the list of monthly game archive URLs for a Chess.com user.
        Arg: username: chess.com username
        Returns:
            JSON dict, example:
                {"archives": [
                    "https://api.chess.com/pub/player/<u>/games/2024/06", ...
                ]}
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
                - Optionally filter games by end_time (unix seconds) to match the
                  from/to range
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
        from_dt = to_utc_dt(from_ts)
        to_dt = to_utc_dt(to_ts)

        if from_dt and to_dt and from_dt > to_dt:
            raise ValueError("from_ts must be <= to_ts")

        archive_data = await self.get_archives(username)
        archive_urls = archive_data.get("archives", [])

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

            kept = await annotate_games(
                r.get("games", []), "end_time", from_dt, to_dt, unit="s"
            )
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
