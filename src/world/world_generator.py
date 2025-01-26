# src/world/world_generator.py
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import numpy as np

from src.world.biome_generator import BiomeGenerator, BiomeType
from src.world.biome_generator import BiomeSettings
from src.world.terrain_generator import TerrainGenerator
from src.world.terrain_settings import TerrainSettings
from src.utils.configuration_manager import ConfigurationManager
from src.world.settlement_generator import SettlementGenerator, Settlement

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
        self.biome_map: Optional[np.ndarray] = None
        self.settlements: List[Settlement] = []
        self.regions: Dict[str, Any] = {}
        self.landmarks: Dict[str, Any] = {}
        self.history: Dict[str, Any] = {}
        self.discovery_mask: Optional[np.ndarray] = None

    def get_render_data(self) -> Dict:
        """Get the world data in a format suitable for rendering."""
        return {
            'heightmap': self.heightmap,
            'biome_map': self.biome_map,
            'settlements': self.settlements,
            'discovery_mask': self.discovery_mask
        }

class WorldGenerator:
    """Handles the generation of the entire world."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        world_gen_config = config_manager.config.get('world_gen', {})
        self.settings = WorldSettings.from_config(world_gen_config)
        
        # Initialize sub-generators
        self.terrain_generator = TerrainGenerator(self.settings.terrain)
        self.biome_generator = BiomeGenerator.from_config(config_manager)
        
        # Set RNG
        if self.settings.seed is None:
            self.settings.seed = np.random.randint(0, 2**32 - 1)
        self.rng = np.random.default_rng(self.settings.seed)
    
    def generate(self) -> World:
        """Generate a complete world."""
        world = World()
        
        # Reset RNG states for reproducibility
        if self.settings.seed is not None:
            # Reset main RNG
            self.rng = np.random.default_rng(self.settings.seed)
            
            # Reset terrain generator RNG and ensure it uses the same seed
            self.terrain_generator.settings.seed = self.settings.seed
            self.terrain_generator.rng = np.random.RandomState(self.settings.seed)
            
            # Reset biome generator RNG
            self.biome_generator.rng = np.random.default_rng(self.settings.seed)
        
        # Generate base terrain
        world.heightmap = self.terrain_generator.generate_heightmap()
        
        # Apply erosion
        if self.terrain_generator.settings.erosion:
            world.heightmap = self.terrain_generator.apply_erosion(world.heightmap)
        
        # Generate temperature and precipitation maps
        temperature = self.biome_generator.generate_temperature_map(
            self.settings.height, 
            self.settings.width, 
            self.settings.seed
        )
        precipitation = self.biome_generator.generate_precipitation_map(
            world.heightmap, 
            self.settings.seed
        )
        
        # Assign biomes
        world.biome_map = self.biome_generator.assign_biomes(
            world.heightmap,
            temperature,
            precipitation
        )

        unique_biomes = np.unique(world.biome_map)
        print(f"Generated biomes: {[BiomeType(b).name for b in unique_biomes]}")

        # Initialize discovery mask (all undiscovered)
        world.discovery_mask = np.ones((self.settings.height, self.settings.width), dtype=bool)
        
        # Generate settlements
        settlement_generator = SettlementGenerator(self.rng)
        world.settlements = settlement_generator.generate_settlements(
            world.heightmap,
            world.biome_map
        )
        
        # Debug print
        # print(f"WorldGenerator: Created {len(world.settlements)} settlements")
        # for settlement in world.settlements:
            # print(f"  {settlement.type.name} at position {settlement.position}")
        
        return world
    
    def save_world(self, world: World, filepath: str):
        """Save the generated world to disk."""
        raise NotImplementedError("World saving not yet implemented")
    
    def load_world(self, filepath: str) -> World:
        """Load a world from disk."""
        raise NotImplementedError("World loading not yet implemented")
    
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