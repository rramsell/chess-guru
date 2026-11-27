"""Provider-independent game models.

No ``from __future__ import annotations`` here: pydantic evaluates these at
runtime, so they have to be valid on Python 3.9 as written.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

Provider = Literal["chesscom", "lichess"]
Color = Literal["white", "black"]
Result = Literal["1-0", "0-1", "1/2-1/2", "*"]
Speed = Literal[
    "ultrabullet", "bullet", "blitz", "rapid", "classical", "correspondence", "other"
]
Termination = Literal[
    "checkmate",
    "resignation",
    "timeout",
    "timeout_vs_insufficient",
    "draw_agreement",
    "stalemate",
    "repetition",
    "insufficient_material",
    "fifty_move",
    "abandoned",
    "aborted",
    "variant_end",
    "other",
]


class _Model(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Player(_Model):
    username: Optional[str] = None
    rating: Optional[int] = None
    rating_diff: Optional[int] = None
    title: Optional[str] = None
    ai_level: Optional[int] = None
    result_raw: Optional[str] = None


class TimeControl(_Model):
    initial_seconds: Optional[int] = None
    increment_seconds: Optional[int] = None
    days_per_move: Optional[int] = None
    raw: Optional[str] = None


class Opening(_Model):
    eco: Optional[str] = None
    name: Optional[str] = None


class Move(_Model):
    ply: int
    move_number: int
    color: Color
    san: str
    clock_seconds: Optional[float] = None
    eval_cp: Optional[int] = None
    eval_mate: Optional[int] = None


class Game(_Model):
    provider: Provider
    id: str
    url: str
    rated: Optional[bool] = None
    variant: str
    variant_raw: Optional[str] = None
    speed: Speed
    speed_raw: Optional[str] = None
    time_control: TimeControl
    start_time: Optional[AwareDatetime] = None
    end_time: Optional[AwareDatetime] = None
    white: Player
    black: Player
    result: Result
    winner: Optional[Color] = None
    termination: Termination
    termination_raw: Optional[str] = None
    opening: Optional[Opening] = None
    initial_fen: Optional[str] = None
    final_fen: Optional[str] = None
    pgn: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    moves: List[Move] = Field(default_factory=list)
    raw: Optional[Dict[str, Any]] = Field(default=None, repr=False)


class GameCollection(_Model):
    provider: Provider
    username: str
    games: List[Game] = Field(default_factory=list)
    errors: Dict[str, str] = Field(default_factory=dict)
    from_ts: Optional[datetime] = None
    to_ts: Optional[datetime] = None
