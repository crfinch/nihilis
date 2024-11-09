import pytest
import tcod.event
from src.engine.input_handler import InputHandler, GameState, GameAction
from src.engine.game_state_manager import GameStateManager
from src.engine.message_manager import MessageManager

@pytest.fixture
def game_state_manager():
    return GameStateManager()

@pytest.fixture
def message_manager():
    return MessageManager()

@pytest.fixture
def input_handler(game_state_manager, message_manager):
    context = tcod.context.new()
    return InputHandler(
        context=context,
        state_manager=game_state_manager,
        message_manager=message_manager,
        debug=False
    )

def test_movement_keys(input_handler, game_state_manager):
    # Set game state to GAME_WORLD
    game_state_manager.change_state(GameState.GAME_WORLD)
    
    # Test basic movement
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.UP,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
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

def test_diagonal_movement(input_handler, game_state_manager):
    game_state_manager.change_state(GameState.GAME_WORLD)
    
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.y,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "move"
    assert action.params == {"dx": -1, "dy": -1}

def test_state_changes(input_handler, game_state_manager):
    game_state_manager.change_state(GameState.GAME_WORLD)
    
    # Test inventory toggle
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.i,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "open_inventory"
    assert game_state_manager.get_current_state() == GameState.INVENTORY

def test_modifier_keys(input_handler, game_state_manager):
    game_state_manager.change_state(GameState.GAME_WORLD)
    
    # Test sprint movement
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.UP,
        mod=tcod.event.KMOD_SHIFT,
        scancode=0,
        repeat=False
    )
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "move"
    assert action.params.get("sprint") is True

def test_command_keys(input_handler, game_state_manager):
    game_state_manager.change_state(GameState.GAME_WORLD)
    
    # Test save game command
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.s,
        mod=tcod.event.KMOD_CTRL,
        scancode=0,
        repeat=False
    )
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "save_game"

def test_mouse_input(input_handler):
    event = tcod.event.MouseMotion(
        position=(100, 100),
        motion=(5, 5),
        state=0
    )
    
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "mouse_move"
    assert "x" in action.params
    assert "y" in action.params
    assert "pixel_x" in action.params
    assert "pixel_y" in action.params

def test_state_specific_handling(input_handler, game_state_manager):
    # Test main menu state
    game_state_manager.change_state(GameState.MAIN_MENU)
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.RETURN,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    action = input_handler.dispatch(event)
    
    assert action is not None
    assert action.action_type == "start_game"
    assert game_state_manager.get_current_state() == GameState.GAME_WORLD

def test_message_manager_integration(input_handler, game_state_manager, message_manager):
    game_state_manager.change_state(GameState.GAME_WORLD)
    
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.i,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    action = input_handler.dispatch(event)
    
    # Verify that a message was added to the message manager
    assert len(message_manager.messages) > 0
    assert any("Opening inventory" in msg[0] for msg in message_manager.messages)

def test_character_screen_key(input_handler, game_state_manager):
    """Test that character screen key changes game state correctly."""
    # Set initial state
    game_state_manager.change_state(GameState.GAME_WORLD)
    
    # Simulate character screen key press (assuming 'c' is the character screen key)
    event = tcod.event.KeyDown(
        sym=tcod.event.KeySym.c,
        mod=tcod.event.KMOD_NONE,
        scancode=0,
        repeat=False
    )
    
    # Handle the key press
    action = input_handler.dispatch(event)
    
    # Process the action
    if action and action.action_type == "open_character":
        game_state_manager.change_state(GameState.CHARACTER_SCREEN)
    
    # Verify state changed
    assert game_state_manager.get_current_state() == GameState.CHARACTER_SCREEN