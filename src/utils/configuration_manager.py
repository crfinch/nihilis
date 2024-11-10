import json
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass
from enum import Enum, auto
from src.world.terrain_settings import TerrainSettings

class ConfigScope(Enum):
    """Defines different configuration scopes."""
    SYSTEM = auto()    # System-wide settings (display, performance, etc.)
    GRAPHICS = auto()  # Graphics settings
    CONTROLS = auto()  # Key bindings and control settings
    AUDIO = auto()     # Audio settings
    GAMEPLAY = auto()  # Gameplay preferences
    DEBUG = auto()     # Debug settings

@dataclass
class DisplayConfig:
    """Configuration settings for display."""
    screen_width: int
    screen_height: int
    fullscreen: bool
    vsync: bool
    tile_width: int
    tile_height: int
    font_path: str
    font_width: int
    font_height: int

@dataclass
class PerformanceConfig:
    target_fps: int
    max_messages: int
    log_interval: int
    warning_threshold_fps: float
    critical_threshold_fps: float
    memory_warning_threshold_mb: float

@dataclass
class KeyBindings:
    move_up: List[str]
    move_down: List[str]
    move_left: List[str]
    move_right: List[str]
    inventory: List[str]
    character: List[str]
    quit: List[str]
    debug_overlay: List[str]

class ConfigurationManager:
    """Manages game configuration settings."""
    
    DEFAULT_CONFIG = {
        "display": {
            "screen_width": 80,
            "screen_height": 50,
            "fullscreen": False,
            "vsync": True,
            "tile_width": 16,
            "tile_height": 16,
            "font_path": "resources/fonts/terminal16x16_gs_ro.png",
            "font_width": 16,
            "font_height": 16
        },
        "performance": {
            "target_fps": 60,
            "max_messages": 100,
            "log_interval": 5,        # 5 for debug, 300 for prod
            "warning_threshold_fps": 55.0,
            "critical_threshold_fps": 30.0,
            "memory_warning_threshold_mb": 400.0
        },
        "keybindings": {
            "move_up": ["UP", "k"],      # UP arrow and 'k'
            "move_down": ["DOWN", "j"],    # DOWN arrow and 'j'
            "move_left": ["LEFT", "h"],    # LEFT arrow and 'h'
            "move_right": ["RIGHT", "l"],   # RIGHT arrow and 'l'
            "inventory": ["i"],         # 'i'
            "character": ["c"],          # 'c'
            "quit": ["ESC"],              # ESC
            "debug_overlay": ["F3"]      # F3
        },
        "debug": {
            "enabled": False,
            "show_fps": True,
            "log_input": False,
            "god_mode": False
        }
    }
    
    def __init__(self, config_dir: Path = Path("config")):
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger('config')
        
        # Load or create default configuration
        if not self.load_config():
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
            
    def load_config(self) -> bool:
        """Load configuration from file."""
        config_file = self.config_dir / "config.yaml"
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self.config = yaml.safe_load(f)
                self._validate_config()
                return True
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
        return False
        
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            with open(self.config_dir / "config.yaml", 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
            
    def get_display_config(self) -> DisplayConfig:
        """Get display configuration settings."""
        display = self.config.get('display', self.DEFAULT_CONFIG['display'])
        return DisplayConfig(**display)
        
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration settings."""
        perf = self.config.get("performance", self.DEFAULT_CONFIG["performance"])
        
        # If the old key exists, migrate it to the new key
        if "logging_interval" in perf:
            perf["log_interval"] = perf.pop("logging_interval")
            
        return PerformanceConfig(**perf)
        
    def get_keybindings(self) -> KeyBindings:
        """Get key binding configuration."""
        bindings = self.config.get('keybindings', self.DEFAULT_CONFIG['keybindings'])
        return KeyBindings(**bindings)
        
    def get_debug_settings(self) -> Dict[str, bool]:
        """Get debug configuration settings."""
        return self.config.get('debug', self.DEFAULT_CONFIG['debug'])
    
    def get_terrain_settings(self) -> TerrainSettings:
        """Get terrain generation settings from config."""
        terrain_config = self.config.get('terrain', {})
        return TerrainSettings(
            width=terrain_config.get('width', 256),
            height=terrain_config.get('height', 256),
            octaves=terrain_config.get('octaves', 6),
            persistence=terrain_config.get('persistence', 0.5),
            lacunarity=terrain_config.get('lacunarity', 2.0),
            scale=terrain_config.get('scale', 100.0),
            height_power=terrain_config.get('height_power', 1.2),
            water_level=terrain_config.get('water_level', 0.4),
            land_scale=terrain_config.get('land_scale', 0.3),
            seed=terrain_config.get('seed'),
            erosion=self._get_erosion_settings(terrain_config)
        )
        
    def update_config(self, scope: ConfigScope, settings: Dict[str, Any]) -> bool:
        """Update configuration settings for a specific scope."""
        scope_name = scope.name.lower()
        try:
            if scope_name in self.config:
                self.config[scope_name].update(settings)
            else:
                self.config[scope_name] = settings
            self._validate_config()
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Error updating config: {e}")
            return False
            
    def _validate_config(self) -> None:
        """Validate configuration and fill in missing values."""
        for section, defaults in self.DEFAULT_CONFIG.items():
            if section not in self.config:
                self.config[section] = defaults
            else:
                for key, value in defaults.items():
                    if key not in self.config[section]:
                        self.config[section][key] = value
                        
    def export_config(self, file_path: Path) -> bool:
        """Export configuration to a file."""
        try:
            with open(file_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            return True
        except Exception as e:
            self.logger.error(f"Error exporting config: {e}")
            return False
            
    def import_config(self, file_path: Path) -> bool:
        """Import configuration from a file."""
        try:
            with open(file_path, 'r') as f:
                new_config = yaml.safe_load(f)
            self.config = new_config
            self._validate_config()
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Error importing config: {e}")
            return False