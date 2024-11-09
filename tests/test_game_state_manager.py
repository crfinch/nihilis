import pytest
from src.engine.game_state_manager import GameStateManager, GameState
from src.engine.message_manager import MessageManager

@pytest.fixture
def message_manager():
    return MessageManager()

@pytest.fixture
def game_state_manager(message_manager):
    return GameStateManager(message_manager)

def test_game_state_manager_initialization():
    """Test that GameStateManager initializes with correct default state."""
    manager = GameStateManager()
    assert manager.get_current_state() == GameState.MAIN_MENU
    assert manager.message_manager is None
    assert manager.state_change_callbacks == {}

def test_state_change():
    """Test basic state change functionality."""
    manager = GameStateManager()
    
    # Change to game world
    manager.change_state(GameState.GAME_WORLD)
    assert manager.get_current_state() == GameState.GAME_WORLD
    
    # Change to inventory
    manager.change_state(GameState.INVENTORY)
    assert manager.get_current_state() == GameState.INVENTORY

def test_state_callbacks():
    """Test that callbacks are properly registered and executed."""
    manager = GameStateManager()
    callback_executed = False
    
    def test_callback():
        nonlocal callback_executed
        callback_executed = True
    
    # Register callback for INVENTORY state
    manager.register_state_callback(GameState.INVENTORY, test_callback)
    
    # Change to INVENTORY state
    manager.change_state(GameState.INVENTORY)
    
    assert callback_executed
    assert GameState.INVENTORY in manager.state_change_callbacks

def test_message_manager_integration(message_manager, game_state_manager):
    """Test that state changes are properly logged to message manager."""
    game_state_manager.change_state(GameState.GAME_WORLD)
    
    assert len(message_manager.messages) > 0
    # Check that all parts of the message exist
    messages = [msg[0] for msg in message_manager.messages]
    assert "State changed from" in messages[0]
    assert "MAIN_MENU to" in messages[1]
    assert "GAME_WORLD" in messages[2]

def test_multiple_state_changes(game_state_manager):
    """Test multiple state transitions."""
    states = [
        GameState.GAME_WORLD,
        GameState.INVENTORY,
        GameState.CHARACTER_SCREEN,
        GameState.DIALOGUE,
        GameState.PAUSED,
        GameState.MAIN_MENU
    ]
    
    for state in states:
        game_state_manager.change_state(state)
        assert game_state_manager.get_current_state() == state

def test_callback_overwrite():
    """Test that registering a new callback for the same state overwrites the old one."""
    manager = GameStateManager()
    callback_count = 0
    
    def callback1():
        nonlocal callback_count
        callback_count += 1
        
    def callback2():
        nonlocal callback_count
        callback_count += 2
    
    # Register first callback
    manager.register_state_callback(GameState.INVENTORY, callback1)
    manager.change_state(GameState.INVENTORY)
    assert callback_count == 1
    
    # Register second callback for same state
    manager.register_state_callback(GameState.INVENTORY, callback2)
    manager.change_state(GameState.GAME_WORLD)  # Change to different state first
    manager.change_state(GameState.INVENTORY)
    assert callback_count == 3  # 1 from first callback + 2 from second callback 