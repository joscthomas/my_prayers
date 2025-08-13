# mpo_model.py
# Defines core business entities and logic shared across MVC components.

"""
This module defines the main data structures and rules for the My Prayers application. It includes classes like
Prayer (for storing prayer details), Category (for grouping prayers), Panel (for display screens), and StateMachine
(for guiding the app's steps). These classes hold the app's core 'business logic,' such as validating prayer
categories or managing state transitions. For learners, this is like the blueprint that describes what a prayer
'looks like' and how the app's parts fit together.
"""

from datetime import date
from typing import List, Optional, Dict
import logging


class ModelError(Exception):
    """
    Custom exception for errors in data model validation.

    Raised when data like prayer text or categories doesn't meet the app's rules, helping catch mistakes early.
    """


class Prayer:
    """
    Represents a prayer in the My Prayers application.

    Stores details like the prayer text, category, creation date, and how many times it's been shown.
    """

    def __init__(self, prayer: str, create_date: Optional[str] = None, answer_date: Optional[str] = None,
                 category: str = "Other", answer: Optional[str] = None, display_count: int = 0):
        """
        Initialize a Prayer object with text, dates, and category.

        Args:
            prayer (str): The text of the prayer.
            create_date (Optional[str]): Date the prayer was created (defaults to today).
            answer_date (Optional[str]): Date the prayer was answered (if any).
            category (str): Category of the prayer (defaults to 'Other').
            answer (Optional[str]): Answer to the prayer (if any).
            display_count (int): Number of times the prayer has been shown (defaults to 0).

        Raises:
            ModelError: If prayer text is empty, category is invalid, or display_count is negative.
        """
        if not prayer:
            raise ModelError("Prayer text cannot be empty")
        if category is None:
            raise ModelError("Category cannot be None")
        valid_categories = ["Praise", "Thanksgiving", "Confession", "Petition", "Intercession", "Other", "General"]
        if category not in valid_categories:
            raise ModelError("Invalid category")
        self._prayer: str = prayer
        self._create_date: str = create_date or date.today().strftime("%d-%b-%Y")
        self._answer_date: Optional[str] = answer_date
        self._category: str = category
        self._answer: Optional[str] = answer
        self._display_count: int = display_count if display_count >= 0 else 0

    @property
    def prayer(self) -> str:
        """
        Get the prayer text.

        Returns:
            str: The text of the prayer.
        """
        return self._prayer

    @property
    def create_date(self) -> str:
        """
        Get the creation date of the prayer.

        Returns:
            str: The date the prayer was created (format: DD-MMM-YYYY).
        """
        return self._create_date

    @property
    def answer_date(self) -> Optional[str]:
        """
        Get the date the prayer was answered.

        Returns:
            Optional[str]: The answer date, or None if not answered.
        """
        return self._answer_date

    @answer_date.setter
    def answer_date(self, value: Optional[str]):
        """
        Set the answer date for the prayer.

        Args:
            value (Optional[str]): The date the prayer was answered.
        """
        self._answer_date = value

    @property
    def category(self) -> str:
        """
        Get the prayer's category.

        Returns:
            str: The category of the prayer (e.g., 'Praise', 'Other').
        """
        return self._category

    @property
    def answer(self) -> Optional[str]:
        """
        Get the answer to the prayer.

        Returns:
            Optional[str]: The answer text, or None if not answered.
        """
        return self._answer

    @answer.setter
    def answer(self, value: Optional[str]):
        """
        Set the answer for the prayer.

        Args:
            value (Optional[str]): The answer text.
        """
        self._answer = value

    @property
    def display_count(self) -> int:
        """
        Get the number of times the prayer has been displayed.

        Returns:
            int: The display count.
        """
        return self._display_count

    @display_count.setter
    def display_count(self, value: int):
        """
        Set the display count for the prayer.

        Args:
            value (int): The new display count.

        Raises:
            ModelError: If the count is negative.
        """
        if value < 0:
            raise ModelError("Display count cannot be negative")
        self._display_count = value


