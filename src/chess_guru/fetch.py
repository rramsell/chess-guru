from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

import aiohttp

from ._http import DEFAULT_USER_AGENT
from .chesscom import ChesscomAPI
from .lichess import LichessAPI
from .models import GameCollection


async def fetch_all_games(
    session: aiohttp.ClientSession,
    *,
    chesscom: Optional[str] = None,
    lichess: Optional[str] = None,
    from_ts: Optional[datetime] = None,
    to_ts: Optional[datetime] = None,
    include_raw: bool = False,
    user_agent: str = DEFAULT_USER_AGENT,
) -> list[GameCollection]:
    """Fetch unified games from each provider given a username, concurrently.
    Returns one collection per provider, Chess.com first."""
    clients = []
    if chesscom:
        clients.append((ChesscomAPI(session, user_agent=user_agent), chesscom))
    if lichess:
        clients.append((LichessAPI(session, user_agent=user_agent), lichess))
    return list(
        await asyncio.gather(
            *(
                api.get_unified_games(
                    name, from_ts=from_ts, to_ts=to_ts, include_raw=include_raw
                )
                for api, name in clients
            )
        )
    )
