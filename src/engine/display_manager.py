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
    
	def __init__(self, message_manager: Optional['MessageManager'] = None, config_manager = None):
		"""Initialize the display manager and create console layers."""
		self.message_manager = message_manager
		
		# Get display configuration
		if config_manager:
			self.display_config = config_manager.get_display_config()
		else:
			# Fallback to default configuration
			from src.utils.configuration_manager import ConfigurationManager
			self.display_config = ConfigurationManager().get_display_config()
		
		# Modify the tileset loading section
		charmap = tcod.tileset.CHARMAP_CP437.copy()

		self.tileset = tcod.tileset.load_tilesheet(
			self.display_config.font_path,
			self.display_config.font_width,
			self.display_config.font_height,
			charmap
		)
		
		# Create the main window
		self.context = tcod.context.new(
			columns=self.display_config.screen_width,
			rows=self.display_config.screen_height,
			title="Nihilis",
			vsync=self.display_config.vsync,
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
			"message_log": tcod.console.Console(self.SIDEBAR_WIDTH, self.SCREEN_HEIGHT - self.MINIMAP_HEIGHT - self.STATUS_HEIGHT),
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
			dest_y=self.MINIMAP_HEIGHT,
			width=self.SIDEBAR_WIDTH,
			height=self.SCREEN_HEIGHT - self.MINIMAP_HEIGHT - self.STATUS_HEIGHT
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