class Category:
    """
    Represents a category to classify prayers.

    Groups prayers and tracks their importance (weight) and how often they're shown.
    """

    def __init__(self, category: str, count: int = 0, weight: int = 1):
        """
        Initialize a Category with name, count, and weight.

        Args:
            category (str): The name of the category (e.g., 'Praise').
            count (int): Number of times the category's prayers are shown (defaults to 0).
            weight (int): Priority of the category (defaults to 1).

        Raises:
            ModelError: If category name is empty, count is negative, or weight is less than 1.
        """
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
        """
        Get the category name.

        Returns:
            str: The name of the category.
        """
        return self._category

    @property
    def category_display_count(self) -> int:
        """
        Get the number of times the category's prayers have been shown.

        Returns:
            int: The display count for the category.
        """
        return self._category_display_count

    @category_display_count.setter
    def category_display_count(self, value: int):
        """
        Set the display count for the category.

        Args:
            value (int): The new display count.

        Raises:
            ModelError: If the count is negative.
        """
        if value < 0:
            raise ModelError("Category display count cannot be negative")
        self._category_display_count = value

    @property
    def category_weight(self) -> int:
        """
        Get the category's weight (priority).

        Returns:
            int: The weight of the category.
        """
        return self._category_weight

    @property
    def category_prayer_list(self) -> List[Prayer]:
        """
        Get the list of prayers in this category.

        Returns:
            List[Prayer]: The list of Prayer objects.
        """
        return self._category_prayer_list

    @category_prayer_list.setter
    def category_prayer_list(self, value: List[Prayer]):
        """
        Set the list of prayers for this category.

        Args:
            value (List[Prayer]): The new list of Prayer objects.
        """
        self._category_prayer_list = value


class Panel:
    """
    Represents a display screen with a header and paragraphs.

    Used to show text like instructions or prayer prompts on the screen.
    """

    def __init__(self, panel_seq: int, panel_header: str, pgraph_list: List['PanelPgraph']):
        """
        Initialize a Panel with sequence, header, and paragraphs.

        Args:
            panel_seq (int): The order of the panel (e.g., 1 for first).
            panel_header (str): The title of the panel.
            pgraph_list (List[PanelPgraph]): List of paragraph objects for the panel.

        Raises:
            ModelError: If panel_seq is negative, header is empty, or pgraph_list contains non-PanelPgraph items.
        """
        if panel_seq < 0:
            raise ModelError("Panel sequence cannot be negative")
        if not panel_header:
            raise ModelError("Panel header cannot be empty")
        if not all(isinstance(p, PanelPgraph) for p in pgraph_list):
            raise ModelError("All items in pgraph_list must be PanelPgraph objects")

        self._panel_seq: int = panel_seq
        self._panel_header: str = panel_header
        self._pgraph_list: List[PanelPgraph] = pgraph_list

    @property
    def panel_seq(self) -> int:
        """
        Get the panel's sequence number.

        Returns:
            int: The sequence number of the panel.
        """
        return self._panel_seq

    @property
    def panel_header(self) -> str:
        """
        Get the panel's header.

        Returns:
            str: The header text of the panel.
        """
        return self._panel_header

    @property
    def pgraph_list(self) -> List['PanelPgraph']:
        """
        Get the list of paragraphs in the panel.

        Returns:
            List[PanelPgraph]: The list of PanelPgraph objects.
        """
        return self._pgraph_list


class PanelPgraph:
    """
    Represents a paragraph of text for a Panel.

    Holds text and an optional Bible verse for display in a panel.
    """

    def __init__(self, pgraph_seq: int, verse: Optional[str], text: str):
        """
        Initialize a PanelPgraph with sequence, verse, and text.

        Args:
            pgraph_seq (int): The order of the paragraph in the panel.
            verse (Optional[str]): A Bible verse reference (if any).
            text (str): The text content of the paragraph.

        Raises:
            ModelError: If pgraph_seq is negative or text is empty.
        """
        if pgraph_seq < 0:
            raise ModelError("Paragraph sequence cannot be negative")
        if not text:
            raise ModelError("Paragraph text cannot be empty")

        self._pgraph_seq: int = pgraph_seq
        self._verse: Optional[str] = verse
        self._text: str = text

    @property
    def pgraph_seq(self) -> int:
        """
        Get the paragraph's sequence number.

        Returns:
            int: The sequence number of the paragraph.
        """
        return self._pgraph_seq

    @property
    def verse(self) -> Optional[str]:
        """
        Get the Bible verse reference for the paragraph.

        Returns:
            Optional[str]: The verse reference, or None if not set.
        """
        return self._verse

    @property
    def text(self) -> str:
        """
        Get the text content of the paragraph.

        Returns:
            str: The paragraph text.
        """
        return self._text


