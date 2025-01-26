from dataclasses import dataclass
import numpy as np
from typing import Tuple, Optional, Dict, Any
from src.utils.configuration_manager import ConfigurationManager
from src.world.terrain_settings import TerrainSettings, ErosionSettings
from src.world.terrain_templates import TerrainTemplate, TerrainTemplateManager

class TerrainGenerator:
	@classmethod
	def from_config(cls, config_manager: ConfigurationManager) -> 'TerrainGenerator':
		"""Create a TerrainGenerator instance from configuration."""
		terrain_settings = config_manager.get_terrain_settings()
		return cls(terrain_settings)
	
	@classmethod
	def from_template(cls, template_name: str) -> 'TerrainGenerator':
		"""Create a TerrainGenerator instance from a template."""
		template_manager = TerrainTemplateManager()
		template = template_manager.get_template(template_name)
		if template is None:
			raise ValueError(f"Template '{template_name}' not found")
		return cls(template.settings)
	
	def __init__(self, settings: TerrainSettings):
		"""Initialize the terrain generator with settings."""
		self.settings = settings
		self.width = settings.width
		self.height = settings.height
		self.octaves = settings.octaves
		self.persistence = settings.persistence
		self.lacunarity = settings.lacunarity
		self.scale = settings.scale
		
		# Initialize RNG with seed if provided
		self.rng = np.random.RandomState(settings.seed)
		
	def generate_heightmap(self) -> np.ndarray:
		"""Generate a heightmap using Perlin noise with multiple octaves."""
		# Reset RNG state to ensure reproducibility
		self.rng = np.random.RandomState(self.settings.seed)
		
		heightmap = np.zeros((self.height, self.width))
		
		# Generate base noise
		amplitude = 1.0
		frequency = 1.0
		max_value = 0.0
		
		for i in range(self.octaves):
			noise = self._generate_octave(frequency)
			heightmap += noise * amplitude
			max_value += amplitude
			
			frequency *= self.lacunarity
			amplitude *= self.persistence
		
		# Normalize to [-1, 1] range first
		heightmap = heightmap / max_value
		
		# Apply redistribution function for more natural terrain
		heightmap = self._redistribute_heights(heightmap)
		
		# Apply smoothing
		heightmap = self._smooth_terrain(heightmap)
		
		return heightmap

	def _generate_octave(self, frequency: float) -> np.ndarray:
		"""Generate a single octave of Perlin noise."""
		# Calculate grid size based on frequency and scale
		grid_height = int(self.height * frequency / self.scale) + 1
		grid_width = int(self.width * frequency / self.scale) + 1
		
		# Generate gradients for the grid
		gradients = self._generate_gradients(grid_height, grid_width)
		
		# Create coordinate grids for vectorized operations
		y_coords = np.linspace(0, grid_height - 1, self.height)
		x_coords = np.linspace(0, grid_width - 1, self.width)
		x_grid, y_grid = np.meshgrid(x_coords, y_coords)
		
		# Get grid cell coordinates
		x0 = np.floor(x_grid).astype(int)
		x1 = x0 + 1
		y0 = np.floor(y_grid).astype(int)
		y1 = y0 + 1
		
		# Ensure we don't exceed grid boundaries
		x0 = np.clip(x0, 0, grid_width - 2)
		x1 = np.clip(x1, 0, grid_width - 1)
		y0 = np.clip(y0, 0, grid_height - 2)
		y1 = np.clip(y1, 0, grid_height - 1)
		
		# Get relative coordinates within each grid cell
		x_frac = x_grid - x0
		y_frac = y_grid - y0
		
		# Calculate dot products for each corner
		n0 = self._dot_grid_gradient(x0, y0, x_grid, y_grid, gradients)
		n1 = self._dot_grid_gradient(x1, y0, x_grid, y_grid, gradients)
		n2 = self._dot_grid_gradient(x0, y1, x_grid, y_grid, gradients)
		n3 = self._dot_grid_gradient(x1, y1, x_grid, y_grid, gradients)
		
		# Interpolate along x
		fx = self._fade(x_frac)
		nx0 = self._lerp(n0, n1, fx)
		nx1 = self._lerp(n2, n3, fx)
		
		# Interpolate along y
		fy = self._fade(y_frac)
		return self._lerp(nx0, nx1, fy)

	def _generate_gradients(self, height: int, width: int) -> np.ndarray:
		"""Generate random gradient vectors for grid points."""
		# Generate angles with better distribution
		angles = self.rng.uniform(0, 2 * np.pi, (height, width))
		
		# Create unit vectors from angles
		gradients = np.dstack([
			np.cos(angles),
			np.sin(angles)
		])
		
		return gradients
	
	def _redistribute_heights(self, heightmap: np.ndarray) -> np.ndarray:
		"""Redistribute height values to create more natural-looking terrain."""
		# First normalize to [0, 1]
		heightmap = (heightmap + 1) * 0.5
		
		# Apply gentler exponential distribution
		heightmap = np.power(heightmap, 1.1)  # Slightly more aggressive to reduce mountains
		
		# Create more distinct elevation bands with better distribution
		mask_lowlands = heightmap < 0.35
		mask_hills = (heightmap >= 0.35) & (heightmap < 0.65)
		mask_mountains = heightmap >= 0.65
		
		# Adjust each band separately with more conservative multipliers
		heightmap[mask_lowlands] *= 0.9  # Slight compression of lowlands
		heightmap[mask_hills] = 0.35 + (heightmap[mask_hills] - 0.35) * 1.1  # Gentle hill expansion
		heightmap[mask_mountains] = 0.65 + (heightmap[mask_mountains] - 0.65) * 1.2  # Moderate mountain expansion
		
		return heightmap
	
	def _smooth_terrain(self, heightmap: np.ndarray) -> np.ndarray:
		"""Apply smoothing to reduce spikiness while preserving features."""
		from scipy.ndimage import gaussian_filter
		
		# Apply selective smoothing based on slope
		gy, gx = np.gradient(heightmap)
		slopes = np.sqrt(gx**2 + gy**2)
		
		# Calculate base smoothing factor
		base_sigma = 0.5
		
		# Apply initial smoothing
		smoothed = gaussian_filter(heightmap, sigma=base_sigma)
		
		# Calculate adaptive blend factor based on slopes
		blend_factor = np.clip(slopes * 3.0, 0.2, 0.8)
		
		# Blend original and smoothed based on slopes
		result = heightmap * (1 - blend_factor) + smoothed * blend_factor
		
		return result

	def _dot_grid_gradient(self, ix: np.ndarray, iy: np.ndarray, x: np.ndarray, y: np.ndarray, 
						gradients: np.ndarray) -> np.ndarray:
		"""Compute dot product of gradient vector with distance vector."""
		# Calculate distance vectors
		dx = x - ix
		dy = y - iy
		
		# Get gradients for each point
		# Reshape indices to access the correct gradients
		gradient_vectors = gradients[iy, ix]
		
		# Compute dot product
		# gradient_vectors has shape (height, width, 2)
		# dx and dy have shape (height, width)
		# We need to multiply corresponding components and sum
		return dx * gradient_vectors[..., 0] + dy * gradient_vectors[..., 1]

	@staticmethod
	def _lerp(a: float, b: float, t: float) -> float:
		"""Linear interpolation between a and b."""
		return a + t * (b - a)

	@staticmethod
	def _fade(t: float) -> float:
		"""Fade function for smooth interpolation."""
		# Improved smoothstep function (Ken Perlin)
		return t * t * t * (t * (t * 6 - 15) + 10)

	def apply_erosion(self, heightmap: np.ndarray) -> np.ndarray:
		"""Apply both hydraulic and thermal erosion to the heightmap."""
		if not self.settings.erosion:  # If no erosion settings, return unchanged
			return heightmap
			
		eroded = self.hydraulic_erosion(heightmap.copy())
		eroded = self.thermal_erosion(eroded)
		return eroded

	def hydraulic_erosion(self, heightmap: np.ndarray) -> np.ndarray:
		"""Simulate hydraulic erosion using a particle-based approach."""
		if not self.settings.erosion:
			return heightmap
		
		erosion_settings = self.settings.erosion
		width, height = heightmap.shape
		
		for _ in range(erosion_settings.droplets):
			# Initialize water droplet
			x = self.rng.random() * (width - 1)
			y = self.rng.random() * (height - 1)
			water = 1.0
			speed = np.zeros(2)
			sediment = 0.0
			
			for _ in range(30):  # Maximum droplet lifetime
				# Get droplet coordinates
				cell_x = int(x)
				cell_y = int(y)
				if not (0 <= cell_x < width - 1 and 0 <= cell_y < height - 1):
					break
					
				# Calculate droplet's height and gradient
				gradient = self._calculate_gradient(heightmap, x, y)
				height = self._sample_height(heightmap, x, y)
				
				# Update droplet's direction and position
				speed = (speed * erosion_settings.inertia - 
						gradient * (1 - erosion_settings.inertia))
				length = np.linalg.norm(speed)
				if length != 0:
					speed /= length
				
				x += speed[0]
				y += speed[1]
				
				# Stop if droplet flows off map
				if not (0 <= x < width - 1 and 0 <= y < height - 1):
					break
				
				# Calculate height difference
				new_height = self._sample_height(heightmap, x, y)
				dh = new_height - height
				
				# Deposit or erode sediment
				capacity = max(-dh * length * water * erosion_settings.capacity, 0.01)
				if sediment > capacity:
					# Deposit
					amount = (sediment - capacity) * erosion_settings.deposition
					sediment -= amount
					self._deposit(heightmap, x, y, amount)
				else:
					# Erode
					amount = min((capacity - sediment) * erosion_settings.erosion, -dh)
					sediment += amount
					self._erode(heightmap, x, y, amount)
				
				# Evaporate water
				water *= (1 - erosion_settings.evaporation)
		
		return heightmap

	def thermal_erosion(self, heightmap: np.ndarray) -> np.ndarray:
		"""Simulate thermal erosion (rock falls)."""
		width, height = heightmap.shape
		iterations = 5  # Number of thermal erosion passes
		
		for _ in range(iterations):
			eroded = heightmap.copy()
			
			for y in range(1, height - 1):
				for x in range(1, width - 1):
					# Check all neighbors
					for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
						diff = heightmap[y,x] - heightmap[y+dy,x+dx]
						if diff > self.settings.erosion.min_slope:
							# Transfer material (conserving mass)
							transfer = diff * 0.25  # Only transfer a portion
							eroded[y,x] -= transfer
							eroded[y+dy,x+dx] += transfer  # Transfer full amount to neighbor
			
			heightmap = eroded
			
		return heightmap

	def _calculate_gradient(self, heightmap: np.ndarray, x: float, y: float) -> np.ndarray:
		"""Calculate the gradient at a given position."""
		cell_x = int(x)
		cell_y = int(y)
		
		# Calculate gradients using bilinear interpolation
		gradient_x = (
			self._sample_height(heightmap, x + 1, y) - 
			self._sample_height(heightmap, x - 1, y)
		) * 0.5
		
		gradient_y = (
			self._sample_height(heightmap, x, y + 1) - 
			self._sample_height(heightmap, x, y - 1)
		) * 0.5
		
		return np.array([gradient_x, gradient_y])

	def _sample_height(self, heightmap: np.ndarray, x: float, y: float) -> float:
		"""Sample height at a position using bilinear interpolation."""
		x0 = int(x)
		x1 = x0 + 1
		y0 = int(y)
		y1 = y0 + 1
		
		# Ensure we're within bounds
		x0 = max(0, min(x0, heightmap.shape[1] - 1))
		x1 = max(0, min(x1, heightmap.shape[1] - 1))
		y0 = max(0, min(y0, heightmap.shape[0] - 1))
		y1 = max(0, min(y1, heightmap.shape[0] - 1))
		
		# Calculate interpolation weights
		wx = x - x0
		wy = y - y0
		
		# Bilinear interpolation
		return (heightmap[y0, x0] * (1 - wx) * (1 - wy) +
				heightmap[y0, x1] * wx * (1 - wy) +
				heightmap[y1, x0] * (1 - wx) * wy +
				heightmap[y1, x1] * wx * wy)

	def _deposit(self, heightmap: np.ndarray, x: float, y: float, amount: float):
		"""Deposit sediment at a position using bilinear interpolation."""
		x0 = int(x)
		x1 = x0 + 1
		y0 = int(y)
		y1 = y0 + 1
		
		# Calculate weights
		wx = x - x0
		wy = y - y0
		
		# Distribute sediment
		heightmap[y0, x0] += amount * (1 - wx) * (1 - wy)
		heightmap[y0, x1] += amount * wx * (1 - wy)
		heightmap[y1, x0] += amount * (1 - wx) * wy
		heightmap[y1, x1] += amount * wx * wy

	def _erode(self, heightmap: np.ndarray, x: float, y: float, amount: float):
		"""Erode terrain at a position using bilinear interpolation."""
		self._deposit(heightmap, x, y, -amount)

	def save_as_template(self, name: str, description: str) -> bool:
		"""Save current settings as a template."""
		template_manager = TerrainTemplateManager()
		return template_manager.save_template(name, description, self.settings)