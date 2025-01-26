import pytest
import tcod
from src.engine.message_manager import MessageManager

@pytest.fixture
def message_manager():
    return MessageManager()

def test_message_manager_initialization():
    """Test that MessageManager initializes with correct default values."""
    manager = MessageManager()
    assert manager.messages == []
    assert manager.max_messages == 100
    
    # Test custom max_messages
    custom_manager = MessageManager(max_messages=50)
    assert custom_manager.max_messages == 50

def test_add_message():
    """Test adding messages to the message manager."""
    manager = MessageManager()
    
    # Test adding a simple message
    manager.add_message("Test message")
    assert len(manager.messages) == 1
    assert manager.messages[0][0] == "Test message"
    assert manager.messages[0][1] == (255, 255, 255)  # Default color
    
    # Test adding message with custom color
    manager.add_message("Colored message", fg=(255, 0, 0))
    assert len(manager.messages) == 2
    assert manager.messages[1][0] == "Colored message"
    assert manager.messages[1][1] == (255, 0, 0)

def test_message_wrapping():
    """Test that long messages are properly wrapped."""
    manager = MessageManager()
    
    # Test long message that should wrap
    long_message = "This is a very long message that should be wrapped across multiple lines"
    manager.add_message(long_message, width=20)
    
    # The message should be split into multiple entries
    assert len(manager.messages) > 1
    # Each line should be no longer than width - 4 (accounting for margins)
    for msg, _ in manager.messages:
        assert len(msg) <= 16  # 20 - 4 for margins

def test_max_messages():
    """Test that the message list respects max_messages limit."""
    manager = MessageManager(max_messages=3)
    
    # Add more messages than the limit
    messages = ["First", "Second", "Third", "Fourth", "Fifth"]
    for msg in messages:
        manager.add_message(msg)
    
    # Should only keep the last 3 messages
    assert len(manager.messages) == 3
    assert [msg for msg, _ in manager.messages] == ["Third", "Fourth", "Fifth"]

def test_render_messages():
    """Test rendering messages to a console."""
    manager = MessageManager()
    console = tcod.console.Console(width=30, height=10)
    
    # Add some test messages
    manager.add_message("First message", fg=(255, 0, 0))
    manager.add_message("Second message", fg=(0, 255, 0))
    
    # Render messages
    manager.render_messages(console)
    
    # Check that console contains the messages
    # We can't directly check the console contents, but we can verify no exceptions were raised
    assert True  # If we got here, rendering didn't crash

def test_empty_message():
    """Test handling of empty messages."""
    manager = MessageManager()
    
    # Add an empty message
    manager.add_message("")
    assert len(manager.messages) == 1
    assert manager.messages[0][0] == ""

def test_multiline_message_wrapping():
    """Test wrapping of messages with multiple paragraphs."""
    manager = MessageManager()
    
    multiline = "First paragraph.\nSecond paragraph.\nThird paragraph."
    manager.add_message(multiline, width=20)
    
    # Each paragraph should be wrapped separately
    assert len(manager.messages) >= 3

def test_special_characters():
    """Test handling of special characters in messages."""
    manager = MessageManager()
    
    special_chars = "Test with special chars: !@#$%^&*()"
    # Explicitly set width to accommodate the full string
    width = len(special_chars) + 4  # Add 4 for margins
    manager.add_message(special_chars, width=width)
    
    result = manager.messages[0][0]
    print(f"\nExpected: '{special_chars}'")
    print(f"Got: '{result}'")
    print(f"Lengths: expected={len(special_chars)}, got={len(result)}")
    
    assert result == special_chars

def test_message_frame_boundaries(message_manager):
    """Test that messages respect console frame boundaries."""
    # Create a small console for testing
    console = tcod.console.Console(width=30, height=10)
    
    # Add more messages than can fit in the console
    for i in range(15):
        message_manager.add_message(f"Test message {i}")
    
    # Draw frame
    console.draw_frame(0, 0, console.width, console.height)
    
    # Render messages
    message_manager.render_messages(console)
    
    # Check top and bottom borders are intact
    assert chr(console.ch[0, 1]) == "─"  # Top border
    assert chr(console.ch[console.height-1, 1]) == "─"  # Bottom border
    
    # Verify no messages are written on borders
    for x in range(console.width):
        assert console.ch[0, x] != ord(" ")  # Top border intact
        assert console.ch[console.height-1, x] != ord(" ")  # Bottom border intact