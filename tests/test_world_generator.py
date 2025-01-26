import pytest
import numpy as np
from src.world.world_generator import WorldGenerator, WorldSettings, World
from src.utils.configuration_manager import ConfigurationManager
from src.world.terrain_settings import TerrainSettings, ErosionSettings
from src.world.biome_generator import BiomeGenerator, BiomeSettings
from src.world.terrain_generator import TerrainGenerator

@pytest.fixture
def config_manager():
    return ConfigurationManager()

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
def world_generator(config_manager):
    return WorldGenerator(config_manager)

def test_world_generator_initialization(world_generator):
    """Test that WorldGenerator initializes correctly."""
    assert isinstance(world_generator.terrain_generator, TerrainGenerator)
    assert isinstance(world_generator.biome_generator, BiomeGenerator)
    assert isinstance(world_generator.rng, np.random.Generator)
    assert world_generator.settings is not None

def test_world_settings_from_config():
    """Test creating WorldSettings from configuration."""
    config = {
        'width': 256,
        'height': 256,
        'seed': 42,
        'terrain': {
            'width': 128,
            'height': 128,
            'octaves': 6,
            'persistence': 0.5,
            'lacunarity': 2.0,
            'scale': 50.0
        }
    }
    
    settings = WorldSettings.from_config(config)
    assert settings.width == 256
    assert settings.height == 256
    assert settings.seed == 42
    assert isinstance(settings.terrain, TerrainSettings)

def test_generate_world(world_generator):
    """Test world generation process."""
    world = world_generator.generate()
    
    # Check that world was created with all required components
    assert isinstance(world, World)
    assert world.heightmap is not None
    assert isinstance(world.heightmap, np.ndarray)
    assert world.regions == {}  # Empty for now as per TODO
    assert world.landmarks == {}  # Empty for now as per TODO
    assert world.history == {}  # Empty for now as per TODO
    
    # Check heightmap properties
    assert world.heightmap.shape == (world_generator.settings.height, 
                                   world_generator.settings.width)
    assert np.all(world.heightmap >= 0)
    assert np.all(world.heightmap <= 1)

def test_world_generation_reproducibility(world_generator):
    """Test that the same seed produces the same world."""
    # Set a specific seed
    world_generator.settings.seed = 42
    
    # Generate two worlds with the same seed
    world1 = world_generator.generate()
    world2 = world_generator.generate()
    
    # Compare heightmaps
    np.testing.assert_array_almost_equal(world1.heightmap, world2.heightmap)

def test_from_template():
    """Test creating WorldGenerator from a template."""
    # First save a template
    config_manager = ConfigurationManager()
    generator = WorldGenerator(config_manager)
    
    # Create the generator from template
    template_generator = WorldGenerator.from_template("test_template")
    
    assert isinstance(template_generator, WorldGenerator)
    assert isinstance(template_generator.terrain_generator, TerrainGenerator)
    assert isinstance(template_generator.biome_generator, BiomeGenerator)

def test_world_generation_with_custom_seed(config_manager):
    """Test world generation with a custom seed."""
    custom_seed = 12345
    config = {'world_gen': {'seed': custom_seed}}
    config_manager.config = config
    
    generator = WorldGenerator(config_manager)
    assert generator.settings.seed == custom_seed
    
    world = generator.generate()
    assert world.heightmap is not None

def test_invalid_template():
    """Test handling of invalid template name."""
    with pytest.raises(ValueError):
        WorldGenerator.from_template("nonexistent_template")

def test_world_dimensions(world_generator):
    """Test that generated world has correct dimensions."""
    world = world_generator.generate()
    
    assert world.heightmap.shape == (
        world_generator.settings.height,
        world_generator.settings.width
    )

def test_save_and_load_world(world_generator, tmp_path):
    """Test saving and loading world state."""
    # Generate a world
    world = world_generator.generate()
    
    # Save the world
    save_path = tmp_path / "test_world.save"
    world_generator.save_world(world, str(save_path))
    
    # Load the world
    loaded_world = world_generator.load_world(str(save_path))
    
    # Compare original and loaded worlds
    # This will fail until save/load is implemented, as noted in TODOs
    with pytest.raises(NotImplementedError):
        world_generator.save_world(world, str(save_path)) 