from enum import Enum, auto
from typing import Optional, Callable, Dict
from src.engine.message_manager import MessageManager

class GameState(Enum):
    """Enum representing different game states."""
    MAIN_MENU = auto()
    GAME_WORLD = auto()
    CHARACTER_SCREEN = auto()
    INVENTORY = auto()
    DIALOGUE = auto()
    PAUSED = auto()

class GameStateManager:
    """Manages game state transitions and associated callbacks."""
    
    def __init__(self, message_manager: Optional[MessageManager] = None):
        self.current_state = GameState.MAIN_MENU
        self.message_manager = message_manager
        self.state_change_callbacks: Dict[GameState, Callable] = {}
        
    def register_state_callback(self, state: GameState, callback: Callable) -> None:
        """Register a callback to be called when entering a state."""
        self.state_change_callbacks[state] = callback
        
    def change_state(self, new_state: GameState) -> None:
        """Change the current game state and trigger associated callbacks."""
        old_state = self.current_state
        self.current_state = new_state
        
        # Log state change if message manager exists
        if self.message_manager:
            self.message_manager.add_message(
                f"State changed from {old_state.name} to {new_state.name}",
                fg=(128, 128, 255)
            )
            
        # Execute callback if it exists
        if new_state in self.state_change_callbacks:
            self.state_change_callbacks[new_state]()
    
    def get_current_state(self) -> GameState:
        """Get the current game state."""
        return self.current_state