# src/engine/input_handler.py

from enum import Enum, auto
from typing import Optional, Dict, Any, Set, Tuple
import tcod.event
import tcod.context
from dataclasses import dataclass
from src.utils.logger_config import logger
from src.engine.message_manager import MessageManager
from src.engine.game_state_manager import GameStateManager


class GameState(Enum):
	"""Enum representing different game states that affect input handling."""
	MAIN_MENU = auto()
	GAME_WORLD = auto()
	CHARACTER_SCREEN = auto()
	INVENTORY = auto()
	DIALOGUE = auto()
	PAUSED = auto()

@dataclass
class GameAction:
	"""Represents an action triggered by input."""
	action_type: str
	params: Dict[str, Any] = None

	def __post_init__(self):
		if self.params is None:
			self.params = {}

class InputHandler(tcod.event.EventDispatch[Optional[GameAction]]):
	"""Handles input events and converts them into game actions."""
	
	def __init__(self, context: tcod.context.Context,  # Change this type hint
	             state_manager: GameStateManager,
	             message_manager: Optional['MessageManager'] = None, 
	             config_manager = None,
	             debug: bool = False):
		super().__init__()
		self.context = context
		self.state_manager = state_manager
		self.message_manager = message_manager
		self.debug = debug

		# Track currently pressed keys to handle multiple key inputs
		self.pressed_keys: Set[int] = set()
        
		# Get keybindings from config manager if available
		if config_manager:
			key_config = config_manager.get_keybindings()
			
			# Initialize empty dictionaries
			self.MOVEMENT_KEYS = {}
			self.COMMAND_KEYS = {}
			
			# Handle movement keys
			movement_mappings = {
				'move_up': (0, -1),
				'move_down': (0, 1),
				'move_left': (-1, 0),
				'move_right': (1, 0),
				'move_up_left': (-1, -1),
				'move_up_right': (1, -1),
				'move_down_left': (-1, 1),
				'move_down_right': (1, 1)
			}
			
			# Process movement keys
			for direction, (dx, dy) in movement_mappings.items():
				keys = getattr(key_config, direction)
				for key in keys:
					keysym = getattr(tcod.event.KeySym, key)
					self.MOVEMENT_KEYS[keysym] = GameAction("move", {"dx": dx, "dy": dy})
			
			# Process command keys
			command_mappings = {
				'inventory': 'open_inventory',
				'character': 'open_character',
				'quit': 'escape',
				'debug_overlay': 'toggle_debug'
			}
			
			for config_key, action_type in command_mappings.items():
				if hasattr(key_config, config_key):
					keys = getattr(key_config, config_key)
					for key in keys:
						keysym = getattr(tcod.event.KeySym, key)
						self.COMMAND_KEYS[keysym] = GameAction(action_type)

		else:
			# Fallback to default keybindings
			self.MOVEMENT_KEYS = {
				# Cardinal directions
				tcod.event.KeySym.UP: GameAction("move", {"dx": 0, "dy": -1}),
				tcod.event.KeySym.DOWN: GameAction("move", {"dx": 0, "dy": 1}),
				tcod.event.KeySym.LEFT: GameAction("move", {"dx": -1, "dy": 0}),
				tcod.event.KeySym.RIGHT: GameAction("move", {"dx": 1, "dy": 0}),

				# Vi keys - cardinal
				tcod.event.KeySym.k: GameAction("move", {"dx": 0, "dy": -1}),
				tcod.event.KeySym.j: GameAction("move", {"dx": 0, "dy": 1}),
				tcod.event.KeySym.h: GameAction("move", {"dx": -1, "dy": 0}),
				tcod.event.KeySym.l: GameAction("move", {"dx": 1, "dy": 0}),
				
				# Vi keys - diagonal
				tcod.event.KeySym.y: GameAction("move", {"dx": -1, "dy": -1}),
				tcod.event.KeySym.u: GameAction("move", {"dx": 1, "dy": -1}),
				tcod.event.KeySym.b: GameAction("move", {"dx": -1, "dy": 1}),
				tcod.event.KeySym.n: GameAction("move", {"dx": 1, "dy": 1}),
			}
			
			self.COMMAND_KEYS = {
				tcod.event.KeySym.i: GameAction("open_inventory"),
				tcod.event.KeySym.c: GameAction("open_character"),
				tcod.event.KeySym.ESCAPE: GameAction("escape"),
			}

	def dispatch(self, event: tcod.event.Event) -> Optional[GameAction]:
		"""Override dispatch to include debug information."""
		action = super().dispatch(event)
		if action and self.debug:
			self._debug_message(f"Input: {event.__class__.__name__} -> Action: {action.action_type} - Params: {action.params}")
		return action

	def ev_quit(self, event: tcod.event.Quit) -> Optional[GameAction]:
		"""Handle window close button."""
		return GameAction("quit")

	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[GameAction]:
		"""Handle key press events based on current game state."""
		if self.debug:
			self._debug_message(f"Key pressed: {event.sym} (type: {type(event.sym)})")
		
		key = event.sym
		self.pressed_keys.add(key)

		# Debug: Check if key is in movement keys
		if self.debug:
			self._debug_message(f"Movement keys: {self.MOVEMENT_KEYS}")
			if key in self.MOVEMENT_KEYS:
				self._debug_message(f"Movement key detected: {key} -> {self.MOVEMENT_KEYS[key]}")
			else:
				self._debug_message(f"Key {key} not found in movement keys")

		# Handle modifier keys
		mod = event.mod
		shift = bool(mod & tcod.event.KMOD_SHIFT)
		ctrl = bool(mod & tcod.event.KMOD_CTRL)
		alt = bool(mod & tcod.event.KMOD_ALT)

		# State-specific handling
		if self.state_manager.get_current_state() == GameState.MAIN_MENU:
			return self._handle_main_menu(key)
		elif self.state_manager.get_current_state() == GameState.GAME_WORLD:
			return self._handle_game_world(key, shift, ctrl, alt)
		elif self.state_manager.get_current_state() == GameState.INVENTORY:
			return self._handle_inventory(key)
		elif self.state_manager.get_current_state() == GameState.CHARACTER_SCREEN:
			return self._handle_character_screen(key)
		elif self.state_manager.get_current_state() == GameState.DIALOGUE:
			return self._handle_dialogue(key)
		elif self.state_manager.get_current_state() == GameState.PAUSED:
			return self._handle_paused(key)
			
		return None

	def ev_keyup(self, event: tcod.event.KeyUp) -> None:
		"""Handle key release events."""
		self.pressed_keys.discard(event.sym)

	def ev_mousemotion(self, event: tcod.event.MouseMotion) -> Optional[GameAction]:
		"""Handle mouse movement."""
		try:
			return GameAction("mouse_move", {
				"x": event.motion.x,	
				"y": event.motion.y,

				"pixel_x": event.position.x,
				"pixel_y": event.position.y
			})
		except AttributeError:
			logger.warning("Mouse motion event received without valid coordinates")
			return None

	def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[GameAction]:
		"""Handle mouse button press."""
		try:
			return GameAction("mouse_click", {
				"button": event.button,
				"x": event.position.x,
				"y": event.position.y
			})
		except AttributeError:
			logger.warning("Mouse button event received without valid coordinates")
			return None

	def _handle_main_menu(self, key: int) -> Optional[GameAction]:
		if key == tcod.event.KeySym.ESCAPE:
			return GameAction("quit")
		elif key == tcod.event.KeySym.RETURN:
			self.state_manager.change_state(GameState.GAME_WORLD)
			if self.message_manager:
				self.message_manager.add_message("Welcome to the game world!", fg=(255, 255, 0))
			return GameAction("start_game")
		return None

	def _handle_game_world(self, key: int, shift: bool, ctrl: bool, alt: bool) -> Optional[GameAction]:
		"""Handle input specific to the game world state."""
		if key == tcod.event.KeySym.ESCAPE:
			self.state_manager.change_state(GameState.MAIN_MENU)
			if self.message_manager:
				self.message_manager.add_message("Returned to main menu", fg=(255, 255, 0))
			return GameAction("escape")
		elif key == tcod.event.KeySym.i:
			self.state_manager.change_state(GameState.INVENTORY)
			if self.message_manager:
				self.message_manager.add_message("Opening inventory...", fg=(200, 200, 200))
			return GameAction("open_inventory")
		elif key == tcod.event.KeySym.c:
			self.state_manager.change_state(GameState.CHARACTER_SCREEN)
			if self.message_manager:
				self.message_manager.add_message("Opening character screen...", fg=(200, 200, 200))
			return GameAction("open_character")
		# Check movement keys first
		if key in self.MOVEMENT_KEYS:
			if self.debug:
				self._debug_message(f"Movement key detected: {key}")
			action = self.MOVEMENT_KEYS[key]
			if shift:
				action.params["sprint"] = True
			return action
			
		# Then check command keys
		if key in self.COMMAND_KEYS:
			return self.COMMAND_KEYS[key]
			
		# Handle combined key presses
		if ctrl and key == tcod.event.KeySym.s:
			return GameAction("save_game")
		if ctrl and key == tcod.event.KeySym.l:
			return GameAction("load_game")
			
		return None

	def _handle_inventory(self, key: int) -> Optional[GameAction]:
		"""Handle input specific to the inventory state."""
		if key == tcod.event.KeySym.ESCAPE:
			self.state_manager.change_state(GameState.GAME_WORLD)
			if self.message_manager:
				self.message_manager.add_message("Closed inventory screen...", fg=(200, 200, 200))
			return GameAction("close_inventory")
		elif key == tcod.event.KeySym.i:
			self.state_manager.change_state(GameState.GAME_WORLD)
			if self.message_manager:
				self.message_manager.add_message("Closed inventory screen...", fg=(200, 200, 200))
			return GameAction("close_inventory")
		return None

	def _handle_character_screen(self, key: int) -> Optional[GameAction]:
		if key == tcod.event.KeySym.ESCAPE:
			self.state_manager.change_state(GameState.GAME_WORLD)
			if self.message_manager:
				self.message_manager.add_message("Closed character screen...", fg=(200, 200, 200))
			return GameAction("close_character")
		elif key == tcod.event.KeySym.c:
			self.state_manager.change_state(GameState.GAME_WORLD)
			if self.message_manager:
				self.message_manager.add_message("Closed character screen...", fg=(200, 200, 200))
			return GameAction("close_character")
		return None

	def _handle_dialogue(self, key: int) -> Optional[GameAction]:
		"""Handle input specific to dialogue state."""
		if key == tcod.event.KeySym.ESCAPE:
			return GameAction("end_dialogue")
		elif key == tcod.event.KeySym.RETURN:
			return GameAction("advance_dialogue")
		return None

	def _handle_paused(self, key: int) -> Optional[GameAction]:
		"""Handle input specific to paused state."""
		if key == tcod.event.KeySym.ESCAPE:
			return GameAction("unpause")
		elif key == tcod.event.KeySym.p:
			return GameAction("unpause")
		return None

	def _debug_message(self, message: str) -> None:
		"""Send debug messages to the message manager if debug mode is enabled."""
		if self.debug and self.message_manager:
			self.message_manager.add_message(f"DEBUG: {message}", fg=(128, 128, 255))

