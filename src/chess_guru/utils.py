from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse


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


def _extract_move_and_clock(color_text: str) -> dict:
    _clock_pattern = re.compile(r"\{\s*\[%clk\s+([0-9:\.]+)\]\s*\}")
    color_text = color_text.strip()

    # pull clock if present
    clk = None
    clk_match = _clock_pattern.search(color_text)
    if clk_match:
        clk = clk_match.group(1)
        # remove the clock chunk from the text
        color_text = _clock_pattern.sub("", color_text).strip()

    # the move is the first token (SAN)
    move = color_text.split(" ", 1)[0] if color_text else None

    return {"move": move, "clock": clk}


def _parse_moves(pgn_moves: str) -> dict:
    round_chunks = re.split(r"(?<=\s)(?=\d+\.\s)", pgn_moves.strip())
    rounds = {}

    for chunk in round_chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        m = re.match(r"^(\d+)\.\s*", chunk)
        if not m:
            continue

        game_round = int(m.group(1))

        # remove leading "<num>. "
        after_white_num = re.sub(r"^\d+\.\s*", "", chunk).strip()

        # split on "<num>... "
        chunk_parts = re.split(
            rf"\s+{game_round}\.\.\.\s+", after_white_num, maxsplit=1
        )

        if len(chunk_parts) > 1:
            white_text = chunk_parts[0].strip()
            black_text = chunk_parts[1].strip()
        else:
            # No "<num>..." marker. PGN only needs one after a comment (e.g. a
            # clock), so a clock-less PGN reads "e4 e5". Split off white's move
            # plus its optional {comment}; whatever remains is black's move.
            wm = re.match(r"(\S+(?:\s*\{[^}]*\})?)\s*(.*)", after_white_num, re.S)
            white_text = wm.group(1) if wm else after_white_num
            black_text = wm.group(2).strip() if wm else None

        rounds[game_round] = {"white": _extract_move_and_clock(white_text)}

        if black_text:
            rounds[game_round]["black"] = _extract_move_and_clock(black_text)

    return rounds


def parse_pgn(pgn: str) -> tuple[dict, str | None, dict]:
    headers, moves, end_result = _split_pgn_headers_and_moves(pgn)
    return _parse_pgn_headers(headers), end_result, _parse_moves(moves)
