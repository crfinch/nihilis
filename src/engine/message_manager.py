from typing import List, Tuple
import tcod

class MessageManager:
    def __init__(self, max_messages: int = 100, console_width: int = None):
        self.messages: List[Tuple[str, Tuple[int, int, int]]] = []
        self.max_messages = max_messages
        self.console_width = console_width or 25  # Default if not specified

    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Break text into lines that fit within the given width."""
        # Handle empty strings
        if not text:
            return [""]
            
        # If text length is less than or equal to width, return as-is
        if len(text) <= width:
            return [text]
            
        # Split on newlines first to handle explicit line breaks
        paragraphs = text.split('\n')
        wrapped_lines = []
        
        for paragraph in paragraphs:
            # Only proceed with wrapping if text is actually longer than width
            words = paragraph.split()
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
                        wrapped_lines.append(" ".join(current_line))
                    current_line = [word]
                    current_length = word_length

            if current_line:
                wrapped_lines.append(" ".join(current_line))

        return wrapped_lines

    def add_message(self, text: str, fg: Tuple[int, int, int] = (255, 255, 255), width: int = None):
        """Add a message, wrapping it if necessary to fit the console width."""
        if not text:
            self.messages.append(("", fg))
            return

        # Use provided width if given, otherwise use console_width
        available_width = width if width is not None else self.console_width
        if len(text) > available_width:
            available_width = available_width - 4  # Apply margins only when wrapping is needed
        
        wrapped_lines = self._wrap_text(text, available_width)
        
        for line in wrapped_lines:
            self.messages.append((line, fg))
            while len(self.messages) > self.max_messages:
                self.messages.pop(0)

    def render_messages(self, console: 'Console') -> None:
        """Render messages to the provided console."""
        # Start from the bottom, accounting for bottom frame border
        y = console.height - 2  # Changed from -1 to -2 to respect bottom border
        
        # Render messages until we hit the top frame border or run out of messages
        for message, color in reversed(self.messages):
            if y <= 1:  # Stop at top frame border
                break
            console.print(x=2, y=y, string=message, fg=color)
            y -= 1