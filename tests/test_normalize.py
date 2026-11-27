from datetime import datetime, timezone

import pytest

import lichess_pgn_fixtures as li_pgn
import raw_game_fixtures as fx
from chess_guru import game_from_chesscom, game_from_lichess
from chess_guru.normalize import (
    chesscom_time_control,
    clock_to_seconds,
    lichess_time_control,
    lichess_variant,
    moves_from_parsed_pgn,
    moves_from_san,
    ms_to_dt,
    parse_eval,
    s_to_dt,
)
from chess_guru.utils import parse_pgn


def utc(*args) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


def parsed(pgn: str) -> dict:
    headers, result, moves = parse_pgn(pgn)
    return {"headers": headers, "result": result, "moves": moves}


# --- helpers ------------------------------------------------------------------


@pytest.mark.parametrize(
    "clock, seconds",
    [
        ("0:09:58.5", 598.5),
        ("0:03:00", 180.0),
        ("1:00:00", 3600.0),
        ("2:27:20.8", 8840.8),
        ("0:59", 59.0),
        (None, None),
        ("", None),
    ],
)
def test_clock_to_seconds(clock, seconds):
    assert clock_to_seconds(clock) == seconds


@pytest.mark.parametrize(
    "value, expected",
    [
        ("0.17", (17, None)),
        ("-0.65", (-65, None)),
        ("0", (0, None)),
        ("12.345", (1234, None)),
        ("#-3", (None, -3)),
        ("#1", (None, 1)),
        (None, (None, None)),
    ],
)
def test_parse_eval(value, expected):
    assert parse_eval(value) == expected


def test_timestamp_helpers():
    assert s_to_dt(1704424322) == utc(2024, 1, 5, 3, 12, 2)
    assert ms_to_dt(1704424322500) == utc(2024, 1, 5, 3, 12, 2, 500000)
    assert s_to_dt(None) is None and ms_to_dt(None) is None


def test_moves_from_parsed_pgn_flattens_plies():
    moves = moves_from_parsed_pgn(parsed(li_pgn.CLOCKS_AND_EVALS))
    assert [m.san for m in moves] == ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4"]
    assert [m.ply for m in moves] == list(range(1, 8))
    assert [m.move_number for m in moves] == [1, 1, 2, 2, 3, 3, 4]
    # ends on a white move
    assert moves[-1].color == "white"
    assert moves[0].clock_seconds == 180.0 and moves[0].eval_cp == 17


def test_moves_from_parsed_pgn_black_first():
    moves = moves_from_parsed_pgn(parsed(li_pgn.FROM_POSITION_BLACK_FIRST))
    assert [(m.ply, m.move_number, m.color, m.san) for m in moves] == [
        (1, 1, "black", "e5"),
        (2, 2, "white", "Nf3"),
        (3, 2, "black", "Nc6"),
    ]


def test_moves_from_parsed_pgn_mate_evals():
    moves = moves_from_parsed_pgn(parsed(li_pgn.MATE_EVALS_BLACK_WINS))
    assert (moves[2].eval_cp, moves[2].eval_mate) == (None, -1)
    assert moves[-1].san == "Qh4#" and moves[-1].eval_mate is None


def test_moves_from_parsed_pgn_handles_string_keys():
    moves = moves_from_parsed_pgn(
        {"moves": {"10": {"white": {"move": "a3"}}, "9": {"black": {"move": "h6"}}}}
    )
    assert [(m.move_number, m.san) for m in moves] == [(9, "h6"), (10, "a3")]


def test_moves_from_san():
    moves = moves_from_san("e4 e5 Nf3")
    assert [(m.ply, m.move_number, m.color) for m in moves] == [
        (1, 1, "white"),
        (2, 1, "black"),
        (3, 2, "white"),
    ]
    assert moves_from_san("") == []


def test_moves_from_san_follows_fen_side_and_number():
    fen = "8/8/8/8/8/8/8/K6k b - - 0 41"
    moves = moves_from_san("Kh2 Ka2", fen)
    assert [(m.move_number, m.color) for m in moves] == [(41, "black"), (42, "white")]


# --- mapping tables -----------------------------------------------------------


@pytest.mark.parametrize(
    "raw, initial, increment, days",
    [
        ("600", 600, 0, None),
        ("180+2", 180, 2, None),
        ("1/259200", None, None, 3),
        ("1/604800", None, None, 7),
        ("-", None, None, None),
        ("", None, None, None),
        (None, None, None, None),
    ],
)
def test_chesscom_time_control(raw, initial, increment, days):
    tc = chesscom_time_control(raw)
    assert (tc.initial_seconds, tc.increment_seconds, tc.days_per_move) == (
        initial,
        increment,
        days,
    )
    assert tc.raw == raw


