"""Realistic PGN strings in the format returned by the Chess.com archive API."""

CHESSCOM_HEADERS = """[Event "Live Chess"]
[Site "Chess.com"]
[Date "2024.06.01"]
[Round "-"]
[White "alice"]
[Black "bob"]
[Result "{result}"]
[CurrentPosition "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq -"]
[Timezone "UTC"]
[ECO "C50"]
[ECOUrl "https://www.chess.com/openings/Italian-Game"]
[UTCDate "2024.06.01"]
[UTCTime "12:00:00"]
[WhiteElo "1500"]
[BlackElo "1480"]
[TimeControl "600"]
[Termination "{termination}"]
[StartTime "12:00:00"]
[EndDate "2024.06.01"]
[EndTime "12:05:00"]
[Link "https://www.chess.com/game/live/123456789"]"""


def _pgn(moves: str, result: str, termination: str) -> str:
    headers = CHESSCOM_HEADERS.format(result=result, termination=termination)
    return f"{headers}\n\n{moves}\n"


# Scholar's mate: ends on a white move, with clocks.
WHITE_MATE_WITH_CLOCKS = _pgn(
    "1. e4 {[%clk 0:09:58.5]} 1... e5 {[%clk 0:09:57.2]} "
    "2. Bc4 {[%clk 0:09:55.1]} 2... Nc6 {[%clk 0:09:54]} "
    "3. Qh5 {[%clk 0:09:50.3]} 3... Nf6 {[%clk 0:09:40.8]} "
    "4. Qxf7# {[%clk 0:09:48.9]} 1-0",
    "1-0",
    "alice won by checkmate",
)

# Fool's mate: ends on a black move, with clocks.
BLACK_MATE_WITH_CLOCKS = _pgn(
    "1. f3 {[%clk 0:09:59]} 1... e5 {[%clk 0:09:58]} "
    "2. g4 {[%clk 0:09:57]} 2... Qh4# {[%clk 0:09:56]} 0-1",
    "0-1",
    "bob won by checkmate",
)

# Draw by repetition, daily-game style clocks (hours > 24).
DRAW_WITH_CLOCKS = _pgn(
    "1. Nf3 {[%clk 167:59:46]} 1... Nf6 {[%clk 167:58:10]} "
    "2. Ng1 {[%clk 167:59:01]} 2... Ng8 {[%clk 167:57:59]} "
    "3. Nf3 {[%clk 167:58:30]} 3... Nf6 {[%clk 167:57:12]} 1/2-1/2",
    "1/2-1/2",
    "Game drawn by repetition",
)

# No clock comments at all (no "N..." markers in the movetext).
NO_CLOCKS = _pgn(
    "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 1-0",
    "1-0",
    "bob resigned",
)

# Game still in progress.
ONGOING = _pgn(
    "1. d4 {[%clk 71:58:12]} 1... d5 {[%clk 71:59:00]} 2. c4 {[%clk 71:40:01]} *",
    "*",
    "",
)

MALFORMED_NO_BLANK_LINE = '[Event "Live Chess"]\n[Site "Chess.com"]\n1. e4 e5 *'
