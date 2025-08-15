# mpo_model.py

from datetime import date
from typing import List, Optional, Dict
import logging


class ModelError(Exception):
    """Custom exception for model-related errors."""
    pass


class Prayer:
    """Represents a prayer in the My Prayers application."""

    def __init__(self, prayer: str, create_date: Optional[str] = None, answer_date: Optional[str] = None,
                 category: str = "Other", answer: Optional[str] = None, display_count: int = 0):
        if not prayer:
            raise ModelError("Prayer text cannot be empty")
        if category is None:
            raise ModelError("Category cannot be None")

        self._prayer: str = prayer
        self._create_date: str = create_date or date.today().strftime("%d-%b-%Y")
        self._answer_date: Optional[str] = answer_date
        self._category: str = category
        self._answer: Optional[str] = answer
        self._display_count: int = display_count if display_count >= 0 else 0

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

        self._category: str = category
        self._category_display_count: int = count
        self._category_weight: int = weight
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

        self._panel_seq: int = panel_seq
        self._panel_header: str = panel_header
        self._pgraph_list: List['PanelPgraph'] = pgraph_list or []

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
    """Represents a paragraph in a Panel, with optional verse and text."""

    def __init__(self, pgraph_seq: int, verse: Optional[str] = None, text: Optional[str] = None):
        if pgraph_seq < 0:
            raise ModelError("Paragraph sequence cannot be negative")

        self._pgraph_seq: int = pgraph_seq
        self._verse: Optional[str] = verse
        self._text: Optional[str] = text

    @property
    def pgraph_seq(self) -> int:
        return self._pgraph_seq

    @property
    def verse(self) -> Optional[str]:
        return self._verse

    @property
    def text(self) -> Optional[str]:
        return self._text


class AppParams:
    """Represents application parameters."""

    def __init__(self, id: str, id_desc: str, app: str, app_desc: str, install_path: str,
                 install_path_desc: str, data_file_path: str, data_file_path_desc: str,
                 past_prayer_display_count: int, past_prayer_display_count_desc: str):
        self._id: str = id
        self._id_desc: str = id_desc
        self._app: str = app
        self._app_desc: str = app_desc
        self._install_path: str = install_path
        self._install_path_desc: str = install_path_desc
        self._data_file_path: str = data_file_path
        self._data_file_path_desc: str = data_file_path_desc
        self._past_prayer_display_count: int = past_prayer_display_count
        self._past_prayer_display_count_desc: str = past_prayer_display_count_desc

    @property
    def id(self) -> str:
        return self._id

    @property
    def id_desc(self) -> str:
        return self._id_desc

    @property
    def app(self) -> str:
        return self._app

    @property
    def app_desc(self) -> str:
        return self._app_desc

    @property
    def install_path(self) -> str:
        return self._install_path

    @property
    def install_path_desc(self) -> str:
        return self._install_path_desc

    @property
    def data_file_path(self) -> str:
        return self._data_file_path

    @property
    def data_file_path_desc(self) -> str:
        return self._data_file_path_desc

    @property
    def past_prayer_display_count(self) -> int:
        return self._past_prayer_display_count

    @property
    def past_prayer_display_count_desc(self) -> str:
        return self._past_prayer_display_count_desc


class PrayerSession:
    """Represents a session of prayer activity."""

    def __init__(self, last_prayer_date: Optional[str] = None, prayer_streak: int = 0,
                 last_panel_set: Optional[str] = None):
        self._last_prayer_date: Optional[str] = last_prayer_date
        self._prayer_streak: int = prayer_streak if prayer_streak >= 0 else 0
        self._last_panel_set: Optional[str] = last_panel_set
        self._new_prayer_added_count: int = 0
        self._past_prayer_prayed_count: int = 0
        self._answered_prayer_count: int = 0

    @property
    def last_prayer_date(self) -> Optional[str]:
        return self._last_prayer_date

    @last_prayer_date.setter
    def last_prayer_date(self, value: Optional[str]):
        self._last_prayer_date = value

    @property
    def prayer_streak(self) -> int:
        return self._prayer_streak

    @prayer_streak.setter
    def prayer_streak(self, value: int):
        if value < 0:
            raise ModelError("Prayer streak cannot be negative")
        self._prayer_streak = value

    @property
    def last_panel_set(self) -> Optional[str]:
        return self._last_panel_set

    @last_panel_set.setter
    def last_panel_set(self, value: Optional[str]):
        self._last_panel_set = value

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

    def __init__(self, state: str, action_event: str, to_state: Optional[str] = None, auto_trigger: bool = False):
        if not state:
            raise ModelError("State cannot be empty")
        if not action_event:
            raise ModelError("Action event cannot be empty")

        self._state: str = state
        self._action_event: str = action_event
        self._to_state: Optional[str] = to_state
        self._auto_trigger: bool = auto_trigger

    @property
    def state(self) -> str:
        return self._state

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
                                     (e.g., [{"state": "1", "action_event": "get_continue", "to_state": "2", "auto_trigger": False}, ...]).

        Raises:
            ModelError: If states_data is empty or validation fails.
        """
        if not states_data:
            raise ModelError("States data cannot be empty")

        self._states: List[State] = []
        for data in states_data:
            if not all(key in data for key in ['state', 'action_event']):
                raise ModelError(f"Invalid state data: Missing required fields in {data}")
            state = State(
                state=data['state'],
                action_event=data['action_event'],
                to_state=data.get('to_state'),
                auto_trigger=data.get('auto_trigger', False)
            )
            self._states.append(state)
        self._current_state: Optional[State] = self._states[0] if self._states else None
        if not self.validate():
            raise ModelError("State machine validation failed")

    def validate(self) -> bool:
        """Validate the state machine configuration."""
        required_states = {'1', '2', '3', '4', '5', '6'}
        required_actions = {'get_new_prayers', 'get_past_prayers', 'quit_app', 'get_continue'}
        state_names = {state.state for state in self._states}
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
            if state.state == self._current_state.state and state.action_event == action_event:
                self._current_state = next((s for s in self._states if s.state == state.to_state), None)
                return self._current_state
        raise ModelError(f"No valid transition for action {action_event} from state {self._current_state.state}")

    @property
    def current_state(self) -> Optional[State]:
        """
        Get the current state.

        Returns:
            Optional[State]: The current state object, or None if not set.
        """
        return self._current_state