@pytest.mark.parametrize(
    "raw, expected",
    [
        ({"clock": {"initial": 180, "increment": 2, "totalTime": 260}}, (180, 2, None)),
        ({"daysPerTurn": 3}, (None, None, 3)),
        ({}, (None, None, None)),
    ],
)
def test_lichess_time_control(raw, expected):
    tc = lichess_time_control(raw)
    assert (tc.initial_seconds, tc.increment_seconds, tc.days_per_move) == expected


def test_lichess_time_control_raw_strings():
    assert lichess_time_control({"clock": {"initial": 60, "increment": 1}}).raw == (
        "60+1"
    )
    assert lichess_time_control({"daysPerTurn": 2}).raw == "1/172800"


def chesscom(**changes) -> dict:
    """The blitz mate fixture with fields swapped out."""
    g = dict(fx.CHESSCOM_BLITZ_MATE)
    for key in ("white", "black"):
        if key in changes:
            g[key] = {**g[key], "result": changes.pop(key)}
    g.update(changes)
    return g


@pytest.mark.parametrize(
    "time_class, speed",
    [
        ("bullet", "bullet"),
        ("blitz", "blitz"),
        ("rapid", "rapid"),
        ("daily", "correspondence"),
        ("standard", "other"),
    ],
)
def test_chesscom_speed(time_class, speed):
    g = game_from_chesscom(chesscom(time_class=time_class))
    assert (g.speed, g.speed_raw) == (speed, time_class)


@pytest.mark.parametrize(
    "rules, variant",
    [
        ("chess", "standard"),
        ("chess960", "chess960"),
        ("crazyhouse", "crazyhouse"),
        ("bughouse", "bughouse"),
        ("kingofthehill", "king_of_the_hill"),
        ("threecheck", "three_check"),
        ("oddschess", "oddschess"),
    ],
)
def test_chesscom_variant(rules, variant):
    g = game_from_chesscom(chesscom(rules=rules))
    assert (g.variant, g.variant_raw) == (variant, rules)


@pytest.mark.parametrize(
    "white, black, termination, termination_raw",
    [
        ("win", "checkmated", "checkmate", "checkmated"),
        ("resigned", "win", "resignation", "resigned"),
        ("timeout", "win", "timeout", "timeout"),
        ("win", "abandoned", "abandoned", "abandoned"),
        ("aborted", "aborted", "aborted", "aborted"),
        ("kingofthehill", "win", "variant_end", "kingofthehill"),
        ("win", "threecheck", "variant_end", "threecheck"),
        ("agreed", "agreed", "draw_agreement", "agreed"),
        ("repetition", "repetition", "repetition", "repetition"),
        ("stalemate", "stalemate", "stalemate", "stalemate"),
        ("insufficient", "insufficient", "insufficient_material", "insufficient"),
        ("50move", "50move", "fifty_move", "50move"),
        (
            "timevsinsufficient",
            "timevsinsufficient",
            "timeout_vs_insufficient",
            "timevsinsufficient",
        ),
        ("win", "lose", "other", "lose"),
        ("bughousepartnerlose", "win", "other", "bughousepartnerlose"),
        ("win", "somethingnew", "other", "somethingnew"),
    ],
)
def test_chesscom_termination(white, black, termination, termination_raw):
    g = game_from_chesscom(chesscom(white=white, black=black))
    assert (g.termination, g.termination_raw) == (termination, termination_raw)
    assert (g.white.result_raw, g.black.result_raw) == (white, black)


@pytest.mark.parametrize(
    "white, black, result, winner",
    [
        ("win", "resigned", "1-0", "white"),
        ("timeout", "win", "0-1", "black"),
        ("agreed", "agreed", "1/2-1/2", None),
        ("timevsinsufficient", "timevsinsufficient", "1/2-1/2", None),
        ("lose", "lose", "*", None),
    ],
)
def test_chesscom_result_falls_back_to_player_codes(white, black, result, winner):
    g = game_from_chesscom(chesscom(pgn=None, white=white, black=black))
    assert (g.result, g.winner) == (result, winner)


