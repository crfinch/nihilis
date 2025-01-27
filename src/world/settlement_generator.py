from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
from typing import List, Tuple, Dict, Set
from scipy.ndimage import distance_transform_edt, gaussian_filter
from src.world.biome_generator import BiomeType
import logging
from .name_generator import NameGenerator

logger = logging.getLogger(__name__)

class SettlementType(Enum):
    CAPITAL = auto()
    CITY = auto()
    TOWN = auto()
    VILLAGE = auto()
    RUINS = auto()
    DUNGEON = auto()
    TEMPLE = auto()
    FORTRESS = auto()

@dataclass
class Settlement:
    type: SettlementType
    position: Tuple[int, int]
    name: str = field(default="")
    population: int = 0
    importance: float = 0.0

    def generate_name(self, name_generator: NameGenerator):
        """Generate a name for this settlement"""
        # Map settlement types to name types
        name_type_mapping = {
            SettlementType.CAPITAL: "settlement",
            SettlementType.CITY: "settlement",
            SettlementType.TOWN: "settlement",
            SettlementType.VILLAGE: "settlement",
            SettlementType.RUINS: "ruins",
            SettlementType.DUNGEON: "dungeon",
            SettlementType.TEMPLE: "temple",
            SettlementType.FORTRESS: "fortress"
        }
        
        # Try to generate a name, fall back to a default if it fails
        try:
            self.name = name_generator.generate_name(
                epoch="empire",  # Default epoch, can be parameterized
                name_type=name_type_mapping[self.type]
            )
        except (KeyError, ValueError) as e:
            logger.warning(f"Failed to generate name for {self.type}: {e}")
            # Fallback names based on type
            fallback_names = {
                SettlementType.CAPITAL: "Capital City",
                SettlementType.CITY: "Great City",
                SettlementType.TOWN: "Small Town",
                SettlementType.VILLAGE: "Village",
                SettlementType.RUINS: "Ancient Ruins",
                SettlementType.DUNGEON: "Dark Dungeon",
                SettlementType.TEMPLE: "Holy Temple",
                SettlementType.FORTRESS: "Mighty Fortress"
            }
            self.name = fallback_names.get(self.type, "Unknown Settlement")

