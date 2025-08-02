# mpo_model.py
# Defines core business entities and logic shared across MVC components.

from datetime import date
from typing import List, Optional, Dict
import logging


class ModelError(Exception):
    """Custom exception for model-related errors."""
    pass


class Prayer:
    """Represents a prayer in the My Prayers application."""

    def __init__(self, prayer: str, create_date: Optional[str] = None, answer_date: Optional[str] = None,
                 category: str = "General", answer: Optional[str] = None, display_count: int = 0):
        if not prayer:
            raise ModelError("Prayer text cannot be empty")
        if category is None:
            raise ModelError("Category cannot be None")

        self._prayer = prayer
        self._create_date = create_date or date.today().strftime("%d-%b-%Y")
        self._answer_date = answer_date
        self._category = category
        self._answer = answer
        self._display_count = display_count if display_count >= 0 else 0

    @property
    def prayer(self) -> str:
        return self._prayer

    @property
    def create_date(self) -> str:
        return self._create_date

    @property
    def answer_date(self) -> Optional[str]:
        return self._answer_date

    @answer_date.setter
    def answer_date(self, value: Optional[str]):
        self._answer_date = value

    @property
    def category(self) -> str:
        return self._category

    @property
    def answer(self) -> Optional[str]:
        return self._answer

    @answer.setter
    def answer(self, value: Optional[str]):
        self._answer = value

    @property
    def display_count(self) -> int:
        return self._display_count

    @display_count.setter
    def display_count(self, value: int):
        if value < 0:
            raise ModelError("Display count cannot be negative")
        self._display_count = value


class Category:
    """Represents a category to classify prayers."""

    def __init__(self, category: str, count: int = 0, weight: int = 1):
        if not category:
            raise ModelError("Category name cannot be empty")
        if count < 0:
            raise ModelError("Category count cannot be negative")
        if weight < 1:
            raise ModelError("Category weight must be at least 1")

        self._category = category
        self._category_display_count = count
        self._category_weight = weight
        self._category_prayer_list: List[Prayer] = []

    @property
    def category(self) -> str:
        return self._category

    @property
    def category_display_count(self) -> int:
        return self._category_display_count

    @category_display_count.setter
    def category_display_count(self, value: int):
        if value < 0:
            raise ModelError("Category display count cannot be negative")
        self._category_display_count = value

    @property
    def category_weight(self) -> int:
        return self._category_weight

    @property
    def category_prayer_list(self) -> List[Prayer]:
        return self._category_prayer_list

    @category_prayer_list.setter
    def category_prayer_list(self, value: List[Prayer]):
        self._category_prayer_list = value


class Panel:
    """Represents a display screen with a header and paragraphs."""

    def __init__(self, panel_seq: int, panel_header: str, pgraph_list: List['PanelPgraph']):
        if panel_seq < 0:
            raise ModelError("Panel sequence cannot be negative")
        if not panel_header:
            raise ModelError("Panel header cannot be empty")
        if not all(isinstance(p, PanelPgraph) for p in pgraph_list):
            raise ModelError("All items in pgraph_list must be PanelPgraph objects")

        self._panel_seq = panel_seq
        self._panel_header = panel_header
        self._pgraph_list = pgraph_list

    @property
    def panel_seq(self) -> int:
        return self._panel_seq

    @property
    def panel_header(self) -> str:
        return self._panel_header

    @property
    def pgraph_list(self) -> List['PanelPgraph']:
        return self._pgraph_list


class PanelPgraph:
    """Represents a paragraph of text for a Panel."""

    def __init__(self, pgraph_seq: int, verse: Optional[str], text: str):
        if pgraph_seq < 0:
            raise ModelError("Paragraph sequence cannot be negative")
        if not text:
            raise ModelError("Paragraph text cannot be empty")

        self._pgraph_seq = pgraph_seq
        self._verse = verse
        self._text = text

    @property
    def pgraph_seq(self) -> int:
        return self._pgraph_seq

    @property
    def verse(self) -> Optional[str]:
        return self._verse

    @property
    def text(self) -> str:
        return self._text


class AppParams:
    """Stores global application parameters from params.json."""

    def __init__(self, params_dict: Dict):
        required_keys = [
            'id', 'id_desc', 'app', 'app_desc', 'last_panel_set', 'last_panel_set_desc',
            'install_path', 'install_path_desc', 'past_prayer_display_count',
            'past_prayer_display_count_desc', 'prayer_streak', 'prayer_streak_desc',
            'last_prayer_date', 'last_prayer_date_desc'
        ]
        if not all(key in params_dict for key in required_keys):
            missing = [key for key in required_keys if key not in params_dict]
            raise ModelError(f"Missing required parameters: {missing}")

        self._id = params_dict['id']
        self._id_desc = params_dict['id_desc']
        self._app = params_dict['app']
        self._app_desc = params_dict['app_desc']
        self._last_panel_set = params_dict['last_panel_set']
        self._last_panel_set_desc = params_dict['last_panel_set_desc']
        self._install_path = params_dict['install_path']
        self._install_path_desc = params_dict['install_path_desc']
        self._past_prayer_display_count = params_dict['past_prayer_display_count']
        self._past_prayer_display_count_desc = params_dict['past_prayer_display_count_desc']
        self._prayer_streak = params_dict['prayer_streak']
        self._prayer_streak_desc = params_dict['prayer_streak_desc']
        self._last_prayer_date = params_dict['last_prayer_date']
        self._last_prayer_date_desc = params_dict['last_prayer_date_desc']

    @property
    def id(self) -> str:
        return self._id

    @property
    def last_panel_set(self) -> str:
        return self._last_panel_set

    @last_panel_set.setter
    def last_panel_set(self, value: str):
        self._last_panel_set = value

    @property
    def install_path(self) -> str:
        return self._install_path

    @property
    def past_prayer_display_count(self) -> int:
        return self._past_prayer_display_count

    @property
    def prayer_streak(self) -> int:
        return self._prayer_streak

    @prayer_streak.setter
    def prayer_streak(self, value: int):
        if value < 0:
            raise ModelError("Prayer streak cannot be negative")
        self._prayer_streak = value

    @property
    def last_prayer_date(self) -> str:
        return self._last_prayer_date

    @last_prayer_date.setter
    def last_prayer_date(self, value: str):
        self._last_prayer_date = value


