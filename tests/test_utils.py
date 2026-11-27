from datetime import datetime, timedelta, timezone

import pytest

import lichess_pgn_fixtures as li
from chess_guru.utils import (
    _extract_move_and_clock,
    _parse_pgn_headers,
    _split_pgn_headers_and_moves,
    annotate_games,
    attach_parsed_pgn,
    game_in_range,
    parse_archive_year_month,
    parse_pgn,
    to_utc_dt,
)
from pgn_fixtures import (
    BLACK_MATE_WITH_CLOCKS,
    DRAW_WITH_CLOCKS,
    MALFORMED_NO_BLANK_LINE,
    NO_CLOCKS,
    ONGOING,
    WHITE_MATE_WITH_CLOCKS,
)

# --- parse_archive_year_month -------------------------------------------------


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://api.chess.com/pub/player/erik/games/2024/06", (2024, 6)),
        ("https://api.chess.com/pub/player/erik/games/2024/06/", (2024, 6)),
        ("https://api.chess.com/pub/player/erik/games/2009/12?x=1", (2009, 12)),
    ],
)
def test_parse_archive_year_month(url, expected):
    assert parse_archive_year_month(url) == expected


def test_parse_archive_year_month_rejects_non_archive_url():
    with pytest.raises(ValueError):
        parse_archive_year_month("https://api.chess.com/pub/player/erik")


# --- to_utc_dt ----------------------------------------------------------------


def test_to_utc_dt_none():
    assert to_utc_dt(None) is None


def test_to_utc_dt_naive_is_assumed_utc():
    out = to_utc_dt(datetime(2024, 1, 1, 12, 0))
    assert out == datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert out.tzinfo is timezone.utc


def test_to_utc_dt_converts_aware():
    est = timezone(timedelta(hours=-5))
    out = to_utc_dt(datetime(2024, 1, 1, 7, 0, tzinfo=est))
    assert out == datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    assert out.utcoffset() == timedelta(0)


# --- header parsing -----------------------------------------------------------


def test_parse_pgn_headers():
    headers = _parse_pgn_headers(
        '[Event "Live Chess"]\n[White "alice"]\n[Termination ""]\n'
        '[Link "https://www.chess.com/game/live/1"]'
    )
    assert headers == {
        "Event": "Live Chess",
        "White": "alice",
        "Termination": "",
        "Link": "https://www.chess.com/game/live/1",
    }


def test_parse_pgn_headers_full_chesscom_block():
    headers, _, _ = parse_pgn(WHITE_MATE_WITH_CLOCKS)
    assert headers["Event"] == "Live Chess"
    assert headers["White"] == "alice"
    assert headers["Black"] == "bob"
    assert headers["Result"] == "1-0"
    assert headers["WhiteElo"] == "1500"
    assert headers["ECOUrl"] == "https://www.chess.com/openings/Italian-Game"
    assert headers["CurrentPosition"].startswith("r1bqkb1r/")
    assert len(headers) == 21


# --- clock extraction ---------------------------------------------------------


@pytest.mark.parametrize(
    "text, expected",
    [
        ("e4 {[%clk 0:09:58.5]}", {"move": "e4", "clock": "0:09:58.5", "eval": None}),
        ("Qxf7# {[%clk 0:00:01]}", {"move": "Qxf7#", "clock": "0:00:01", "eval": None}),
        (
            "O-O-O {[%clk 167:59:46]}",
            {"move": "O-O-O", "clock": "167:59:46", "eval": None},
        ),
        ("e8=Q+", {"move": "e8=Q+", "clock": None, "eval": None}),
        ("", {"move": None, "clock": None, "eval": None}),
    ],
)
def test_extract_move_and_clock(text, expected):
    assert _extract_move_and_clock(text) == expected


# --- result parsing -----------------------------------------------------------


@pytest.mark.parametrize(
    "pgn, expected",
    [
        (WHITE_MATE_WITH_CLOCKS, "1-0"),
        (BLACK_MATE_WITH_CLOCKS, "0-1"),
        (DRAW_WITH_CLOCKS, "1/2-1/2"),
        (ONGOING, "*"),
        (NO_CLOCKS, "1-0"),
    ],
)
def test_result_parsing(pgn, expected):
    _, result = parse_pgn(pgn)[:2]
    assert result == expected


def test_result_is_stripped_from_movetext():
    _, moves, result = _split_pgn_headers_and_moves(DRAW_WITH_CLOCKS)
    assert result == "1/2-1/2"
    assert not moves.endswith("1/2-1/2")
    assert moves.endswith("{[%clk 167:57:12]}")


