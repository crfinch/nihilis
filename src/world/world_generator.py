# src/world/world_generator.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np

from src.world.terrain_generator import TerrainGenerator
from src.world.terrain_settings import TerrainSettings
from src.utils.configuration_manager import ConfigurationManager

@dataclass
class WorldSettings:
    """Settings for world generation."""
    width: int
    height: int
    seed: Optional[int]
    terrain: TerrainSettings
    
    @classmethod
    def from_config(cls, config: dict) -> 'WorldSettings':
        terrain_config = config.get('terrain', {})
        return cls(
            width=config.get('width', 256),
            height=config.get('height', 256),
            seed=config.get('seed'),
            terrain=TerrainSettings.from_config(terrain_config)
        )

class World:
    """Represents a generated world with all its components."""
    def __init__(self):
        self.heightmap: Optional[np.ndarray] = None
        self.regions: Dict[str, Any] = {}
        self.landmarks: Dict[str, Any] = {}
        self.history: Dict[str, Any] = {}

class WorldGenerator:
    """Handles the generation of the entire world."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        world_gen_config = config_manager.config.get('world_gen', {})
        self.settings = WorldSettings.from_config(world_gen_config)
        
        # Initialize sub-generators
        self.terrain_generator = TerrainGenerator(self.settings.terrain)
        
        # Set RNG
        if self.settings.seed is None:
            self.settings.seed = np.random.randint(0, 2**32 - 1)
        self.rng = np.random.default_rng(self.settings.seed)
    
    def generate(self) -> World:
        """Generate a complete world."""
        world = World()
        
        # Generate base terrain
        world.heightmap = self.terrain_generator.generate_heightmap()
        
        # Apply erosion
        world.heightmap = self.terrain_generator.apply_erosion(world.heightmap)
        
        # TODO: Future steps will include:
        # - Climate generation
        # - Biome assignment
        # - Region partitioning
        # - Landmark placement
        # - Historical event generation
        
        return world
    
    def save_world(self, world: World, filepath: str):
        """Save the generated world to disk."""
        # TODO: Implement world saving
        pass
    
    def load_world(self, filepath: str) -> World:
        """Load a world from disk."""
        # TODO: Implement world loading
        pass
    
    @classmethod
    def from_template(cls, template_name: str) -> 'WorldGenerator':
        """Create a WorldGenerator instance from a terrain template."""
        # Create a minimal config manager for non-terrain settings
        config_manager = ConfigurationManager()
        
        # Create the terrain generator from template
        terrain_generator = TerrainGenerator.from_template(template_name)
        
        # Create instance
        instance = cls(config_manager)
        
        # Override the terrain generator with our template-based one
        instance.terrain_generator = terrain_generator
        
        # Update settings to match the template
        instance.settings.terrain = terrain_generator.settings
        
        return instance