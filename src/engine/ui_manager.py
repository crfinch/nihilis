# src/engine/ui_manager.py
from typing import Dict, Optional, Tuple, Set
import tcod
import time

from src.engine.display_manager import DisplayManager
from src.engine.message_manager import MessageManager
from src.utils.performance_monitor import PerformanceMonitor
from src.world.map_renderer import MapRenderer
from src.world.biome_type import BiomeType

class UIManager:
	"""Manages UI layout and rendering."""

	def __init__(self, display_manager: DisplayManager, message_manager=None, debug=False):
		self.display_manager = display_manager
		self.message_manager = message_manager
		self.map_renderer = MapRenderer()
		self.world_data = None
		self.debug = debug
		self.performance_monitor = None
		self.player = None
		self.use_los = True  # Can be toggled
		self.visible_positions: Set[Tuple[int, int]] = set()
        
	def set_world_data(self, world_data):
		"""Update the world data used for rendering maps."""
		print(f"Setting world data with {len(world_data.get('settlements', []))} settlements")
		self.world_data = world_data
        
	def set_performance_monitor(self, monitor):
		"""Set the performance monitor for debug information."""
		self.performance_monitor = monitor
        
	def set_player(self, player):
		"""Set the player character for rendering."""
		self.player = player
        
	def render_game_screen(self):
		"""Render the main game screen with all UI elements."""
		# render_start = time.perf_counter()
		
		self.display_manager.clear_all()
		
		self._render_main_view()
		self._render_status_bar()
		self._render_minimap()
		self._render_message_log()
		
		# Render everything to the screen
		self.display_manager.render()
		
		# render_time = time.perf_counter() - render_start
		# if render_time > 0.016:  # Longer than 16ms
			# print(f"Long UI render time: {render_time*1000:.1f}ms")
        
	def _render_main_view(self):
		"""Render the main game view."""
		console = self.display_manager.get_console("main")
		if not console or not self.world_data or not self.player:
			return
			
		# Get the console dimensions (excluding a 1-cell border)
		view_width = console.width - 2
		view_height = console.height - 2
		
		# Get the player's current position
		center_pos = (int(self.player.y), int(self.player.x))
		
		# Render the local map centered on the player
		ascii_map, biome_info = self.map_renderer.render_local_map(
			self.world_data,
			center_pos,
			view_width,
			view_height
		)
		
		# Calculate visible positions if LOS is enabled
		if self.use_los:
			# Since the local map is centered on the player, they will be at the center of the view
			view_center = (view_height // 2, view_width // 2)
			self.visible_positions = self.map_renderer.calculate_los(
				ascii_map,
				view_center,  # Player is at the center of the view
				view_height,
				view_width
			)
		
		# Draw frame around the map
		console.draw_frame(0, 0, console.width, console.height, title=" World View ")
		
		# Draw the map to the console
		for y in range(len(ascii_map)):
			for x in range(len(ascii_map[0])):
				# Skip if position is not visible and LOS is enabled
				if self.use_los and (y, x) not in self.visible_positions:
					console.print(x+1, y+1, ' ', fg=(0, 0, 0))
					continue
				
				symbol = ascii_map[y][x]
				# Get biome type from the biome_info dictionary
				biome_type = biome_info.get(f"{y},{x}")
				
				# Draw the character with appropriate color
				if symbol == self.player.char:
					# Draw player in white
					console.print(x+1, y+1, symbol, fg=(255, 255, 255))
				else:
					color = self._get_terrain_color(symbol, biome_type)
					console.print(x+1, y+1, symbol, fg=color)
            
	def _render_status_bar(self):
		"""Render the status bar with optional performance metrics."""
		console = self.display_manager.get_console("status")
		if console:
			# Status indicator
			console.print(1, 1, "Status: Active", fg=(0, 255, 0))
			
			# Get current biome if world data and player exist
			current_biome = "Unknown"
			current_location = None
			if self.world_data and self.player:
				# Get biome information
				biome_map = self.world_data.get('biome_map')
				if biome_map is not None:
					# Get biome at player position
					player_y, player_x = int(self.player.y), int(self.player.x)
					if 0 <= player_y < biome_map.shape[0] and 0 <= player_x < biome_map.shape[1]:
						biome_value = biome_map[player_y, player_x]
						current_biome = BiomeType(biome_value).name.replace('_', ' ').title()
				
				# Debug print for settlements
				settlements = self.world_data.get('settlements', [])
				
				# Check for settlements/POIs at player position
				for settlement in settlements:
					# Debug print for position comparison
					if hasattr(settlement, 'position'):
						settlement_y, settlement_x = settlement.position
						if (int(settlement_y) == int(self.player.y) and 
							int(settlement_x) == int(self.player.x)):
							current_location = settlement
							break
			
			# Construct status text
			status_text = f"Biome: {current_biome}"
			if current_location:
				try:
					location_type = current_location.type.name.replace('_', ' ').title()
					location_name = current_location.name if current_location.name else ""
					status_text += f" | {location_type}"
					if location_name != "Unnamed":
						status_text += f": {location_name}"
				except Exception as e:
					print(f"Error formatting location: {e}")
			
			# Print status text in the middle
			status_x = (console.width - len(status_text)) // 2
			console.print(status_x, 1, status_text, fg=(255, 255, 255))
			
			# HP display on the right
			console.print(console.width - 20, 1, "HP: 100/100", fg=(255, 0, 0))
			
			# Add performance metrics in debug mode
			if self.debug and self.performance_monitor:
				metrics = self.performance_monitor.get_performance_summary()
				fps_text = f"FPS: {metrics['fps']:.1f}"
				console.print(console.width - 45, 1, fps_text, fg=(255, 255, 0))
            
	def _render_minimap(self):
		"""Render the world map in minimap console."""
		console = self.display_manager.get_console("minimap")
		if not console or not self.world_data:
			return
			
		# Get console dimensions (excluding frame)
		map_width = console.width - 2
		map_height = console.height - 2
		
		# Create a complete world data dictionary including settlements
		render_data = {
			'heightmap': self.world_data.get('heightmap'),
			'biome_map': self.world_data.get('biome_map'),
			'settlements': self.world_data.get('settlements', []),
			'discovery_mask': self.world_data.get('discovery_mask')
		}
		
		# Render the world map with player
		ascii_map, biome_info = self.map_renderer.render_world_map(
			render_data,
			map_width,
			map_height,
			render_data['discovery_mask'],
			self.player
		)
		
		# Add frame
		framed_map = self.map_renderer.add_frame(ascii_map)
		
		# Draw title
		title = " World Map "
		title_x = (console.width - len(title)) // 2
		console.print(title_x, 0, title, fg=(255, 255, 255))
		
		# Draw the map with appropriate colors
		for y in range(len(framed_map)):
			for x in range(len(framed_map[0])):
				char = framed_map[y][x]
				# Get biome type for this position
				biome_type = biome_info.get(f"{y},{x}")
				# Set colors based on terrain type
				fg = self._get_terrain_color(char, biome_type)
				console.print(x, y, char, fg=fg)
            
	def _get_terrain_color(self, char: str, biome_type: Optional[BiomeType] = None) -> Tuple[int, int, int]:
		"""Get the color for a terrain or settlement symbol."""
		# Special case for forests in cold biomes
		if char == '♠' and biome_type in [BiomeType.TUNDRA, BiomeType.COLD_DESERT]:
			return (200, 200, 200)  # White-ish trees for cold forests
		if char == '^' and biome_type in [BiomeType.TEMPERATE_FOREST, BiomeType.TEMPERATE_RAINFOREST, BiomeType.TROPICAL_RAINFOREST]:
			return (139, 69, 19)  # Brown earthy mountains for warm forests
		
		TERRAIN_COLORS = {
			'≈': (0, 148, 255),    # Deep water (blue)
			'~': (65, 185, 255),   # Shallow water (light blue)
			'.': (100, 220, 100),  # Plains (green)
			chr(239): (160, 160, 160),  # Hills (gray)
			'^': (128, 128, 128),  # Mountains (dark gray)
			'▲': (200, 200, 200),  # Peaks (light gray)
			'♠': (0, 180, 0),      # Forest (dark green)
			'∙': (255, 255, 150),  # Desert (yellow)
			',': (200, 200, 200),  # Tundra (white)
			':': (255, 240, 150),  # Beach (sand)
			'?': (100, 100, 100),  # Unknown (dark gray)
			'*': (255, 215, 0),    # Capital city (gold)
			'■': (220, 220, 220),  # Major city (light gray)
			'□': (180, 180, 180),  # Minor city (darker gray)
			'@': (255, 128, 255),  # Player character (lavender)
			# Frame characters
			'┌': (255, 255, 255),  # White
			'┐': (255, 255, 255),
			'└': (255, 255, 255),
			'┘': (255, 255, 255),
			'─': (255, 255, 255),
			'│': (255, 255, 255),
		}
		return TERRAIN_COLORS.get(char, (255, 255, 255))
            
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

	def toggle_los(self):
		"""Toggle line of sight rendering."""
		self.use_los = not self.use_los
