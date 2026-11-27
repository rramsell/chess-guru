"""Raw game dicts trimmed from real Chess.com and Lichess API responses,
with usernames swapped for fake ones."""

CHESSCOM_BLITZ_MATE = {
    "url": "https://www.chess.com/game/live/100000001",
    "pgn": '[Event "Live Chess"]\n'
    '[Site "Chess.com"]\n'
    '[Date "2024.01.05"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "1-0"]\n'
    "[CurrentPosition "
    '"r1bqkb1r/1pp1nQpp/p1n1p3/1B1pN3/3P4/8/PPP2PPP/RNB1K2R b KQkq -"]\n'
    '[Timezone "UTC"]\n'
    '[ECO "C00"]\n'
    "[ECOUrl "
    '"https://www.chess.com/openings/French-Defense-Knight-Variation-2...d5-3.e5"]\n'
    '[UTCDate "2024.01.05"]\n'
    '[UTCTime "03:10:53"]\n'
    '[WhiteElo "653"]\n'
    '[BlackElo "636"]\n'
    '[TimeControl "300"]\n'
    '[Termination "alice won by checkmate"]\n'
    '[StartTime "03:10:53"]\n'
    '[EndDate "2024.01.05"]\n'
    '[EndTime "03:12:02"]\n'
    '[Link "https://www.chess.com/game/live/100000001"]\n'
    "\n"
    "1. e4 {[%clk 0:04:59]} 1... e6 {[%clk 0:04:59]} 2. Nf3 {[%clk "
    "0:04:57.5]} 2... d5 {[%clk 0:04:56.2]} 3. e5 {[%clk 0:04:52.3]} 3... "
    "f6 {[%clk 0:04:52]} 4. d4 {[%clk 0:04:48.6]} 4... fxe5 {[%clk "
    "0:04:46.6]} 5. Nxe5 {[%clk 0:04:47.1]} 5... Nc6 {[%clk 0:04:44.5]} 6. "
    "Bb5 {[%clk 0:04:39.6]} 6... Ne7 {[%clk 0:04:28.8]} 7. Qf3 {[%clk "
    "0:04:34]} 7... a6 {[%clk 0:04:24.9]} 8. Qf7# {[%clk 0:04:30]} 1-0\n",
    "time_control": "300",
    "end_time": 1704424322,
    "rated": True,
    "accuracies": {"white": 90.49, "black": 43.5},
    "uuid": "00000000-0000-4000-8000-000000000001",
    "initial_setup": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "fen": "r1bqkb1r/1pp1nQpp/p1n1p3/1B1pN3/3P4/8/PPP2PPP/RNB1K2R b KQkq -",
    "time_class": "blitz",
    "rules": "chess",
    "white": {
        "rating": 653,
        "result": "win",
        "@id": "https://api.chess.com/pub/player/alice",
        "username": "alice",
    },
    "black": {
        "rating": 636,
        "result": "checkmated",
        "@id": "https://api.chess.com/pub/player/bob",
        "username": "bob",
    },
    "eco": "https://www.chess.com/openings/French-Defense-Knight-Variation-2...d5-3.e5",
}


CHESSCOM_RAPID_TIMEOUT = {
    "url": "https://www.chess.com/game/live/100000002",
    "pgn": '[Event "Live Chess"]\n'
    '[Site "Chess.com"]\n'
    '[Date "2023.06.12"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "0-1"]\n'
    '[CurrentPosition "Q4nk1/4pp1r/4N1pb/7p/2B1pPb1/p5P1/PPPR1n1P/2K3R1 w '
    '- -"]\n'
    '[Timezone "UTC"]\n'
    '[ECO "D00"]\n'
    "[ECOUrl "
    '"https://www.chess.com/openings/Queens-Pawn-Opening-Chigorin-Variation-2...c6"]\n'
    '[UTCDate "2023.06.12"]\n'
    '[UTCTime "23:49:28"]\n'
    '[WhiteElo "306"]\n'
    '[BlackElo "428"]\n'
    '[TimeControl "600"]\n'
    '[Termination "bob won on time"]\n'
    '[StartTime "23:49:28"]\n'
    '[EndDate "2023.06.13"]\n'
    '[EndTime "00:05:58"]\n'
    '[Link "https://www.chess.com/game/live/100000002"]\n'
    "\n"
    "1. d4 {[%clk 0:10:00]} 1... d5 {[%clk 0:10:00]} 2. Nc3 {[%clk "
    "0:09:58.2]} 2... c6 {[%clk 0:09:56.3]} 3. Be3 {[%clk 0:09:43.4]} 3... "
    "Bf5 {[%clk 0:09:39.3]} 4. Qd2 {[%clk 0:09:16.1]} 4... Qd6 {[%clk "
    "0:09:18.4]} 5. O-O-O {[%clk 0:08:55.2]} 5... Nf6 {[%clk 0:08:51]} 6. "
    "Nh3 {[%clk 0:08:37.7]} 6... g6 {[%clk 0:08:26.5]} 7. f4 {[%clk "
    "0:08:19.1]} 7... h5 {[%clk 0:08:11.8]} 8. g3 {[%clk 0:08:00.2]} 8... "
    "Bh6 {[%clk 0:08:02.9]} 9. Bg2 {[%clk 0:07:53.8]} 9... Nbd7 {[%clk "
    "0:07:58]} 10. Rhg1 {[%clk 0:06:57.4]} 10... b5 {[%clk 0:07:55.4]} 11. "
    "Bf2 {[%clk 0:06:21.8]} 11... a5 {[%clk 0:07:49.5]} 12. e4 {[%clk "
    "0:05:50.4]} 12... dxe4 {[%clk 0:06:56.4]} 13. d5 {[%clk 0:04:48.6]} "
    "13... cxd5 {[%clk 0:06:28.4]} 14. Nxb5 {[%clk 0:04:21.7]} 14... Qa6 "
    "{[%clk 0:05:19.3]} 15. Bf1 {[%clk 0:04:19.5]} 15... a4 {[%clk "
    "0:05:12.2]} 16. Nc7+ {[%clk 0:04:14.2]} 16... Kf8 {[%clk 0:05:04.7]} "
    "17. Bxa6 {[%clk 0:03:59.6]} 17... a3 {[%clk 0:04:55.9]} 18. Nxa8 "
    "{[%clk 0:03:44.4]} 18... Bxh3 {[%clk 0:04:54.5]} 19. Nc7 {[%clk "
    "0:01:45.4]} 19... Ng4 {[%clk 0:04:42.9]} 20. Qxd5 {[%clk 0:01:16.2]} "
    "20... Nxf2 {[%clk 0:04:30.4]} 21. Bc4 {[%clk 0:00:59.5]} 21... Rh7 "
    "{[%clk 0:04:13.7]} 22. Rd2 {[%clk 0:00:08.2]} 22... Bg4 {[%clk "
    "0:04:11.6]} 23. Ne6+ {[%clk 0:00:01.8]} 23... Kg8 {[%clk 0:03:52.5]} "
    "24. Qa8+ {[%clk 0:00:00.8]} 24... Nf8 {[%clk 0:03:42.8]} 0-1\n",
    "time_control": "600",
    "end_time": 1686614758,
    "rated": True,
    "uuid": "00000000-0000-4000-8000-000000000002",
    "initial_setup": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "fen": "Q4nk1/4pp1r/4N1pb/7p/2B1pPb1/p5P1/PPPR1n1P/2K3R1 w - -",
    "time_class": "rapid",
    "rules": "chess",
    "white": {
        "rating": 306,
        "result": "timeout",
        "@id": "https://api.chess.com/pub/player/alice",
        "username": "alice",
    },
    "black": {
        "rating": 428,
        "result": "win",
        "@id": "https://api.chess.com/pub/player/bob",
        "username": "bob",
    },
    "eco": "https://www.chess.com/openings/Queens-Pawn-Opening-Chigorin-Variation-2...c6",
}


