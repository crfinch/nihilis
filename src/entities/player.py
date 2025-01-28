from dataclasses import dataclass, field
from typing import Tuple, Set

@dataclass
class Player:
    """
    Represents the player character in the game world.
    
    Attributes:
        x (int): The player's x-coordinate in the world
        y (int): The player's y-coordinate in the world
        char (str): The character used to represent the player on the map
        color (Tuple[int, int, int]): RGB color tuple for rendering the player
        visited_locations (Set[Tuple[int, int]]): Set of coordinates the player has visited
    """
    x: int
    y: int
    char: str = "@"
    color: Tuple[int, int, int] = (255, 200, 255)  # lavender color by default
    visited_locations: Set[Tuple[int, int]] = field(default_factory=set)
    
    def move(self, dx: int, dy: int) -> None:
        """
        Move the player by the given delta values.
        
        Args:
            dx (int): Change in x-coordinate
            dy (int): Change in y-coordinate
        """
        self.x += dx
        self.y += dy
        self.visited_locations.add((self.x, self.y))
    
    def teleport(self, x: int, y: int) -> None:
        """
        Instantly move the player to the specified coordinates.
        
        Args:
            x (int): New x-coordinate
            y (int): New y-coordinate
        """
        self.x = x
        self.y = y
        self.visited_locations.add((x, y))
    
    @property
    def position(self) -> Tuple[int, int]:
        """Get the current position of the player."""
        return (self.x, self.y)
    
    def has_visited(self, position: Tuple[int, int]) -> bool:
        """
        Check if the player has visited a specific position.
        
        Args:
            position (Tuple[int, int]): The position to check
            
        Returns:
            bool: True if the player has visited this position, False otherwise
        """
        return position in self.visited_locations
