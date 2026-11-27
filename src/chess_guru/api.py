"""Kept so ``from chess_guru.api import ...`` keeps working after the split."""

from __future__ import annotations

from ._http import (
    DEFAULT_USER_AGENT,
    _log_backoff,
    _log_giveup,
    _terminal_error,
    logger,
)
from .chesscom import ChesscomAPI

__all__ = [
    "DEFAULT_USER_AGENT",
    "ChesscomAPI",
    "_log_backoff",
    "_log_giveup",
    "_terminal_error",
    "logger",
]
