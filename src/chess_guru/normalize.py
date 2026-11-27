"""Convert raw Chess.com and Lichess game dicts into :class:`Game` models.

Everything here is pure: no I/O, so the converters can be used on game dicts
you already have, with or without ``parsed_pgn`` attached.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional

from .models import Game, Move, Opening, Player, TimeControl
from .utils import parse_pgn

STANDARD_START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

_RESULTS = {"1-0", "0-1", "1/2-1/2", "*"}

CHESSCOM_SPEEDS = {
    "bullet": "bullet",
    "blitz": "blitz",
    "rapid": "rapid",
    "daily": "correspondence",
}

CHESSCOM_VARIANTS = {
    "chess": "standard",
    "chess960": "chess960",
    "crazyhouse": "crazyhouse",
    "bughouse": "bughouse",
    "kingofthehill": "king_of_the_hill",
    "threecheck": "three_check",
}

# Per-player result codes; "win", "lose" and the bughouse one say nothing
# about how the game ended.
CHESSCOM_TERMINATIONS = {
    "checkmated": "checkmate",
    "resigned": "resignation",
    "timeout": "timeout",
    "timevsinsufficient": "timeout_vs_insufficient",
    "agreed": "draw_agreement",
    "repetition": "repetition",
    "stalemate": "stalemate",
    "insufficient": "insufficient_material",
    "50move": "fifty_move",
    "abandoned": "abandoned",
    "aborted": "aborted",
    "kingofthehill": "variant_end",
    "threecheck": "variant_end",
}

_ECO_MOVES = re.compile(r"\.\.\.|-\d+\.")

CHESSCOM_DRAW_CODES = {
    "agreed",
    "repetition",
    "stalemate",
    "insufficient",
    "50move",
    "timevsinsufficient",
}

LICHESS_SPEEDS = {
    "ultraBullet": "ultrabullet",
    "bullet": "bullet",
    "blitz": "blitz",
    "rapid": "rapid",
    "classical": "classical",
    "correspondence": "correspondence",
}

# Lichess "timeout" means a player left and the opponent claimed the win.
# "draw" covers agreement, repetition and the 50-move rule alike, so it's "other".
LICHESS_TERMINATIONS = {
    "mate": "checkmate",
    "resign": "resignation",
    "outoftime": "timeout",
    "timeout": "abandoned",
    "noStart": "abandoned",
    "stalemate": "stalemate",
    "insufficientMaterialClaim": "insufficient_material",
    "aborted": "aborted",
    "variantEnd": "variant_end",
}

LICHESS_UNFINISHED = {"created", "started", "aborted", "noStart", "unknownFinish"}


# --- shared helpers -----------------------------------------------------------


def clock_to_seconds(clock: Optional[str]) -> Optional[float]:
    """``"0:09:58.5"`` -> ``598.5``. Also takes ``"M:SS"``; ``None`` passes through."""
    if not clock:
        return None
    seconds = 0.0
    for part in clock.split(":"):
        seconds = seconds * 60 + float(part)
    return seconds


def parse_eval(value: Optional[str]) -> tuple[Optional[int], Optional[int]]:
    """``"0.17"`` -> ``(17, None)``, ``"#-3"`` -> ``(None, -3)``."""
    if not value:
        return None, None
    if value.startswith("#"):
        return None, int(value[1:])
    return round(float(value) * 100), None


def ms_to_dt(ms: Optional[float]) -> Optional[datetime]:
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def s_to_dt(seconds: Optional[float]) -> Optional[datetime]:
    if seconds is None:
        return None
    return datetime.fromtimestamp(seconds, tz=timezone.utc)


def _move(ply: int, move_number: int, color: str, entry: dict) -> Move:
    eval_cp, eval_mate = parse_eval(entry.get("eval"))
    return Move(
        ply=ply,
        move_number=move_number,
        color=color,
        san=entry["move"],
        clock_seconds=clock_to_seconds(entry.get("clock")),
        eval_cp=eval_cp,
        eval_mate=eval_mate,
    )


def moves_from_parsed_pgn(parsed: dict) -> list[Move]:
    """Flatten ``parsed_pgn["moves"]`` (``{1: {"white": ..., "black": ...}}``)
    into one ``Move`` per ply, counting plies from the first move played."""
    rounds = parsed.get("moves") or {}
    moves: list[Move] = []
    for number in sorted(rounds, key=int):
        for color in ("white", "black"):
            entry = rounds[number].get(color)
            if entry and entry.get("move"):
                moves.append(_move(len(moves) + 1, int(number), color, entry))
    return moves


def moves_from_san(san: str, initial_fen: Optional[str] = None) -> list[Move]:
    """Moves from a space-separated SAN string such as Lichess's ``moves``."""
    color, number = "white", 1
    if initial_fen:
        fields = initial_fen.split()
        if len(fields) > 1 and fields[1] == "b":
            color = "black"
        if len(fields) > 5 and fields[5].isdigit():
            number = int(fields[5])
    moves = []
    for i, token in enumerate(san.split()):
        moves.append(Move(ply=i + 1, move_number=number, color=color, san=token))
        if color == "black":
            number += 1
        color = "black" if color == "white" else "white"
    return moves


