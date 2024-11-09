# src/engine/input_handler.py

from enum import Enum, auto
from typing import Optional, Dict, Any, Set
import tcod.event
from dataclasses import dataclass
from src.utils.logger_config import logger
from engine.message_manager import MessageManager


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
	
	def __init__(self, context: tcod.context.Context, message_manager: Optional['MessageManager'] = None, debug: bool = False):
		super().__init__()
		self.context = context
		self.current_state = GameState.GAME_WORLD
		self.message_manager = message_manager
		self.debug = debug
		# Track currently pressed keys to handle multiple key inputs
		self.pressed_keys: Set[int] = set()
        
		# Define key mappings - can be loaded from config later
		self.MOVEMENT_KEYS = {
			# Arrow keys
			tcod.event.KeySym.UP: GameAction("move", {"dx": 0, "dy": -1}),
			tcod.event.KeySym.DOWN: GameAction("move", {"dx": 0, "dy": 1}),
			tcod.event.KeySym.LEFT: GameAction("move", {"dx": -1, "dy": 0}),
			tcod.event.KeySym.RIGHT: GameAction("move", {"dx": 1, "dy": 0}),
			# Vi keys
			tcod.event.KeySym.k: GameAction("move", {"dx": 0, "dy": -1}),
			tcod.event.KeySym.j: GameAction("move", {"dx": 0, "dy": 1}),
			tcod.event.KeySym.h: GameAction("move", {"dx": -1, "dy": 0}),
			tcod.event.KeySym.l: GameAction("move", {"dx": 1, "dy": 0}),
			# Diagonal movement
			tcod.event.KeySym.y: GameAction("move", {"dx": -1, "dy": -1}),
			tcod.event.KeySym.u: GameAction("move", {"dx": 1, "dy": -1}),
			tcod.event.KeySym.b: GameAction("move", {"dx": -1, "dy": 1}),
			tcod.event.KeySym.n: GameAction("move", {"dx": 1, "dy": 1}),
		}
        
		self.COMMAND_KEYS = {
			tcod.event.KeySym.i: GameAction("open_inventory"),
			tcod.event.KeySym.c: GameAction("open_character"),
			tcod.event.KeySym.ESCAPE: GameAction("escape"),
			tcod.event.KeySym.RETURN: GameAction("confirm"),
			tcod.event.KeySym.F11: GameAction("toggle_fullscreen"),
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
			self._debug_message(f"Key pressed: {event.sym}")
		
		key = event.sym
		self.pressed_keys.add(key)

		# Handle modifier keys
		mod = event.mod
		shift = bool(mod & tcod.event.KMOD_SHIFT)
		ctrl = bool(mod & tcod.event.KMOD_CTRL)
		alt = bool(mod & tcod.event.KMOD_ALT)

		# State-specific handling
		if self.current_state == GameState.MAIN_MENU:
			return self._handle_main_menu(key)
		elif self.current_state == GameState.GAME_WORLD:
			return self._handle_game_world(key, shift, ctrl, alt)
		elif self.current_state == GameState.INVENTORY:
			return self._handle_inventory(key)
		elif self.current_state == GameState.CHARACTER_SCREEN:
			return self._handle_character_screen(key)
		elif self.current_state == GameState.DIALOGUE:
			return self._handle_dialogue(key)
		elif self.current_state == GameState.PAUSED:
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
		"""Handle input specific to the main menu state."""
		if key == tcod.event.KeySym.ESCAPE:
			return GameAction("quit")
		elif key == tcod.event.KeySym.RETURN:
			return GameAction("start_game")
		return None

	def _handle_game_world(self, key: int, shift: bool, ctrl: bool, alt: bool) -> Optional[GameAction]:
		"""Handle input specific to the game world state."""
		# Check movement keys first
		if key in self.MOVEMENT_KEYS:
			# Modify movement based on modifiers (e.g., shift for sprint)
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
			return GameAction("close_inventory")
		elif key == tcod.event.KeySym.i:
			return GameAction("close_inventory")
		return None

	def _handle_character_screen(self, key: int) -> Optional[GameAction]:
		"""Handle input specific to the character screen state."""
		if key == tcod.event.KeySym.ESCAPE:
			return GameAction("close_character")
		elif key == tcod.event.KeySym.c:
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

	def set_game_state(self, new_state: GameState) -> None:
		"""Change the current game state."""
		self.current_state = new_state

	def _debug_message(self, message: str) -> None:
		"""Send debug messages to the message manager if debug mode is enabled."""
		if self.debug and self.message_manager:
			self.message_manager.add_message(f"DEBUG: {message}", fg=(128, 128, 255))