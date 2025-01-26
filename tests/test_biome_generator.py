import pytest
import numpy as np
from src.world.biome_generator import BiomeGenerator, BiomeSettings, BiomeType
from src.config.configuration_manager import ConfigurationManager

@pytest.fixture
def config_manager():
    config = {
        'world_gen': {
            'biomes': {
                'temperature_weight': 1.0,
                'precipitation_weight': 1.0,
                'altitude_weight': 1.0,
                'ocean_level': 0.4,
                'mountain_level': 0.7,
                'cold_thresh': 0.2,
                'temperate_thresh': 0.6,
                'dry_thresh': 0.2,
                'wet_thresh': 0.6
            }
        }
    }
    manager = ConfigurationManager()
    manager.config = config
    return manager

@pytest.fixture
def biome_generator(config_manager):
    return BiomeGenerator.from_config(config_manager)

def test_biome_generator_initialization(biome_generator, config_manager):
    """Test that BiomeGenerator initializes correctly."""
    assert biome_generator.settings == BiomeSettings.from_config(config_manager.config['world_gen']['biomes'])

def test_generate_temperature_map(biome_generator):
    """Test temperature map generation."""
    height, width = 100, 100
    seed = 42
    
    temp_map = biome_generator.generate_temperature_map(height, width, seed)
    
    # Check dimensions
    assert temp_map.shape == (height, width)
    
    # Check value ranges
    assert np.all(temp_map >= 0)
    assert np.all(temp_map <= 1)
    
    # Check latitude gradient (should be warmer at equator/bottom)
    assert np.mean(temp_map[height-10:]) > np.mean(temp_map[:10])

def test_generate_precipitation_map(biome_generator):
    """Test precipitation map generation."""
    height, width = 100, 100
    seed = 42
    
    # Create a test heightmap with some water bodies
    heightmap = np.random.rand(height, width)
    heightmap[40:60, 40:60] = 0.3  # Create a lake/ocean
    
    precip_map = biome_generator.generate_precipitation_map(heightmap, seed)
    
    # Check dimensions
    assert precip_map.shape == (height, width)
    
    # Check value ranges
    assert np.all(precip_map >= 0)
    assert np.all(precip_map <= 1)
    
    # Check that areas near water have higher precipitation
    water_mask = heightmap < biome_generator.settings.ocean_level
    near_water_precip = np.mean(precip_map[water_mask])
    far_water_precip = np.mean(precip_map[~water_mask])
    assert near_water_precip > far_water_precip

def test_assign_biomes(biome_generator):
    """Test biome assignment based on height, temperature, and precipitation."""
    height, width = 50, 50
    
    # Create test data
    heightmap = np.full((height, width), 0.5)  # Mid-level terrain
    temperature = np.full((height, width), 0.5)  # Temperate
    precipitation = np.full((height, width), 0.5)  # Moderate rainfall
    
    # Create specific test regions
    # Ocean
    heightmap[0:10, :] = 0.3
    
    # Mountains
    heightmap[10:20, :] = 0.8
    
    # Cold region
    temperature[20:30, :] = 0.1
    
    # Desert
    temperature[30:40, :] = 0.8
    precipitation[30:40, :] = 0.1
    
    # Rainforest
    temperature[40:50, :] = 0.8
    precipitation[40:50, :] = 0.8
    
    biome_map = biome_generator.assign_biomes(heightmap, temperature, precipitation)
    
    # Check dimensions
    assert biome_map.shape == (height, width)
    
    # Verify biome assignments
    assert BiomeType(biome_map[5, 5]).name == "OCEAN"  # Ocean region
    assert BiomeType(biome_map[15, 5]).name == "SNOW_PEAKS"  # Mountain region
    assert BiomeType(biome_map[25, 5]).name == "TUNDRA"  # Cold region
    assert BiomeType(biome_map[35, 5]).name == "DESERT"  # Desert region
    assert BiomeType(biome_map[45, 5]).name == "TROPICAL_RAINFOREST"  # Rainforest region

def test_biome_assignment_edge_cases(biome_generator):
    """Test biome assignment with edge cases and boundary values."""
    height, width = 10, 10
    
    # Create arrays with boundary values
    heightmap = np.full((height, width), biome_generator.settings.ocean_level)
    temperature = np.full((height, width), biome_generator.settings.cold_thresh)
    precipitation = np.full((height, width), biome_generator.settings.dry_thresh)
    
    biome_map = biome_generator.assign_biomes(heightmap, temperature, precipitation)
    
    # Test that boundary values are handled consistently
    assert np.all(biome_map >= min(b.value for b in BiomeType))
    assert np.all(biome_map <= max(b.value for b in BiomeType))

def test_reproducibility(biome_generator):
    """Test that the same seed produces the same results."""
    height, width = 50, 50
    seed = 42
    
    # Generate two temperature maps with the same seed
    temp_map1 = biome_generator.generate_temperature_map(height, width, seed)
    temp_map2 = biome_generator.generate_temperature_map(height, width, seed)
    
    # Generate two precipitation maps with the same seed
    heightmap = np.random.rand(height, width)
    precip_map1 = biome_generator.generate_precipitation_map(heightmap, seed)
    precip_map2 = biome_generator.generate_precipitation_map(heightmap, seed)
    
    # Check that both generations produced identical results
    np.testing.assert_array_equal(temp_map1, temp_map2)
    np.testing.assert_array_equal(precip_map1, precip_map2) 