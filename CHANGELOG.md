# Changelog

All notable changes to this project are documented here.

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