class PrayerSession:
    """Tracks details about a prayer session."""

    def __init__(self, session_date: Optional[str] = None):
        self._session_date = session_date or date.today().strftime("%d-%b-%Y")
        self._new_prayer_added_count = 0
        self._past_prayer_prayed_count = 0
        self._answered_prayer_count = 0

    @property
    def session_date(self) -> str:
        return self._session_date

    @property
    def new_prayer_added_count(self) -> int:
        return self._new_prayer_added_count

    @new_prayer_added_count.setter
    def new_prayer_added_count(self, value: int):
        if value < 0:
            raise ModelError("New prayer count cannot be negative")
        self._new_prayer_added_count = value

    @property
    def past_prayer_prayed_count(self) -> int:
        return self._past_prayer_prayed_count

    @past_prayer_prayed_count.setter
    def past_prayer_prayed_count(self, value: int):
        if value < 0:
            raise ModelError("Past prayer prayed count cannot be negative")
        self._past_prayer_prayed_count = value

    @property
    def answered_prayer_count(self) -> int:
        return self._answered_prayer_count

    @answered_prayer_count.setter
    def answered_prayer_count(self, value: int):
        if value < 0:
            raise ModelError("Answered prayer count cannot be negative")
        self._answered_prayer_count = value


class State:
    """Represents a state in the application's state machine."""

    def __init__(self, name: str, action_event: str, to_state: Optional[str] = None, auto_trigger: Optional[bool] = False):
        """
        Initialize a state.

        Args:
            name (str): Name of the state.
            action_event (str): Event that triggers this state.
            to_state (Optional[str]): Target state for the transition.
            auto_trigger (str): Whether the action_event should be triggered automatically (True or False).

        Raises:
            ModelError: If name or action_event is empty.
        """
        if not name:
            raise ModelError("State name cannot be empty")
        if not action_event:
            raise ModelError("Action event cannot be empty")
        self._name = name
        self._action_event = action_event
        self._to_state = to_state
        self._auto_trigger = auto_trigger

    @property
    def name(self) -> str:
        return self._name

    @property
    def action_event(self) -> str:
        return self._action_event

    @property
    def to_state(self) -> Optional[str]:
        return self._to_state

    @property
    def auto_trigger(self) -> bool:
        return self._auto_trigger


class StateMachine:
    """Manages the finite state machine for application navigation."""

    def __init__(self, states_data: List[Dict]):
        """
        Initialize the state machine with state data.

        Args:
            states_data (List[Dict]): List of dictionaries with state data
                                     (e.g., [{"name": "WELCOME", "action_event": "get_continue", "to_state": "HONOR GOD", "auto_trigger": "False"}, ...]).

        Raises:
            ModelError: If states_data is empty or validation fails.
        """
        if not states_data:
            raise ModelError("States data cannot be empty")

        self._states: List[State] = []
        for data in states_data:
            if not all(key in data for key in ['name', 'action_event']):
                raise ModelError(f"Invalid state data: Missing required fields in {data}")
            state = State(
                name=data['name'],
                action_event=data['action_event'],
                to_state=data.get('to_state'),
                auto_trigger=data.get('auto_trigger', 'False')
            )
            self._states.append(state)
        self._current_state: Optional[State] = self._states[0] if self._states else None
        if not self.validate():
            raise ModelError("State machine validation failed")

    def validate(self) -> bool:
        """Validate the state machine configuration."""
        required_states = {'WELCOME', 'HONOR GOD', 'MY CONCERNS', 'prayers_done', "GOD'S WILL", 'CLOSING'}
        required_actions = {'get_new_prayers', 'get_past_prayers', 'quit_app', 'get_continue'}
        state_names = {state.name for state in self._states}
        action_events = {state.action_event for state in self._states}
        missing_states = required_states - state_names
        missing_actions = required_actions - action_events
        if missing_states:
            logging.error(f"Missing required states: {missing_states}")
        if missing_actions:
            logging.error(f"Missing required actions: {missing_actions}")
        return not missing_states and not missing_actions

    def transition(self, action_event: str) -> Optional[State]:
        """
        Transition to the next state based on the action event.

        Args:
            action_event (str): Event triggering the transition.

        Returns:
            Optional[State]: The new current state, or None if no transition.

        Raises:
            ModelError: If no valid transition exists.
        """
        for state in self._states:
            if state.name == self._current_state.name and state.action_event == action_event:
                self._current_state = next((s for s in self._states if s.name == state.to_state), None)
                return self._current_state
        raise ModelError(f"No valid transition for action {action_event} from state {self._current_state.name}")

    @property
    def current_state(self) -> Optional[State]:
        """
        Get the current state.

        Returns:
            Optional[State]: The current state object, or None if not set.
        """
        return self._current_state