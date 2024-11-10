#!/usr/bin/env python3

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import argparse
from datetime import datetime

from src.utils.world_visualization import TerrainVisualizer
from src.world.world_generator import WorldGenerator
from src.utils.configuration_manager import ConfigurationManager

DEFAULT_OUTPUT_DIR = Path("output/terrain_preview")

def preview_terrain(
    save_dir: Path = DEFAULT_OUTPUT_DIR,
    template_name: str = None,
    save_as_template: str = None
):
    """Generate and visualize terrain using either current settings or a template."""
    # Initialize configuration and world generator
    config_manager = ConfigurationManager()
    
    if template_name:
        # Create generator from template
        world_generator = WorldGenerator.from_template(template_name)
    else:
        # Create generator from config
        world_generator = WorldGenerator(config_manager)
    
    # Generate a world and get its heightmap
    world = world_generator.generate()
    heightmap = world.heightmap
    
    # Save as template if requested
    if save_as_template:
        success = world_generator.terrain_generator.save_as_template(
            save_as_template,
            f"Terrain template created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        if success:
            print(f"Successfully saved terrain template: {save_as_template}")
        else:
            print(f"Failed to save terrain template: {save_as_template}")
    
    # Initialize visualizer
    visualizer = TerrainVisualizer()
    
    # Create output directory if saving
    if save_dir:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate different visualizations
    visualizations = [
        (visualizer.display_heightmap, "heightmap", {'save_path': None}),
        (visualizer.display_3d, "terrain_3d", {'save_path': None}),
        (visualizer.display_analysis, "analysis", {'save_dir': None})
    ]
    
    # Generate each visualization
    for viz_func, name, kwargs in visualizations:
        if save_dir:
            if 'save_path' in kwargs:
                kwargs['save_path'] = save_dir / f"{name}.png"
            elif 'save_dir' in kwargs:
                kwargs['save_dir'] = save_dir
                kwargs['base_filename'] = name
            viz_func(heightmap, **kwargs)
            print(f"Saved {name} visualization to {save_dir}/{name}.png")
        else:
            kwargs = {k: v for k, v in kwargs.items() if not k.startswith('save')}
            viz_func(heightmap, **kwargs)
            plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Preview terrain generation')
    parser.add_argument('--output-dir', type=str, 
                      default=str(DEFAULT_OUTPUT_DIR),
                      help='Directory to save visualizations')
    parser.add_argument('--template', type=str,
                      help='Name of template to use')
    parser.add_argument('--save-template', type=str,
                      help='Save current settings as template with given name')
    
    args = parser.parse_args()
    
    preview_terrain(
        save_dir=Path(args.output_dir),
        template_name=args.template,
        save_as_template=args.save_template
    )