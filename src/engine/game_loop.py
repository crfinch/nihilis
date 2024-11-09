from typing import Optional
import tcod
from src.engine.display_manager import DisplayManager
from src.engine.input_handler import InputHandler, GameState
from src.engine.message_manager import MessageManager
from src.engine.game_state_manager import GameStateManager
from src.engine.ui_manager import UIManager
from src.utils.logger_config import logger

class GameLoop:
    def __init__(
        self,
        display_manager: DisplayManager,
        input_handler: InputHandler,
        state_manager: GameStateManager,
        message_manager: MessageManager,
        ui_manager: UIManager
    ):
        self.display_manager = display_manager
        self.input_handler = input_handler
        self.state_manager = state_manager
        self.message_manager = message_manager
        self.ui_manager = ui_manager
    def handle_action(self, action) -> bool:
        """Handle a game action. Returns True if game should continue, False if should quit."""
        if not action:
            return True
            
        if action.action_type == "quit":
            return False
        elif action.action_type == "start_game":
            self.message_manager.messages.clear()
            self.message_manager.add_message("Welcome to Nihilis!", fg=(255, 223, 0))
        elif action.action_type == "move":
            self._handle_movement(action)
        elif action.action_type == "mouse_move":
            self._handle_mouse_move(action)
        elif action.action_type == "open_inventory":
            self.message_manager.add_message("Opening inventory...", fg=(255, 255, 0))
        elif action.action_type == "open_character":
            self.message_manager.add_message("Opening character screen...", fg=(255, 255, 0))
        
        return True
        
    def _handle_movement(self, action):
        if self.state_manager.get_current_state() == GameState.GAME_WORLD:
            dx, dy = action.params["dx"], action.params["dy"]
            direction = self._get_movement_direction(dx, dy)
            sprint = "sprinting " if action.params.get("sprint") else ""
            self.message_manager.add_message(
                f"Moving {sprint}{direction}...",
                fg=(200, 200, 200)
            )
            
    def _get_movement_direction(self, dx: int, dy: int) -> str:
        direction = ""
        if dy < 0: direction = "north"
        elif dy > 0: direction = "south"
        if dx < 0: direction = f"{direction}west"
        elif dx > 0: direction = f"{direction}east"
        return direction
        
    def _handle_mouse_move(self, action):
        status_console = self.display_manager.get_console("status")
        if status_console:
            status_console.print(
                30, 1,
                f"Mouse: {action.params['x']}, {action.params['y']}", 
                fg=(200, 200, 200)
            )
    
    def run(self):
        """Main game loop."""
        try:
            while True:
                # Render the game screen (this will handle all console rendering)
                self.ui_manager.render_game_screen()
                
                for event in tcod.event.wait():
                    if isinstance(event, (tcod.event.MouseMotion, tcod.event.MouseButtonDown)):
                        self.display_manager.context.convert_event(event)
                        logger.debug(f"Converted Event: {event}")
                        action = self.input_handler.dispatch(event)
                    else:
                        action = self.input_handler.dispatch(event)
                    
                    if not self.handle_action(action):
                        return
                        
        except Exception as e:
            logger.error(f"Error in game loop: {e}")
            raise 