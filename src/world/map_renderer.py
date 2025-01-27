from enum import Enum
from typing import Dict, Optional, Tuple
import numpy as np
from src.world.biome_generator import BiomeType
from src.world.settlement_generator import SettlementType

class TerrainSymbols:
    """ASCII symbols for different terrain features."""
    DEEP_WATER = '≈'    # Deep ocean
    SHALLOW_WATER = '~' # Shallow water
    PLAINS = '.'        # Plains/grassland
    HILLS = '∩'         # Hills
    MOUNTAINS = '^'     # Mountains
    PEAKS = '▲'         # Mountain peaks '△'
    FOREST = '♠'        # Forest
    DESERT = '∙'        # Desert
    TUNDRA = ','       # Tundra/snow '⚬'
    UNKNOWN = '?'       # Unexplored areas
    BEACH = ':'         # Beach/shore
    CAPITAL = '*'      # Capital city 
    CITY = '■'         # Major city 
    TOWN = '□'         # Minor city 
    VILLAGE = '○'      # Village
    RUINS = '∅'        # Ruins
    DUNGEON = '◊'      # Dungeon
    TEMPLE = '†'       # Temple
    FORTRESS = '▣'     # Fortress

    # Frame characters
    FRAME_TOP_LEFT = '┌'
    FRAME_TOP_RIGHT = '┐'
    FRAME_BOTTOM_LEFT = '└'
    FRAME_BOTTOM_RIGHT = '┘'
    FRAME_HORIZONTAL = '─'
    FRAME_VERTICAL = '│'