def test_chesscom_result_prefers_pgn_header():
    # the header wins even if the player codes disagree
    g = game_from_chesscom(chesscom(white="timeout", black="win"))
    assert (g.result, g.winner) == ("1-0", "white")


@pytest.mark.parametrize(
    "key, variant",
    [
        ("standard", "standard"),
        ("chess960", "chess960"),
        ("crazyhouse", "crazyhouse"),
        ("antichess", "antichess"),
        ("atomic", "atomic"),
        ("horde", "horde"),
        ("kingOfTheHill", "king_of_the_hill"),
        ("racingKings", "racing_kings"),
        ("threeCheck", "three_check"),
        ("fromPosition", "standard"),
        ("someNewThing", "some_new_thing"),
        (None, "standard"),
    ],
)
def test_lichess_variant(key, variant):
    assert lichess_variant(key) == variant


def lichess(**changes) -> dict:
    return {**fx.LICHESS_RESIGN, **changes}


@pytest.mark.parametrize(
    "speed, expected",
    [
        ("ultraBullet", "ultrabullet"),
        ("bullet", "bullet"),
        ("blitz", "blitz"),
        ("rapid", "rapid"),
        ("classical", "classical"),
        ("correspondence", "correspondence"),
        ("hyperBullet", "other"),
    ],
)
def test_lichess_speed(speed, expected):
    g = game_from_lichess(lichess(speed=speed))
    assert (g.speed, g.speed_raw) == (expected, speed)


@pytest.mark.parametrize(
    "status, winner, termination, result",
    [
        ("mate", "white", "checkmate", "1-0"),
        ("resign", "black", "resignation", "0-1"),
        ("outoftime", "white", "timeout", "1-0"),
        ("outoftime", None, "timeout_vs_insufficient", "1/2-1/2"),
        ("timeout", "black", "abandoned", "0-1"),
        ("noStart", "white", "abandoned", "1-0"),
        ("noStart", None, "abandoned", "*"),
        ("draw", None, "other", "1/2-1/2"),
        ("stalemate", None, "stalemate", "1/2-1/2"),
        ("insufficientMaterialClaim", None, "insufficient_material", "1/2-1/2"),
        ("aborted", None, "aborted", "*"),
        ("variantEnd", "black", "variant_end", "0-1"),
        ("variantEnd", None, "variant_end", "1/2-1/2"),
        ("cheat", "white", "other", "1-0"),
        ("unknownFinish", None, "other", "*"),
        ("started", None, "other", "*"),
        ("created", None, "other", "*"),
        ("brandNew", "white", "other", "1-0"),
    ],
)
def test_lichess_status(status, winner, termination, result):
    raw = {k: v for k, v in lichess(status=status).items() if k != "winner"}
    if winner:
        raw["winner"] = winner
    g = game_from_lichess(raw)
    assert (g.termination, g.termination_raw) == (termination, status)
    assert (g.result, g.winner) == (result, winner)


# --- Chess.com fixtures -------------------------------------------------------


def test_chesscom_blitz_mate():
    g = game_from_chesscom(fx.CHESSCOM_BLITZ_MATE)
    assert g.provider == "chesscom"
    assert g.id == "00000000-0000-4000-8000-000000000001"
    assert g.url == "https://www.chess.com/game/live/100000001"
    assert g.rated is True
    assert (g.variant, g.speed) == ("standard", "blitz")
    assert g.time_control.initial_seconds == 300
    assert g.start_time == utc(2024, 1, 5, 3, 10, 53)
    assert g.end_time == utc(2024, 1, 5, 3, 12, 2)
    assert (g.white.username, g.white.rating) == ("alice", 653)
    assert (g.black.username, g.black.rating) == ("bob", 636)
    assert (g.result, g.winner, g.termination) == ("1-0", "white", "checkmate")
    assert g.opening.eco == "C00"
    assert g.opening.name == "French Defense Knight Variation"
    assert g.initial_fen is None
    assert g.final_fen.startswith("r1bqkb1r/1pp1nQpp/")
    assert g.headers["Termination"] == "alice won by checkmate"
    assert len(g.moves) == 15
    assert (g.moves[-1].san, g.moves[-1].color) == ("Qf7#", "white")
    assert g.moves[0].clock_seconds == 299.0
    assert g.raw is None


def test_chesscom_rapid_timeout():
    g = game_from_chesscom(fx.CHESSCOM_RAPID_TIMEOUT)
    assert (g.speed, g.result, g.winner) == ("rapid", "0-1", "black")
    assert (g.termination, g.termination_raw) == ("timeout", "timeout")
    assert g.opening.name == "Queens Pawn Opening Chigorin Variation"
    assert len(g.moves) == 48


