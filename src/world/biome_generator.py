from dataclasses import dataclass
from enum import Enum, auto
import numpy as np
from typing import Dict, Optional
from src.utils.configuration_manager import ConfigurationManager
from scipy.ndimage import distance_transform_edt

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
	temperature_weight: float
	precipitation_weight: float
	altitude_weight: float
	ocean_level: float
	mountain_level: float
	cold_thresh: float
	temperate_thresh: float
	dry_thresh: float
	wet_thresh: float

	@classmethod
	def from_config(cls, config: dict) -> 'BiomeSettings':
		biome_config = config.get('world_gen', {}).get('biomes', {})
		return cls(
			temperature_weight=biome_config.get('temperature_weight', 1.0),
			precipitation_weight=biome_config.get('precipitation_weight', 1.0),
			altitude_weight=biome_config.get('altitude_weight', 1.0),
			ocean_level=biome_config.get('ocean_level', 0.35),
			mountain_level=biome_config.get('mountain_level', 0.65),
			cold_thresh=biome_config.get('cold_thresh', 0.3),
			temperate_thresh=biome_config.get('temperate_thresh', 0.6),
			dry_thresh=biome_config.get('dry_thresh', 0.3),
			wet_thresh=biome_config.get('wet_thresh', 0.6)
		)

