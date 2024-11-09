# src/main.py

import tcod
from engine.display_manager import DisplayManager
from engine.input_handler import InputHandler, GameState
from utils.logger_config import logger

def main() -> None:
	"""Main game entry point."""
	display_manager = DisplayManager()
	input_handler = InputHandler(display_manager.context)
    
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
				# Add some sample messages with different colors
				message_console.print(2, 2, "You enter the region.", fg=(255, 255, 255))
				message_console.print(2, 3, "You see mountains.", fg=(192, 192, 192))
				message_console.print(2, 4, "A cool breeze blows.", fg=(128, 192, 255))
			
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
					elif action.action_type == "move":
						# Add movement info to message log
						if message_console:
							dx, dy = action.params["dx"], action.params["dy"]
							direction = ""
							if dy < 0: direction = "north"
							elif dy > 0: direction = "south"
							if dx < 0: direction = f"west{direction}"
							elif dx > 0: direction = f"east{direction}"
							
							sprint = "sprinting " if action.params.get("sprint") else ""
							message_console.print(
								2, 6, 
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