from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, AsyncIterator, Callable, Generator, Optional

import aiohttp
import backoff

from ._version import __version__
from .models import Game, GameCollection
from .utils import to_utc_dt

DEFAULT_USER_AGENT = f"chess-guru/{__version__}"

# Same name as before the split so existing logging config keeps working.
logger = logging.getLogger("chess_guru.api")
if not logger.handlers:
    logger.addHandler(logging.NullHandler())

RETRYABLE_ERRORS = (aiohttp.ClientError, asyncio.TimeoutError)


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


def _terminal_error(e: Exception) -> bool:
    """Return True for errors that should not be retried (4xx other than 429)."""
    if isinstance(e, aiohttp.ClientResponseError):
        return e.status is not None and e.status < 500 and e.status != 429
    return False


class BaseAPIClient:
    """Shared plumbing for the provider clients: session, headers, URL handling
    and retries. Subclasses set ``provider_name`` and can tune the retry policy
    through ``max_tries``, ``retry_jitter`` and ``_retry_wait_gen``."""

    provider_name = "API"
    max_tries = 5
    retry_jitter = staticmethod(backoff.full_jitter)

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        timeout_sec: float = 20,
        user_agent: str = DEFAULT_USER_AGENT,
        headers: Optional[dict[str, str]] = None,
    ) -> None:
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
    def _retry_wait_gen() -> Generator[Any, Any, None]:
        return backoff.expo()

    def _with_retry(self, func: Callable[..., Any]) -> Callable[..., Any]:
        return backoff.on_exception(
            self._retry_wait_gen,
            RETRYABLE_ERRORS,
            max_tries=self.max_tries,
            jitter=self.retry_jitter,
            giveup=_terminal_error,
            on_backoff=_log_backoff,
            on_giveup=_log_giveup,
        )(func)

    def _resolve_url(
        self, url: Optional[str] = None, endpoint: Optional[str] = None
    ) -> str:
        if (url is None) == (endpoint is None):
            raise ValueError("Requires only one endpoint or url parameter.")
        if endpoint is not None:
            return self.base_url + endpoint.lstrip("/")
        assert url is not None
        if not url.startswith(self.base_url):
            raise ValueError(f"{url} is not a valid {self.provider_name} url.")
        return url

    @staticmethod
    def _raise_for_status(response: Any, url: str) -> None:
        try:
            response.raise_for_status()
        except aiohttp.ClientError as e:
            logger.debug(
                "Request failed (status=%s, terminal=%s, url=%s): %r",
                response.status,
                _terminal_error(e),
                url,
                e,
            )
            raise  # lets backoff see it

    async def _get_json(self, url: str, **kwargs: Any) -> Any:
        kwargs.setdefault("headers", self.headers)
        kwargs.setdefault("timeout", self.timeout)
        async with self.session.get(url, **kwargs) as response:
            self._raise_for_status(response, url)
            return await response.json(content_type=None)

    async def _request_json(
        self, *, url: Optional[str] = None, endpoint: Optional[str] = None, **kwargs
    ) -> Any:
        resolved = self._resolve_url(url=url, endpoint=endpoint)
        return await self._with_retry(self._get_json)(resolved, **kwargs)

    # --- unified games ---------------------------------------------------------

    provider_key = ""

    def _raw_unified_games(
        self,
        username: str,
        from_dt: Optional[datetime],
        to_dt: Optional[datetime],
        errors: dict[str, str],
        **provider_kwargs: Any,
    ) -> AsyncIterator[dict]:
        """Raw game dicts for the unified methods. Fetch problems that don't
        stop the whole request go into ``errors``."""
        raise NotImplementedError

    @staticmethod
    def _to_game(raw: dict, include_raw: bool) -> Game:
        raise NotImplementedError

    @staticmethod
    def _game_key(raw: dict) -> str:
        raise NotImplementedError

    async def _unified_games(
        self,
        username: str,
        from_ts: Optional[datetime],
        to_ts: Optional[datetime],
        include_raw: bool,
        errors: dict[str, str],
        provider_kwargs: dict[str, Any],
    ) -> AsyncIterator[Game]:
        from_dt = to_utc_dt(from_ts)
        to_dt = to_utc_dt(to_ts)
        if from_dt and to_dt and from_dt > to_dt:
            raise ValueError("from_ts must be <= to_ts")

        async for raw in self._raw_unified_games(
            username, from_dt, to_dt, errors, **provider_kwargs
        ):
            try:
                yield self._to_game(raw, include_raw)
            except Exception as e:
                key = self._game_key(raw)
                logger.debug("Skipping %s game %s: %r", self.provider_name, key, e)
                errors[key] = repr(e)

    async def iter_unified_games(
        self,
        username: str,
        *,
        from_ts: Optional[datetime] = None,
        to_ts: Optional[datetime] = None,
        include_raw: bool = False,
        **provider_kwargs: Any,
    ) -> AsyncIterator[Game]:
        """
        Yields the user's games as :class:`Game` models, newest first.

        ``from_ts`` / ``to_ts`` work as in ``get_games``. ``include_raw`` keeps
        the provider's game dict on ``Game.raw``. Other keyword arguments go to
        the provider's ``get_games``. Games that fail to fetch or convert are
        logged and skipped; use ``get_unified_games`` to see which.
        """
        async for game in self._unified_games(
            username, from_ts, to_ts, include_raw, {}, provider_kwargs
        ):
            yield game

    async def get_unified_games(
        self,
        username: str,
        *,
        from_ts: Optional[datetime] = None,
        to_ts: Optional[datetime] = None,
        include_raw: bool = False,
        **provider_kwargs: Any,
    ) -> GameCollection:
        """Same as ``iter_unified_games`` but returns a :class:`GameCollection`
        that also lists what failed in ``errors``."""
        errors: dict[str, str] = {}
        games = [
            g
            async for g in self._unified_games(
                username, from_ts, to_ts, include_raw, errors, provider_kwargs
            )
        ]
        return GameCollection(
            provider=self.provider_key,
            username=username,
            games=games,
            errors=errors,
            from_ts=to_utc_dt(from_ts),
            to_ts=to_utc_dt(to_ts),
        )

    # Defined last so nothing above picks up the staticmethod object, which
    # isn't callable on Python 3.9.
    _terminal_error = staticmethod(_terminal_error)
