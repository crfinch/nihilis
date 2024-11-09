import pytest
import tcod
from src.engine.display_manager import DisplayManager
from src.engine.message_manager import MessageManager

@pytest.fixture
def message_manager():
    return MessageManager()

@pytest.fixture
def display_manager(message_manager):
    return DisplayManager(message_manager)

def test_display_manager_initialization(display_manager):
    """Test that the DisplayManager initializes correctly with all required consoles."""
    # Check that tileset was loaded
    assert isinstance(display_manager.tileset, tcod.tileset.Tileset)
    
    # Check that all required consoles exist
    assert "main" in display_manager.consoles
    assert "status" in display_manager.consoles
    assert "message_log" in display_manager.consoles
    assert "minimap" in display_manager.consoles
    
    # Check console dimensions
    main_console = display_manager.get_console("main")
    assert main_console.width == DisplayManager.SCREEN_WIDTH - DisplayManager.SIDEBAR_WIDTH
    assert main_console.height == DisplayManager.SCREEN_HEIGHT - DisplayManager.STATUS_HEIGHT
    
    status_console = display_manager.get_console("status")
    assert status_console.width == DisplayManager.SCREEN_WIDTH
    assert status_console.height == DisplayManager.STATUS_HEIGHT
    
    message_log = display_manager.get_console("message_log")
    assert message_log.width == DisplayManager.SIDEBAR_WIDTH
    assert message_log.height == DisplayManager.SCREEN_HEIGHT - DisplayManager.MINIMAP_HEIGHT
    
    minimap = display_manager.get_console("minimap")
    assert minimap.width == DisplayManager.SIDEBAR_WIDTH
    assert minimap.height == DisplayManager.MINIMAP_HEIGHT

def test_get_console(display_manager):
    """Test the get_console method."""
    # Test getting valid console
    assert display_manager.get_console("main") is not None
    assert display_manager.get_console("status") is not None
    
    # Test getting invalid console
    assert display_manager.get_console("nonexistent") is None

def test_clear_all(display_manager):
    """Test the clear_all method."""
    # Write some content to consoles
    main_console = display_manager.get_console("main")
    main_console.print(0, 0, "Test content")
    
    status_console = display_manager.get_console("status")
    status_console.print(0, 0, "Status content")
    
    # Clear all consoles
    display_manager.clear_all()
    
    # Check that consoles are cleared
    # When cleared, the character at each position should be space (32 in ASCII)
    assert main_console.ch[0,0] == 32  # ASCII code for space
    assert status_console.ch[0,0] == 32  # ASCII code for space

def test_render(display_manager):
    """Test the render method."""
    # Write some test content
    main_console = display_manager.get_console("main")
    main_console.print(0, 0, "Test content")
    
    # Verify render doesn't raise exceptions
    try:
        display_manager.render()
    except Exception as e:
        pytest.fail(f"render() raised {e} unexpectedly!")

def test_context_initialization(display_manager):
    """Test that the context is properly initialized."""
    assert display_manager.context is not None
    assert isinstance(display_manager.context, tcod.context.Context)

def test_console_content(display_manager):
    """Test that we can write to and read from consoles."""
    console = display_manager.get_console("main")
    test_text = "Test content"
    test_color = (255, 0, 0)  # Red
    
    # Write some content
    console.print(0, 0, test_text, fg=test_color)
    
    # Check that the content was written correctly
    assert console.fg[0,0].tolist() == list(test_color)
