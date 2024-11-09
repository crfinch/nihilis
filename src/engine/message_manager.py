from typing import List, Tuple
import tcod

class MessageManager:
    def __init__(self, max_messages: int = 100):
        self.messages: List[Tuple[str, Tuple[int, int, int]]] = []
        self.max_messages = max_messages

    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Break text into lines that fit within the given width."""
        # Handle empty strings
        if not text:
            return [""]
            
        # If text length is less than or equal to width, return as-is
        if len(text) <= width:
            return [text]
            
        # Only proceed with wrapping if text is actually longer than width
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)
            space_length = 1 if current_line else 0
            
            if current_length + word_length + space_length <= width:
                current_line.append(word)
                current_length += word_length + space_length
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def add_message(self, text: str, fg: Tuple[int, int, int] = (255, 255, 255), width: int = 26):
        """Add a message, wrapping it if necessary to fit the console width."""
        if not text:
            self.messages.append(("", fg))
            return

        # Only subtract margins if we actually need to wrap
        available_width = width
        if len(text) > width:
            available_width = width - 4  # Apply margins only when wrapping is needed
        
        wrapped_lines = self._wrap_text(text, available_width)
        
        for line in wrapped_lines:
            self.messages.append((line, fg))
            while len(self.messages) > self.max_messages:
                self.messages.pop(0)

    def render_messages(self, console: tcod.console.Console, start_y: int = 2):
        """Render messages to the console, maintaining proper spacing."""
        # Calculate available height for messages
        available_height = console.height - 3  # Subtract 3 for top/bottom frame
        
        # Get the messages that will fit in the available height
        visible_messages = self.messages[-available_height:]
        
        for i, (text, fg) in enumerate(visible_messages):
            if start_y + i < console.height - 1:  # Prevent overflow
                console.print(2, start_y + i, text, fg=fg)