class AppParams:
    """
    Stores global application parameters from params.json.

    Holds settings like the number of past prayers to display and file paths.
    """

    def __init__(self, params_dict: Dict):
        """
        Initialize AppParams with a dictionary of parameters.

        Args:
            params_dict (Dict): Dictionary with required keys like 'id', 'app', and 'past_prayer_display_count'.

        Raises:
            ModelError: If required parameters are missing.
        """
        required_keys = [
            'id', 'id_desc', 'app', 'app_desc',
            'install_path', 'install_path_desc', 'data_file_path', 'data_file_path_desc',
            'past_prayer_display_count', 'past_prayer_display_count_desc'
        ]
        if not all(key in params_dict for key in required_keys):
            missing = [key for key in required_keys if key not in params_dict]
            raise ModelError(f"Missing required parameters: {missing}")

        self._id: str = params_dict['id']
        self._id_desc: str = params_dict['id_desc']
        self._app: str = params_dict['app']
        self._app_desc: str = params_dict['app_desc']
        self._install_path: str = params_dict['install_path']
        self._install_path_desc: str = params_dict['install_path_desc']
        self._data_file_path: str = params_dict['data_file_path']
        self._data_file_path_desc: str = params_dict['data_file_path_desc']
        self._past_prayer_display_count: int = params_dict['past_prayer_display_count']
        self._past_prayer_display_count_desc: str = params_dict['past_prayer_display_count_desc']

    @property
    def id(self) -> str:
        """
        Get the application ID.

        Returns:
            str: The unique ID of the application.
        """
        return self._id

    @property
    def id_desc(self) -> str:
        """
        Get the description of the application ID.

        Returns:
            str: The description of the ID.
        """
        return self._id_desc

    @property
    def app(self) -> str:
        """
        Get the application name.

        Returns:
            str: The name of the application.
        """
        return self._app

    @property
    def app_desc(self) -> str:
        """
        Get the application description.

        Returns:
            str: The description of the application.
        """
        return self._app_desc

    @property
    def install_path(self) -> str:
        """
        Get the installation path.

        Returns:
            str: The file path where the app is installed.
        """
        return self._install_path

    @property
    def install_path_desc(self) -> str:
        """
        Get the description of the installation path.

        Returns:
            str: The description of the install path.
        """
        return self._install_path_desc

    @property
    def data_file_path(self) -> str:
        """
        Get the data file path.

        Returns:
            str: The path where data files are stored.
        """
        return self._data_file_path

    @property
    def data_file_path_desc(self) -> str:
        """
        Get the description of the data file path.

        Returns:
            str: The description of the data file path.
        """
        return self._data_file_path_desc

    @property
    def past_prayer_display_count(self) -> int:
        """
        Get the number of past prayers to display.

        Returns:
            int: The number of past prayers shown per session.
        """
        return self._past_prayer_display_count

    @property
    def past_prayer_display_count_desc(self) -> str:
        """
        Get the description of the past prayer display count.

        Returns:
            str: The description of the display count setting.
        """
        return self._past_prayer_display_count_desc


class PrayerSession:
    """
    Tracks data for a single prayer session.

    Stores counts like new prayers added, past prayers reviewed, and the user's prayer streak.
    """

    def __init__(self, session_date: Optional[str] = None, new_prayer_added_count: int = 0,
                 past_prayer_prayed_count: int = 0, answered_prayer_count: int = 0,
                 last_prayer_date: Optional[str] = None, prayer_streak: int = 0,
                 last_panel_set: Optional[str] = None):
        """
        Initialize a PrayerSession with counts and dates.

        Args:
            session_date (Optional[str]): Date of the session (defaults to today).
            new_prayer_added_count (int): Number of new prayers added (defaults to 0).
            past_prayer_prayed_count (int): Number of past prayers reviewed (defaults to 0).
            answered_prayer_count (int): Number of prayers marked answered (defaults to 0).
            last_prayer_date (Optional[str]): Date of the last prayer session.
            prayer_streak (int): Number of consecutive days prayed (defaults to 0).
            last_panel_set (Optional[str]): Last panel set displayed.

        Raises:
            ModelError: If counts are negative.
        """
        self._session_date: str = session_date or date.today().strftime("%d-%b-%Y")
        self._new_prayer_added_count: int = new_prayer_added_count
        self._past_prayer_prayed_count: int = past_prayer_prayed_count
        self._answered_prayer_count: int = answered_prayer_count
        self._last_prayer_date: Optional[str] = last_prayer_date
        self._prayer_streak: int = prayer_streak if prayer_streak >= 0 else 0
        self._last_panel_set: Optional[str] = last_panel_set

    @property
    def session_date(self) -> str:
        """
        Get the session date.

        Returns:
            str: The date of the session (format: DD-MMM-YYYY).
        """
        return self._session_date

    @property
    def new_prayer_added_count(self) -> int:
        """
        Get the count of new prayers added in the session.

        Returns:
            int: The number of new prayers.
        """
        return self._new_prayer_added_count

    @new_prayer_added_count.setter
    def new_prayer_added_count(self, value: int):
        """
        Set the count of new prayers added.

        Args:
            value (int): The new count.

        Raises:
            ModelError: If the count is negative.
        """
        if value < 0:
            raise ModelError("New prayer count cannot be negative")
        self._new_prayer_added_count = value

    @property
    def past_prayer_prayed_count(self) -> int:
        """
        Get the count of past prayers reviewed in the session.

        Returns:
            int: The number of past prayers reviewed.
        """
        return self._past_prayer_prayed_count

    @past_prayer_prayed_count.setter
    def past_prayer_prayed_count(self, value: int):
        """
        Set the count of past prayers reviewed.

        Args:
            value (int): The new count.

        Raises:
            ModelError: If the count is negative.
        """
        if value < 0:
            raise ModelError("Past prayer prayed count cannot be negative")
        self._past_prayer_prayed_count = value

    @property
    def answered_prayer_count(self) -> int:
        """
        Get the count of prayers marked as answered.

        Returns:
            int: The number of answered prayers.
        """
        return self._answered_prayer_count

    @answered_prayer_count.setter
    def answered_prayer_count(self, value: int):
        """
        Set the count of answered prayers.

        Args:
            value (int): The new count.

        Raises:
            ModelError: If the count is negative.
        """
        if value < 0:
            raise ModelError("Answered prayer count cannot be negative")
        self._answered_prayer_count = value

    @property
    def last_prayer_date(self) -> Optional[str]:
        """
        Get the date of the last prayer session.

        Returns:
            Optional[str]: The last prayer date, or None if not set.
        """
        return self._last_prayer_date

    @last_prayer_date.setter
    def last_prayer_date(self, value: Optional[str]):
        """
        Set the date of the last prayer session.

        Args:
            value (Optional[str]): The new last prayer date.
        """
        self._last_prayer_date = value

    @property
    def prayer_streak(self) -> int:
        """
        Get the prayer streak (consecutive days).

        Returns:
            int: The number of consecutive days prayed.
        """
        return self._prayer_streak

    @prayer_streak.setter
    def prayer_streak(self, value: int):
        """
        Set the prayer streak.

        Args:
            value (int): The new streak count.

        Raises:
            ModelError: If the streak is negative.
        """
        if value < 0:
            raise ModelError("Prayer streak cannot be negative")
        self._prayer_streak = value

    @property
    def last_panel_set(self) -> Optional[str]:
        """
        Get the last panel set displayed.

        Returns:
            Optional[str]: The name of the last panel set, or None if not set.
        """
        return self._last_panel_set

    @last_panel_set.setter
    def last_panel_set(self, value: Optional[str]):
        """
        Set the last panel set displayed.

        Args:
            value (Optional[str]): The new panel set name.
        """
        self._last_panel_set = value


