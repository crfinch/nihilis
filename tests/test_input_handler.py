# tests/test_input_handler.py

import pytest
import tcod.event
from src.engine.input_handler import InputHandler, GameState, GameAction

@pytest.fixture
def input_handler():
    context = tcod.context.new()
    return InputHandler(context)

def test_movement_keys(input_handler):
    # Test basic movement
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.UP,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    input_handler.set_game_state(GameState.GAME_WORLD)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "move"
    assert action.params == {"dx": 0, "dy": -1}

    # Test vi key movement
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.k,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "move"
    assert action.params == {"dx": 0, "dy": -1}

def test_diagonal_movement(input_handler):
    # Test diagonal movement with vi keys
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.y,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    input_handler.set_game_state(GameState.GAME_WORLD)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "move"
    assert action.params == {"dx": -1, "dy": -1}

def test_game_state_changes(input_handler):
    # Test inventory toggle
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.i,
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
        sym=tcod.event.KeySym.UP,
        mod=tcod.event.KMOD_SHIFT,
        scancode=0,
        repeat=False
    )
    input_handler.set_game_state(GameState.GAME_WORLD)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "move"
    assert action.params.get("sprint") is True

def test_command_keys(input_handler):
    # Test save game command
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.s,
        mod=tcod.event.KMOD_CTRL,
        scancode=0,
        repeat=False
    )
    input_handler.set_game_state(GameState.GAME_WORLD)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "save_game"

def test_mouse_input(input_handler):
    # Create basic mouse motion event
    event = tcod.event.MouseMotion(
        position=(100, 100),  # x, y coordinates
        motion=(5, 5),        # delta x, delta y
        state=0               # button state
    )
    
    # Convert the event using the context
    event = input_handler.context.convert_event(event)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "mouse_move"
    assert action.params["x"] == event.motion.x
    assert action.params["y"] == event.motion.y
    assert action.params["pixel_x"] == event.position.x
    assert action.params["pixel_y"] == event.position.y

def test_state_specific_handling(input_handler):
    # Test main menu state
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.RETURN,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    input_handler.set_game_state(GameState.MAIN_MENU)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "start_game"

    # Test dialogue state
    input_handler.set_game_state(GameState.DIALOGUE)
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "advance_dialogue"