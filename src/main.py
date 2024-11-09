# src/main.py

import tcod
from src.engine.display_manager import DisplayManager
from src.engine.input_handler import InputHandler, GameState
from src.utils.logger_config import logger
from src.engine.message_manager import MessageManager
from src.engine.game_state_manager import GameStateManager
from src.engine.game_loop import GameLoop
from src.engine.ui_manager import UIManager

def main() -> None:
	"""Main game entry point."""
	message_manager = MessageManager()
	display_manager = DisplayManager(message_manager)
	ui_manager = UIManager(display_manager, message_manager)
	state_manager = GameStateManager(message_manager)
	state_manager.change_state(GameState.MAIN_MENU)
	
	input_handler = InputHandler(
		display_manager.context,
		state_manager,
		message_manager=message_manager,
		debug=False
	)
	
	# Register state callbacks
	state_manager.register_state_callback(
		GameState.GAME_WORLD,
		lambda: message_manager.add_message("Entered game world!", fg=(255, 255, 0))
	)
	
	# Initial messages
	message_manager.add_message("Welcome to Nihilis!", fg=(255, 223, 0))
	message_manager.add_message("You enter the region.", fg=(255, 255, 255))
	message_manager.add_message("You see BIG mountains.", fg=(192, 192, 192))
	message_manager.add_message("A cool breeze blows.", fg=(128, 192, 255))
	message_manager.add_message("Arte is a really serious damned hottie!", fg=(255, 192, 255))
	
	# Create and run game loop
	game_loop = GameLoop(display_manager, input_handler, state_manager, message_manager, ui_manager)
	try:
		game_loop.run()
	finally:
		display_manager.close()

if __name__ == "__main__":
	main()