CHESSCOM_AGREED = {
    "url": "https://www.chess.com/game/live/100000003",
    "pgn": '[Event "Live Chess"]\n'
    '[Site "Chess.com"]\n'
    '[Date "2023.06.30"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "1/2-1/2"]\n'
    "[CurrentPosition "
    '"r1bqk2r/pppp1p1p/5np1/2b1p3/2BnP3/3Q4/PPP2PPP/RNB1K1NR w KQkq -"]\n'
    '[Timezone "UTC"]\n'
    '[ECO "C20"]\n'
    '[ECOUrl "https://www.chess.com/openings/Kings-Pawn-Opening-1...e5"]\n'
    '[UTCDate "2023.06.30"]\n'
    '[UTCTime "20:53:23"]\n'
    '[WhiteElo "547"]\n'
    '[BlackElo "507"]\n'
    '[TimeControl "1800"]\n'
    '[Termination "Game drawn by agreement"]\n'
    '[StartTime "20:53:23"]\n'
    '[EndDate "2023.06.30"]\n'
    '[EndTime "20:55:20"]\n'
    '[Link "https://www.chess.com/game/live/100000003"]\n'
    "\n"
    "1. e4 {[%clk 0:30:00]} 1... e5 {[%clk 0:30:00]} 2. Qh5 {[%clk "
    "0:29:54.6]} 2... Nc6 {[%clk 0:29:58.8]} 3. Bc4 {[%clk 0:29:52.2]} "
    "3... g6 {[%clk 0:29:53.4]} 4. Qf3 {[%clk 0:29:50.5]} 4... Nf6 {[%clk "
    "0:29:48.7]} 5. d4 {[%clk 0:29:24.8]} 5... Nxd4 {[%clk 0:29:44]} 6. "
    "Qd3 {[%clk 0:29:15.9]} 6... Bc5 {[%clk 0:29:19.8]} 1/2-1/2\n",
    "time_control": "1800",
    "end_time": 1688158520,
    "rated": False,
    "uuid": "00000000-0000-4000-8000-000000000003",
    "initial_setup": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "fen": "r1bqk2r/pppp1p1p/5np1/2b1p3/2BnP3/3Q4/PPP2PPP/RNB1K1NR w KQkq -",
    "time_class": "rapid",
    "rules": "chess",
    "white": {
        "rating": 547,
        "result": "agreed",
        "@id": "https://api.chess.com/pub/player/alice",
        "username": "alice",
    },
    "black": {
        "rating": 507,
        "result": "agreed",
        "@id": "https://api.chess.com/pub/player/bob",
        "username": "bob",
    },
    "eco": "https://www.chess.com/openings/Kings-Pawn-Opening-1...e5",
}


CHESSCOM_REPETITION = {
    "url": "https://www.chess.com/game/live/100000004",
    "pgn": '[Event "Live Chess"]\n'
    '[Site "Chess.com"]\n'
    '[Date "2025.03.29"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "1/2-1/2"]\n'
    "[Tournament "
    '"https://www.chess.com/tournament/live/bullet-brawl-4093041"]\n'
    '[CurrentPosition "3r1rk1/pp1bppbp/n5p1/2P5/Qn6/N4NP1/PP2PPBP/R1B3K1 w '
    '- - 16 20"]\n'
    '[Timezone "UTC"]\n'
    '[ECO "D75"]\n'
    "[ECOUrl "
    '"https://www.chess.com/openings/Neo-Grunfeld-Defense-with-3-d5...6.cxd5-Nxd5-7.O-O-c5-8.dxc5"]\n'
    '[UTCDate "2025.03.29"]\n'
    '[UTCTime "16:07:50"]\n'
    '[WhiteElo "2614"]\n'
    '[BlackElo "3255"]\n'
    '[TimeControl "60"]\n'
    '[Termination "Game drawn by repetition"]\n'
    '[StartTime "16:07:50"]\n'
    '[EndDate "2025.03.29"]\n'
    '[EndTime "16:08:32"]\n'
    '[Link "https://www.chess.com/game/live/100000004"]\n'
    "\n"
    "1. g3 {[%clk 0:00:57.6]} 1... d5 {[%clk 0:00:59.9]} 2. Bg2 {[%clk "
    "0:00:57.3]} 2... Nf6 {[%clk 0:00:59.8]} 3. Nf3 {[%clk 0:00:56.7]} "
    "3... g6 {[%clk 0:00:59.5]} 4. O-O {[%clk 0:00:56.6]} 4... Bg7 {[%clk "
    "0:00:59.3]} 5. d4 {[%clk 0:00:56.1]} 5... O-O {[%clk 0:00:59.2]} 6. "
    "c4 {[%clk 0:00:55.8]} 6... c5 {[%clk 0:00:59.1]} 7. cxd5 {[%clk "
    "0:00:55.2]} 7... Nxd5 {[%clk 0:00:58.2]} 8. dxc5 {[%clk 0:00:54.5]} "
    "8... Nb4 {[%clk 0:00:57.1]} 9. Qb3 {[%clk 0:00:53.1]} 9... N8a6 "
    "{[%clk 0:00:55.5]} 10. Rd1 {[%clk 0:00:51.7]} 10... Be6 {[%clk "
    "0:00:51.4]} 11. Rxd8 {[%clk 0:00:49.7]} 11... Raxd8 {[%clk "
    "0:00:50.9]} 12. Qa4 {[%clk 0:00:46.7]} 12... Bd7 {[%clk 0:00:50.2]} "
    "13. Qb3 {[%clk 0:00:45.5]} 13... Be6 {[%clk 0:00:49.6]} 14. Qa4 "
    "{[%clk 0:00:44.9]} 14... Bf5 {[%clk 0:00:48.8]} 15. Na3 {[%clk "
    "0:00:42.8]} 15... Bd7 {[%clk 0:00:47.4]} 16. Qb3 {[%clk 0:00:41]} "
    "16... Be6 {[%clk 0:00:46.8]} 17. Qa4 {[%clk 0:00:40.3]} 17... Bd7 "
    "{[%clk 0:00:46.5]} 18. Qb3 {[%clk 0:00:39.8]} 18... Be6 {[%clk "
    "0:00:46]} 19. Qa4 {[%clk 0:00:39.2]} 19... Bd7 {[%clk 0:00:43.8]} "
    "1/2-1/2\n",
    "time_control": "60",
    "end_time": 1743264512,
    "rated": True,
    "accuracies": {"white": 95.26, "black": 85.72},
    "uuid": "00000000-0000-4000-8000-000000000004",
    "initial_setup": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "fen": "3r1rk1/pp1bppbp/n5p1/2P5/Qn6/N4NP1/PP2PPBP/R1B3K1 w - - 16 20",
    "time_class": "bullet",
    "rules": "chess",
    "white": {
        "rating": 2614,
        "result": "repetition",
        "@id": "https://api.chess.com/pub/player/alice",
        "username": "alice",
    },
    "black": {
        "rating": 3255,
        "result": "repetition",
        "@id": "https://api.chess.com/pub/player/bob",
        "username": "bob",
    },
    "eco": "https://www.chess.com/openings/Neo-Grunfeld-Defense-with-3-d5...6.cxd5-Nxd5-7.O-O-c5-8.dxc5",
}


CHESSCOM_DAILY = {
    "url": "https://www.chess.com/game/daily/100000005",
    "pgn": '[Event "Let\'s Play!"]\n'
    '[Site "Chess.com"]\n'
    '[Date "2023.06.16"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "0-1"]\n'
    '[CurrentPosition "r1bqkbnr/pppppppp/2n5/8/3P4/8/PPP1PPPP/RNBQKBNR w '
    'KQkq - 1 2"]\n'
    '[Timezone "UTC"]\n'
    '[ECO "A40"]\n'
    "[ECOUrl "
    '"https://www.chess.com/openings/Queens-Pawn-Opening-Mikenas-Defense"]\n'
    '[UTCDate "2023.06.16"]\n'
    '[UTCTime "00:08:46"]\n'
    '[WhiteElo "1200"]\n'
    '[BlackElo "400"]\n'
    '[TimeControl "1/259200"]\n'
    '[Termination "bob won on time"]\n'
    '[StartTime "00:08:46"]\n'
    '[EndDate "2023.06.19"]\n'
    '[EndTime "16:49:16"]\n'
    '[Link "https://www.chess.com/game/daily/100000005"]\n'
    "\n"
    "1. d4 {[%clk 1:36:48.5]} 1... Nc6 {[%clk 0:03:08.7]} 0-1\n",
    "time_control": "1/259200",
    "end_time": 1687193356,
    "rated": True,
    "uuid": "00000000-0000-4000-8000-000000000005",
    "initial_setup": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "fen": "r1bqkbnr/pppppppp/2n5/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 1 2",
    "start_time": 1686874126,
    "time_class": "daily",
    "rules": "chess",
    "white": {
        "rating": 1200,
        "result": "timeout",
        "@id": "https://api.chess.com/pub/player/alice",
        "username": "alice",
    },
    "black": {
        "rating": 400,
        "result": "win",
        "@id": "https://api.chess.com/pub/player/bob",
        "username": "bob",
    },
    "eco": "https://www.chess.com/openings/Queens-Pawn-Opening-Mikenas-Defense",
}


