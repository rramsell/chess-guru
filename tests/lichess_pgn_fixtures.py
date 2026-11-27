"""PGN strings in the format returned by the Lichess game export API."""

LICHESS_HEADERS = """[Event "Rated blitz game"]
[Site "https://lichess.org/AbCd1234"]
[Date "2024.06.01"]
[White "alice"]
[Black "bob"]
[Result "{result}"]
[GameId "AbCd1234"]
[UTCDate "2024.06.01"]
[UTCTime "12:00:00"]
[WhiteElo "1500"]
[BlackElo "1480"]
[WhiteRatingDiff "+6"]
[BlackRatingDiff "-6"]
[Variant "Standard"]
[TimeControl "180+0"]
[ECO "{eco}"]
[Opening "{opening}"]
[Termination "Normal"]{extra}"""


def _pgn(
    moves: str,
    result: str,
    eco: str = "C50",
    opening: str = "Italian Game",
    extra: str = "",
) -> str:
    headers = LICHESS_HEADERS.format(
        result=result, eco=eco, opening=opening, extra=extra
    )
    # the export ends each game with blank lines
    return f"{headers}\n\n{moves}\n\n\n"


# Scholar's mate, clocks only.
CLOCKS_ONLY = _pgn(
    "1. e4 { [%clk 0:03:00] } 1... e5 { [%clk 0:03:00] } "
    "2. Bc4 { [%clk 0:02:58] } 2... Nc6 { [%clk 0:02:57] } "
    "3. Qh5 { [%clk 0:02:55] } 3... Nf6 { [%clk 0:02:50] } "
    "4. Qxf7# { [%clk 0:02:53] } 1-0",
    "1-0",
)

# Analysed game: evals before clocks in the same comment.
CLOCKS_AND_EVALS = _pgn(
    "1. e4 { [%eval 0.17] [%clk 0:03:00] } 1... e5 { [%eval 0.19] [%clk 0:03:00] } "
    "2. Nf3 { [%eval 0.2] [%clk 0:02:59] } 2... Nc6 { [%eval 0.22] [%clk 0:02:58] } "
    "3. Bb5 { [%eval 0.14] [%clk 0:02:57] } 3... a6 { [%eval 0.25] [%clk 0:02:55] } "
    "4. Ba4 { [%eval 0.13] [%clk 0:02:55] } 1-0",
    "1-0",
    eco="C70",
    opening="Ruy Lopez: Morphy Defense",
    extra='\n[Annotator "lichess.org"]',
)

# Fool's mate with mate-in-N evals; ends on a black move.
MATE_EVALS_BLACK_WINS = _pgn(
    "1. f3 { [%eval -0.65] [%clk 0:03:00] } 1... e5 { [%eval -0.4] [%clk 0:03:00] } "
    "2. g4 { [%eval #-1] [%clk 0:02:58] } 2... Qh4# { [%clk 0:02:59] } 0-1",
    "0-1",
    eco="A00",
    opening="Barnes Opening: Fool's Mate",
    extra='\n[Annotator "lichess.org"]',
)

# Clocks turned off in the export.
NO_CLOCKS = _pgn("1. d4 d5 2. c4 e6 3. Nc3 Nf6 4. Bg5 1-0", "1-0", "D35", "QGD")

# Draw by repetition, clocks only.
DRAW = _pgn(
    "1. Nf3 { [%clk 0:03:00] } 1... Nf6 { [%clk 0:03:00] } "
    "2. Ng1 { [%clk 0:02:59] } 2... Ng8 { [%clk 0:02:59] } "
    "3. Nf3 { [%clk 0:02:58] } 3... Nf6 { [%clk 0:02:58] } 1/2-1/2",
    "1/2-1/2",
    eco="A04",
    opening="Zukertort Opening",
)

# Game from a position with black to move.
FROM_POSITION_BLACK_FIRST = _pgn(
    "1... e5 { [%clk 0:03:00] } "
    "2. Nf3 { [%clk 0:02:59] } 2... Nc6 { [%clk 0:02:58] } *",
    "*",
    eco="?",
    opening="?",
    extra=(
        '\n[FEN "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"]'
        '\n[SetUp "1"]'
    ),
)
