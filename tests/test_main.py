import warnings
import pytest
import tcod
from src.main import main
from src.engine.display_manager import DisplayManager
from src.engine.input_handler import InputHandler
from src.engine.message_manager import MessageManager
from src.engine.game_state_manager import GameStateManager, GameState
from src.engine.game_loop import GameLoop
from src.engine.ui_manager import UIManager

@pytest.fixture(autouse=True)
def ignore_tcod_warnings():
    """Fixture to ignore specific TCOD deprecation warnings."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning, module="tcod.*")
        yield

@pytest.fixture
def message_manager():
    return MessageManager()

@pytest.fixture
def display_manager(message_manager):
    return DisplayManager(message_manager)

@pytest.fixture
def ui_manager(display_manager, message_manager):
    return UIManager(display_manager, message_manager)

@pytest.fixture
def state_manager(message_manager):
    return GameStateManager(message_manager)

@pytest.fixture
def input_handler(state_manager, message_manager):
    context = tcod.context.new()
    return InputHandler(
        context=context,
        state_manager=state_manager,
        message_manager=message_manager,
        debug=False
    )

def test_main_initialization(monkeypatch, message_manager, display_manager, ui_manager, state_manager, input_handler):
    """Test that main initializes all components correctly."""
    # Mock GameLoop to prevent actual game execution
    class MockGameLoop:
        def __init__(self, *args, **kwargs):
            self.display_manager = args[0]
            self.input_handler = args[1]
            self.state_manager = args[2]
            self.message_manager = args[3]
            self.ui_manager = args[4]
        
        def run(self):
            pass

    monkeypatch.setattr("src.engine.game_loop.GameLoop", MockGameLoop)
    
    # Run main and verify components
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised {e} unexpectedly!")

def test_initial_messages(message_manager):
    """Test that initial messages are added correctly."""
    main()
    
    expected_messages = [
        ("Welcome to Nihilis!", (255, 223, 0)),
        ("You enter the region.", (255, 255, 255)),
        ("You see BIG mountains.", (192, 192, 192)),
        ("A cool breeze blows.", (128, 192, 255)),
        ("Arte is a really serious damned hottie!", (255, 192, 255))
    ]
    
    for expected, actual in zip(expected_messages, message_manager.messages):
        assert expected[0] in actual[0]
        assert expected[1] == actual[1]

def test_state_callback_registration(state_manager):
    """Test that game state changes are properly handled."""
    main()
    
    current_state = state_manager.get_current_state()
    expected_state = GameState.MAIN_MENU
    
    # Test state change
    state_manager.change_state(GameState.GAME_WORLD)
    assert str(state_manager.get_current_state()) == str(GameState.GAME_WORLD)
    
    # Get all messages as a list
    messages = [msg[0] for msg in state_manager.message_manager.messages]
    
    # Check for all parts of the state change message
    assert "State changed from" in messages, f"Missing state change prefix in messages: {messages}"
    assert "MAIN_MENU to" in messages, f"Missing original state in messages: {messages}"
    assert "GAME_WORLD" in messages, f"Missing new state in messages: {messages}"

def test_error_handling(monkeypatch):
    """Test that errors during initialization are handled properly."""
    def mock_display_init(*args, **kwargs):
        raise RuntimeError("Test error")
    
    monkeypatch.setattr(DisplayManager, "__init__", mock_display_init)
    
    with pytest.raises(RuntimeError):
        main() 