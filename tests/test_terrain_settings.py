# tests/test_terrain_settings.py

import pytest
from src.world.terrain_settings import TerrainSettings, ErosionSettings

def test_erosion_settings_initialization():
    """Test that ErosionSettings initializes correctly with provided parameters."""
    erosion = ErosionSettings(
        droplets=1000,
        inertia=0.05,
        capacity=4.0,
        deposition=0.1,
        erosion=0.3,
        evaporation=0.02,
        min_slope=0.01
    )
    
    assert erosion.droplets == 1000
    assert erosion.inertia == 0.05
    assert erosion.capacity == 4.0
    assert erosion.deposition == 0.1
    assert erosion.erosion == 0.3
    assert erosion.evaporation == 0.02
    assert erosion.min_slope == 0.01

def test_erosion_settings_from_config():
    """Test creating ErosionSettings from a valid configuration dictionary."""
    config = {
        'droplets': 1500,
        'inertia': 0.07,
        'capacity': 5.0,
        'deposition': 0.15,
        'erosion': 0.35,
        'evaporation': 0.03,
        'min_slope': 0.02
    }
    erosion = ErosionSettings.from_config(config)
    
    assert erosion.droplets == 1500
    assert erosion.inertia == 0.07
    assert erosion.capacity == 5.0
    assert erosion.deposition == 0.15
    assert erosion.erosion == 0.35
    assert erosion.evaporation == 0.03
    assert erosion.min_slope == 0.02

def test_erosion_settings_from_config_missing_fields():
    """Test creating ErosionSettings from a configuration dictionary with missing fields."""
    config = {
        'droplets': 2000,
        'inertia': 0.06,
        # 'capacity' is missing
        'deposition': 0.2,
        'erosion': 0.4,
        'evaporation': 0.04,
        'min_slope': 0.03
    }
    
    with pytest.raises(KeyError) as exc_info:
        ErosionSettings.from_config(config)
    
    assert 'capacity' in str(exc_info.value)

def test_terrain_settings_initialization():
    """Test that TerrainSettings initializes correctly with provided parameters."""
    erosion = ErosionSettings(
        droplets=1000,
        inertia=0.05,
        capacity=4.0,
        deposition=0.1,
        erosion=0.3,
        evaporation=0.02,
        min_slope=0.01
    )
    
    terrain = TerrainSettings(
        width=128,
        height=128,
        octaves=6,
        persistence=0.5,
        lacunarity=2.0,
        scale=100.0,
        height_power=1.2,
        water_level=0.4,
        land_scale=0.3,
        seed=42,
        erosion=erosion
    )
    
    assert terrain.width == 128
    assert terrain.height == 128
    assert terrain.octaves == 6
    assert terrain.persistence == 0.5
    assert terrain.lacunarity == 2.0
    assert terrain.scale == 100.0
    assert terrain.height_power == 1.2
    assert terrain.water_level == 0.4
    assert terrain.land_scale == 0.3
    assert terrain.seed == 42
    assert terrain.erosion == erosion

def test_terrain_settings_from_config_full():
    """Test creating TerrainSettings from a complete configuration dictionary."""
    config = {
        'width': 256,
        'height': 256,
        'octaves': 8,
        'persistence': 0.6,
        'lacunarity': 2.5,
        'scale': 150.0,
        'height_power': 1.5,
        'water_level': 0.5,
        'land_scale': 0.35,
        'seed': 123,
        'erosion': {
            'droplets': 2000,
            'inertia': 0.06,
            'capacity': 5.0,
            'deposition': 0.2,
            'erosion': 0.4,
            'evaporation': 0.03,
            'min_slope': 0.02
        }
    }
    terrain = TerrainSettings.from_config(config)
    
    assert terrain.width == 256
    assert terrain.height == 256
    assert terrain.octaves == 8
    assert terrain.persistence == 0.6
    assert terrain.lacunarity == 2.5
    assert terrain.scale == 150.0
    assert terrain.height_power == 1.5
    assert terrain.water_level == 0.5
    assert terrain.land_scale == 0.35
    assert terrain.seed == 123
    assert terrain.erosion.droplets == 2000
    assert terrain.erosion.inertia == 0.06
    assert terrain.erosion.capacity == 5.0
    assert terrain.erosion.deposition == 0.2
    assert terrain.erosion.erosion == 0.4
    assert terrain.erosion.evaporation == 0.03
    assert terrain.erosion.min_slope == 0.02

