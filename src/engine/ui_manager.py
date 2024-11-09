# src/engine/ui_manager.py
from typing import Dict, Optional
import tcod
from .display_manager import DisplayManager
from .message_manager import MessageManager

class UIManager:
	"""Manages UI layout and rendering."""

	def __init__(self, display_manager: DisplayManager, message_manager: Optional[MessageManager] = None):
		self.display_manager = display_manager
		self.message_manager = message_manager
        
	def render_game_screen(self):
		"""Render the main game screen with all UI elements."""
		self.display_manager.clear_all()
		
		self._render_main_view()
		self._render_status_bar()
		self._render_minimap()
		self._render_message_log()
		
		# Render everything to the screen
		self.display_manager.render()
        
	def _render_main_view(self):
		"""Render the main game view."""
		console = self.display_manager.get_console("main")
		if console:
			# Note: console.print still takes (x,y) coordinates
			console.print(2, 1, "Welcome to Nihilis!", fg=(255, 223, 0))
			console.print(2, 3, "▲ Mountains", fg=(128, 128, 128))
			console.print(2, 4, "≈ Rivers", fg=(0, 148, 255))
			console.print(2, 5, "♠ Forests", fg=(0, 255, 0))
            
	def _render_status_bar(self):
		"""Render the status bar."""
		console = self.display_manager.get_console("status")
		if console:
			console.print(1, 1, "Status: Active", fg=(0, 255, 0))
			console.print(console.width - 20, 1, "HP: 100/100", fg=(255, 0, 0))
            
	def _render_minimap(self):
		"""Render the minimap."""
		console = self.display_manager.get_console("minimap")
		if console:
			# Draw frame without title
			console.draw_frame(0, 0, console.width, console.height)
			
			# Draw title manually
			title = " World Map "
			title_x = (console.width - len(title)) // 2  # Center the title
			console.print(title_x, 0, title, fg=(255, 255, 255))
			
			# Render terrain markers
			console.print(5, 5, "▲", fg=(128, 128, 128))
			console.print(7, 7, "≈", fg=(0, 148, 255))
			console.print(6, 9, "♠", fg=(0, 255, 0))
			
			# Debug print
			print("\nDebug - After rendering:")
			print(f"Forest character at [9,6]: {chr(console.ch[9,6])}")
			print(f"Forest character at [6,9]: {chr(console.ch[6,9])}")
            
	def _render_message_log(self):
		"""Render the message log."""
		console = self.display_manager.get_console("message_log")
		if console and self.message_manager:
			# Draw frame without title
			console.draw_frame(0, 0, console.width, console.height)
			
			# Draw title manually
			title = " Messages "
			title_x = (console.width - len(title)) // 2  # Center the title
			console.print(title_x, 0, title, fg=(255, 255, 255))
			
			# Render messages
			self.message_manager.render_messages(console)
			
			# Debug print
			print("\nDebug - Message Log Dimensions:")
			print(f"Console size: {console.width}x{console.height}")
			print(f"Frame corners: TL={chr(console.ch[0,0])}, BL={chr(console.ch[console.height-1,0])}")