from dataclasses import dataclass
from typing import Optional

@dataclass
class ErosionSettings:
    """Settings for terrain erosion simulation."""
    droplets: int          # Number of droplets to simulate
    inertia: float        # Water's tendency to maintain velocity
    capacity: float       # How much sediment a droplet can carry
    deposition: float     # Rate of sediment deposition
    erosion: float        # Rate of erosion
    evaporation: float    # Rate of water evaporation
    min_slope: float      # Minimum slope for erosion

    @classmethod
    def from_config(cls, config: dict) -> 'ErosionSettings':
        return cls(
            droplets=config['droplets'],
            inertia=config['inertia'],
            capacity=config['capacity'],
            deposition=config['deposition'],
            erosion=config['erosion'],
            evaporation=config['evaporation'],
            min_slope=config['min_slope']
        )

@dataclass
class TerrainSettings:
	"""Settings for terrain generation."""
	width: int
	height: int
	octaves: int
	persistence: float
	lacunarity: float
	scale: float
	height_power: float = 1.2      # Controls height distribution curve
	water_level: float = 0.4       # Base water level
	land_scale: float = 0.3        # Controls land height scaling
	seed: Optional[int] = None
	erosion: Optional[ErosionSettings] = None
    
	@classmethod
	def from_config(cls, config: dict) -> 'TerrainSettings':
		"""Create TerrainSettings from a configuration dictionary."""
		erosion_config = config.get('erosion')
		erosion_settings = None
		if erosion_config:
			erosion_settings = ErosionSettings.from_config(erosion_config)
			
		return cls(
			width=config.get('width', 256),
			height=config.get('height', 256),
			octaves=config.get('octaves', 6),
			persistence=config.get('persistence', 0.5),
			lacunarity=config.get('lacunarity', 2.0),
			scale=config.get('scale', 100.0),
			height_power=config.get('height_power', 1.2),
			water_level=config.get('water_level', 0.4),
			land_scale=config.get('land_scale', 0.3),
			seed=config.get('seed'),
			erosion=erosion_settings
		) 