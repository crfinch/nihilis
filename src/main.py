# src/main.py

import tcod
from engine.display_manager import DisplayManager
from engine.input_handler import InputHandler, GameState
from utils.logger_config import logger
from engine.message_manager import MessageManager
from engine.game_state_manager import GameStateManager

def main() -> None:
	"""Main game entry point."""
	message_manager = MessageManager()
	display_manager = DisplayManager()
	state_manager = GameStateManager(message_manager)
	state_manager.change_state(GameState.MAIN_MENU) # set initial state
	
	input_handler = InputHandler(
		display_manager.context,
		state_manager,
		message_manager=message_manager,
		debug=False
	)
	
	# Register state callbacks if needed
	state_manager.register_state_callback(
		GameState.GAME_WORLD,
		lambda: message_manager.add_message("Entered game world!", fg=(255, 255, 0))
	)
	
	message_manager.add_message("You enter the region.", fg=(255, 255, 255))	
	message_manager.add_message("You see BIG mountains.", fg=(192, 192, 192))
	message_manager.add_message("A cool breeze blows.", fg=(128, 192, 255))	
	message_manager.add_message("Arte is a really serious damned hottie!", fg=(255, 192, 255))
    
	try:
		while True:
			# Clear all consoles
			display_manager.clear_all()
			
			# Draw test content with some formatting to showcase the larger font
			main_console = display_manager.get_console("main")
			if main_console:
				# Title with custom colors
				main_console.print(2, 1, "Welcome to Nihilis!", fg=(255, 223, 0))  # Gold color
				main_console.print(2, 3, "▲ Mountains", fg=(128, 128, 128))  # Gray
				main_console.print(2, 4, "≈ Rivers", fg=(0, 148, 255))  # Blue
				main_console.print(2, 5, "♠ Forests", fg=(0, 255, 0))  # Green
				
			status_console = display_manager.get_console("status")
			if status_console:
				status_console.print(1, 1, "Status: Active", fg=(0, 255, 0))
				status_console.print(status_console.width - 20, 1, "HP: 100/100", fg=(255, 0, 0))
				
			minimap_console = display_manager.get_console("minimap")
			if minimap_console:
				minimap_console.draw_frame(
					0, 0, 
					minimap_console.width, 
					minimap_console.height,
					title=" World Map "
				)
				# Add some sample terrain markers
				minimap_console.print(5, 5, "▲", fg=(128, 128, 128))
				minimap_console.print(7, 7, "≈", fg=(0, 148, 255))
				minimap_console.print(9, 6, "♠", fg=(0, 255, 0))
				
			message_console = display_manager.get_console("message_log")
			if message_console:
				message_console.draw_frame(
					0, 0,
					message_console.width,
					message_console.height,
					title=" Messages "
				)
				# print the message manager's messages to the message console.
				message_manager.render_messages(message_console)
			
			# Render everything to the screen
			display_manager.render()
            
            # Handle input events
			for event in tcod.event.wait():
				# Convert mouse events before dispatching
				if isinstance(event, (tcod.event.MouseMotion, tcod.event.MouseButtonDown)):
					display_manager.context.convert_event(event)
					logger.debug(f"Converted Event: {event}")
					action = input_handler.dispatch(event)
				else:
					action = input_handler.dispatch(event)
                
				if action:
					if action.action_type == "quit":
						raise SystemExit()
					elif action.action_type == "start_game":
						# Clear any existing messages when starting new game
						message_manager.messages.clear()
						message_manager.add_message("Welcome to Nihilis!", fg=(255, 223, 0))
					elif action.action_type == "move":
						if state_manager.get_current_state() == GameState.GAME_WORLD:
							dx, dy = action.params["dx"], action.params["dy"]
							direction = ""
							if dy < 0: direction = "north"
							elif dy > 0: direction = "south"
							if dx < 0: direction = f"{direction}west"
							elif dx > 0: direction = f"{direction}east"
							
							sprint = "sprinting " if action.params.get("sprint") else ""
							message_manager.add_message(
								f"Moving {sprint}{direction}...",
								fg=(200, 200, 200)
							)
					elif action.action_type == "mouse_move":
						# Update status bar with mouse position
						if status_console:
							status_console.print(
								30, 1,
								f"Mouse: {action.params['x']}, {action.params['y']}", 
								fg=(200, 200, 200)
							)
					elif action.action_type == "open_inventory":
						if message_console:
							message_console.print(2, 5, "Opening inventory...", fg=(255, 255, 0))
					elif action.action_type == "open_character":
						if message_console:
							message_console.print(2, 5, "Opening character screen...", fg=(255, 255, 0))
            
	except Exception as e:
		print(f"Error: {e}")
	finally:
		display_manager.close()

if __name__ == "__main__":
	main()