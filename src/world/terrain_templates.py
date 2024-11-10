from dataclasses import dataclass, asdict
from pathlib import Path
import yaml
from typing import Dict, Optional
from src.world.terrain_generator import TerrainSettings, ErosionSettings
from src.world.terrain_settings import TerrainSettings, ErosionSettings

@dataclass
class TerrainTemplate:
    name: str
    description: str
    settings: TerrainSettings

class TerrainTemplateManager:
	def __init__(self, templates_dir: Path = Path("config/terrain_templates")):
		self.templates_dir = templates_dir
		self.templates_dir.mkdir(parents=True, exist_ok=True)
		self.templates: Dict[str, TerrainTemplate] = {}
		self.load_templates()
    
	def save_template(self, name: str, description: str, settings: TerrainSettings) -> bool:
		"""Save a terrain template to disk."""
		template = TerrainTemplate(name=name, description=description, settings=settings)
		
		# Convert settings to dictionary
		template_dict = {
			'name': template.name,
			'description': template.description,
			'settings': {
				'width': template.settings.width,
				'height': template.settings.height,
				'octaves': template.settings.octaves,
				'persistence': template.settings.persistence,
				'lacunarity': template.settings.lacunarity,
				'scale': template.settings.scale,
				'height_power': template.settings.height_power,
				'water_level': template.settings.water_level,
				'land_scale': template.settings.land_scale,
				'erosion': asdict(template.settings.erosion) if template.settings.erosion else None
			}
		}
		
		try:
			file_path = self.templates_dir / f"{name.lower().replace(' ', '_')}.yaml"
			with open(file_path, 'w') as f:
				yaml.dump(template_dict, f, default_flow_style=False)
			self.templates[name] = template
			return True
		except Exception as e:
			print(f"Error saving template: {e}")
			return False
    
	def load_templates(self) -> None:
		"""Load all terrain templates from disk."""
		for template_file in self.templates_dir.glob("*.yaml"):
			try:
				with open(template_file, 'r') as f:
					template_dict = yaml.safe_load(f)
				
				# Create erosion settings if present
				erosion_dict = template_dict['settings'].get('erosion')
				erosion_settings = ErosionSettings(**erosion_dict) if erosion_dict else None
				
				# Create terrain settings
				settings_dict = template_dict['settings']
				settings_dict['erosion'] = erosion_settings
				terrain_settings = TerrainSettings(**settings_dict)
				
				# Create and store template
				template = TerrainTemplate(
					name=template_dict['name'],
					description=template_dict['description'],
					settings=terrain_settings
				)
				self.templates[template.name] = template
				
			except Exception as e:
				print(f"Error loading template {template_file}: {e}")

	def get_template(self, name: str) -> Optional[TerrainTemplate]:
		"""Get a terrain template by name."""
		return self.templates.get(name)

	def list_templates(self) -> Dict[str, str]:
		"""Return a dictionary of template names and their descriptions."""
		return {name: template.description for name, template in self.templates.items()}