def test_terrain_settings_from_config_partial_defaults():
    """Test creating TerrainSettings from a configuration dictionary with partial fields."""
    config = {
        'width': 128,
        'height': 128,
        'octaves': 5,
        'persistence': 0.55,
        'scale': 120.0
        # Missing lacunarity, height_power, water_level, land_scale, seed, and erosion
    }
    terrain = TerrainSettings.from_config(config)
    
    assert terrain.width == 128
    assert terrain.height == 128
    assert terrain.octaves == 5
    assert terrain.persistence == 0.55
    assert terrain.lacunarity == 2.0  # Default
    assert terrain.scale == 120.0
    assert terrain.height_power == 1.2  # Default
    assert terrain.water_level == 0.4  # Default
    assert terrain.land_scale == 0.3    # Default
    assert terrain.seed is None
    assert terrain.erosion is None

def test_terrain_settings_from_config_no_erosion():
    """Test creating TerrainSettings from a configuration dictionary without erosion settings."""
    config = {
        'width': 200,
        'height': 200,
        'octaves': 7,
        'persistence': 0.65,
        'lacunarity': 2.2,
        'scale': 130.0,
        'height_power': 1.3,
        'water_level': 0.45,
        'land_scale': 0.32,
        'seed': 789
        # No erosion settings
    }
    terrain = TerrainSettings.from_config(config)
    
    assert terrain.width == 200
    assert terrain.height == 200
    assert terrain.octaves == 7
    assert terrain.persistence == 0.65
    assert terrain.lacunarity == 2.2
    assert terrain.scale == 130.0
    assert terrain.height_power == 1.3
    assert terrain.water_level == 0.45
    assert terrain.land_scale == 0.32
    assert terrain.seed == 789
    assert terrain.erosion is None

def test_terrain_settings_from_config_invalid_config():
    """Test creating TerrainSettings from an invalid configuration dictionary."""
    config = {
        'width': 'not_an_int',  # Invalid type
        'height': 256,
        'octaves': 6,
        'persistence': 0.5,
        'lacunarity': 2.0,
        'scale': 100.0,
        'height_power': 1.2,
        'water_level': 0.4,
        'land_scale': 0.3,
        'seed': 42,
        'erosion': {
            'droplets': 1000,
            'inertia': 0.05,
            'capacity': 4.0,
            'deposition': 0.1,
            'erosion': 0.3,
            'evaporation': 0.02,
            'min_slope': 0.01
        }
    }

    with pytest.raises(TypeError) as exc_info:
        TerrainSettings.from_config(config)
    
    assert "width must be int" in str(exc_info.value)

def test_terrain_settings_default_values():
    """Test that TerrainSettings uses default values when not provided."""
    config = {}
    terrain = TerrainSettings.from_config(config)
    
    assert terrain.width == 256
    assert terrain.height == 256
    assert terrain.octaves == 6
    assert terrain.persistence == 0.5
    assert terrain.lacunarity == 2.0
    assert terrain.scale == 100.0
    assert terrain.height_power == 1.2
    assert terrain.water_level == 0.4
    assert terrain.land_scale == 0.3
    assert terrain.seed is None
    assert terrain.erosion is None

def test_terrain_settings_with_partial_erosion_config():
    """Test creating TerrainSettings with partial erosion configuration."""
    config = {
        'width': 150,
        'height': 150,
        'octaves': 4,
        'persistence': 0.5,
        'lacunarity': 2.0,
        'scale': 90.0,
        'erosion': {
            'droplets': 1200,
            # 'inertia' is missing
            'capacity': 3.5,
            'deposition': 0.2,
            'erosion': 0.25,
            'evaporation': 0.03,
            'min_slope': 0.015
        }
    }
    
    with pytest.raises(KeyError) as exc_info:
        TerrainSettings.from_config(config)
    
    assert 'inertia' in str(exc_info.value)