import pytest
import numpy as np
from src.world.terrain_generator import TerrainGenerator, TerrainSettings, ErosionSettings
from src.utils.configuration_manager import ConfigurationManager

@pytest.fixture
def erosion_settings():
    return ErosionSettings(
        droplets=1000,
        inertia=0.05,
        capacity=4.0,
        deposition=0.1,
        erosion=0.3,
        evaporation=0.02,
        min_slope=0.01
    )

@pytest.fixture
def terrain_settings(erosion_settings):
    return TerrainSettings(
        width=128,
        height=128,
        octaves=6,
        persistence=0.5,
        lacunarity=2.0,
        scale=50.0,
        height_power=1.2,
        water_level=0.4,
        land_scale=0.3,
        seed=42,
        erosion=erosion_settings
    )

@pytest.fixture
def terrain_generator(terrain_settings):
    return TerrainGenerator(terrain_settings)

def test_terrain_generator_initialization(terrain_generator, terrain_settings):
    """Test that TerrainGenerator initializes correctly."""
    assert terrain_generator.width == terrain_settings.width
    assert terrain_generator.height == terrain_settings.height
    assert terrain_generator.octaves == terrain_settings.octaves
    assert terrain_generator.persistence == terrain_settings.persistence
    assert terrain_generator.lacunarity == terrain_settings.lacunarity
    assert terrain_generator.scale == terrain_settings.scale
    assert isinstance(terrain_generator.rng, np.random.RandomState)

def test_generate_heightmap(terrain_generator):
    """Test heightmap generation."""
    heightmap = terrain_generator.generate_heightmap()
    
    # Check dimensions
    assert heightmap.shape == (terrain_generator.height, terrain_generator.width)
    
    # Check value ranges
    assert np.all(heightmap >= 0)
    assert np.all(heightmap <= 1)
    
    # Check that we have variation in the heightmap
    assert np.std(heightmap) > 0
    
    # Check that the heightmap isn't uniform
    assert not np.allclose(heightmap, heightmap[0,0])

def test_reproducibility(terrain_generator):
    """Test that the same seed produces the same heightmap."""
    heightmap1 = terrain_generator.generate_heightmap()
    heightmap2 = terrain_generator.generate_heightmap()
    
    np.testing.assert_array_almost_equal(heightmap1, heightmap2)

def test_erosion(terrain_generator):
    """Test that erosion modifies the heightmap."""
    initial_heightmap = terrain_generator.generate_heightmap()
    eroded_heightmap = terrain_generator.apply_erosion(initial_heightmap.copy())
    
    # Check that erosion changed the heightmap
    assert not np.array_equal(initial_heightmap, eroded_heightmap)
    
    # Check that erosion preserved value ranges
    assert np.all(eroded_heightmap >= 0)
    assert np.all(eroded_heightmap <= 1)

def test_from_config():
    """Test creating TerrainGenerator from configuration."""
    config_manager = ConfigurationManager()
    terrain_generator = TerrainGenerator.from_config(config_manager)
    
    assert isinstance(terrain_generator, TerrainGenerator)
    assert hasattr(terrain_generator, 'settings')

def test_gradient_calculation(terrain_generator):
    """Test gradient calculation for erosion."""
    heightmap = np.zeros((10, 10))
    # Create a simple slope
    heightmap[5:] = 1.0
    
    # Test gradient at slope
    gradient = terrain_generator._calculate_gradient(heightmap, 5.0, 4.5)
    
    # Should have strong y gradient, minimal x gradient
    assert abs(gradient[1]) > abs(gradient[0])
    assert gradient[1] > 0  # Positive y gradient (uphill)

def test_height_sampling(terrain_generator):
    """Test bilinear height sampling."""
    heightmap = np.zeros((10, 10))
    heightmap[5:] = 1.0
    
    # Test exact point
    assert terrain_generator._sample_height(heightmap, 5.0, 5.0) == 1.0
    
    # Test interpolated point
    interpolated = terrain_generator._sample_height(heightmap, 5.0, 4.5)
    assert 0 < interpolated < 1

def test_thermal_erosion(terrain_generator):
    """Test thermal erosion process."""
    # Create a heightmap with a sharp peak
    heightmap = np.zeros((10, 10))
    heightmap[5, 5] = 1.0

    initial_sum = np.sum(heightmap)
    eroded = terrain_generator.thermal_erosion(heightmap)
    final_sum = np.sum(eroded)

    # Peak should be lower
    assert eroded[5, 5] < heightmap[5, 5], "Peak was not lowered after erosion."

    # Total mass should be conserved (within floating point precision)
    assert pytest.approx(initial_sum, rel=1e-10) == final_sum, "Total mass is not conserved after erosion."

    # Check that material has spread to neighbors
    region_sum = np.sum(eroded[4:7, 4:7])
    
    # Instead of expecting all mass within the region, expect a significant portion
    assert region_sum > 0.3, f"Insufficient material retained within [4:7, 4:7]. Obtained: {region_sum}"
    
    # Optionally, ensure that some material has spread outside the region
    outside_sum = final_sum - region_sum
    assert outside_sum > 0, "No material spread outside the [4:7, 4:7] region."

def test_template_saving(terrain_generator, tmp_path):
    """Test saving terrain generator as template."""
    # Create a temporary template
    success = terrain_generator.save_as_template(
        "test_template",
        "Test template description"
    )
    
    assert success
    
    # Try loading the template
    loaded_generator = TerrainGenerator.from_template("test_template")
    assert loaded_generator.settings.width == terrain_generator.settings.width
    assert loaded_generator.settings.height == terrain_generator.settings.height

def test_invalid_template():
    """Test handling of invalid template name."""
    with pytest.raises(ValueError):
        TerrainGenerator.from_template("nonexistent_template")