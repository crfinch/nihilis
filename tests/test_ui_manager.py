import pytest
import tcod
from src.engine.display_manager import DisplayManager
from src.engine.message_manager import MessageManager
from src.engine.ui_manager import UIManager

@pytest.fixture
def message_manager():
    return MessageManager()

@pytest.fixture
def display_manager(message_manager):
    return DisplayManager(message_manager)

@pytest.fixture
def ui_manager(display_manager, message_manager):
    return UIManager(display_manager, message_manager)

def test_ui_manager_initialization(ui_manager):
    """Test that UIManager initializes correctly."""
    assert ui_manager.display_manager is not None
    assert ui_manager.message_manager is not None

def test_render_game_screen(ui_manager, message_manager):
    """Test that render_game_screen properly coordinates all UI elements."""
    # Add some test messages
    message_manager.add_message("Test message 1", fg=(255, 0, 0))
    message_manager.add_message("Test message 2", fg=(0, 255, 0))
    
    # Attempt to render the game screen
    try:
        ui_manager.render_game_screen()
    except Exception as e:
        pytest.fail(f"render_game_screen() raised {e} unexpectedly!")

def test_render_main_view(ui_manager):
    """Test that main console rendering works correctly."""
    main_console = ui_manager.display_manager.get_console("main")
    
    # Clear to known state
    main_console.clear()
    
    # Render
    ui_manager._render_main_view()
    
    # Check specific positions - Note: coordinates are now (y,x)
    tests = [
        ((1, 2), "W", (255, 223, 0), "Welcome message"),  # First char of welcome
        ((3, 2), "▲", (128, 128, 128), "Mountain symbol"),
        ((4, 2), "≈", (0, 148, 255), "River symbol"),
        ((5, 2), "♠", (0, 255, 0), "Forest symbol")
    ]
    
    for (y, x), char, color, desc in tests:
        # Get the character at the y,x position
        actual_char = chr(main_console.ch[y,x])
        actual_color = main_console.fg[y,x].tolist()
        
        print(f"\nTesting {desc}")
        print(f"Testing position (y={y}, x={x})")
        print(f"Expected char: {char}, got: {actual_char}")
        print(f"Expected color: {color}, got: {actual_color}")
        print(f"Raw character value: {main_console.ch[y,x]}")
        
        assert actual_char == char, (
            f"Character mismatch for {desc} at position (y={y}, x={x}). "
            f"Expected '{char}' (ASCII: {ord(char)}), "
            f"got '{actual_char}' (ASCII: {main_console.ch[y,x]})"
        )
        assert actual_color == list(color), (
            f"Color mismatch for {desc} at position (y={y}, x={x}). "
            f"Expected {color}, got {actual_color}"
        )

def test_render_status_bar(ui_manager):
    """Test that status console rendering works correctly."""
    status_console = ui_manager.display_manager.get_console("status")
    ui_manager._render_status_bar()
    
    # Check status text - coordinates are [y,x]
    status_text = "Status: Active"
    fg_color = status_console.fg[1,1].tolist()
    assert fg_color == [0, 255, 0]  # Green color
    
    # Check HP display - coordinates are [y,x]
    hp_text = "HP: 100/100"
    hp_x = status_console.width - 20
    fg_color = status_console.fg[1,hp_x].tolist()  # Fixed: y=1, x=hp_x
    assert fg_color == [255, 0, 0]  # Red color
    
    # Add some debug output
    print(f"\nDebug - Status Console:")
    print(f"Console dimensions: {status_console.width}x{status_console.height}")
    print(f"HP position: y=1, x={hp_x}")
    print(f"Status color at (1,1): {status_console.fg[1,1].tolist()}")
    print(f"HP color at (1,{hp_x}): {status_console.fg[1,hp_x].tolist()}")