def test_chesscom_agreed_draw():
    g = game_from_chesscom(fx.CHESSCOM_AGREED)
    assert (g.result, g.winner, g.termination) == ("1/2-1/2", None, "draw_agreement")
    assert g.time_control.initial_seconds == 1800


def test_chesscom_repetition():
    g = game_from_chesscom(fx.CHESSCOM_REPETITION)
    assert (g.result, g.termination) == ("1/2-1/2", "repetition")
    # "with-3-d5...6.cxd5" keeps the name, drops the moves
    assert g.opening.name == "Neo Grunfeld Defense with 3 d5"


def test_chesscom_daily():
    g = game_from_chesscom(fx.CHESSCOM_DAILY)
    assert (g.speed, g.speed_raw) == ("correspondence", "daily")
    assert g.time_control.days_per_move == 3
    assert g.time_control.raw == "1/259200"
    # daily games carry their own start_time
    assert g.start_time == s_to_dt(fx.CHESSCOM_DAILY["start_time"])
    assert g.url.startswith("https://www.chess.com/game/daily/")


def test_chesscom_960():
    g = game_from_chesscom(fx.CHESSCOM_960)
    assert (g.variant, g.variant_raw) == ("chess960", "chess960")
    assert g.initial_fen == fx.CHESSCOM_960["initial_setup"]
    assert g.headers["Variant"] == "Chess960"
    assert g.moves


def test_chesscom_custom_setup():
    g = game_from_chesscom(fx.CHESSCOM_CUSTOM_SETUP)
    assert g.variant == "standard"
    assert g.initial_fen == "4k3/8/8/8/8/8/4P3/4K3 w - - 0 1"


def test_chesscom_abandoned_without_moves():
    g = game_from_chesscom(fx.CHESSCOM_ABANDONED)
    assert (g.termination, g.result) == ("abandoned", "0-1")
    assert g.moves == []
    # chess.com's placeholder opening
    assert g.opening.eco == "A00" and g.opening.name is None


def test_chesscom_unparseable_pgn():
    g = game_from_chesscom(fx.CHESSCOM_BAD_PGN)
    assert g.moves == [] and g.headers == {}
    assert g.pgn == "not a pgn"
    # still built from the JSON fields
    assert (g.result, g.termination) == ("1-0", "checkmate")
    assert g.start_time is None
    assert g.opening.eco is None
    assert g.opening.name == "French Defense Knight Variation"


def test_chesscom_uses_existing_parsed_pgn():
    raw = {**fx.CHESSCOM_BLITZ_MATE, "parsed_pgn": parsed(fx.CHESSCOM_AGREED["pgn"])}
    g = game_from_chesscom(raw)
    assert len(g.moves) == 12


def test_chesscom_id_from_url_without_uuid():
    raw = {k: v for k, v in fx.CHESSCOM_BLITZ_MATE.items() if k != "uuid"}
    assert game_from_chesscom(raw).id == "100000001"


def test_chesscom_include_raw_drops_parsed_pgn():
    raw = {**fx.CHESSCOM_BLITZ_MATE, "parsed_pgn": parsed(fx.CHESSCOM_AGREED["pgn"])}
    g = game_from_chesscom(raw, include_raw=True)
    assert g.raw == fx.CHESSCOM_BLITZ_MATE


# --- Lichess fixtures ---------------------------------------------------------


def test_lichess_blitz_mate_with_clocks_and_evals():
    g = game_from_lichess(fx.LICHESS_BLITZ_MATE)
    assert g.provider == "lichess"
    assert g.id == "Game0008"
    assert g.url == "https://lichess.org/Game0008"
    assert g.rated is True
    assert (g.variant, g.speed) == ("standard", "blitz")
    assert (g.time_control.initial_seconds, g.time_control.increment_seconds) == (
        300,
        3,
    )
    assert g.start_time == ms_to_dt(fx.LICHESS_BLITZ_MATE["createdAt"])
    assert g.end_time == ms_to_dt(fx.LICHESS_BLITZ_MATE["lastMoveAt"])
    assert (g.white.username, g.white.rating, g.white.rating_diff) == (
        "alice",
        1731,
        -4,
    )
    assert (g.black.username, g.black.rating_diff) == ("bob", 5)
    assert (g.result, g.winner, g.termination) == ("0-1", "black", "checkmate")
    assert g.opening.eco == "C38"
    assert g.opening.name == "King's Gambit Accepted: Traditional Variation"
    assert g.initial_fen is None
    assert len(g.moves) == 20
    assert (g.moves[0].clock_seconds, g.moves[0].eval_cp) == (300.0, 18)
    assert any(m.eval_mate == -1 for m in g.moves)
    assert g.moves[-1].san == "Qxh4#"


