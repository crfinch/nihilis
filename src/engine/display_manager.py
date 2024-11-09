# src/engine/display_manager.py

import tcod
from typing import Dict, Optional
from .message_manager import MessageManager


class DisplayManager:
	"""Manages the game's display windows and rendering."""

	# Window dimensions - adjusted for larger tileset
	# Since the font is 10x16, we'll reduce cell counts to maintain similar pixel dimensions
	SCREEN_WIDTH = 80  # Reduced from 100 to account for larger tiles
	SCREEN_HEIGHT = 50  # Reduced from 60 to account for larger tiles

	# UI component dimensions
	STATUS_HEIGHT = 3
	SIDEBAR_WIDTH = 25  # Reduced from 30 to account for larger tiles
	MINIMAP_HEIGHT = 25  # Reduced from 30 to account for larger tiles
    
	def __init__(self, message_manager: Optional['MessageManager'] = None):
		"""Initialize the display manager and create console layers."""
		# Load the tileset
		self.tileset = tcod.tileset.load_tilesheet(
			"resources/fonts/terminal16x16_gs_ro.png", 16, 16, tcod.tileset.CHARMAP_CP437
		)
		
		# initialize the message manager reference.
		self.message_manager = message_manager
			
			# Create the main window
		self.context = tcod.context.new(
			columns=self.SCREEN_WIDTH,
			rows=self.SCREEN_HEIGHT,
			title="Nihilis",
			vsync=True,
			sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE,
			tileset=self.tileset
			)

			# Verify context initialization
		if not self.context:
			raise RuntimeError("Failed to initialize TCOD context")
		
		# Create console layers
		self.consoles: Dict[str, tcod.console.Console] = {
			"main": tcod.console.Console(self.SCREEN_WIDTH - self.SIDEBAR_WIDTH, self.SCREEN_HEIGHT - self.STATUS_HEIGHT),
			"status": tcod.console.Console(self.SCREEN_WIDTH, self.STATUS_HEIGHT),
			"message_log": tcod.console.Console(self.SIDEBAR_WIDTH, self.SCREEN_HEIGHT - self.MINIMAP_HEIGHT),
			"minimap": tcod.console.Console(self.SIDEBAR_WIDTH, self.MINIMAP_HEIGHT)
		}
			
			# Create root console
		self.root_console = tcod.console.Console(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)



	def render(self) -> None:

		"""Render all console layers to the screen."""
		# Clear the root console
		self.root_console.clear()
    
		# Blit all console layers to the root console using modern syntax
		# Main game view
		self.consoles["main"].blit(
			dest=self.root_console,
			dest_x=0,
			dest_y=0
		)

		# Status bar at bottom
		self.consoles["status"].blit(
			dest=self.root_console,
			dest_x=0,
			dest_y=self.SCREEN_HEIGHT - self.STATUS_HEIGHT
		)
    
		# Message log on right
		self.consoles["message_log"].blit(
			dest=self.root_console,
			dest_x=self.SCREEN_WIDTH - self.SIDEBAR_WIDTH,
			dest_y=self.MINIMAP_HEIGHT
		)
    
		# Minimap in top-right
		self.consoles["minimap"].blit(
			dest=self.root_console,
			dest_x=self.SCREEN_WIDTH - self.SIDEBAR_WIDTH,
			dest_y=0
		)
    
		# Present the root console to the screen
		self.context.present(self.root_console)
    
	def clear_all(self) -> None:
		"""Clear all console layers."""
		for console in self.consoles.values():
			console.clear()
		self.root_console.clear()
    
	def get_console(self, name: str) -> Optional[tcod.console.Console]:
		"""Get a specific console layer by name."""
		return self.consoles.get(name)
    
	def close(self) -> None:
		"""Clean up and close the display."""
		self.context.close()

