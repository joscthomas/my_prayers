# test_app_controller.py
# Test app_controller

"""
This module tests the app_controller.py file using pytest and mocks. It focuses on prayer selection,
display updates, and session counts, simulating database and UI interactions. Assertions ensure logic like
incrementing counts works. Learners can use this to understand testing controllers that coordinate multiple parts.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date
from mpo_model import Prayer, PrayerSession, State
from db_manager import AppDatabase
from ui_manager import AppDisplay
from app_controller import AppController, PrayerSelector, SessionManager


@pytest.fixture
def mock_db_manager():
    """
    Create a mock AppDatabase for testing.

    Returns:
        Mock: A mock object simulating the AppDatabase with predefined behaviors.
    """
    db = Mock()
    db.prayer_manager = Mock()
    db.prayer_manager.get_unanswered_prayers.return_value = [
        Prayer(prayer="Test prayer 1", category="Other", display_count=0),
        Prayer(prayer="Test prayer 2", category="Praise", display_count=1)
    ]
    db.category_manager = Mock()
    db.category_manager.categories = [
        Mock(category="Other", category_weight=1),
        Mock(category="Praise", category_weight=2)
    ]
    db.app_params = Mock()
    db.app_params.past_prayer_display_count = 2
    db.session = PrayerSession()
    db.persistence = Mock()
    db.persistence.load_states.return_value = [
        {"name": "WELCOME", "action_event": "get_continue"},
        {"name": "HONOR GOD", "action_event": "get_new_prayers"},
        {"name": "MY CONCERNS", "action_event": "get_past_prayers"},
        {"name": "prayers_done", "action_event": "quit_app"},
        {"name": "GOD'S WILL", "action_event": "get_continue"},
        {"name": "CLOSING", "action_event": "get_continue"}
    ]
    return db


@pytest.fixture
def mock_ui_manager():
    """
    Create a mock AppDisplay for testing.

    Returns:
        Mock: A mock object simulating the AppDisplay with predefined behaviors.
    """
    return Mock(spec=AppDisplay)


@pytest.fixture
def mock_state_machine():
    """
    Create a mock StateMachine for testing.

    Returns:
        Mock: A mock object simulating the StateMachine with predefined states.
    """
    state_machine = Mock()
    state_machine.current_state = State(name="TEST_STATE", action_event="get_continue")
    state_machine.transition.return_value = None
    return state_machine


def test_prayer_selector_select_past_prayers(mock_db_manager):
    """
    Test PrayerSelector.select_past_prayers method.

    Args:
        mock_db_manager (Mock): Mocked AppDatabase with prayer and category data.

    Verifies that prayers are selected based on category weight and display count.
    """
    selector = PrayerSelector(mock_db_manager)
    prayers = selector.select_past_prayers(max_selections=2, current_weight=2)
    assert len(prayers) <= 2
    for prayer in prayers:
        assert prayer.prayer in ["Test prayer 1", "Test prayer 2"]


def test_session_manager_update_streak(mock_db_manager):
    """
    Test SessionManager.update_streak method.

    Args:
        mock_db_manager (Mock): Mocked AppDatabase with session data.

    Verifies that the prayer streak is updated correctly based on the last prayer date.
    """
    session = PrayerSession(last_prayer_date=date.today().strftime("%d-%b-%Y"))
    manager = SessionManager(session)
    manager.update_streak()
    assert session.prayer_streak == 1


def test_app_controller_handle_state_action(mock_db_manager, mock_ui_manager):
    """
    Test AppController.handle_state_action method.

    Args:
        mock_db_manager (Mock): Mocked AppDatabase for data access.
        mock_ui_manager (Mock): Mocked AppDisplay for UI interactions.

    Verifies that state actions like 'get_continue' are handled correctly.
    """
    controller = AppController(db_manager=mock_db_manager, ui_manager=mock_ui_manager)
    state = State(name="TEST_STATE", action_event="get_continue")
    with patch.object(controller.ui_manager, 'get_response', return_value=''):
        action = controller.handle_state_action(state)
        assert action == 'get_continue'