def test_missing_result_is_none():
    _, result, moves = parse_pgn('[Event "x"]\n\n1. e4 e5')
    assert result is None
    assert moves[1]["black"]["move"] == "e5"


# --- full parse_pgn -----------------------------------------------------------


def test_parse_pgn_game_ending_on_white_move():
    _, result, moves = parse_pgn(WHITE_MATE_WITH_CLOCKS)
    assert result == "1-0"
    assert sorted(moves) == [1, 2, 3, 4]
    assert moves[1] == {
        "white": {"move": "e4", "clock": "0:09:58.5", "eval": None},
        "black": {"move": "e5", "clock": "0:09:57.2", "eval": None},
    }
    assert moves[4] == {"white": {"move": "Qxf7#", "clock": "0:09:48.9", "eval": None}}


def test_parse_pgn_game_ending_on_black_move():
    _, result, moves = parse_pgn(BLACK_MATE_WITH_CLOCKS)
    assert result == "0-1"
    assert moves[2]["black"] == {"move": "Qh4#", "clock": "0:09:56", "eval": None}


def test_parse_pgn_draw():
    _, result, moves = parse_pgn(DRAW_WITH_CLOCKS)
    assert result == "1/2-1/2"
    assert [moves[i]["white"]["move"] for i in (1, 2, 3)] == ["Nf3", "Ng1", "Nf3"]
    assert moves[3]["black"] == {"move": "Nf6", "clock": "167:57:12", "eval": None}


def test_parse_pgn_ongoing():
    _, result, moves = parse_pgn(ONGOING)
    assert result == "*"
    assert moves[2] == {"white": {"move": "c4", "clock": "71:40:01", "eval": None}}


def test_parse_pgn_without_clocks_keeps_black_moves():
    _, result, moves = parse_pgn(NO_CLOCKS)
    assert result == "1-0"
    assert moves == {
        1: {
            "white": {"move": "e4", "clock": None, "eval": None},
            "black": {"move": "e5", "clock": None, "eval": None},
        },
        2: {
            "white": {"move": "Nf3", "clock": None, "eval": None},
            "black": {"move": "Nc6", "clock": None, "eval": None},
        },
        3: {
            "white": {"move": "Bb5", "clock": None, "eval": None},
            "black": {"move": "a6", "clock": None, "eval": None},
        },
        4: {"white": {"move": "Ba4", "clock": None, "eval": None}},
    }


def test_parse_pgn_crlf_line_endings():
    crlf = WHITE_MATE_WITH_CLOCKS.replace("\n", "\r\n")
    assert parse_pgn(crlf) == parse_pgn(WHITE_MATE_WITH_CLOCKS)


def test_parse_pgn_malformed_raises_value_error():
    with pytest.raises(ValueError, match="blank line"):
        parse_pgn(MALFORMED_NO_BLANK_LINE)


# --- lichess PGNs -------------------------------------------------------------


def mv(move, clock=None, ev=None):
    return {"move": move, "clock": clock, "eval": ev}


@pytest.mark.parametrize(
    "text, expected",
    [
        ("e4 { [%clk 0:03:00] }", mv("e4", "0:03:00")),
        ("e4 { [%eval 0.17] [%clk 0:02:59] }", mv("e4", "0:02:59", "0.17")),
        ("g4 { [%eval #-1] [%clk 0:00:41] }", mv("g4", "0:00:41", "#-1")),
        ("Nf3 { [%clk 0:02:59] [%eval -1.5] }", mv("Nf3", "0:02:59", "-1.5")),
        ("Qh4# { [%eval #3,25] }", mv("Qh4#", None, "#3")),
        ("e5 { just a note }", mv("e5")),
    ],
)
def test_extract_lichess_comments(text, expected):
    assert _extract_move_and_clock(text) == expected


def test_lichess_headers():
    headers, _, _ = parse_pgn(li.CLOCKS_AND_EVALS)
    assert headers["Site"] == "https://lichess.org/AbCd1234"
    assert headers["Variant"] == "Standard"
    assert headers["Opening"] == "Ruy Lopez: Morphy Defense"
    assert headers["UTCDate"] == "2024.06.01"
    assert headers["Annotator"] == "lichess.org"
    assert headers["WhiteRatingDiff"] == "+6"


def test_lichess_fen_headers():
    headers, _, _ = parse_pgn(li.FROM_POSITION_BLACK_FIRST)
    assert headers["SetUp"] == "1"
    assert headers["FEN"].endswith("b KQkq - 0 1")


def test_lichess_clocks_only():
    _, result, moves = parse_pgn(li.CLOCKS_ONLY)
    assert result == "1-0"
    assert sorted(moves) == [1, 2, 3, 4]
    assert moves[1] == {"white": mv("e4", "0:03:00"), "black": mv("e5", "0:03:00")}
    assert moves[4] == {"white": mv("Qxf7#", "0:02:53")}


