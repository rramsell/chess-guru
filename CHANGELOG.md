# Changelog

All notable changes to this project are documented here.

## [0.2.0] - 2026-11-27

### Added
- `LichessAPI` client: `get_user`, `get_rating_history`, `get_perf`, and
  `iter_games` / `get_games` over the NDJSON game export. Supports an optional
  API token, `max_games`, `perf_type`, `rated`, `color` and `vs`, and
  `from_ts` / `to_ts` matched on when a game ended (`lastMoveAt`), with a
  `created_lookback` to widen the request for long games.
- Lichess rate-limit handling: a `429` waits a full minute before retrying.
  Only the initial request of a game export is retried.
- `parse_pgn` reads Lichess comments such as `{ [%eval 0.17] [%clk 0:02:59] }`,
  including mate scores, and games set up from a position that open with a
  black move.

### Changed
- Every parsed move now has an `eval` key (`None` when the PGN has no eval),
  so Chess.com moves look like
  `{"move": "e4", "clock": "0:09:58.5", "eval": None}`. Code that compares
  whole move dicts needs updating.
- `ChesscomAPI` moved to `chess_guru.chesscom`. `chess_guru.api` still
  re-exports it along with `DEFAULT_USER_AGENT` and `_terminal_error`.

### Internal
- Shared `BaseAPIClient` for session, headers, URL checks and retries, and an
  `annotate_games` helper for time filtering and PGN parsing.
- Retry, header and URL tests run against both clients. Integration tests are
  marked `chesscom` or `lichess`; CI runs them per provider on manual dispatch
  and weekly.

## [0.1.4] - 2026-11-26

### Fixed
- License metadata is now consistently MIT, matching the `LICENSE` file. Uses
  the SPDX `license = "MIT"` field and `license-files` (PEP 639), and drops the
  `Other/Proprietary License` classifier and the PolyForm text in the README.

## [0.1.3] - 2026-11-26

### Fixed
- Python 3.9: the package failed to import (`str | None` annotations), and any
  HTTP error raised `TypeError: 'staticmethod' object is not callable` instead
  of retrying or giving up.
- PGNs without clock comments (`1. e4 e5 2. Nf3 ...`) lost every black move in
  `parsed_pgn["moves"]`.
- `parse_pgn` now accepts CRLF line endings and raises a clear `ValueError` for
  PGNs with no blank line between headers and movetext.
- `get_games()` rejects `from_ts > to_ts` before making any request.

### Changed
- Default `User-Agent` is `chess-guru/<installed version>` instead of a
  hardcoded `chess-guru/0.1.0`. `chess_guru.__version__` now reports the
  installed version.
- Minimum `aiohttp` raised to 3.13.5 (the newest release that still supports
  Python 3.9; newer Pythons install 3.14+).

### Internal
- Offline unit tests for the parser and client (HTTP mocked with an
  in-repo fake session). Live chess.com tests are marked `integration`, skipped by
  default, and run in CI only on manual dispatch.
- CI runs on Python 3.9–3.13 and lints with ruff.

## [0.1.2] - 2026-02-08
- Added `get_player_stats`, `get_games_to_move` and `get_tournaments`.