class BiomeGenerator:
	@classmethod
	def from_config(cls, config_manager: ConfigurationManager) -> 'BiomeGenerator':
		settings = BiomeSettings.from_config(config_manager.config)
		return cls(settings)

	def __init__(self, settings: BiomeSettings):
		self.settings = settings
		
	def generate_temperature_map(self, height: int, width: int, seed: Optional[int] = None) -> np.ndarray:
		"""Generate temperature distribution with more distinct climate zones."""
		rng = np.random.default_rng(seed)
		
		# Create more extreme latitude-based temperature gradient
		y = np.linspace(-1, 1, height)[:, np.newaxis]
		base_temp = 1.2 - np.power(np.abs(y), 0.75)  # More extreme gradient
		base_temp = np.tile(base_temp, (1, width))
		
		# Add large-scale continental temperature variations
		x = np.linspace(0, 4*np.pi, width)
		y = np.linspace(0, 4*np.pi, height)
		X, Y = np.meshgrid(x, y)
		
		# Create larger temperature variation patterns
		continental = 0.4 * np.sin(X/3) * np.cos(Y/3)
		regional = 0.2 * np.sin(X) * np.cos(Y)
		local = 0.1 * rng.normal(0, 1, (height, width))
		
		# Combine all effects with more weight on the base temperature
		temperature = (0.5 * base_temp + 
					0.25 * continental +
					0.15 * regional +
					0.1 * local)
		
		# Clip but allow slightly wider range
		return np.clip(temperature, 0, 1.2)
    
	def generate_precipitation_map(self, heightmap: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
		"""Generate precipitation with more distinct wet and dry regions."""
		rng = np.random.default_rng(seed)
		height, width = heightmap.shape
		
		# Find water bodies
		water_mask = heightmap < self.settings.ocean_level
		
		# Calculate distance from water with less weight
		distance_from_water = distance_transform_edt(~water_mask)
		distance_from_water = distance_from_water / distance_from_water.max()
		
		# Create large-scale precipitation patterns
		x = np.linspace(0, 6*np.pi, width)
		y = np.linspace(0, 6*np.pi, height)
		X, Y = np.meshgrid(x, y)
		
		# Create monsoon-like patterns
		monsoon = 0.5 * (np.sin(X/4) + np.cos(Y/4))
		
		# Add orographic effect (more rain on mountain slopes)
		slopes = np.abs(np.gradient(heightmap)[0]) + np.abs(np.gradient(heightmap)[1])
		slopes = slopes / slopes.max()
		
		# Create rain shadow effect
		rain_shadow = np.roll(slopes, shift=int(width/8), axis=1)  # Shift effect downwind
		
		# Combine effects with adjusted weights
		precipitation = (0.2 * (1 - distance_from_water) +  # Reduced coastal effect
						0.3 * monsoon +                     # Large-scale patterns
						0.3 * slopes +                      # Mountain effects
						0.1 * (1 - rain_shadow) +          # Rain shadow
						0.1 * rng.normal(0, 1, (height, width)))  # Local variation
		
		# Before power operation, ensure all values are non-negative
		precipitation = np.clip(precipitation, 0, None)
		# Now apply power function
		precipitation = np.power(precipitation, 0.8)
		
		# Apply some non-linear scaling to create more distinct wet/dry regions
		precipitation = np.power(precipitation, 0.8)
		
		return np.clip(precipitation, 0, 1)
    
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
				
				# Ocean and mountains first
				if height_val < self.settings.ocean_level:
					if height_val < self.settings.ocean_level - 0.1:
						biome_map[y, x] = BiomeType.OCEAN.value
					else:
						biome_map[y, x] = BiomeType.SHALLOW_OCEAN.value
					continue
				
				# Beach
				if height_val < self.settings.ocean_level + 0.05:
					biome_map[y, x] = BiomeType.BEACH.value
					continue
				
				# Mountains and peaks
				if height_val > self.settings.mountain_level:
					if temp_val < self.settings.cold_thresh:
						biome_map[y, x] = BiomeType.SNOW_PEAKS.value
					else:
						biome_map[y, x] = BiomeType.MOUNTAIN.value
					continue
				
				# Other biomes based on temperature and precipitation
				if temp_val < self.settings.cold_thresh:
					if precip_val < self.settings.dry_thresh:
						biome_map[y, x] = BiomeType.COLD_DESERT.value
					else:
						biome_map[y, x] = BiomeType.TUNDRA.value
				elif temp_val < self.settings.temperate_thresh:
					if precip_val < self.settings.dry_thresh:
						biome_map[y, x] = BiomeType.GRASSLAND.value
					elif precip_val < self.settings.wet_thresh:
						biome_map[y, x] = BiomeType.TEMPERATE_FOREST.value
					else:
						biome_map[y, x] = BiomeType.TEMPERATE_RAINFOREST.value
				else:  # warm
					if precip_val < self.settings.dry_thresh:
						biome_map[y, x] = BiomeType.DESERT.value
					elif precip_val < self.settings.wet_thresh:
						biome_map[y, x] = BiomeType.SAVANNA.value
					else:
						biome_map[y, x] = BiomeType.TROPICAL_RAINFOREST.value
		
		return biome_map
	
	# def assign_biomes(self, heightmap: np.ndarray, temperature: np.ndarray, 
	# 					precipitation: np.ndarray) -> np.ndarray:
	# 	"""Assign biomes based on height, temperature, and precipitation."""
	# 	height, width = heightmap.shape
	# 	biome_map = np.zeros((height, width), dtype=np.int32)
		
	# 	for y in range(height):
	# 		for x in range(width):
	# 			height_val = heightmap[y, x]
	# 			temp_val = temperature[y, x]
	# 			precip_val = precipitation[y, x]
				
	# 			# Ocean and mountains first
	# 			if height_val < self.settings.ocean_level:
	# 				if height_val < self.settings.ocean_level - 0.1:
	# 					biome_map[y, x] = BiomeType.OCEAN.value
	# 				else:
	# 					biome_map[y, x] = BiomeType.SHALLOW_OCEAN.value
	# 				continue
				
	# 			# Beach
	# 			if height_val < self.settings.ocean_level + 0.05:
	# 				biome_map[y, x] = BiomeType.BEACH.value
	# 				continue
				
	# 			# Mountains and peaks
	# 			if height_val > self.settings.mountain_level:
	# 				if temp_val < self.settings.cold_thresh:
	# 					biome_map[y, x] = BiomeType.SNOW_PEAKS.value
	# 				else:
	# 					biome_map[y, x] = BiomeType.MOUNTAIN.value
	# 				continue
				
	# 			# Other biomes based on temperature and precipitation
	# 			if temp_val < self.settings.cold_thresh:
	# 				if precip_val < self.settings.dry_thresh:
	# 					biome_map[y, x] = BiomeType.COLD_DESERT.value
	# 				else:
	# 					biome_map[y, x] = BiomeType.TUNDRA.value
	# 			elif temp_val < self.settings.temperate_thresh:
	# 				if precip_val < self.settings.dry_thresh:
	# 					biome_map[y, x] = BiomeType.GRASSLAND.value
	# 				elif precip_val < self.settings.wet_thresh:
	# 					biome_map[y, x] = BiomeType.TEMPERATE_FOREST.value
	# 				else:
	# 					biome_map[y, x] = BiomeType.TEMPERATE_RAINFOREST.value
	# 			else:  # warm
	# 				if precip_val < self.settings.dry_thresh:
	# 					biome_map[y, x] = BiomeType.DESERT.value
	# 				elif precip_val < self.settings.wet_thresh:
	# 					biome_map[y, x] = BiomeType.SAVANNA.value
	# 				else:
	# 					biome_map[y, x] = BiomeType.TROPICAL_RAINFOREST.value
		
	# 	return biome_map