def test_lichess_resign():
    g = game_from_lichess(fx.LICHESS_RESIGN)
    assert (g.termination, g.result) == ("resignation", "0-1")
    assert g.time_control.raw == "360+0"
    assert g.final_fen is None


def test_lichess_final_fen_from_last_fen():
    fen = "1K6/1qr5/8/8/8/4k3/8/8 w - - 8 1"
    g = game_from_lichess({**fx.LICHESS_RESIGN, "lastFen": fen})
    assert g.final_fen == fen


def test_lichess_outoftime():
    g = game_from_lichess(fx.LICHESS_OUTOFTIME)
    assert (g.termination, g.result, g.winner) == ("timeout", "0-1", "black")


def test_lichess_outoftime_draw():
    g = game_from_lichess(fx.LICHESS_OUTOFTIME_DRAW)
    assert (g.termination, g.result) == ("timeout_vs_insufficient", "1/2-1/2")
    assert g.white.title == "GM"


def test_lichess_draw():
    g = game_from_lichess(fx.LICHESS_DRAW)
    assert (g.result, g.winner) == ("1/2-1/2", None)
    assert (g.termination, g.termination_raw) == ("other", "draw")
    assert g.white.title == "BOT"


def test_lichess_stalemate():
    g = game_from_lichess(fx.LICHESS_STALEMATE)
    assert (g.termination, g.result) == ("stalemate", "1/2-1/2")


def test_lichess_aborted():
    g = game_from_lichess(fx.LICHESS_ABORTED)
    assert (g.termination, g.result, g.winner) == ("aborted", "*", None)
    assert [m.san for m in g.moves] == ["e4"]


def test_lichess_ai_opponent():
    g = game_from_lichess(fx.LICHESS_AI)
    ai = g.black
    assert (ai.username, ai.rating, ai.ai_level) == (None, None, 1)
    assert g.white.username == "alice"


def test_lichess_from_position():
    g = game_from_lichess(fx.LICHESS_FROM_POSITION)
    assert (g.variant, g.variant_raw) == ("standard", "fromPosition")
    assert g.initial_fen == fx.LICHESS_FROM_POSITION["initialFen"]
    assert g.moves[0].move_number == 75


def test_lichess_from_position_fen_from_pgn_header():
    raw = {k: v for k, v in fx.LICHESS_FROM_POSITION.items() if k != "initialFen"}
    g = game_from_lichess(raw)
    assert g.initial_fen == fx.LICHESS_FROM_POSITION["initialFen"]


def test_lichess_960():
    g = game_from_lichess(fx.LICHESS_960)
    assert (g.variant, g.variant_raw) == ("chess960", "chess960")
    assert g.initial_fen.startswith("nqrkrbbn/")
    assert g.opening is None


def test_lichess_king_of_the_hill():
    g = game_from_lichess(fx.LICHESS_KOTH)
    assert (g.variant, g.speed) == ("king_of_the_hill", "ultrabullet")
    assert g.termination == "variant_end"


def test_lichess_correspondence():
    g = game_from_lichess(fx.LICHESS_CORRESPONDENCE)
    assert g.speed == "correspondence"
    assert g.time_control.days_per_move == 14
    assert g.time_control.initial_seconds is None


def test_lichess_no_pgn_falls_back_to_moves_string():
    g = game_from_lichess(fx.LICHESS_NO_PGN)
    assert g.pgn is None and g.headers == {}
    expected = fx.LICHESS_NO_PGN["moves"].split()
    assert [m.san for m in g.moves] == expected
    assert all(m.clock_seconds is None for m in g.moves)
    # opening still comes from the JSON
    assert g.opening.eco == "A06"


def test_lichess_include_raw():
    g = game_from_lichess(fx.LICHESS_RESIGN, include_raw=True)
    assert g.raw == fx.LICHESS_RESIGN
    assert g.raw is not fx.LICHESS_RESIGN


def test_lichess_missing_id_raises():
    with pytest.raises(KeyError):
        game_from_lichess({"players": {}})
