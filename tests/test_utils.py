from datetime import datetime, timedelta, timezone

import pytest

from chess_guru.utils import (
    _extract_move_and_clock,
    _parse_pgn_headers,
    _split_pgn_headers_and_moves,
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
        ("e4 {[%clk 0:09:58.5]}", {"move": "e4", "clock": "0:09:58.5"}),
        ("Qxf7# {[%clk 0:00:01]}", {"move": "Qxf7#", "clock": "0:00:01"}),
        ("O-O-O {[%clk 167:59:46]}", {"move": "O-O-O", "clock": "167:59:46"}),
        ("e8=Q+", {"move": "e8=Q+", "clock": None}),
        ("", {"move": None, "clock": None}),
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
        "white": {"move": "e4", "clock": "0:09:58.5"},
        "black": {"move": "e5", "clock": "0:09:57.2"},
    }
    assert moves[4] == {"white": {"move": "Qxf7#", "clock": "0:09:48.9"}}


def test_parse_pgn_game_ending_on_black_move():
    _, result, moves = parse_pgn(BLACK_MATE_WITH_CLOCKS)
    assert result == "0-1"
    assert moves[2]["black"] == {"move": "Qh4#", "clock": "0:09:56"}


def test_parse_pgn_draw():
    _, result, moves = parse_pgn(DRAW_WITH_CLOCKS)
    assert result == "1/2-1/2"
    assert [moves[i]["white"]["move"] for i in (1, 2, 3)] == ["Nf3", "Ng1", "Nf3"]
    assert moves[3]["black"] == {"move": "Nf6", "clock": "167:57:12"}


def test_parse_pgn_ongoing():
    _, result, moves = parse_pgn(ONGOING)
    assert result == "*"
    assert moves[2] == {"white": {"move": "c4", "clock": "71:40:01"}}


def test_parse_pgn_without_clocks_keeps_black_moves():
    _, result, moves = parse_pgn(NO_CLOCKS)
    assert result == "1-0"
    assert moves == {
        1: {
            "white": {"move": "e4", "clock": None},
            "black": {"move": "e5", "clock": None},
        },
        2: {
            "white": {"move": "Nf3", "clock": None},
            "black": {"move": "Nc6", "clock": None},
        },
        3: {
            "white": {"move": "Bb5", "clock": None},
            "black": {"move": "a6", "clock": None},
        },
        4: {"white": {"move": "Ba4", "clock": None}},
    }


def test_parse_pgn_crlf_line_endings():
    crlf = WHITE_MATE_WITH_CLOCKS.replace("\n", "\r\n")
    assert parse_pgn(crlf) == parse_pgn(WHITE_MATE_WITH_CLOCKS)


def test_parse_pgn_malformed_raises_value_error():
    with pytest.raises(ValueError, match="blank line"):
        parse_pgn(MALFORMED_NO_BLANK_LINE)
