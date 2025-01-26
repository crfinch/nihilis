import pytest
import numpy as np
from src.world.map_renderer import MapRenderer, TerrainSymbols
from src.world.biome_generator import BiomeType

@pytest.fixture
def map_renderer():
    return MapRenderer()

@pytest.fixture
def sample_world_data():
    """Create sample world data for testing."""
    height, width = 50, 50
    heightmap = np.full((height, width), 0.5)  # Mid-level terrain
    
    # Create specific test regions
    # Ocean (0.0-0.2)
    heightmap[0:10, :] = 0.1
    
    # Shallow water (0.2-0.4)
    heightmap[10:15, :] = 0.3
    
    # Beach (0.4-0.45)
    heightmap[15:20, :] = 0.42
    
    # Plains (0.45-0.6)
    heightmap[20:30, :] = 0.5
    
    # Hills (0.6-0.75)
    heightmap[30:35, :] = 0.7
    
    # Mountains (0.75-0.85)
    heightmap[35:40, :] = 0.8
    
    # Peaks (0.85-1.0)
    heightmap[40:45, :] = 0.9
    
    return {
        'heightmap': heightmap,
        'biome_map': None  # Optional for initial tests
    }

def test_terrain_symbols_initialization():
    """Test that terrain symbols are correctly defined."""
    symbols = TerrainSymbols()
    
    # Check frame characters match our UI tests
    # Reference: tests/test_ui_manager.py lines 109-116
    assert symbols.FRAME_TOP_LEFT == '┌'
    assert symbols.FRAME_TOP_RIGHT == '┐'
    assert symbols.FRAME_BOTTOM_LEFT == '└'
    assert symbols.FRAME_BOTTOM_RIGHT == '┘'
    assert symbols.FRAME_HORIZONTAL == '─'
    assert symbols.FRAME_VERTICAL == '│'
    
    # Check terrain characters match our UI tests
    # Reference: tests/test_ui_manager.py lines 48-51
    assert symbols.MOUNTAINS == '▲'
    assert symbols.DEEP_WATER == '≈'
    assert symbols.FOREST == '♠'

def test_get_terrain_symbol_height_based(map_renderer):
    """Test terrain symbol assignment based on height."""
    test_cases = [
        (0.1, None, map_renderer.symbols.DEEP_WATER),    # Deep ocean
        (0.3, None, map_renderer.symbols.SHALLOW_WATER), # Shallow water
        (0.42, None, map_renderer.symbols.BEACH),        # Beach
        (0.5, None, map_renderer.symbols.PLAINS),        # Plains
        (0.7, None, map_renderer.symbols.HILLS),         # Hills
        (0.8, None, map_renderer.symbols.MOUNTAINS),     # Mountains
        (0.9, None, map_renderer.symbols.PEAKS)          # Peaks
    ]
    
    for height, biome, expected in test_cases:
        symbol = map_renderer.get_terrain_symbol(height, biome)
        assert symbol == expected, f"Expected {expected} for height {height}, got {symbol}"

def test_get_terrain_symbol_biome_based(map_renderer):
    """Test terrain symbol assignment based on biome type."""
    test_cases = [
        (0.5, BiomeType.OCEAN, map_renderer.symbols.DEEP_WATER),
        (0.5, BiomeType.SHALLOW_OCEAN, map_renderer.symbols.SHALLOW_WATER),
        (0.5, BiomeType.BEACH, map_renderer.symbols.BEACH),
        (0.5, BiomeType.DESERT, map_renderer.symbols.DESERT),
        (0.5, BiomeType.TUNDRA, map_renderer.symbols.TUNDRA),
        (0.5, BiomeType.TEMPERATE_FOREST, map_renderer.symbols.FOREST),
        (0.5, BiomeType.MOUNTAIN, map_renderer.symbols.MOUNTAINS),
        (0.5, BiomeType.SNOW_PEAKS, map_renderer.symbols.PEAKS)
    ]
    
    for height, biome, expected in test_cases:
        symbol = map_renderer.get_terrain_symbol(height, biome)
        assert symbol == expected, f"Expected {expected} for biome {biome}, got {symbol}"

def test_render_world_map(map_renderer, sample_world_data):
    """Test world map rendering with compression."""
    width, height = 20, 15
    ascii_map = map_renderer.render_world_map(sample_world_data, width, height)
    
    # Check dimensions
    assert len(ascii_map) == height
    assert len(ascii_map[0]) == width
    
    # Check that different terrain types are represented
    symbols = set()
    for row in ascii_map:
        symbols.update(row)
    
    # Should have at least water, plains, and mountains
    assert map_renderer.symbols.DEEP_WATER in symbols
    assert map_renderer.symbols.PLAINS in symbols
    assert map_renderer.symbols.MOUNTAINS in symbols

def test_render_local_map(map_renderer, sample_world_data):
    """Test local map rendering."""
    center_pos = (25, 25)  # Center in plains region
    view_width, view_height = 10, 10
    
    ascii_map = map_renderer.render_local_map(
        sample_world_data, 
        center_pos,
        view_width,
        view_height
    )
    
    # Check dimensions
    assert len(ascii_map) == view_height
    assert len(ascii_map[0]) == view_width
    
    # Center should be plains
    center_y = view_height // 2
    center_x = view_width // 2
    assert ascii_map[center_y][center_x] == map_renderer.symbols.PLAINS

def test_add_frame(map_renderer):
    """Test adding frame to ASCII map."""
    test_map = [
        ['A', 'B', 'C'],
        ['D', 'E', 'F'],
        ['G', 'H', 'I']
    ]
    
    framed_map = map_renderer.add_frame(test_map)
    
    # Check dimensions
    assert len(framed_map) == len(test_map) + 2
    assert len(framed_map[0]) == len(test_map[0]) + 2
    
    # Check frame characters
    assert framed_map[0][0] == map_renderer.symbols.FRAME_TOP_LEFT
    assert framed_map[0][-1] == map_renderer.symbols.FRAME_TOP_RIGHT
    assert framed_map[-1][0] == map_renderer.symbols.FRAME_BOTTOM_LEFT
    assert framed_map[-1][-1] == map_renderer.symbols.FRAME_BOTTOM_RIGHT
    
    # Check content preservation
    assert framed_map[1][1] == 'A'
    assert framed_map[1][2] == 'B'
    assert framed_map[1][3] == 'C' 