class State:
    """
    Represents a state in the application's state machine.

    Defines a step in the app's flow, like showing a welcome screen or collecting prayers.
    """

    def __init__(self, name: str, action_event: str, to_state: Optional[str] = None,
                 auto_trigger: Optional[bool] = False) -> None:
        """
        Initialize a state.

        Args:
            name (str): Name of the state (e.g., 'WELCOME').
            action_event (str): Event that triggers this state (e.g., 'get_continue').
            to_state (Optional[str]): Target state for the transition (defaults to None).
            auto_trigger (Optional[bool]): Whether the action triggers automatically (defaults to False).

        Raises:
            ModelError: If name or action_event is empty.
        """
        if not name:
            raise ModelError("State name cannot be empty")
        if not action_event:
            raise ModelError("Action event cannot be empty")
        self._name: str = name
        self._action_event: str = action_event
        self._to_state: Optional[str] = to_state
        self._auto_trigger: bool = auto_trigger

    @property
    def name(self) -> str:
        """
        Get the state name.

        Returns:
            str: The name of the state.
        """
        return self._name

    @property
    def action_event(self) -> str:
        """
        Get the action event for the state.

        Returns:
            str: The event that triggers this state.
        """
        return self._action_event

    @property
    def to_state(self) -> Optional[str]:
        """
        Get the target state for transition.

        Returns:
            Optional[str]: The next state name, or None if not set.
        """
        return self._to_state

    @property
    def auto_trigger(self) -> bool:
        """
        Get whether the state triggers automatically.

        Returns:
            bool: True if the state triggers without user input, False otherwise.
        """
        return self._auto_trigger


class StateMachine:
    """
    Manages the finite state machine for application navigation.

    Controls the app's flow by moving between states based on user actions or automatic triggers.
    """

    def __init__(self, states_data: List[Dict]):
        """
        Initialize the state machine with state data.

        Args:
            states_data (List[Dict]): List of dictionaries with state data (e.g., name, action_event, to_state).

        Raises:
            ModelError: If states_data is empty or invalid.
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
                auto_trigger=data.get('auto_trigger', False)
            )
            self._states.append(state)
        self._current_state: Optional[State] = self._states[0] if self._states else None
        if not self.validate():
            raise ModelError("State machine validation failed")

    def validate(self) -> bool:
        """
        Validate the state machine configuration.

        Returns:
            bool: True if all required states and actions are present, False otherwise.

        Checks for required states (e.g., 'WELCOME') and actions (e.g., 'get_continue').
        """
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
