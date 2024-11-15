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