def _parsed(raw: dict) -> Optional[dict]:
    parsed = raw.get("parsed_pgn")
    if parsed is not None or not raw.get("pgn"):
        return parsed
    try:
        headers, result, moves = parse_pgn(raw["pgn"])
    except Exception:
        return None
    return {"headers": headers, "result": result, "moves": moves}


def _header(headers: dict, key: str) -> Optional[str]:
    value = headers.get(key)
    if value in (None, "", "?", "-"):
        return None
    return value


def _non_standard_fen(fen: Optional[str]) -> Optional[str]:
    if not fen:
        return None
    # ignore move counters, chess.com and lichess write them the same anyway
    if fen.split()[:4] == STANDARD_START_FEN.split()[:4]:
        return None
    return fen


def _winner(result: str) -> Optional[str]:
    return {"1-0": "white", "0-1": "black"}.get(result)


def _raw_copy(raw: dict, include_raw: bool) -> Optional[dict]:
    # parsed_pgn is ours, and its int keys wouldn't survive a JSON round trip
    if not include_raw:
        return None
    return {k: v for k, v in raw.items() if k != "parsed_pgn"}


# --- Chess.com ----------------------------------------------------------------


def chesscom_time_control(raw: Optional[str]) -> TimeControl:
    """Parse ``"600"``, ``"180+2"`` or daily ``"1/259200"`` (seconds per move)."""
    if not raw:
        return TimeControl(raw=raw)
    try:
        if "/" in raw:
            _, per_move = raw.split("/", 1)
            return TimeControl(days_per_move=round(int(per_move) / 86400), raw=raw)
        initial, _, increment = raw.partition("+")
        return TimeControl(
            initial_seconds=int(initial),
            increment_seconds=int(increment or 0),
            raw=raw,
        )
    except ValueError:
        return TimeControl(raw=raw)


def _chesscom_id(raw: dict) -> str:
    if raw.get("uuid"):
        return raw["uuid"]
    return raw["url"].rstrip("/").rsplit("/", 1)[-1]


def _chesscom_result(white_code: str, black_code: str, parsed: Optional[dict]) -> str:
    if parsed:
        for value in (parsed.get("headers", {}).get("Result"), parsed.get("result")):
            if value in _RESULTS:
                return value
    if white_code == "win":
        return "1-0"
    if black_code == "win":
        return "0-1"
    if white_code in CHESSCOM_DRAW_CODES and black_code in CHESSCOM_DRAW_CODES:
        return "1/2-1/2"
    return "*"


def _chesscom_termination(
    white_code: Optional[str], black_code: Optional[str], winner: Optional[str]
) -> tuple[str, Optional[str]]:
    # the loser's code is the informative one, e.g. ("win", "checkmated")
    codes = [white_code, black_code]
    if winner == "white":
        codes.reverse()
    for code in codes:
        if code in CHESSCOM_TERMINATIONS:
            return CHESSCOM_TERMINATIONS[code], code
    raw = next((c for c in codes if c and c != "win"), None)
    return "other", raw


def _chesscom_start(raw: dict, headers: dict) -> Optional[datetime]:
    if raw.get("start_time") is not None:
        return s_to_dt(raw["start_time"])
    date, time = headers.get("UTCDate"), headers.get("UTCTime")
    if not date or not time:
        return None
    try:
        dt = datetime.strptime(f"{date} {time}", "%Y.%m.%d %H:%M:%S")
    except ValueError:
        return None
    return dt.replace(tzinfo=timezone.utc)


def _chesscom_opening(raw: dict, headers: dict) -> Optional[Opening]:
    eco = _header(headers, "ECO")
    url = headers.get("ECOUrl") or raw.get("eco")
    name = None
    if url:
        # "Sicilian-Defense-2...e5-3.Nf3" -> "Sicilian Defense"
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        slug = _ECO_MOVES.split(slug, maxsplit=1)[0]
        name = slug.replace("-", " ").strip()
        if name in ("", "Undefined"):
            name = None
    if eco is None and name is None:
        return None
    return Opening(eco=eco, name=name)


def _chesscom_player(side: dict) -> Player:
    return Player(
        username=side.get("username"),
        rating=side.get("rating"),
        result_raw=side.get("result"),
    )