CHESSCOM_960 = {
    "url": "https://www.chess.com/game/live/100000006",
    "pgn": '[Event "Live Chess - Chess960"]\n'
    '[Site "Chess.com"]\n'
    '[Date "2025.03.28"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "0-1"]\n'
    '[Variant "Chess960"]\n'
    '[SetUp "1"]\n'
    '[FEN "rnbkrnqb/pppppppp/8/8/8/8/PPPPPPPP/RNBKRNQB w EAea - 0 1"]\n'
    "[Tournament "
    '"https://www.chess.com/tournament/live/freestyle-friday-march-28-2025-5542049"]\n'
    '[CurrentPosition "2k1r1qb/ppp4p/8/5PP1/3p3P/1b1n2N1/PP1B1P2/R2K2QB w '
    'Q - 2 20"]\n'
    '[Timezone "UTC"]\n'
    '[ECO "A00"]\n'
    '[ECOUrl "https://www.chess.com/openings/Grob-Opening-1...g6"]\n'
    '[UTCDate "2025.03.28"]\n'
    '[UTCTime "15:18:21"]\n'
    '[WhiteElo "2868"]\n'
    '[BlackElo "2330"]\n'
    '[TimeControl "180+1"]\n'
    '[Termination "bob won by resignation"]\n'
    '[StartTime "15:18:21"]\n'
    '[EndDate "2025.03.28"]\n'
    '[EndTime "15:22:58"]\n'
    '[Link "https://www.chess.com/game/live/100000006"]\n'
    "\n"
    "1. g4 {[%clk 0:03:00.9]} 1... g6 {[%clk 0:02:58.1]} 2. Ng3 {[%clk "
    "0:03:00.7]} 2... d6 {[%clk 0:02:53.4]} 3. h3 {[%clk 0:02:49.2]} 3... "
    "Nc6 {[%clk 0:02:53.2]} 4. d3 {[%clk 0:02:44.4]} 4... f5 {[%clk "
    "0:02:44.6]} 5. g5 {[%clk 0:02:26.6]} 5... e5 {[%clk 0:02:37.5]} 6. h4 "
    "{[%clk 0:02:26.6]} 6... d5 {[%clk 0:02:10.7]} 7. e3 {[%clk "
    "0:02:21.6]} 7... Be6 {[%clk 0:02:00.9]} 8. Nc3 {[%clk 0:02:18.6]} "
    "8... O-O-O {[%clk 0:02:00.4]} 9. Nce2 {[%clk 0:02:18.6]} 9... f4 "
    "{[%clk 0:01:55.3]} 10. exf4 {[%clk 0:02:17.5]} 10... e4 {[%clk "
    "0:01:55.9]} 11. f5 {[%clk 0:02:12.1]} 11... gxf5 {[%clk 0:01:51]} 12. "
    "Nf4 {[%clk 0:02:10.1]} 12... Ng6 {[%clk 0:01:48.5]} 13. c3 {[%clk "
    "0:01:52.9]} 13... Nxf4 {[%clk 0:01:23.1]} 14. Bxf4 {[%clk 0:01:53.8]} "
    "14... d4 {[%clk 0:01:23.9]} 15. c4 {[%clk 0:01:20.1]} 15... Nb4 "
    "{[%clk 0:01:22.5]} 16. dxe4 {[%clk 0:01:11.9]} 16... Nd3 {[%clk "
    "0:01:21.5]} 17. exf5 {[%clk 0:01:12.3]} 17... Bxc4 {[%clk 0:01:15.2]} "
    "18. Rxe8 {[%clk 0:01:03.9]} 18... Rxe8 {[%clk 0:01:16.1]} 19. Bd2 "
    "{[%clk 0:01:04.2]} 19... Bb3+ {[%clk 0:01:15.7]} 0-1\n",
    "time_control": "180+1",
    "end_time": 1743175378,
    "rated": True,
    "accuracies": {"white": 71.98, "black": 91.89},
    "uuid": "00000000-0000-4000-8000-000000000006",
    "initial_setup": "rnbkrnqb/pppppppp/8/8/8/8/PPPPPPPP/RNBKRNQB w KQkq - 0 1",
    "fen": "2k1r1qb/ppp4p/8/5PP1/3p3P/1b1n2N1/PP1B1P2/R2K2QB w Q - 2 20",
    "time_class": "blitz",
    "rules": "chess960",
    "white": {
        "rating": 2868,
        "result": "resigned",
        "@id": "https://api.chess.com/pub/player/alice",
        "username": "alice",
    },
    "black": {
        "rating": 2330,
        "result": "win",
        "@id": "https://api.chess.com/pub/player/bob",
        "username": "bob",
    },
}


CHESSCOM_ABANDONED = {
    "url": "https://www.chess.com/game/live/100000007",
    "pgn": '[Event "Live Chess"]\n'
    '[Site "Chess.com"]\n'
    '[Date "2025.03.01"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "0-1"]\n'
    "[Tournament "
    '"https://www.chess.com/tournament/live/bullet-brawl-4037267"]\n'
    '[CurrentPosition "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq '
    '- 0 1"]\n'
    '[Timezone "UTC"]\n'
    '[ECO "A00"]\n'
    '[ECOUrl "https://www.chess.com/openings/Undefined"]\n'
    '[UTCDate "2025.03.01"]\n'
    '[UTCTime "17:17:53"]\n'
    '[WhiteElo "2600"]\n'
    '[BlackElo "3259"]\n'
    '[TimeControl "60"]\n'
    '[Termination "bob won - game abandoned"]\n'
    '[StartTime "17:17:53"]\n'
    '[EndDate "2025.03.01"]\n'
    '[EndTime "17:18:09"]\n'
    '[Link "https://www.chess.com/game/live/100000007"]\n'
    "\n"
    "0-1\n",
    "time_control": "60",
    "end_time": 1740849489,
    "rated": True,
    "uuid": "00000000-0000-4000-8000-000000000007",
    "initial_setup": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "time_class": "bullet",
    "rules": "chess",
    "white": {
        "rating": 2600,
        "result": "abandoned",
        "@id": "https://api.chess.com/pub/player/alice",
        "username": "alice",
    },
    "black": {
        "rating": 3259,
        "result": "win",
        "@id": "https://api.chess.com/pub/player/bob",
        "username": "bob",
    },
    "eco": "https://www.chess.com/openings/Undefined",
}


