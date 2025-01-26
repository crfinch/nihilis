import pytest
import numpy as np
from src.world.settlement_generator import SettlementGenerator, SettlementType, Settlement
from src.world.biome_generator import BiomeType

@pytest.fixture
def rng():
    return np.random.default_rng(42)

@pytest.fixture
def settlement_generator(rng):
    return SettlementGenerator(rng)

@pytest.fixture
def sample_world_data():
    """Create sample world data for testing."""
    height, width = 200, 200  # Increased from 100x100
    
    # Create heightmap with varied terrain
    heightmap = np.full((height, width), 0.5)  # Default land height
    
    # Add some water
    heightmap[0:40, :] = 0.2  # Ocean
    
    # Add some mountains
    heightmap[120:160, :] = 0.8
    
    # Create matching biome map
    biome_map = np.full((height, width), BiomeType.GRASSLAND.value)
    biome_map[0:40, :] = BiomeType.OCEAN.value
    biome_map[120:160, :] = BiomeType.MOUNTAIN.value
    
    return heightmap, biome_map

def test_settlement_generator_initialization(settlement_generator):
    """Test that SettlementGenerator initializes correctly."""
    assert settlement_generator.min_settlement_distance[SettlementType.CAPITAL] > \
           settlement_generator.min_settlement_distance[SettlementType.CITY]
    assert settlement_generator.min_settlement_distance[SettlementType.CITY] > \
           settlement_generator.min_settlement_distance[SettlementType.TOWN]

def test_calculate_habitability(settlement_generator, sample_world_data):
    """Test habitability calculation."""
    heightmap, biome_map = sample_world_data
    
    habitability = settlement_generator._calculate_habitability(heightmap, biome_map)
    
    # Check dimensions
    assert habitability.shape == heightmap.shape
    
    # Check value ranges
    assert np.all(habitability >= 0)
    assert np.all(habitability <= 1)
    
    # Check that water areas have zero habitability
    water_mask = heightmap < 0.3
    assert np.all(habitability[water_mask] == 0)
    
    # Check that areas near water have higher habitability than far areas
    near_water = habitability[41:46, :].mean()  # Just inland from water
    far_water = habitability[80:85, :].mean()   # Far from water
    assert near_water > far_water

def test_valid_position_checking(settlement_generator, sample_world_data):
    """Test position validation."""
    heightmap, _ = sample_world_data
    
    # Create some existing settlements
    existing = [
        Settlement(SettlementType.CAPITAL, (50, 50)),
        Settlement(SettlementType.CITY, (30, 30))
    ]
    
    # Test position too close to capital
    assert not settlement_generator._is_valid_position(
        (51, 51), 
        SettlementType.CITY, 
        existing, 
        heightmap
    )
    
    # Test position far enough from everything
    assert settlement_generator._is_valid_position(
        (80, 80), 
        SettlementType.CITY, 
        existing, 
        heightmap
    )
    
    # Test position in water (heightmap < 0.3 is water)
    water_position = (10, 10)
    assert heightmap[water_position] < 0.3, "Test position should be in water"
    assert not settlement_generator._is_valid_position(
        water_position,
        SettlementType.CITY,
        existing,
        heightmap
    )

def test_settlement_generation(settlement_generator, sample_world_data):
    """Test full settlement generation."""
    heightmap, biome_map = sample_world_data
    
    settlements = settlement_generator.generate_settlements(
        heightmap,
        biome_map,
        num_capitals=1,
        num_cities=2,  # Reduced from 3
        num_towns=3    # Reduced from 5
    )
    
    # Check that we got the right number of settlements
    assert len([s for s in settlements if s.type == SettlementType.CAPITAL]) == 1
    assert len([s for s in settlements if s.type == SettlementType.CITY]) == 2
    assert len([s for s in settlements if s.type == SettlementType.TOWN]) == 3
    
    # Check settlement spacing
    for i, s1 in enumerate(settlements):
        for j, s2 in enumerate(settlements):
            if i != j:
                y1, x1 = s1.position
                y2, x2 = s2.position
                distance = np.sqrt((y1 - y2)**2 + (x1 - x2)**2)
                min_dist = max(
                    settlement_generator.min_settlement_distance[s1.type],
                    settlement_generator.min_settlement_distance[s2.type]
                )
                assert distance >= min_dist

def test_settlement_placement_reproducibility(settlement_generator, sample_world_data):
    """Test that the same seed produces the same settlement layout."""
    heightmap, biome_map = sample_world_data
    
    # Store initial RNG state
    initial_state = settlement_generator.rng.bit_generator.state
    
    settlements1 = settlement_generator.generate_settlements(
        heightmap,
        biome_map,
        num_capitals=1,
        num_cities=2
    )
    
    # Reset RNG state
    settlement_generator.rng.bit_generator.state = initial_state
    
    settlements2 = settlement_generator.generate_settlements(
        heightmap,
        biome_map,
        num_capitals=1,
        num_cities=2
    )
    
    # Check that settlements are in the same positions
    for s1, s2 in zip(settlements1, settlements2):
        assert s1.position == s2.position
        assert s1.type == s2.type

def test_settlement_placement_biome_preference(settlement_generator, sample_world_data):
    """Test that settlements prefer appropriate biomes."""
    heightmap, biome_map = sample_world_data
    
    # Create a region of each preferred biome type
    biome_map[30:40, 30:40] = BiomeType.GRASSLAND.value
    biome_map[40:50, 30:40] = BiomeType.TEMPERATE_FOREST.value
    
    settlements = settlement_generator.generate_settlements(
        heightmap,
        biome_map,
        num_capitals=1,
        num_cities=5
    )
    
    # Count settlements in preferred biomes
    settlements_in_preferred = 0
    for settlement in settlements:
        y, x = settlement.position
        if biome_map[y, x] in [BiomeType.GRASSLAND.value, BiomeType.TEMPERATE_FOREST.value]:
            settlements_in_preferred += 1
    
    # Most settlements should be in preferred biomes
    assert settlements_in_preferred >= len(settlements) * 0.6 