class MapRenderer:
    def __init__(self):
        self.symbols = TerrainSymbols()
        
    def get_terrain_symbol(self, height: float, biome_type: Optional[BiomeType] = None) -> str:
        """Convert height and biome data into an ASCII symbol."""
        # If we have biome data, use that first
        if biome_type is not None:
            if biome_type == BiomeType.OCEAN:
                return self.symbols.DEEP_WATER
            elif biome_type == BiomeType.SHALLOW_OCEAN:
                return self.symbols.SHALLOW_WATER
            elif biome_type == BiomeType.BEACH:
                return self.symbols.BEACH
            elif biome_type == BiomeType.DESERT:
                return self.symbols.DESERT
            elif biome_type in [BiomeType.TUNDRA, BiomeType.COLD_DESERT]:
                return self.symbols.TUNDRA
            elif biome_type in [BiomeType.TEMPERATE_FOREST, BiomeType.TROPICAL_RAINFOREST, BiomeType.TEMPERATE_RAINFOREST]:
                return self.symbols.FOREST
            elif biome_type == BiomeType.MOUNTAIN:
                return self.symbols.MOUNTAINS
            elif biome_type == BiomeType.SNOW_PEAKS:
                return self.symbols.PEAKS
            elif biome_type == BiomeType.SAVANNA:
                return self.symbols.PLAINS  # Using plains symbol for savanna
            elif biome_type == BiomeType.GRASSLAND:
                return self.symbols.PLAINS
            # Add other biome cases as needed
        
        # Fall back to height-based terrain if no biome data or no match
        if height < 0.2:
            return self.symbols.DEEP_WATER
        elif height < 0.35:
            return self.symbols.SHALLOW_WATER
        elif height < 0.4:
            return self.symbols.BEACH
        elif height < 0.6:
            return self.symbols.PLAINS
        elif height < 0.75:
            return self.symbols.HILLS
        elif height < 0.85:
            return self.symbols.MOUNTAINS
        return self.symbols.PEAKS

    def render_world_map(self, world_data: Dict, width: int, height: int, 
                        discovery_mask: Optional[np.ndarray] = None,
                        player = None) -> tuple[list[list[str]], dict]:
        """Render the world map at the specified dimensions."""
        heightmap = world_data['heightmap']
        biome_map = world_data.get('biome_map')
        settlements = world_data.get('settlements', [])
    
        # Calculate compression ratios and zoom level
        y_ratio = heightmap.shape[0] / height
        x_ratio = heightmap.shape[1] / width
        zoom_level = max(y_ratio, x_ratio)  # Higher ratio means more zoomed out
        
        # Initialize the ASCII map and biome info
        ascii_map = [['' for _ in range(width)] for _ in range(height)]
        biome_info = {}  # Store biome info for each position
        
        for y in range(height):
            for x in range(width):
                # Skip if not discovered and discovery_mask is provided
                if discovery_mask is not None and not discovery_mask[y, x]:
                    ascii_map[y][x] = self.symbols.UNKNOWN
                    continue
                
                # Calculate the region of original map this pixel represents
                y_start = int(y * y_ratio)
                y_end = int((y + 1) * y_ratio)
                x_start = int(x * x_ratio)
                x_end = int((x + 1) * x_ratio)
                
                # Take the most common biome in this region
                if biome_map is not None:
                    region_biomes = biome_map[y_start:y_end, x_start:x_end]
                    unique_biomes, counts = np.unique(region_biomes, return_counts=True)
                    dominant_biome = unique_biomes[np.argmax(counts)]
                    height_val = np.mean(heightmap[y_start:y_end, x_start:x_end])
                    biome_type = BiomeType(dominant_biome)
                    ascii_map[y][x] = self.get_terrain_symbol(height_val, biome_type)
                    biome_info[f"{y},{x}"] = biome_type
                else:
                    height_val = np.mean(heightmap[y_start:y_end, x_start:x_end])
                    ascii_map[y][x] = self.get_terrain_symbol(height_val)
        
        # Add settlements on top of terrain, sorted by importance
        if settlements:
            # Sort settlements by type priority
            type_priority = {
                SettlementType.CAPITAL: 0,
                SettlementType.CITY: 1,
                SettlementType.TOWN: 2,
                SettlementType.FORTRESS: 3,
                SettlementType.TEMPLE: 4,
                SettlementType.RUINS: 5,
                SettlementType.VILLAGE: 6,
                SettlementType.DUNGEON: 7
            }
            
            sorted_settlements = sorted(settlements, key=lambda s: type_priority[s.type])
            
            # Filter settlements based on zoom level
            for settlement in sorted_settlements:
                # Skip settlements based on zoom level
                if zoom_level > 4:  # Very zoomed out
                    if settlement.type not in [SettlementType.CAPITAL, SettlementType.CITY]:
                        continue
                elif zoom_level > 2:  # Moderately zoomed out
                    if settlement.type in [SettlementType.VILLAGE, SettlementType.DUNGEON]:
                        continue
                elif zoom_level > 1.5:  # Slightly zoomed out
                    if settlement.type in [SettlementType.RUINS]:
                        continue
                
                # Scale settlement position to map coordinates
                map_y = int(settlement.position[0] / heightmap.shape[0] * height)
                map_x = int(settlement.position[1] / heightmap.shape[1] * width)
                
                # Ensure position is within bounds
                if 0 <= map_y < height and 0 <= map_x < width:
                    # Get the appropriate symbol based on settlement type
                    symbol = getattr(self.symbols, settlement.type.name)
                    ascii_map[map_y][map_x] = symbol
        
        # Add player character on top of everything else if provided
        if player is not None:
            # Scale player position to map coordinates
            map_y = int(player.y / heightmap.shape[0] * height)
            map_x = int(player.x / heightmap.shape[1] * width)
            
            # Ensure position is within bounds
            if 0 <= map_y < height and 0 <= map_x < width:
                ascii_map[map_y][map_x] = player.char
        
        return ascii_map, biome_info

    def render_local_map(self, world_data: Dict, 
                        center_pos: Tuple[int, int], 
                        view_width: int, view_height: int) -> tuple[list[list[str]], dict]:
        """Render a local area map centered on the given position."""
        heightmap = world_data['heightmap']
        biome_map = world_data.get('biome_map')
        settlements = world_data.get('settlements', [])
        
        # Calculate view boundaries
        y_center, x_center = center_pos
        y_start = max(0, y_center - view_height // 2)
        y_end = min(heightmap.shape[0], y_center + view_height // 2)
        x_start = max(0, x_center - view_width // 2)
        x_end = min(heightmap.shape[1], x_center + view_width // 2)
        
        # Initialize the ASCII map and biome info
        ascii_map = [[self.symbols.UNKNOWN for _ in range(view_width)] 
                    for _ in range(view_height)]
        biome_info = {}  # Store biome info for each position
        
        # Fill in the visible area
        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                map_y = y - y_start
                map_x = x - x_start
                
                height_val = heightmap[y, x]
                if biome_map is not None:
                    biome_type = BiomeType(biome_map[y, x])
                    ascii_map[map_y][map_x] = self.get_terrain_symbol(height_val, biome_type)
                    biome_info[f"{map_y},{map_x}"] = biome_type
                else:
                    ascii_map[map_y][map_x] = self.get_terrain_symbol(height_val)
        
        # Add settlements that are within view
        for settlement in settlements:
            # Convert settlement position to map coordinates
            map_y = settlement.position[0] - y_start
            map_x = settlement.position[1] - x_start
            
            # Only draw if within view bounds
            if 0 <= map_y < view_height and 0 <= map_x < view_width:
                # Get the appropriate symbol based on settlement type
                symbol = getattr(self.symbols, settlement.type.name)
                ascii_map[map_y][map_x] = symbol
        
        # Place player at center (on top of everything else)
        center_y = view_height // 2
        center_x = view_width // 2
        if 0 <= center_y < len(ascii_map) and 0 <= center_x < len(ascii_map[0]):
            ascii_map[center_y][center_x] = '@'
        
        return ascii_map, biome_info

    def add_frame(self, ascii_map: list[list[str]]) -> list[list[str]]:
        """Add a frame around the ASCII map."""
        height = len(ascii_map)
        width = len(ascii_map[0])
        
        # Create new map with frame
        framed_map = [[' ' for _ in range(width + 2)] for _ in range(height + 2)]
        
        # Add corners
        framed_map[0][0] = self.symbols.FRAME_TOP_LEFT
        framed_map[0][width + 1] = self.symbols.FRAME_TOP_RIGHT
        framed_map[height + 1][0] = self.symbols.FRAME_BOTTOM_LEFT
        framed_map[height + 1][width + 1] = self.symbols.FRAME_BOTTOM_RIGHT
        
        # Add horizontal borders
        for x in range(1, width + 1):
            framed_map[0][x] = self.symbols.FRAME_HORIZONTAL
            framed_map[height + 1][x] = self.symbols.FRAME_HORIZONTAL
        
        # Add vertical borders
        for y in range(1, height + 1):
            framed_map[y][0] = self.symbols.FRAME_VERTICAL
            framed_map[y][width + 1] = self.symbols.FRAME_VERTICAL
        
        # Copy the map contents
        for y in range(height):
            for x in range(width):
                framed_map[y + 1][x + 1] = ascii_map[y][x]
        
        return framed_map 

    def _get_settlement_color(self, settlement_type: SettlementType) -> Tuple[int, int, int]:
        """Return the color for a settlement type."""
        SETTLEMENT_COLORS = {
            SettlementType.CAPITAL: (255, 215, 0),     # Gold
            SettlementType.CITY: (255, 255, 255),      # White
            SettlementType.TOWN: (192, 192, 192),      # Silver
            SettlementType.VILLAGE: (139, 139, 139),   # Gray
            SettlementType.RUINS: (139, 69, 19),       # Brown
            SettlementType.DUNGEON: (148, 0, 211),     # Purple
            SettlementType.TEMPLE: (218, 165, 32),     # Golden Rod
            SettlementType.FORTRESS: (178, 34, 34)     # Firebrick Red
        }
        return SETTLEMENT_COLORS.get(settlement_type, (255, 255, 255)) 