LICHESS_BLITZ_MATE = {
    "id": "Game0008",
    "rated": True,
    "variant": "standard",
    "speed": "blitz",
    "perf": "blitz",
    "createdAt": 1789562547406,
    "lastMoveAt": 1789562723471,
    "status": "mate",
    "source": "pool",
    "players": {
        "white": {
            "user": {"name": "alice", "id": "alice"},
            "rating": 1731,
            "ratingDiff": -4,
        },
        "black": {
            "user": {"name": "bob", "id": "bob"},
            "rating": 1838,
            "ratingDiff": 5,
        },
    },
    "winner": "black",
    "opening": {
        "eco": "C38",
        "name": "King's Gambit Accepted: Traditional Variation",
        "ply": 8,
    },
    "moves": "e4 e5 f4 exf4 Nf3 g5 Bc4 Bg7 O-O d6 h4 g4 Ng5 Be6 Nxe6 fxe6 Bxe6 "
    "Bd4+ Kh1 Qxh4#",
    "clocks": [
        30003,
        30003,
        29971,
        30043,
        30123,
        29891,
        30227,
        29883,
        29355,
        29387,
        28907,
        28939,
        27467,
        25291,
        25147,
        25371,
        25283,
        23539,
        25003,
        23236,
    ],
    "pgn": '[Event "rated blitz game"]\n'
    '[Site "https://lichess.org/game/Game0008"]\n'
    '[Date "2026.09.16"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "0-1"]\n'
    '[GameId "Game0008"]\n'
    '[UTCDate "2026.09.16"]\n'
    '[UTCTime "12:42:27"]\n'
    '[WhiteElo "1731"]\n'
    '[BlackElo "1838"]\n'
    '[WhiteRatingDiff "-4"]\n'
    '[BlackRatingDiff "+5"]\n'
    '[Variant "Standard"]\n'
    '[TimeControl "300+3"]\n'
    '[ECO "C38"]\n'
    '[Opening "King\'s Gambit Accepted: Traditional Variation"]\n'
    '[Termination "Normal"]\n'
    "\n"
    "1. e4 { [%eval 0.18] [%clk 0:05:00] } 1... e5 { [%eval 0.22] [%clk "
    "0:05:00] } 2. f4 { [%eval -0.34] [%clk 0:05:00] } 2... exf4 { [%eval "
    "-0.39] [%clk 0:05:00] } 3. Nf3 { [%eval -0.39] [%clk 0:05:01] } 3... "
    "g5 { [%eval -0.13] [%clk 0:04:59] } 4. Bc4 { [%eval -1.11] [%clk "
    "0:05:02] } 4... Bg7 { [%eval -0.36] [%clk 0:04:59] } 5. O-O { [%eval "
    "-1.51] [%clk 0:04:54] } 5... d6 { [%eval -1.0] [%clk 0:04:54] } 6. h4 "
    "{ [%eval -2.82] [%clk 0:04:49] } 6... g4 { [%eval -3.07] [%clk "
    "0:04:49] } 7. Ng5 { [%eval -7.01] [%clk 0:04:35] } 7... Be6 { [%eval "
    "2.24] [%clk 0:04:13] } 8. Nxe6 { [%eval 2.19] [%clk 0:04:11] } 8... "
    "fxe6 { [%eval 2.02] [%clk 0:04:14] } 9. Bxe6 { [%eval -7.66] [%clk "
    "0:04:13] } 9... Bd4+ { [%eval -6.05] [%clk 0:03:55] } 10. Kh1 { "
    "[%eval #-1] [%clk 0:04:10] } 10... Qxh4# { [%clk 0:03:52] } 0-1\n"
    "\n"
    "\n",
    "clock": {"initial": 300, "increment": 3, "totalTime": 420},
}


LICHESS_RESIGN = {
    "id": "Game0009",
    "rated": True,
    "variant": "standard",
    "speed": "blitz",
    "perf": "blitz",
    "createdAt": 1795797776272,
    "lastMoveAt": 1795797784514,
    "status": "resign",
    "source": "friend",
    "players": {
        "white": {
            "user": {"name": "alice", "id": "alice"},
            "rating": 1320,
            "ratingDiff": -88,
            "provisional": True,
        },
        "black": {
            "user": {"name": "bob", "title": "BOT", "id": "bob"},
            "rating": 1375,
            "ratingDiff": 3,
        },
    },
    "winner": "black",
    "opening": {"eco": "A06", "name": "Zukertort Opening: Tennison Gambit", "ply": 3},
    "moves": "e4 d5 Nf3 dxe4 Nd4 Qxd4",
    "clocks": [36003, 36003, 35955, 35995, 35827, 35890, 35232],
    "pgn": '[Event "rated blitz game"]\n'
    '[Site "https://lichess.org/game/Game0009"]\n'
    '[Date "2026.11.27"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "0-1"]\n'
    '[GameId "Game0009"]\n'
    '[UTCDate "2026.11.27"]\n'
    '[UTCTime "16:42:56"]\n'
    '[WhiteElo "1320"]\n'
    '[BlackElo "1375"]\n'
    '[WhiteRatingDiff "-88"]\n'
    '[BlackRatingDiff "+3"]\n'
    '[BlackTitle "BOT"]\n'
    '[Variant "Standard"]\n'
    '[TimeControl "360+0"]\n'
    '[ECO "A06"]\n'
    '[Opening "Zukertort Opening: Tennison Gambit"]\n'
    '[Termination "Normal"]\n'
    "\n"
    "1. e4 { [%clk 0:06:00] } 1... d5 { [%clk 0:06:00] } 2. Nf3 { [%clk "
    "0:06:00] } 2... dxe4 { [%clk 0:06:00] } 3. Nd4 { [%clk 0:05:58] } "
    "3... Qxd4 { [%clk 0:05:59] } 0-1\n"
    "\n"
    "\n",
    "clock": {"initial": 360, "increment": 0, "totalTime": 360},
}


LICHESS_OUTOFTIME = {
    "id": "Game0010",
    "rated": False,
    "variant": "standard",
    "speed": "classical",
    "perf": "classical",
    "createdAt": 1791703276398,
    "lastMoveAt": 1791703286270,
    "status": "outoftime",
    "source": "ai",
    "players": {
        "white": {
            "user": {"name": "alice", "id": "alice"},
            "rating": 1858,
            "provisional": True,
        },
        "black": {"aiLevel": 3},
    },
    "winner": "black",
    "opening": {"eco": "B06", "name": "Modern Defense", "ply": 2},
    "moves": "e4 g6",
    "clocks": [180000, 180000, 0],
    "pgn": '[Event "casual classical game"]\n'
    '[Site "https://lichess.org/game/Game0010"]\n'
    '[Date "2026.10.11"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "lichess AI level 3"]\n'
    '[Result "0-1"]\n'
    '[GameId "Game0010"]\n'
    '[UTCDate "2026.10.11"]\n'
    '[UTCTime "07:21:16"]\n'
    '[WhiteElo "1858"]\n'
    '[BlackElo "?"]\n'
    '[Variant "Standard"]\n'
    '[TimeControl "1800+20"]\n'
    '[ECO "B06"]\n'
    '[Opening "Modern Defense"]\n'
    '[Termination "Time forfeit"]\n'
    "\n"
    "1. e4 { [%clk 0:30:00] } 1... g6 { [%clk 0:30:00] } 0-1\n"
    "\n"
    "\n",
    "clock": {"initial": 1800, "increment": 20, "totalTime": 2600},
}


