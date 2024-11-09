# tests/test_input_handler.py

import pytest
import tcod.event
from engine.input_handler import InputHandler, GameState, GameAction

@pytest.fixture
def input_handler():
    context = tcod.context.new()
    return InputHandler(context)

def test_movement_keys(input_handler):
    # Test basic movement
    event = tcod.event.KeyDown(
        sym=tcod.event.K_UP,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    input_handler.set_game_state(GameState.GAME_WORLD)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "move"
    assert action.params == {"dx": 0, "dy": -1}

def test_game_state_changes(input_handler):
    # Test inventory toggle
    event = tcod.event.KeyDown(
        sym=tcod.event.K_i,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    input_handler.set_game_state(GameState.GAME_WORLD)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "open_inventory"

def test_modifier_keys(input_handler):
    # Test sprint movement
    event = tcod.event.KeyDown(
        sym=tcod.event.K_UP,
        mod=tcod.event.KMOD_SHIFT,
        scancode=0,
        repeat=False
    )
    input_handler.set_game_state(GameState.GAME_WORLD)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "move"
    assert action.params.get("sprint") is True

def test_mouse_input(input_handler):
    # Test mouse movement
    event = tcod.event.MouseMotion(
        pixel=tcod.event.Point(x=100, y=100),
        tile=tcod.event.Point(x=10, y=10),
        motion=tcod.event.Point(x=5, y=5)
    )
    event = input_handler.context.convert_event(event)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "mouse_move"
    assert action.params["x"] == 10
    assert action.params["y"] == 10