def game_from_chesscom(raw: dict, *, include_raw: bool = False) -> Game:
    """Build a :class:`Game` from one game of a Chess.com monthly archive."""
    parsed = _parsed(raw)
    headers = dict(parsed["headers"]) if parsed else {}
    white = raw.get("white") or {}
    black = raw.get("black") or {}

    result = _chesscom_result(white.get("result"), black.get("result"), parsed)
    winner = _winner(result)
    termination, termination_raw = _chesscom_termination(
        white.get("result"), black.get("result"), winner
    )

    time_class = raw.get("time_class")
    rules = raw.get("rules")

    return Game(
        provider="chesscom",
        id=_chesscom_id(raw),
        url=raw["url"],
        rated=raw.get("rated"),
        variant=CHESSCOM_VARIANTS.get(rules, rules or "standard"),
        variant_raw=rules,
        speed=CHESSCOM_SPEEDS.get(time_class, "other"),
        speed_raw=time_class,
        time_control=chesscom_time_control(raw.get("time_control")),
        start_time=_chesscom_start(raw, headers),
        end_time=s_to_dt(raw.get("end_time")),
        white=_chesscom_player(white),
        black=_chesscom_player(black),
        result=result,
        winner=winner,
        termination=termination,
        termination_raw=termination_raw,
        opening=_chesscom_opening(raw, headers),
        initial_fen=_non_standard_fen(raw.get("initial_setup") or headers.get("FEN")),
        final_fen=raw.get("fen") or headers.get("CurrentPosition"),
        pgn=raw.get("pgn"),
        headers=headers,
        moves=moves_from_parsed_pgn(parsed) if parsed else [],
        raw=_raw_copy(raw, include_raw),
    )


# --- Lichess ------------------------------------------------------------------


def lichess_variant(key: Optional[str]) -> str:
    """``kingOfTheHill`` -> ``king_of_the_hill``. ``fromPosition`` is played
    under standard rules, so it becomes ``standard``."""
    if not key or key == "fromPosition":
        return "standard"
    return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()


def lichess_time_control(raw: dict) -> TimeControl:
    clock = raw.get("clock")
    if clock:
        initial, increment = clock.get("initial"), clock.get("increment")
        return TimeControl(
            initial_seconds=initial,
            increment_seconds=increment,
            raw=f"{initial}+{increment}",
        )
    days = raw.get("daysPerTurn")
    if days:
        # same shape chess.com uses for daily games
        return TimeControl(days_per_move=days, raw=f"1/{days * 86400}")
    return TimeControl()


def _lichess_result(winner: Optional[str], status: Optional[str]) -> str:
    if winner == "white":
        return "1-0"
    if winner == "black":
        return "0-1"
    if status in LICHESS_UNFINISHED:
        return "*"
    return "1/2-1/2"


def _lichess_termination(status: Optional[str], winner: Optional[str]) -> str:
    # flagging against a lone king is a draw on lichess
    if status == "outoftime" and winner is None:
        return "timeout_vs_insufficient"
    return LICHESS_TERMINATIONS.get(status, "other")


def _lichess_player(side: dict) -> Player:
    user = side.get("user") or {}
    return Player(
        username=user.get("name") or side.get("name"),
        rating=side.get("rating"),
        rating_diff=side.get("ratingDiff"),
        title=user.get("title"),
        ai_level=side.get("aiLevel"),
    )


def _lichess_opening(raw: dict, headers: dict) -> Optional[Opening]:
    opening = raw.get("opening") or {}
    eco = opening.get("eco") or _header(headers, "ECO")
    name = opening.get("name") or _header(headers, "Opening")
    if eco is None and name is None:
        return None
    return Opening(eco=eco, name=name)


def game_from_lichess(raw: dict, *, include_raw: bool = False) -> Game:
    """Build a :class:`Game` from one game of the Lichess game export."""
    parsed = _parsed(raw)
    headers = dict(parsed["headers"]) if parsed else {}
    players = raw.get("players") or {}
    status = raw.get("status")
    winner = raw.get("winner")
    if winner not in ("white", "black"):
        winner = None

    initial_fen = _non_standard_fen(raw.get("initialFen") or headers.get("FEN"))
    if parsed:
        moves = moves_from_parsed_pgn(parsed)
    else:
        moves = moves_from_san(raw.get("moves") or "", initial_fen)

    game_id = raw["id"]
    return Game(
        provider="lichess",
        id=game_id,
        url=f"https://lichess.org/{game_id}",
        rated=raw.get("rated"),
        variant=lichess_variant(raw.get("variant")),
        variant_raw=raw.get("variant"),
        speed=LICHESS_SPEEDS.get(raw.get("speed"), "other"),
        speed_raw=raw.get("speed"),
        time_control=lichess_time_control(raw),
        start_time=ms_to_dt(raw.get("createdAt")),
        end_time=ms_to_dt(raw.get("lastMoveAt")),
        white=_lichess_player(players.get("white") or {}),
        black=_lichess_player(players.get("black") or {}),
        result=_lichess_result(winner, status),
        winner=winner,
        termination=_lichess_termination(status, winner),
        termination_raw=status,
        opening=_lichess_opening(raw, headers),
        initial_fen=initial_fen,
        final_fen=raw.get("lastFen"),
        pgn=raw.get("pgn"),
        headers=headers,
        moves=moves,
        raw=_raw_copy(raw, include_raw),
    )