LICHESS_OUTOFTIME_DRAW = {
    "id": "Game0011",
    "rated": True,
    "variant": "standard",
    "speed": "ultraBullet",
    "perf": "ultraBullet",
    "createdAt": 1794261933986,
    "lastMoveAt": 1794261970868,
    "status": "outoftime",
    "source": "lobby",
    "players": {
        "white": {
            "user": {"name": "alice", "title": "GM", "id": "alice"},
            "rating": 2527,
            "ratingDiff": -1,
        },
        "black": {
            "user": {"name": "bob", "id": "bob"},
            "rating": 2444,
            "ratingDiff": 2,
        },
    },
    "opening": {"eco": "B06", "name": "Modern Defense", "ply": 2},
    "moves": "e4 g6 Nc3 d5 Nf3 dxe4 Nxe4 Nf6 Nxf6+ exf6 Bb5+ c6 Qe2+ Be6 Bc4 Bg7 "
    "Bxe6 fxe6 Nd4 Qe7 Nxe6 Kf7 Nxg7 Qxe2+ Kxe2 Kxg7 d3 Re8+ Be3 Rd8 h4 "
    "Kf7 h5 Nd7 hxg6+ hxg6 Rh7+ Kg8 Rah1 Nf8 Rxb7 Re8 Rxa7 Rxa7 a4 Rae7 "
    "b3 f5 Kf3 f4 Bxf4 Rf7 g3 Ne6 Kg2 Nxf4+ gxf4 Re2 Kg3 Re5 f3 Ref5 Rh4 "
    "Rxf4 Rxf4 Rg7 Rg4 g5 f4 gxf4+ Kxf4 Rxg4+ Kxg4 Kf7 Kf4 Ke6 Ke4 c5 d4 "
    "c4 bxc4 Kd6 d5 Kc7 Ke5 Kd7 d6 Kd8 c5 Ke8 c6 Kd8 Kd5 Ke8 d7+ Kf7",
    "clocks": [
        1499,
        1499,
        1499,
        1483,
        1475,
        1483,
        1419,
        1475,
        1339,
        1475,
        1299,
        1403,
        1299,
        1331,
        1299,
        1307,
        1227,
        1307,
        1187,
        1307,
        1179,
        1219,
        1091,
        1219,
        1043,
        1203,
        1019,
        1203,
        995,
        1163,
        995,
        1147,
        978,
        1147,
        958,
        1115,
        925,
        1107,
        869,
        966,
        757,
        873,
        724,
        787,
        679,
        736,
        673,
        703,
        673,
        698,
        608,
        687,
        601,
        640,
        601,
        598,
        579,
        561,
        579,
        455,
        567,
        454,
        488,
        454,
        432,
        419,
        432,
        379,
        432,
        374,
        353,
        374,
        323,
        374,
        290,
        370,
        283,
        346,
        188,
        346,
        166,
        346,
        138,
        323,
        115,
        323,
        100,
        323,
        52,
        323,
        39,
        298,
        39,
        290,
        18,
        273,
        0,
    ],
    "pgn": '[Event "rated ultraBullet game"]\n'
    '[Site "https://lichess.org/game/Game0011"]\n'
    '[Date "2026.11.09"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "1/2-1/2"]\n'
    '[GameId "Game0011"]\n'
    '[UTCDate "2026.11.09"]\n'
    '[UTCTime "22:05:33"]\n'
    '[WhiteElo "2527"]\n'
    '[BlackElo "2444"]\n'
    '[WhiteRatingDiff "-1"]\n'
    '[BlackRatingDiff "+2"]\n'
    '[WhiteTitle "GM"]\n'
    '[Variant "Standard"]\n'
    '[TimeControl "15+0"]\n'
    '[ECO "B06"]\n'
    '[Opening "Modern Defense"]\n'
    '[Termination "Time forfeit"]\n'
    "\n"
    "1. e4 { [%clk 0:00:15] } 1... g6 { [%clk 0:00:15] } 2. Nc3 { [%clk "
    "0:00:15] } 2... d5 { [%clk 0:00:15] } 3. Nf3 { [%clk 0:00:15] } 3... "
    "dxe4 { [%clk 0:00:15] } 4. Nxe4 { [%clk 0:00:14] } 4... Nf6 { [%clk "
    "0:00:15] } 5. Nxf6+ { [%clk 0:00:13] } 5... exf6 { [%clk 0:00:15] } "
    "6. Bb5+ { [%clk 0:00:13] } 6... c6 { [%clk 0:00:14] } 7. Qe2+ { [%clk "
    "0:00:13] } 7... Be6 { [%clk 0:00:13] } 8. Bc4 { [%clk 0:00:13] } 8... "
    "Bg7 { [%clk 0:00:13] } 9. Bxe6 { [%clk 0:00:12] } 9... fxe6 { [%clk "
    "0:00:13] } 10. Nd4 { [%clk 0:00:12] } 10... Qe7 { [%clk 0:00:13] } "
    "11. Nxe6 { [%clk 0:00:12] } 11... Kf7 { [%clk 0:00:12] } 12. Nxg7 { "
    "[%clk 0:00:11] } 12... Qxe2+ { [%clk 0:00:12] } 13. Kxe2 { [%clk "
    "0:00:10] } 13... Kxg7 { [%clk 0:00:12] } 14. d3 { [%clk 0:00:10] } "
    "14... Re8+ { [%clk 0:00:12] } 15. Be3 { [%clk 0:00:10] } 15... Rd8 { "
    "[%clk 0:00:12] } 16. h4 { [%clk 0:00:10] } 16... Kf7 { [%clk 0:00:11] "
    "} 17. h5 { [%clk 0:00:10] } 17... Nd7 { [%clk 0:00:11] } 18. hxg6+ { "
    "[%clk 0:00:10] } 18... hxg6 { [%clk 0:00:11] } 19. Rh7+ { [%clk "
    "0:00:09] } 19... Kg8 { [%clk 0:00:11] } 20. Rah1 { [%clk 0:00:09] } "
    "20... Nf8 { [%clk 0:00:10] } 21. Rxb7 { [%clk 0:00:08] } 21... Re8 { "
    "[%clk 0:00:09] } 22. Rxa7 { [%clk 0:00:07] } 22... Rxa7 { [%clk "
    "0:00:08] } 23. a4 { [%clk 0:00:07] } 23... Rae7 { [%clk 0:00:07] } "
    "24. b3 { [%clk 0:00:07] } 24... f5 { [%clk 0:00:07] } 25. Kf3 { [%clk "
    "0:00:07] } 25... f4 { [%clk 0:00:07] } 26. Bxf4 { [%clk 0:00:06] } "
    "26... Rf7 { [%clk 0:00:07] } 27. g3 { [%clk 0:00:06] } 27... Ne6 { "
    "[%clk 0:00:06] } 28. Kg2 { [%clk 0:00:06] } 28... Nxf4+ { [%clk "
    "0:00:06] } 29. gxf4 { [%clk 0:00:06] } 29... Re2 { [%clk 0:00:06] } "
    "30. Kg3 { [%clk 0:00:06] } 30... Re5 { [%clk 0:00:05] } 31. f3 { "
    "[%clk 0:00:06] } 31... Ref5 { [%clk 0:00:05] } 32. Rh4 { [%clk "
    "0:00:05] } 32... Rxf4 { [%clk 0:00:05] } 33. Rxf4 { [%clk 0:00:04] } "
    "33... Rg7 { [%clk 0:00:04] } 34. Rg4 { [%clk 0:00:04] } 34... g5 { "
    "[%clk 0:00:04] } 35. f4 { [%clk 0:00:04] } 35... gxf4+ { [%clk "
    "0:00:04] } 36. Kxf4 { [%clk 0:00:04] } 36... Rxg4+ { [%clk 0:00:04] } "
    "37. Kxg4 { [%clk 0:00:03] } 37... Kf7 { [%clk 0:00:04] } 38. Kf4 { "
    "[%clk 0:00:03] } 38... Ke6 { [%clk 0:00:04] } 39. Ke4 { [%clk "
    "0:00:03] } 39... c5 { [%clk 0:00:03] } 40. d4 { [%clk 0:00:02] } "
    "40... c4 { [%clk 0:00:03] } 41. bxc4 { [%clk 0:00:02] } 41... Kd6 { "
    "[%clk 0:00:03] } 42. d5 { [%clk 0:00:01] } 42... Kc7 { [%clk 0:00:03] "
    "} 43. Ke5 { [%clk 0:00:01] } 43... Kd7 { [%clk 0:00:03] } 44. d6 { "
    "[%clk 0:00:01] } 44... Kd8 { [%clk 0:00:03] } 45. c5 { [%clk 0:00:01] "
    "} 45... Ke8 { [%clk 0:00:03] } 46. c6 { [%clk 0:00:00] } 46... Kd8 { "
    "[%clk 0:00:03] } 47. Kd5 { [%clk 0:00:00] } 47... Ke8 { [%clk "
    "0:00:03] } 48. d7+ { [%clk 0:00:00] } 48... Kf7 { [%clk 0:00:03] } "
    "1/2-1/2\n"
    "\n"
    "\n",
    "clock": {"initial": 15, "increment": 0, "totalTime": 15},
}


