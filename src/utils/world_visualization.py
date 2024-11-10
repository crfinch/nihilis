# src/utils/visualization.py
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple, List
from pathlib import Path
from src.world.terrain_settings import TerrainSettings

class TerrainVisualizer:
    """Utility class for visualizing terrain data."""
    
    def __init__(self, terrain_settings: Optional[TerrainSettings] = None):
        # Default color maps for different terrain features
        self.TERRAIN_CMAP = 'terrain'
        self.EROSION_CMAP = 'RdYlBu'
        self.GRADIENT_CMAP = 'coolwarm'
        
        # Use provided settings or defaults
        self.WATER_LEVEL = (terrain_settings.water_level if terrain_settings 
                           else 0.4)
        self.MOUNTAIN_LEVEL = (self.WATER_LEVEL + 
                              (1.0 - self.WATER_LEVEL) * 0.7)
        
    def display_heightmap(self, 
                         heightmap: np.ndarray,
                         title: str = "Terrain Heightmap",
                         cmap: str = None,
                         show_colorbar: bool = True,
                         save_path: Optional[Path] = None,
                         dpi: int = 300):
        """Display or save a visualization of the heightmap."""
        plt.figure(figsize=(12, 8))
        
        # Create the main heightmap plot
        im = plt.imshow(heightmap, 
                       cmap=cmap or self.TERRAIN_CMAP,
                       interpolation='nearest')
        
        if show_colorbar:
            cbar = plt.colorbar(im)
            cbar.set_label('Elevation')
        
        plt.title(title)
        
        # Add terrain type contours
        self._add_terrain_contours(heightmap)
        
        if save_path:
            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
            
    def display_3d(self,
                   heightmap: np.ndarray,
                   title: str = "3D Terrain View",
                   azim: float = -60,
                   elev: float = 45,
                   save_path: Optional[Path] = None,
                   dpi: int = 300):
        """Display or save a 3D visualization of the heightmap."""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create meshgrid for 3D plot
        x, y = np.meshgrid(
            np.arange(heightmap.shape[1]),
            np.arange(heightmap.shape[0])
        )
        
        # Plot surface
        surf = ax.plot_surface(x, y, heightmap,
                             cmap=self.TERRAIN_CMAP,
                             linewidth=0,
                             antialiased=True)
        
        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        
        # Set viewing angle
        ax.view_init(elev=elev, azim=azim)
        
        ax.set_title(title)
        
        if save_path:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
            
    def display_analysis(self,
                        heightmap: np.ndarray,
                        save_dir: Optional[Path] = None,
                        base_filename: str = "terrain_analysis",
                        dpi: int = 300):
        """Generate a comprehensive analysis of the terrain."""
        analyses = [
            (self._height_distribution, "Height Distribution"),
            (self._slope_analysis, "Slope Analysis"),
            (self._terrain_types, "Terrain Types"),
            (self._erosion_patterns, "Erosion Patterns")
        ]
        
        fig = plt.figure(figsize=(20, 15))
        
        for idx, (analysis_func, title) in enumerate(analyses, 1):
            ax = fig.add_subplot(2, 2, idx)
            analysis_func(heightmap, ax, title)
            
        plt.tight_layout()
        
        if save_dir:
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / f"{base_filename}.png"
            plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
            plt.close()
        else:
            plt.show()
            
    def _add_terrain_contours(self, heightmap: np.ndarray):
        """Add contour lines for different terrain types."""
        levels = [self.WATER_LEVEL, self.MOUNTAIN_LEVEL]
        plt.contour(heightmap, levels=levels, colors='black', alpha=0.3)
        
    def _height_distribution(self, heightmap: np.ndarray, ax: plt.Axes, title: str):
        """Plot height distribution histogram."""
        ax.hist(heightmap.ravel(), bins=50, color='skyblue', alpha=0.7)
        ax.axvline(self.WATER_LEVEL, color='blue', linestyle='--', alpha=0.5)
        ax.axvline(self.MOUNTAIN_LEVEL, color='brown', linestyle='--', alpha=0.5)
        ax.set_title(title)
        ax.set_xlabel('Height')
        ax.set_ylabel('Frequency')
        
    def _slope_analysis(self, heightmap: np.ndarray, ax: plt.Axes, title: str):
        """Plot terrain slopes."""
        gy, gx = np.gradient(heightmap)
        slopes = np.sqrt(gx**2 + gy**2)
        im = ax.imshow(slopes, cmap='viridis')
        plt.colorbar(im, ax=ax)
        ax.set_title(title)
        
    def _terrain_types(self, heightmap: np.ndarray, ax: plt.Axes, title: str):
        """Visualize different terrain types."""
        terrain_types = np.zeros_like(heightmap)
        terrain_types[heightmap < self.WATER_LEVEL] = 0  # Water
        terrain_types[(heightmap >= self.WATER_LEVEL) & 
                     (heightmap < self.MOUNTAIN_LEVEL)] = 1  # Land
        terrain_types[heightmap >= self.MOUNTAIN_LEVEL] = 2  # Mountains
        
        im = ax.imshow(terrain_types, cmap='tab10')
        cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2])
        cbar.ax.set_yticklabels(['Water', 'Land', 'Mountains'])  # Set labels after creating colorbar
        ax.set_title(title)
        
    def _erosion_patterns(self, heightmap: np.ndarray, ax: plt.Axes, title: str):
        """Visualize potential erosion patterns."""
        gy, gx = np.gradient(heightmap)
        erosion = np.abs(gx) + np.abs(gy)
        im = ax.imshow(erosion, cmap=self.EROSION_CMAP)
        plt.colorbar(im, ax=ax)
        ax.set_title(title)