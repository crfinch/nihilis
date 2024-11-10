# src/main.py

import tcod
from src.engine.display_manager import DisplayManager
from src.engine.input_handler import InputHandler, GameState
from src.utils.logger_config import logger
from src.engine.message_manager import MessageManager
from src.engine.game_state_manager import GameStateManager
from src.engine.game_loop import GameLoop
from src.engine.ui_manager import UIManager
from src.utils.configuration_manager import ConfigurationManager
from src.utils.performance_monitor import PerformanceMonitor


def main() -> None:
	"""Main game entry point."""
	# Initialize configuration manager
	config_manager = ConfigurationManager()
	
	# Load configurations
	display_config = config_manager.get_display_config()
	performance_config = config_manager.get_performance_config()
	keybindings = config_manager.get_keybindings()
	debug_settings = config_manager.get_debug_settings()
	
	# Initialize managers with configuration
	display_manager = DisplayManager(config_manager=config_manager)
	message_console = display_manager.get_console("message_log")
	message_manager = MessageManager(max_messages=performance_config.max_messages, console_width=message_console.width)
	
	# Initialize performance monitor with configuration
	performance_monitor = PerformanceMonitor(
		log_interval=performance_config.log_interval,
		warning_threshold_fps=performance_config.warning_threshold_fps,
		critical_threshold_fps=performance_config.critical_threshold_fps,
		memory_warning_threshold_mb=performance_config.memory_warning_threshold_mb,
		target_fps=performance_config.target_fps,
		max_messages=performance_config.max_messages
	)
	
	# Initialize UI manager with debug settings
	ui_manager = UIManager(
		display_manager, 
		message_manager,
		performance_monitor,
		debug=debug_settings['enabled']
	)
	
	state_manager = GameStateManager(message_manager)
	state_manager.change_state(GameState.MAIN_MENU)
	
	# Initialize input handler with keybindings and debug settings
	input_handler = InputHandler(
		display_manager.context,
		state_manager,
		message_manager=message_manager,
		config_manager=config_manager,
		debug=debug_settings['enabled']
	)
	
	# Create and run game loop with performance monitoring
	game_loop = GameLoop(
		display_manager, 
		input_handler, 
		state_manager, 
		message_manager, 
		ui_manager,
		performance_monitor
	)
	
	# Initial messages
	message_manager.add_message("Welcome to Nihilis!", fg=(255, 223, 0))
	message_manager.add_message("You enter the region.", fg=(255, 255, 255))
	message_manager.add_message("You see BIG mountains.", fg=(192, 192, 192))
	message_manager.add_message("A cool breeze blows.", fg=(128, 192, 255))
	message_manager.add_message("Arte is a really serious damned hottie!", fg=(255, 192, 255))
	
	# Create and run game loop
	# game_loop = GameLoop(display_manager, input_handler, state_manager, message_manager, ui_manager)
	try:
		game_loop.run()
	finally:
		display_manager.close()

if __name__ == "__main__":
	main()