LICHESS_DRAW = {
    "id": "Game0012",
    "rated": True,
    "variant": "standard",
    "speed": "blitz",
    "perf": "blitz",
    "createdAt": 1795797800355,
    "lastMoveAt": 1795798008947,
    "status": "draw",
    "source": "friend",
    "players": {
        "white": {
            "user": {"name": "alice", "title": "BOT", "id": "alice"},
            "rating": 1371,
            "ratingDiff": 0,
        },
        "black": {
            "user": {"name": "bob", "id": "bob"},
            "rating": 1337,
            "ratingDiff": 0,
        },
    },
    "opening": {
        "eco": "A30",
        "name": "English Opening: Symmetrical Variation",
        "ply": 2,
    },
    "moves": "c4 c5 e3 d6 d4 b6 d5 Bf5 Bd3 Bd7 Nf3 Bg4 O-O Bxf3 Qxf3 h6 Nc3 g5 e4 "
    "Bg7 Nb5 a6 Nc3 Bxc3 bxc3 e6 dxe6 Qf6 Qxf6 Nxf6 exf7+ Kxf7 f4 g4 e5 "
    "dxe5 fxe5 Re8 Rxf6+ Kg7 Bxh6+ Kg8 Rg6+ Kh7 Rxg4+ Kxh6 Rh4+ Kg7 Rh7+ "
    "Kf8 Rf1+ Kg8 Rff7 Nc6 Rfg7+ Kf8 Rf7+ Kg8 Rhg7+ Kh8 Rh7+ Kg8",
    "clocks": [
        30003,
        30003,
        29995,
        29883,
        29795,
        29659,
        29595,
        29315,
        29451,
        29019,
        29195,
        28787,
        29179,
        28683,
        29163,
        28083,
        28923,
        27747,
        28739,
        27627,
        28451,
        27307,
        28315,
        27171,
        27739,
        25619,
        27523,
        25331,
        27107,
        25195,
        26899,
        25099,
        26411,
        24563,
        25987,
        24443,
        25363,
        23763,
        25027,
        23611,
        25011,
        23379,
        24819,
        23235,
        24483,
        23123,
        24003,
        22891,
        23211,
        22635,
        22715,
        21955,
        22043,
        20571,
        21627,
        20435,
        20987,
        20339,
        20667,
        20163,
        20651,
        20054,
        20654,
    ],
    "pgn": '[Event "rated blitz game"]\n'
    '[Site "https://lichess.org/game/Game0012"]\n'
    '[Date "2026.11.27"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "1/2-1/2"]\n'
    '[GameId "Game0012"]\n'
    '[UTCDate "2026.11.27"]\n'
    '[UTCTime "16:43:20"]\n'
    '[WhiteElo "1371"]\n'
    '[BlackElo "1337"]\n'
    '[WhiteRatingDiff "+0"]\n'
    '[BlackRatingDiff "+0"]\n'
    '[WhiteTitle "BOT"]\n'
    '[Variant "Standard"]\n'
    '[TimeControl "300+0"]\n'
    '[ECO "A30"]\n'
    '[Opening "English Opening: Symmetrical Variation"]\n'
    '[Termination "Normal"]\n'
    "\n"
    "1. c4 { [%clk 0:05:00] } 1... c5 { [%clk 0:05:00] } 2. e3 { [%clk "
    "0:05:00] } 2... d6 { [%clk 0:04:59] } 3. d4 { [%clk 0:04:58] } 3... "
    "b6 { [%clk 0:04:57] } 4. d5 { [%clk 0:04:56] } 4... Bf5 { [%clk "
    "0:04:53] } 5. Bd3 { [%clk 0:04:55] } 5... Bd7 { [%clk 0:04:50] } 6. "
    "Nf3 { [%clk 0:04:52] } 6... Bg4 { [%clk 0:04:48] } 7. O-O { [%clk "
    "0:04:52] } 7... Bxf3 { [%clk 0:04:47] } 8. Qxf3 { [%clk 0:04:52] } "
    "8... h6 { [%clk 0:04:41] } 9. Nc3 { [%clk 0:04:49] } 9... g5 { [%clk "
    "0:04:37] } 10. e4 { [%clk 0:04:47] } 10... Bg7 { [%clk 0:04:36] } 11. "
    "Nb5 { [%clk 0:04:45] } 11... a6 { [%clk 0:04:33] } 12. Nc3 { [%clk "
    "0:04:43] } 12... Bxc3 { [%clk 0:04:32] } 13. bxc3 { [%clk 0:04:37] } "
    "13... e6 { [%clk 0:04:16] } 14. dxe6 { [%clk 0:04:35] } 14... Qf6 { "
    "[%clk 0:04:13] } 15. Qxf6 { [%clk 0:04:31] } 15... Nxf6 { [%clk "
    "0:04:12] } 16. exf7+ { [%clk 0:04:29] } 16... Kxf7 { [%clk 0:04:11] } "
    "17. f4 { [%clk 0:04:24] } 17... g4 { [%clk 0:04:06] } 18. e5 { [%clk "
    "0:04:20] } 18... dxe5 { [%clk 0:04:04] } 19. fxe5 { [%clk 0:04:14] } "
    "19... Re8 { [%clk 0:03:58] } 20. Rxf6+ { [%clk 0:04:10] } 20... Kg7 { "
    "[%clk 0:03:56] } 21. Bxh6+ { [%clk 0:04:10] } 21... Kg8 { [%clk "
    "0:03:54] } 22. Rg6+ { [%clk 0:04:08] } 22... Kh7 { [%clk 0:03:52] } "
    "23. Rxg4+ { [%clk 0:04:05] } 23... Kxh6 { [%clk 0:03:51] } 24. Rh4+ { "
    "[%clk 0:04:00] } 24... Kg7 { [%clk 0:03:49] } 25. Rh7+ { [%clk "
    "0:03:52] } 25... Kf8 { [%clk 0:03:46] } 26. Rf1+ { [%clk 0:03:47] } "
    "26... Kg8 { [%clk 0:03:40] } 27. Rff7 { [%clk 0:03:40] } 27... Nc6 { "
    "[%clk 0:03:26] } 28. Rfg7+ { [%clk 0:03:36] } 28... Kf8 { [%clk "
    "0:03:24] } 29. Rf7+ { [%clk 0:03:30] } 29... Kg8 { [%clk 0:03:23] } "
    "30. Rhg7+ { [%clk 0:03:27] } 30... Kh8 { [%clk 0:03:22] } 31. Rh7+ { "
    "[%clk 0:03:27] } 31... Kg8 { [%clk 0:03:21] } 1/2-1/2\n"
    "\n"
    "\n",
    "clock": {"initial": 300, "increment": 0, "totalTime": 300},
}