def test_render_minimap(ui_manager):
    """Test that minimap console rendering works correctly."""
    minimap_console = ui_manager.display_manager.get_console("minimap")
    ui_manager._render_minimap()
    
    # Debug print the actual characters we're getting
    print("\nDebug - Minimap Frame Characters:")
    print(f"Top-left (0,0): {chr(minimap_console.ch[0,0])} (ASCII: {minimap_console.ch[0,0]})")
    print(f"Top-right ({minimap_console.width-1},0): {chr(minimap_console.ch[minimap_console.width-1,0])} (ASCII: {minimap_console.ch[minimap_console.width-1,0]})")
    
    # Define expected box-drawing characters
    FRAME_CHARS = {
        'top_left': '┌',    # Unicode: 9484
        'top_right': '┐',   # Unicode: 9488
        'bottom_left': '└',  # Unicode: 9492
        'bottom_right': '┘', # Unicode: 9496
        'horizontal': '─',   # Unicode: 9472
        'vertical': '│'      # Unicode: 9474
    }
    
    # Check frame with better error messages
    assert minimap_console.ch[0,0] == ord(FRAME_CHARS['top_left']), (
        f"Wrong top-left corner character. "
        f"Expected '{FRAME_CHARS['top_left']}' ({ord(FRAME_CHARS['top_left'])}), "
        f"got '{chr(minimap_console.ch[0,0])}' ({minimap_console.ch[0,0]})"
    )
    
    # Check terrain markers with [y,x] coordinates
    terrain_tests = [
        ((5,5), '▲', "Mountain"),
        ((7,7), '≈', "River"),
        ((9,6), '♠', "Forest")
    ]
    
    for (y,x), char, desc in terrain_tests:
        actual_char = chr(minimap_console.ch[y,x])
        print(f"\nTesting {desc}:")
        print(f"Position (y={y}, x={x})")
        print(f"Expected: {char} ({ord(char)})")
        print(f"Got: {actual_char} ({minimap_console.ch[y,x]})")
        assert minimap_console.ch[y,x] == ord(char), f"{desc} character mismatch"

def test_render_message_log(ui_manager, message_manager):
    """Test that message console rendering works correctly."""
    message_console = ui_manager.display_manager.get_console("message_log")
    
    # Add some test messages
    test_messages = [
        ("Test message 1", (255, 0, 0)),
        ("Test message 2", (0, 255, 0)),
        ("Test message 3", (0, 0, 255))
    ]
    
    for msg, color in test_messages:
        message_manager.add_message(msg, fg=color)
    
    # Render messages
    ui_manager._render_message_log()
    
    # Define expected frame characters
    FRAME_CHARS = {
        'top_left': '┌',     # 9484
        'top_right': '┐',    # 9488
        'bottom_left': '└',  # 9492
        'bottom_right': '┘'  # 9496
    }
    
    # Check frame corners with [y,x] coordinates
    corners = [
        ((0, 0), 'top_left'),
        ((0, message_console.width-1), 'top_right'),
        ((message_console.height-1, 0), 'bottom_left'),
        ((message_console.height-1, message_console.width-1), 'bottom_right')
    ]
    
    for (y, x), corner_name in corners:
        expected_char = FRAME_CHARS[corner_name]
        actual_char = chr(message_console.ch[y,x])
        print(f"\nChecking {corner_name} corner at ({y},{x}):")
        print(f"Expected: {expected_char} ({ord(expected_char)})")
        print(f"Got: {actual_char} ({message_console.ch[y,x]})")
        assert message_console.ch[y,x] == ord(expected_char), (
            f"Wrong {corner_name} character. "
            f"Expected '{expected_char}' ({ord(expected_char)}), "
            f"got '{actual_char}' ({message_console.ch[y,x]})"
        )

def test_message_overflow(ui_manager, message_manager):
    """Test that messages properly handle overflow in the console."""
    message_console = ui_manager.display_manager.get_console("message_log")
    available_height = message_console.height - 3  # Account for frame and padding
    
    # Add more messages than can fit
    for i in range(available_height + 5):
        message_manager.add_message(f"Test message {i}", fg=(255, 255, 255))
    
    ui_manager._render_message_log()
    
    # Check that only the last 'available_height' messages are visible
    visible_messages = 0
    for y in range(2, message_console.height - 1):  # Skip frame
        if message_console.ch[2, y] != ord(' '):
            visible_messages += 1
    
    assert visible_messages <= available_height

def test_ui_state_changes(ui_manager, message_manager):
    """Test that UI updates correctly with different game states."""
    # Test main menu state
    message_manager.add_message("Main Menu", fg=(255, 255, 255))
    ui_manager.render_game_screen()
    
    # Test game world state
    message_manager.add_message("Entered Game World", fg=(255, 255, 0))
    ui_manager.render_game_screen()
    
    # No assertions needed - just checking for no exceptions
    # Could be expanded later to check for state-specific UI elements

def test_ui_responsiveness(ui_manager):
    """Test that UI responds correctly to window/console size changes."""
    # Get original console dimensions
    main_console = ui_manager.display_manager.get_console("main")
    original_width = main_console.width
    original_height = main_console.height
    
    # Render UI
    ui_manager.render_game_screen()
    
    # Verify dimensions haven't changed
    assert main_console.width == original_width
    assert main_console.height == original_height 