class SettlementGenerator:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng
        self.min_settlement_distance = {
            SettlementType.CAPITAL: 40,  # Minimum tiles between capitals
            SettlementType.CITY: 20,     # Minimum tiles between cities
            SettlementType.TOWN: 10,     # Minimum tiles between towns
            SettlementType.VILLAGE: 5,   # Minimum tiles between villages
            SettlementType.RUINS: 8,     # Minimum tiles between ruins
            SettlementType.DUNGEON: 12,  # Minimum tiles between dungeons
            SettlementType.TEMPLE: 15,   # Minimum tiles between temples
            SettlementType.FORTRESS: 18  # Minimum tiles between fortresses
        }

    def _calculate_habitability(self, heightmap: np.ndarray, biome_map: np.ndarray) -> np.ndarray:
        """Calculate habitability scores for the terrain."""
        height, width = heightmap.shape
        habitability = np.zeros((height, width))
        
        # First set all land areas to base habitability
        land_mask = heightmap >= 0.3
        habitability[land_mask] = 0.5
        
        # Calculate distance from water for all points
        water_mask = heightmap < 0.3
        distance_to_water = distance_transform_edt(~water_mask)
        
        # Create water proximity bonus that decays exponentially
        # Increase the decay factor to make the effect more pronounced
        water_bonus = np.exp(-distance_to_water / 5.0)  # Changed from 10.0 to 5.0
        
        # Apply water bonus only to land areas
        habitability[land_mask] += water_bonus[land_mask] * 0.5
        
        # Reduce habitability in mountains
        mountain_mask = heightmap > 0.7
        habitability[mountain_mask] *= 0.5
        
        # Ensure water areas have zero habitability
        habitability[water_mask] = 0
        
        # Normalize to [0, 1]
        if habitability.max() > 0:
            habitability = habitability / habitability.max()
        
        return habitability

    def _is_valid_position(self, position, settlement_type, existing_settlements, heightmap):
        y, x = position
        
        # Check if position is in water (heightmap < 0.3)
        if heightmap[y, x] < 0.3:
            return False
            
        # Check distance from other settlements
        for settlement in existing_settlements:
            y2, x2 = settlement.position
            distance = np.sqrt((y - y2)**2 + (x - x2)**2)
            # Use the larger of the two minimum distances
            min_distance = max(
                self.min_settlement_distance[settlement_type],
                self.min_settlement_distance[settlement.type]
            )
            if distance < min_distance:
                return False
                
        return True

    def generate_settlements(self, heightmap: np.ndarray, biome_map: np.ndarray,
                           num_capitals: int = 1,
                           num_cities: int = 3,
                           num_towns: int = 5,
                           num_villages: int = 30,
                           num_ruins: int = 10,
                           num_dungeons: int = 8,
                           num_temples: int = 6,
                           num_fortresses: int = 4) -> List[Settlement]:
        """Generate settlements based on terrain and biome data."""

        # Store the RNG state
        rng_state = self.rng.bit_generator.state

        settlements: List[Settlement] = []
        habitability = self._calculate_habitability(heightmap, biome_map)
        
        # Initialize name generator
        name_generator = NameGenerator(self.rng)
        
        # Generate settlements in order of importance
        settlement_counts = {
            SettlementType.CAPITAL: num_capitals,
            SettlementType.CITY: num_cities,
            SettlementType.TOWN: num_towns,
            SettlementType.VILLAGE: num_villages,
            SettlementType.RUINS: num_ruins,
            SettlementType.DUNGEON: num_dungeons,
            SettlementType.TEMPLE: num_temples,
            SettlementType.FORTRESS: num_fortresses
        }

        for settlement_type, count in settlement_counts.items():
            # Create a modified habitability map for this settlement type
            type_habitability = habitability.copy()
            attempts = 0
            max_attempts = 1000  # Prevent infinite loops
            percentile = 90  # Start with top 10%
            
            for _ in range(count):
                placed = False
                while not placed and attempts < max_attempts:
                    attempts += 1
                    
                    # Get indices of most habitable locations, gradually lowering standards
                    threshold = np.percentile(type_habitability, max(0, percentile - (attempts // 100) * 10))
                    candidate_positions = np.where(type_habitability >= threshold)
                    
                    if len(candidate_positions[0]) == 0:
                        continue
                        
                    # Randomly select from candidates
                    idx = self.rng.integers(len(candidate_positions[0]))
                    pos = (candidate_positions[0][idx], candidate_positions[1][idx])
                    
                    if self._is_valid_position(pos, settlement_type, settlements, heightmap):
                        # Create settlement
                        settlement = Settlement(
                            type=settlement_type,
                            position=pos,
                            importance=type_habitability[pos]
                        )
                        # Generate name for the settlement
                        settlement.generate_name(name_generator)
                        settlements.append(settlement)
                        
                        # Mark area as less habitable for future settlements
                        y, x = pos
                        radius = self.min_settlement_distance[settlement_type]
                        y_indices, x_indices = np.ogrid[-radius:radius+1, -radius:radius+1]
                        mask = x_indices**2 + y_indices**2 <= radius**2
                        
                        # Get bounds for the circular mask
                        y_start = max(0, y - radius)
                        y_end = min(heightmap.shape[0], y + radius + 1)
                        x_start = max(0, x - radius)
                        x_end = min(heightmap.shape[1], x + radius + 1)
                        
                        # Apply mask to habitability
                        mask_height = y_end - y_start
                        mask_width = x_end - x_start
                        type_habitability[y_start:y_end, x_start:x_end] *= (
                            1 - mask[:mask_height, :mask_width] * 0.8
                        )
                        placed = True
                        attempts = 0  # Reset for next settlement
                    else:
                        # If position invalid, mark it as less habitable
                        type_habitability[pos] *= 0.5
                
                if not placed:
                    logger.warning(f"Failed to place {settlement_type} after {max_attempts} attempts")
                    break  # Move on to next settlement type if we can't place this one
        # Restore RNG state before returning
        self.rng.bit_generator.state = rng_state
        return settlements 