from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Any, Iterable, Optional
from urllib.parse import urlparse

logger = logging.getLogger("chess_guru.api")


def parse_archive_year_month(archive_url: str) -> tuple[int, int]:
    path = urlparse(archive_url).path.rstrip("/")
    parts = path.split("/")
    return int(parts[-2]), int(parts[-1])


def to_utc_dt(ts: Optional[datetime]) -> Optional[datetime]:
    if ts is None:
        return None
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def _split_pgn_headers_and_moves(pgn: str) -> tuple[str, str, str | None]:
    _end_result_pattern = re.compile(r"(1-0|0-1|1/2-1/2|\*)\s*$")
    pgn = pgn.replace("\r\n", "\n").strip()
    if "\n\n" not in pgn:
        raise ValueError(
            "Malformed PGN: expected a blank line between headers and movetext."
        )
    headers, moves = pgn.split("\n\n", 1)
    moves = moves.strip()

    # pull result off the very end
    m = _end_result_pattern.search(moves)
    end_result = m.group(1) if m else None

    # remove it from moves text
    if m:
        moves = moves[: m.start()].rstrip()

    return headers, moves, end_result


def _parse_pgn_headers(pgn_header: str) -> dict:
    parsed_header = {}

    for line in pgn_header.splitlines():
        key, value = line.strip("[]").split(" ", 1)
        parsed_header[key] = value.strip('"')

    return parsed_header


_COMMENT_PATTERN = re.compile(r"\{[^}]*\}")
_CLOCK_PATTERN = re.compile(r"\[%clk\s+([0-9:.]+)\]")
_EVAL_PATTERN = re.compile(r"\[%eval\s+([^\],\s]+)")


def _extract_move_and_clock(color_text: str) -> dict:
    color_text = color_text.strip()

    # chess.com writes {[%clk ...]}, lichess {[%eval 0.17] [%clk 0:02:59]}
    clk = None
    ev = None
    for comment in _COMMENT_PATTERN.findall(color_text):
        clk_match = _CLOCK_PATTERN.search(comment)
        if clk_match and clk is None:
            clk = clk_match.group(1)
        eval_match = _EVAL_PATTERN.search(comment)
        if eval_match and ev is None:
            ev = eval_match.group(1)
    color_text = _COMMENT_PATTERN.sub(" ", color_text).strip()

    # the move is the first token (SAN)
    move = color_text.split(None, 1)[0] if color_text else None

    return {"move": move, "clock": clk, "eval": ev}


def _parse_moves(pgn_moves: str) -> dict:
    # Swap comments for placeholders so text inside them can't confuse the
    # move-number splitting below.
    comments: list[str] = []

    def _stash(m: re.Match) -> str:
        comments.append(m.group(0))
        return f"{{{len(comments) - 1}}}"

    def _restore(text: str) -> str:
        return re.sub(r"\{(\d+)\}", lambda m: comments[int(m.group(1))], text)

    pgn_moves = _COMMENT_PATTERN.sub(_stash, pgn_moves.strip())
    round_chunks = re.split(r"(?<=\s)(?=\d+\.\s)|(?<=\s)(?=\d+\.\.\.\s)", pgn_moves)
    rounds: dict = {}

    for chunk in round_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        # Games set up from a position (FEN) can open with black, e.g. "1... e5"
        black_first = re.match(r"^(\d+)\.\.\.\s*(.*)", chunk, re.S)
        if black_first:
            game_round = int(black_first.group(1))
            text = black_first.group(2).strip()
            if text:
                rounds.setdefault(game_round, {})["black"] = _extract_move_and_clock(
                    _restore(text)
                )
            continue

        m = re.match(r"^(\d+)\.\s*", chunk)
        if not m:
            continue

        game_round = int(m.group(1))

        # remove leading "<num>. "
        after_white_num = chunk[m.end() :].strip()

        # No "<num>..." marker, e.g. clock-less "e4 e5": white's move and
        # its optional {comment} come first, the rest is black's.
        wm = re.match(r"(\S+(?:\s*\{\d+\})?)\s*(.*)", after_white_num, re.S)
        white_text = wm.group(1) if wm else after_white_num
        black_text = wm.group(2).strip() if wm else None

        rounds[game_round] = {"white": _extract_move_and_clock(_restore(white_text))}

        if black_text:
            rounds[game_round]["black"] = _extract_move_and_clock(_restore(black_text))

    return rounds


def parse_pgn(pgn: str) -> tuple[dict, str | None, dict]:
    headers, moves, end_result = _split_pgn_headers_and_moves(pgn)
    return _parse_pgn_headers(headers), end_result, _parse_moves(moves)


def game_in_range(
    game: dict,
    time_key: str,
    from_dt: Optional[datetime],
    to_dt: Optional[datetime],
    unit: str = "s",
) -> bool:
    """Inclusive check of ``game[time_key]`` against the bounds. Games without
    the key only pass when there are no bounds."""
    if from_dt is None and to_dt is None:
        return True
    value = game.get(time_key)
    if value is None:
        return False
    if unit == "ms":
        value = value / 1000
    elif unit != "s":
        raise ValueError(f"unit must be 's' or 'ms', got {unit!r}")
    g_dt = datetime.fromtimestamp(value, tz=timezone.utc)
    if from_dt and g_dt < from_dt:
        return False
    if to_dt and g_dt > to_dt:
        return False
    return True


async def attach_parsed_pgn(game: dict) -> dict:
    """Return a copy of ``game`` with ``parsed_pgn`` added. If there's no PGN or
    it doesn't parse, the game comes back unchanged."""
    pgn = game.get("pgn")
    if not pgn:
        return game
    try:
        headers, end_result, moves = await asyncio.to_thread(parse_pgn, pgn)
    except Exception as exc:
        logger.debug("PGN parse failed for game: %r", exc)
        return game
    game = dict(game)
    game["parsed_pgn"] = {"headers": headers, "result": end_result, "moves": moves}
    return game


async def annotate_games(
    games: Iterable[dict],
    time_key: str,
    from_dt: Optional[datetime] = None,
    to_dt: Optional[datetime] = None,
    unit: str = "s",
) -> list[dict[str, Any]]:
    """Drop games outside the time range and attach ``parsed_pgn`` to the rest."""
    kept = []
    for g in games:
        if game_in_range(g, time_key, from_dt, to_dt, unit):
            kept.append(await attach_parsed_pgn(g))
    return kept
