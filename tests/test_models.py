from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

import raw_game_fixtures as fx
from chess_guru import Game, GameCollection, Move, Player, game_from_lichess


def minimal_game(**overrides) -> dict:
    data = {
        "provider": "lichess",
        "id": "abc",
        "url": "https://lichess.org/abc",
        "variant": "standard",
        "speed": "blitz",
        "time_control": {},
        "white": {},
        "black": {},
        "result": "*",
        "termination": "other",
    }
    data.update(overrides)
    return data


def test_minimal_game_defaults():
    g = Game.model_validate(minimal_game())
    assert g.moves == [] and g.headers == {}
    assert g.raw is None and g.opening is None


def test_models_are_frozen():
    g = Game.model_validate(minimal_game())
    with pytest.raises(ValidationError):
        g.result = "1-0"
    with pytest.raises(ValidationError):
        g.white.username = "x"


@pytest.mark.parametrize("model", [Game, Player, Move, GameCollection])
def test_extra_fields_forbidden(model):
    data = {
        Game: minimal_game(),
        Player: {},
        Move: {"ply": 1, "move_number": 1, "color": "white", "san": "e4"},
        GameCollection: {"provider": "chesscom", "username": "a"},
    }[model]
    with pytest.raises(ValidationError):
        model.model_validate({**data, "surprise": 1})


@pytest.mark.parametrize(
    "field, value",
    [
        ("provider", "fics"),
        ("speed", "hyperbullet"),
        ("result", "2-0"),
        ("termination", "nap"),
        ("winner", "red"),
    ],
)
def test_literal_fields_reject_unknown_values(field, value):
    with pytest.raises(ValidationError):
        Game.model_validate(minimal_game(**{field: value}))


def test_naive_datetimes_rejected():
    with pytest.raises(ValidationError):
        Game.model_validate(minimal_game(end_time=datetime(2024, 1, 1)))


def test_converted_datetimes_are_utc():
    g = game_from_lichess(fx.LICHESS_BLITZ_MATE)
    assert g.start_time.utcoffset() == timedelta(0)
    assert g.end_time.tzinfo is timezone.utc


@pytest.mark.parametrize("include_raw", [False, True])
def test_json_round_trip(include_raw):
    g = game_from_lichess(fx.LICHESS_BLITZ_MATE, include_raw=include_raw)
    assert Game.model_validate_json(g.model_dump_json()) == g
    dumped = g.model_dump(mode="json")
    assert dumped["end_time"].endswith("Z") or dumped["end_time"].endswith("+00:00")
    assert Game.model_validate(dumped) == g


def test_collection_round_trip():
    c = GameCollection(
        provider="lichess",
        username="alice",
        games=[game_from_lichess(fx.LICHESS_RESIGN)],
        errors={"x": "ValueError()"},
        from_ts=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    assert GameCollection.model_validate_json(c.model_dump_json()) == c


def test_raw_left_out_of_repr():
    g = game_from_lichess(fx.LICHESS_RESIGN, include_raw=True)
    assert g.raw is not None
    assert "raw={" not in repr(g)
