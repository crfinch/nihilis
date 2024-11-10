from dataclasses import dataclass
from enum import Enum, auto
import numpy as np
from typing import Dict, Optional

class BiomeType(Enum):
	OCEAN = auto()
	SHALLOW_OCEAN = auto()
	BEACH = auto()
	TUNDRA = auto()
	COLD_DESERT = auto()
	GRASSLAND = auto()
	TEMPERATE_FOREST = auto()
	TEMPERATE_RAINFOREST = auto()
	SAVANNA = auto()
	DESERT = auto()
	TROPICAL_RAINFOREST = auto()
	MOUNTAIN = auto()
	SNOW_PEAKS = auto()

@dataclass
class BiomeSettings:
	temperature_weight: float = 1.0
	precipitation_weight: float = 1.0
	altitude_weight: float = 1.0

	# Thresholds for different climate factors
	ocean_level: float = 0.4
	mountain_level: float = 0.7

	# Temperature ranges (normalized 0-1)
	cold_thresh: float = 0.2
	temperate_thresh: float = 0.6

	# Precipitation ranges (normalized 0-1)
	dry_thresh: float = 0.2
	wet_thresh: float = 0.6

class BiomeGenerator:
	def __init__(self, settings: BiomeSettings):
		self.settings = settings
		
	def generate_temperature_map(self, height: int, width: int, seed: Optional[int] = None) -> np.ndarray:
		"""Generate temperature distribution based on latitude and altitude."""
		rng = np.random.default_rng(seed)
		
		# Base temperature decreases with latitude
		latitudes = np.linspace(1, 0, height)[:, np.newaxis]
		base_temp = np.tile(latitudes, (1, width))
		
		# Add some noise for local variation
		noise = rng.normal(0, 0.1, (height, width))
		return np.clip(base_temp + noise, 0, 1)
    
	def generate_precipitation_map(self, heightmap: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
		"""Generate precipitation based on altitude and distance from water."""
		rng = np.random.default_rng(seed)
		height, width = heightmap.shape
		
		# Find water bodies
		water_mask = heightmap < self.settings.ocean_level
		
		# Calculate distance from water for each point
		from scipy.ndimage import distance_transform_edt
		distance_from_water = distance_transform_edt(~water_mask)
		distance_from_water = distance_from_water / distance_from_water.max()
		
		# Precipitation decreases with distance from water
		precipitation = 1 - distance_from_water
		
		# Add orographic effect (more rain on mountain slopes)
		slopes = np.abs(np.gradient(heightmap)[0]) + np.abs(np.gradient(heightmap)[1])
		slopes = slopes / slopes.max()
		
		# Combine effects and add noise
		precipitation = 0.6 * precipitation + 0.4 * slopes
		noise = rng.normal(0, 0.1, (height, width))
		return np.clip(precipitation + noise, 0, 1)
    
	def assign_biomes(self, heightmap: np.ndarray, temperature: np.ndarray, 
						precipitation: np.ndarray) -> np.ndarray:
		"""Assign biomes based on height, temperature, and precipitation."""
		height, width = heightmap.shape
		biome_map = np.zeros((height, width), dtype=np.int32)
		
		for y in range(height):
			for x in range(width):
				height_val = heightmap[y, x]
				temp_val = temperature[y, x]
				precip_val = precipitation[y, x]
				
				# Ocean
				if height_val < self.settings.ocean_level:
					biome_map[y, x] = BiomeType.OCEAN.value
					continue
				
				# Alpine (high mountains)
				if height_val > self.settings.mountain_level:
					biome_map[y, x] = BiomeType.ALPINE.value
					continue
				
				# Assign land biomes based on temperature and precipitation
				if temp_val < self.settings.cold_thresh:
					biome_map[y, x] = BiomeType.TUNDRA.value
				elif temp_val < self.settings.temperate_thresh:
					if precip_val < self.settings.dry_thresh:
						biome_map[y, x] = BiomeType.TAIGA.value
					else:
						biome_map[y, x] = BiomeType.TEMPERATE_FOREST.value
				else:  # warm
					if precip_val < self.settings.dry_thresh:
						biome_map[y, x] = BiomeType.DESERT.value
					elif precip_val < self.settings.wet_thresh:
						biome_map[y, x] = BiomeType.SAVANNA.value
					else:
						biome_map[y, x] = BiomeType.TROPICAL_RAINFOREST.value
		
		return biome_map