LICHESS_STALEMATE = {
    "id": "Game0013",
    "rated": True,
    "variant": "standard",
    "speed": "rapid",
    "perf": "rapid",
    "createdAt": 1795797247365,
    "lastMoveAt": 1795797756163,
    "status": "stalemate",
    "source": "friend",
    "players": {
        "white": {
            "user": {"name": "alice", "title": "BOT", "id": "alice"},
            "rating": 1515,
            "ratingDiff": -3,
        },
        "black": {
            "user": {"name": "bob", "id": "bob"},
            "rating": 1377,
            "ratingDiff": 1,
        },
    },
    "opening": {"eco": "C24", "name": "Bishop's Opening: Berlin Defense", "ply": 4},
    "moves": "e4 e5 Bc4 Nf6 g4 Nxe4 Qf3 Nf6 g5 d5 gxf6 dxc4 fxg7 Bxg7 d3 Bd7 dxc4 "
    "Bc6 Qg3 Bxh1 Qxg7 Rf8 Qxe5+ Qe7 Qxe7+ Kxe7 Bg5+ f6 Bh6 Rg8 Nc3 "
    "Rxg1+ Ke2 Rxa1 Nd5+ Kd7 Nxf6+ Kc6 Nxh7 Rxa2 f4 Rxb2 f5 Rxc2+ Kd3 "
    "Rf2 f6 Nd7 f7 Rxf7 Ng5 Ne5+ Kd4 Nf3+ Ke4 Re8+ Kd3 Rd7+ Kc3 Re3+ Kb4 "
    "a5+ Kxa5 Rd5+ Kb4 Rxg5 Bxg5 Nxg5 h4 Nh7 h5 Rh3 h6 Rxh6 c5 Rh4+ Ka5 "
    "Kxc5",
    "clocks": [
        90003,
        90003,
        89891,
        89651,
        89683,
        89187,
        89483,
        88851,
        89307,
        88171,
        88627,
        88003,
        88243,
        87443,
        87755,
        86099,
        87347,
        85971,
        86739,
        85747,
        86107,
        83043,
        85419,
        82083,
        84491,
        82003,
        83947,
        81595,
        83195,
        81011,
        82403,
        80539,
        81267,
        80131,
        80563,
        79819,
        79803,
        78923,
        79051,
        78731,
        77851,
        78219,
        77435,
        77963,
        76499,
        76363,
        75899,
        75875,
        75195,
        75699,
        74147,
        74899,
        72779,
        73979,
        71947,
        73363,
        70979,
        72619,
        69891,
        71115,
        69027,
        69883,
        68107,
        69739,
        67139,
        68779,
        66387,
        68627,
        65483,
        68075,
        65011,
        67859,
        64403,
        67699,
        64003,
        67411,
        62918,
        67292,
    ],
    "pgn": '[Event "rated rapid game"]\n'
    '[Site "https://lichess.org/game/Game0013"]\n'
    '[Date "2026.11.27"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "1/2-1/2"]\n'
    '[GameId "Game0013"]\n'
    '[UTCDate "2026.11.27"]\n'
    '[UTCTime "16:34:07"]\n'
    '[WhiteElo "1515"]\n'
    '[BlackElo "1377"]\n'
    '[WhiteRatingDiff "-3"]\n'
    '[BlackRatingDiff "+1"]\n'
    '[WhiteTitle "BOT"]\n'
    '[Variant "Standard"]\n'
    '[TimeControl "900+0"]\n'
    '[ECO "C24"]\n'
    '[Opening "Bishop\'s Opening: Berlin Defense"]\n'
    '[Termination "Normal"]\n'
    "\n"
    "1. e4 { [%clk 0:15:00] } 1... e5 { [%clk 0:15:00] } 2. Bc4 { [%clk "
    "0:14:59] } 2... Nf6 { [%clk 0:14:57] } 3. g4 { [%clk 0:14:57] } 3... "
    "Nxe4 { [%clk 0:14:52] } 4. Qf3 { [%clk 0:14:55] } 4... Nf6 { [%clk "
    "0:14:49] } 5. g5 { [%clk 0:14:53] } 5... d5 { [%clk 0:14:42] } 6. "
    "gxf6 { [%clk 0:14:46] } 6... dxc4 { [%clk 0:14:40] } 7. fxg7 { [%clk "
    "0:14:42] } 7... Bxg7 { [%clk 0:14:34] } 8. d3 { [%clk 0:14:38] } 8... "
    "Bd7 { [%clk 0:14:21] } 9. dxc4 { [%clk 0:14:33] } 9... Bc6 { [%clk "
    "0:14:20] } 10. Qg3 { [%clk 0:14:27] } 10... Bxh1 { [%clk 0:14:17] } "
    "11. Qxg7 { [%clk 0:14:21] } 11... Rf8 { [%clk 0:13:50] } 12. Qxe5+ { "
    "[%clk 0:14:14] } 12... Qe7 { [%clk 0:13:41] } 13. Qxe7+ { [%clk "
    "0:14:05] } 13... Kxe7 { [%clk 0:13:40] } 14. Bg5+ { [%clk 0:13:59] } "
    "14... f6 { [%clk 0:13:36] } 15. Bh6 { [%clk 0:13:52] } 15... Rg8 { "
    "[%clk 0:13:30] } 16. Nc3 { [%clk 0:13:44] } 16... Rxg1+ { [%clk "
    "0:13:25] } 17. Ke2 { [%clk 0:13:33] } 17... Rxa1 { [%clk 0:13:21] } "
    "18. Nd5+ { [%clk 0:13:26] } 18... Kd7 { [%clk 0:13:18] } 19. Nxf6+ { "
    "[%clk 0:13:18] } 19... Kc6 { [%clk 0:13:09] } 20. Nxh7 { [%clk "
    "0:13:11] } 20... Rxa2 { [%clk 0:13:07] } 21. f4 { [%clk 0:12:59] } "
    "21... Rxb2 { [%clk 0:13:02] } 22. f5 { [%clk 0:12:54] } 22... Rxc2+ { "
    "[%clk 0:13:00] } 23. Kd3 { [%clk 0:12:45] } 23... Rf2 { [%clk "
    "0:12:44] } 24. f6 { [%clk 0:12:39] } 24... Nd7 { [%clk 0:12:39] } 25. "
    "f7 { [%clk 0:12:32] } 25... Rxf7 { [%clk 0:12:37] } 26. Ng5 { [%clk "
    "0:12:21] } 26... Ne5+ { [%clk 0:12:29] } 27. Kd4 { [%clk 0:12:08] } "
    "27... Nf3+ { [%clk 0:12:20] } 28. Ke4 { [%clk 0:11:59] } 28... Re8+ { "
    "[%clk 0:12:14] } 29. Kd3 { [%clk 0:11:50] } 29... Rd7+ { [%clk "
    "0:12:06] } 30. Kc3 { [%clk 0:11:39] } 30... Re3+ { [%clk 0:11:51] } "
    "31. Kb4 { [%clk 0:11:30] } 31... a5+ { [%clk 0:11:39] } 32. Kxa5 { "
    "[%clk 0:11:21] } 32... Rd5+ { [%clk 0:11:37] } 33. Kb4 { [%clk "
    "0:11:11] } 33... Rxg5 { [%clk 0:11:28] } 34. Bxg5 { [%clk 0:11:04] } "
    "34... Nxg5 { [%clk 0:11:26] } 35. h4 { [%clk 0:10:55] } 35... Nh7 { "
    "[%clk 0:11:21] } 36. h5 { [%clk 0:10:50] } 36... Rh3 { [%clk 0:11:19] "
    "} 37. h6 { [%clk 0:10:44] } 37... Rxh6 { [%clk 0:11:17] } 38. c5 { "
    "[%clk 0:10:40] } 38... Rh4+ { [%clk 0:11:14] } 39. Ka5 { [%clk "
    "0:10:29] } 39... Kxc5 { [%clk 0:11:13] } 1/2-1/2\n"
    "\n"
    "\n",
    "clock": {"initial": 900, "increment": 0, "totalTime": 900},
}


LICHESS_AI = {
    "id": "Game0014",
    "rated": False,
    "variant": "standard",
    "speed": "correspondence",
    "perf": "correspondence",
    "createdAt": 1766486592056,
    "lastMoveAt": 1766487228494,
    "status": "resign",
    "source": "ai",
    "players": {
        "white": {
            "user": {"name": "alice", "id": "alice"},
            "rating": 1942,
            "provisional": True,
        },
        "black": {"aiLevel": 1},
    },
    "winner": "black",
    "opening": {"eco": "B20", "name": "Sicilian Defense", "ply": 2},
    "moves": "e4 c5",
    "pgn": '[Event "casual correspondence game"]\n'
    '[Site "https://lichess.org/game/Game0014"]\n'
    '[Date "2025.12.23"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "lichess AI level 1"]\n'
    '[Result "0-1"]\n'
    '[GameId "Game0014"]\n'
    '[UTCDate "2025.12.23"]\n'
    '[UTCTime "10:43:12"]\n'
    '[WhiteElo "1942"]\n'
    '[BlackElo "?"]\n'
    '[Variant "Standard"]\n'
    '[TimeControl "-"]\n'
    '[ECO "B20"]\n'
    '[Opening "Sicilian Defense"]\n'
    '[Termination "Normal"]\n'
    "\n"
    "1. e4 c5 0-1\n"
    "\n"
    "\n",
}


LICHESS_FROM_POSITION = {
    "id": "Game0015",
    "rated": False,
    "variant": "fromPosition",
    "speed": "correspondence",
    "perf": "correspondence",
    "createdAt": 1760102305039,
    "lastMoveAt": 1760102318940,
    "status": "resign",
    "source": "position",
    "players": {
        "white": {
            "user": {"name": "alice", "id": "alice"},
            "rating": 1942,
            "provisional": True,
        },
        "black": {"aiLevel": 1},
    },
    "initialFen": "8/2Pk1b2/8/1p6/3K4/8/p7/8 w - - 1 75",
    "winner": "black",
    "moves": "c8=Q+ Kd6 Ke4 a1=R",
    "pgn": '[Event "casual correspondence game"]\n'
    '[Site "https://lichess.org/game/Game0015"]\n'
    '[Date "2025.10.10"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "lichess AI level 1"]\n'
    '[Result "0-1"]\n'
    '[GameId "Game0015"]\n'
    '[UTCDate "2025.10.10"]\n'
    '[UTCTime "13:18:25"]\n'
    '[WhiteElo "1942"]\n'
    '[BlackElo "?"]\n'
    '[Variant "From Position"]\n'
    '[TimeControl "-"]\n'
    '[Termination "Normal"]\n'
    '[FEN "8/2Pk1b2/8/1p6/3K4/8/p7/8 w - - 1 75"]\n'
    '[SetUp "1"]\n'
    "\n"
    "75. c8=Q+ Kd6 76. Ke4 a1=R 0-1\n"
    "\n"
    "\n",
}


