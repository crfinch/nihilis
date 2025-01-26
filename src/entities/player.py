from dataclasses import dataclass
from typing import Tuple

@dataclass
class Player:
    """
    Represents the player character in the game world.
    
    Attributes:
        x (int): The player's x-coordinate in the world
        y (int): The player's y-coordinate in the world
        char (str): The character used to represent the player on the map
        color (Tuple[int, int, int]): RGB color tuple for rendering the player
    """
    x: int
    y: int
    char: str = "@"
    color: Tuple[int, int, int] = (255, 200, 255)  # lavender color by default
    
    def move(self, dx: int, dy: int) -> None:
        """
        Move the player by the given delta values.
        
        Args:
            dx (int): Change in x-coordinate
            dy (int): Change in y-coordinate
        """
        self.x += dx
        self.y += dy
    
    def teleport(self, x: int, y: int) -> None:
        """
        Instantly move the player to the specified coordinates.
        
        Args:
            x (int): New x-coordinate
            y (int): New y-coordinate
        """
        self.x = x
        self.y = y
    
    @property
    def position(self) -> Tuple[int, int]:
        """Get the current position of the player."""
        return (self.x, self.y)