def test_lichess_clocks_and_evals():
    _, result, moves = parse_pgn(li.CLOCKS_AND_EVALS)
    assert result == "1-0"
    assert moves[1]["white"] == mv("e4", "0:03:00", "0.17")
    assert moves[3]["black"] == mv("a6", "0:02:55", "0.25")
    assert moves[4] == {"white": mv("Ba4", "0:02:55", "0.13")}


def test_lichess_mate_evals_and_black_finish():
    _, result, moves = parse_pgn(li.MATE_EVALS_BLACK_WINS)
    assert result == "0-1"
    assert moves[2] == {
        "white": mv("g4", "0:02:58", "#-1"),
        "black": mv("Qh4#", "0:02:59"),
    }


def test_lichess_no_clocks():
    _, result, moves = parse_pgn(li.NO_CLOCKS)
    assert result == "1-0"
    assert moves[3] == {"white": mv("Nc3"), "black": mv("Nf6")}
    assert moves[4] == {"white": mv("Bg5")}


def test_lichess_draw():
    _, result, moves = parse_pgn(li.DRAW)
    assert result == "1/2-1/2"
    assert moves[3] == {"white": mv("Nf3", "0:02:58"), "black": mv("Nf6", "0:02:58")}


def test_lichess_game_starting_with_black():
    _, result, moves = parse_pgn(li.FROM_POSITION_BLACK_FIRST)
    assert result == "*"
    assert moves == {
        1: {"black": mv("e5", "0:03:00")},
        2: {"white": mv("Nf3", "0:02:59"), "black": mv("Nc6", "0:02:58")},
    }


def test_comment_text_does_not_split_rounds():
    pgn = '[Event "x"]\n\n1. e4 { see 2. d4 instead } 1... e5 *'
    _, _, moves = parse_pgn(pgn)
    assert moves == {1: {"white": mv("e4"), "black": mv("e5")}}


# --- game_in_range / annotate_games ------------------------------------------

FROM = datetime(2024, 6, 1, tzinfo=timezone.utc)
TO = datetime(2024, 6, 30, tzinfo=timezone.utc)


def secs(dt):
    return int(dt.timestamp())


@pytest.mark.parametrize(
    "value, unit, expected",
    [
        (secs(FROM), "s", True),
        (secs(TO), "s", True),
        (secs(FROM) - 1, "s", False),
        (secs(TO) + 1, "s", False),
        (secs(FROM) * 1000, "ms", True),
        (secs(TO) * 1000, "ms", True),
        (secs(FROM) * 1000 - 1, "ms", False),
        (secs(TO) * 1000 + 1, "ms", False),
    ],
)
def test_game_in_range_bounds_are_inclusive(value, unit, expected):
    assert game_in_range({"t": value}, "t", FROM, TO, unit) is expected


def test_game_in_range_missing_key():
    assert game_in_range({}, "t", None, None) is True
    assert game_in_range({}, "t", FROM, None) is False
    assert game_in_range({}, "t", None, TO) is False


def test_game_in_range_rejects_unknown_unit():
    with pytest.raises(ValueError):
        game_in_range({"t": 1}, "t", FROM, TO, unit="us")


async def test_attach_parsed_pgn():
    g = {"pgn": li.CLOCKS_ONLY}
    out = await attach_parsed_pgn(g)
    assert out["parsed_pgn"]["result"] == "1-0"
    assert out["parsed_pgn"]["headers"]["White"] == "alice"
    assert "parsed_pgn" not in g


async def test_attach_parsed_pgn_keeps_bad_or_missing_pgn():
    bad = {"pgn": "garbage"}
    assert await attach_parsed_pgn(bad) is bad
    assert await attach_parsed_pgn({"id": 1}) == {"id": 1}


async def test_annotate_games_filters_and_parses():
    games = [
        {"t": secs(FROM) - 1, "pgn": li.DRAW},
        {"t": secs(FROM), "pgn": li.DRAW},
        {"pgn": li.DRAW},
        {"t": secs(TO), "pgn": "garbage"},
    ]
    out = await annotate_games(games, "t", FROM, TO)
    assert [g["t"] for g in out] == [secs(FROM), secs(TO)]
    assert out[0]["parsed_pgn"]["result"] == "1/2-1/2"
    assert "parsed_pgn" not in out[1]


async def test_annotate_games_without_bounds_keeps_everything():
    out = await annotate_games([{"pgn": li.DRAW}, {}], "t")
    assert len(out) == 2