LICHESS_960 = {
    "id": "Game0016",
    "rated": True,
    "variant": "chess960",
    "speed": "blitz",
    "perf": "chess960",
    "createdAt": 1534022113154,
    "lastMoveAt": 1534022226170,
    "status": "resign",
    "source": "arena",
    "players": {
        "white": {
            "user": {"name": "alice", "id": "alice"},
            "rating": 1554,
            "ratingDiff": -3,
        },
        "black": {
            "user": {"name": "bob", "id": "bob"},
            "rating": 1908,
            "ratingDiff": 3,
        },
    },
    "initialFen": "nqrkrbbn/pppppppp/8/8/8/8/PPPPPPPP/NQRKRBBN w KQkq - 0 1",
    "winner": "black",
    "moves": "e4 Nb6 Ng3 f6 f4 e5 f5 d5 Nb3 d4 d3 c5 Bf2 Nf7 Na5 Nd6 Ne2 c4 dxc4 "
    "Nbxc4 Nxc4 Nxc4 b3 Nd6 Qb2 Nxe4 Ng3 Nxf2+",
    "clocks": [
        18003,
        18003,
        17803,
        17819,
        17459,
        17643,
        17219,
        17379,
        16219,
        17147,
        14291,
        16739,
        14011,
        16307,
        13771,
        15915,
        12475,
        15819,
        12331,
        15811,
        12171,
        15811,
        11987,
        15571,
        11763,
        15459,
        11499,
        15357,
        11181,
    ],
    "pgn": '[Event "Chess960 Revolution #1"]\n'
    '[Site "https://lichess.org/game/Game0016"]\n'
    '[Date "2018.08.11"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "0-1"]\n'
    '[GameId "Game0016"]\n'
    '[UTCDate "2018.08.11"]\n'
    '[UTCTime "21:15:13"]\n'
    '[WhiteElo "1554"]\n'
    '[BlackElo "1908"]\n'
    '[WhiteRatingDiff "-3"]\n'
    '[BlackRatingDiff "+3"]\n'
    '[Variant "Chess960"]\n'
    '[TimeControl "180+0"]\n'
    '[Termination "Normal"]\n'
    '[FEN "nqrkrbbn/pppppppp/8/8/8/8/PPPPPPPP/NQRKRBBN w KQkq - 0 1"]\n'
    '[SetUp "1"]\n'
    "\n"
    "1. e4 { [%clk 0:03:00] } 1... Nb6 { [%clk 0:03:00] } 2. Ng3 { [%clk "
    "0:02:58] } 2... f6 { [%clk 0:02:58] } 3. f4 { [%clk 0:02:55] } 3... "
    "e5 { [%clk 0:02:56] } 4. f5 { [%clk 0:02:52] } 4... d5 { [%clk "
    "0:02:54] } 5. Nb3 { [%clk 0:02:42] } 5... d4 { [%clk 0:02:51] } 6. d3 "
    "{ [%clk 0:02:23] } 6... c5 { [%clk 0:02:47] } 7. Bf2 { [%clk 0:02:20] "
    "} 7... Nf7 { [%clk 0:02:43] } 8. Na5 { [%clk 0:02:18] } 8... Nd6 { "
    "[%clk 0:02:39] } 9. Ne2 { [%clk 0:02:05] } 9... c4 { [%clk 0:02:38] } "
    "10. dxc4 { [%clk 0:02:03] } 10... Nbxc4 { [%clk 0:02:38] } 11. Nxc4 { "
    "[%clk 0:02:02] } 11... Nxc4 { [%clk 0:02:38] } 12. b3 { [%clk "
    "0:02:00] } 12... Nd6 { [%clk 0:02:36] } 13. Qb2 { [%clk 0:01:58] } "
    "13... Nxe4 { [%clk 0:02:35] } 14. Ng3 { [%clk 0:01:55] } 14... Nxf2+ "
    "{ [%clk 0:02:34] } 0-1\n"
    "\n"
    "\n",
    "clock": {"initial": 180, "increment": 0, "totalTime": 180},
}


LICHESS_KOTH = {
    "id": "Game0017",
    "rated": False,
    "variant": "kingOfTheHill",
    "speed": "ultraBullet",
    "perf": "kingOfTheHill",
    "createdAt": 1493133258142,
    "lastMoveAt": 1493133267708,
    "status": "variantEnd",
    "source": "arena",
    "players": {
        "white": {"user": {"name": "alice", "id": "alice"}, "rating": 1462},
        "black": {"user": {"name": "bob", "id": "bob"}, "rating": 1728},
    },
    "winner": "black",
    "opening": {"eco": "B20", "name": "Sicilian Defense: Bowdler Attack", "ply": 3},
    "moves": "e4 c5 Bc4 d6 Bxf7+ Kxf7 Ke2 Ke6 Ke3 Ke5#",
    "clocks": [1499, 1499, 1475, 1499, 1363, 1411, 1363, 1379, 1334, 1329],
    "pgn": '[Event "Speelman Arena"]\n'
    '[Site "https://lichess.org/game/Game0017"]\n'
    '[Date "2017.04.25"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "0-1"]\n'
    '[GameId "Game0017"]\n'
    '[UTCDate "2017.04.25"]\n'
    '[UTCTime "15:14:18"]\n'
    '[WhiteElo "1462"]\n'
    '[BlackElo "1728"]\n'
    '[Variant "King of the Hill"]\n'
    '[TimeControl "15+0"]\n'
    '[ECO "B20"]\n'
    '[Opening "Sicilian Defense: Bowdler Attack"]\n'
    '[Termination "Normal"]\n'
    "\n"
    "1. e4 { [%clk 0:00:15] } 1... c5 { [%clk 0:00:15] } 2. Bc4 { [%clk "
    "0:00:15] } 2... d6 { [%clk 0:00:15] } 3. Bxf7+ { [%clk 0:00:14] } "
    "3... Kxf7 { [%clk 0:00:14] } 4. Ke2 { [%clk 0:00:14] } 4... Ke6 { "
    "[%clk 0:00:14] } 5. Ke3 { [%clk 0:00:13] } 5... Ke5# { [%clk 0:00:13] "
    "} 0-1\n"
    "\n"
    "\n",
    "clock": {"initial": 15, "increment": 0, "totalTime": 15},
}


LICHESS_CORRESPONDENCE = {
    "id": "Game0018",
    "rated": False,
    "variant": "standard",
    "speed": "correspondence",
    "perf": "correspondence",
    "createdAt": 1786005386535,
    "lastMoveAt": 1786005491237,
    "status": "outoftime",
    "source": "friend",
    "players": {
        "white": {
            "user": {"name": "alice", "id": "alice"},
            "rating": 1942,
            "provisional": True,
        },
        "black": {
            "user": {"name": "bob", "id": "bob"},
            "rating": 1500,
            "provisional": True,
        },
    },
    "winner": "black",
    "opening": {
        "eco": "C30",
        "name": "King's Gambit Declined: Queen's Knight Defense",
        "ply": 4,
    },
    "moves": "e4 e5 f4 Nc6",
    "pgn": '[Event "casual correspondence game"]\n'
    '[Site "https://lichess.org/game/Game0018"]\n'
    '[Date "2026.08.06"]\n'
    '[Round "-"]\n'
    '[White "alice"]\n'
    '[Black "bob"]\n'
    '[Result "0-1"]\n'
    '[GameId "Game0018"]\n'
    '[UTCDate "2026.08.06"]\n'
    '[UTCTime "08:36:26"]\n'
    '[WhiteElo "1942"]\n'
    '[BlackElo "1500"]\n'
    '[Variant "Standard"]\n'
    '[TimeControl "14 days per move"]\n'
    '[ECO "C30"]\n'
    "[Opening \"King's Gambit Declined: Queen's Knight Defense\"]\n"
    '[Termination "Time forfeit"]\n'
    "\n"
    "1. e4 e5 2. f4 Nc6 0-1\n"
    "\n"
    "\n",
    "daysPerTurn": 14,
}


# --- variations on the real games above ---------------------------------------

CHESSCOM_BAD_PGN = {**CHESSCOM_BLITZ_MATE, "pgn": "not a pgn"}

# Same game set up from a custom position, as daily games allow.
CHESSCOM_CUSTOM_SETUP = {
    **CHESSCOM_DAILY,
    "initial_setup": "4k3/8/8/8/8/8/4P3/4K3 w - - 0 1",
}

LICHESS_ABORTED = {
    **{k: v for k, v in LICHESS_RESIGN.items() if k not in ("winner", "pgn")},
    "status": "aborted",
    "moves": "e4",
}

LICHESS_NO_PGN = {k: v for k, v in LICHESS_RESIGN.items() if k != "pgn"}
