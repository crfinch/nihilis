from typing import Optional
import tcod
from src.engine.display_manager import DisplayManager
from src.engine.input_handler import InputHandler, GameState
from src.engine.message_manager import MessageManager
from src.engine.game_state_manager import GameStateManager
from src.engine.ui_manager import UIManager
from src.utils.logger_config import logger
from src.utils.performance_monitor import PerformanceMonitor
import time
from src.world.world_generator import WorldGenerator
from src.utils.configuration_manager import ConfigurationManager

class GameLoop:
    def __init__(
        self,
        display_manager: DisplayManager,
        input_handler: InputHandler,
        state_manager: GameStateManager,
        message_manager: MessageManager,
        ui_manager: UIManager,
        performance_monitor: PerformanceMonitor
    ):
        self.display_manager = display_manager
        self.input_handler = input_handler
        self.state_manager = state_manager
        self.message_manager = message_manager
        self.ui_manager = ui_manager
        self.performance_monitor = performance_monitor
        self.target_fps = 60
        self.frame_time = 1.0 / self.target_fps
        
        # Initialize world generation
        config_manager = ConfigurationManager()
        self.world_generator = WorldGenerator(config_manager)
        
        # Generate initial world
        self._initialize_world()
        # Add debug print to confirm initialization
        # print("Game loop initialized with performance monitoring")

    def _initialize_world(self):
        """Generate the world and prepare it for rendering."""
        world = self.world_generator.generate()
        
        # Get world data for rendering using the proper method
        world_data = world.get_render_data()
        
        # Update UI manager with world data
        self.ui_manager.set_world_data(world_data)

    def handle_action(self, action) -> bool:
        """Handle a game action. Returns False if the game should exit."""
        if action is None:
            return True
            
        if action.action_type == "quit":
            return False
            
        if action.action_type == "start_game":
            self.message_manager.add_message("Welcome to Nihilis!", fg=(255, 223, 0))
            return True
            
        if action.action_type == "open_inventory":
            self.state_manager.change_state(GameState.INVENTORY)
            self.message_manager.add_message("Opening inventory...", fg=(200, 200, 200))
            return True
            
        if action.action_type == "open_character":
            self.message_manager.add_message("Opening character screen...", fg=(200, 200, 200))
            return True
            
        if action.action_type == "move":
            self._handle_movement(action)
        elif action.action_type == "mouse_move":
            self._handle_mouse_move(action)
            
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
            next_frame_time = time.perf_counter()
            
            while True:
                current_time = time.perf_counter()
                
                # If it's not time for the next frame, sleep a bit
                if current_time < next_frame_time:
                    time.sleep(max(0, next_frame_time - current_time))
                    continue
                
                # Start frame timing
                self.performance_monitor.start_frame()
                
                # Process all pending events
                for event in tcod.event.get():
                    if isinstance(event, (tcod.event.MouseMotion, tcod.event.MouseButtonDown)):
                        self.display_manager.context.convert_event(event)
                        action = self.input_handler.dispatch(event)
                    else:
                        action = self.input_handler.dispatch(event)
                    
                    if not self.handle_action(action):
                        return
                
                # Update game state and render
                self.ui_manager.render_game_screen()
                
                # End frame timing
                self.performance_monitor.end_frame()
                
                # Calculate next frame time
                next_frame_time = current_time + self.frame_time
                
        except Exception as e:
            logger.error(f"Error in game loop: {e}")
            raise