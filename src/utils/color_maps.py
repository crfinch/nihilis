# src/utils/color_maps.py
def height_to_color(height: float) -> tuple[int, int, int]:
    """Convert a height value to a color."""
    if height < 0.3:  # Deep water
        return (0, 0, 139)
    elif height < 0.4:  # Shallow water
        return (0, 0, 255)
    elif height < 0.5:  # Plains
        return (34, 139, 34)
    elif height < 0.7:  # Hills
        return (139, 69, 19)
    else:  # Mountains
        return (128, 128, 128)

# src/debug/commands.py
from src.game_states.map_viewer_state import MapViewerState

def cmd_view_heightmap(engine, args):
    """Debug command to view the current world's heightmap."""
    if engine.world and engine.world.heightmap is not None:
        return MapViewerState(engine, engine.world.heightmap)
    else:
        engine.message_log.add_message("No heightmap available to view.", fg=(255, 0, 0))
        return None