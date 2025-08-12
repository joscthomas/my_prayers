# test_app_controller
# Test app_controller

import pytest
from unittest.mock import Mock
from ..src.app_controller import AppController, PrayerSelector
from ..src.mpo_model import Prayer, PrayerSession

@pytest.fixture
def app_controller():
    """Fixture to create a mocked AppController instance."""
    db_manager = Mock()
    ui_manager = Mock()
    prayer = Prayer(prayer="Test prayer", category="Other")
    state_data = [
        {"name": "WELCOME", "action_event": "get_continue", "to_state": "HONOR GOD", "auto_trigger": False},
        {"name": "HONOR GOD", "action_event": "get_continue", "to_state": "MY CONCERNS", "auto_trigger": False},
        {"name": "MY CONCERNS", "action_event": "get_new_prayers", "to_state": "GOD'S WILL", "auto_trigger": False},
        {"name": "GOD'S WILL", "action_event": "get_past_prayers", "to_state": "CLOSING", "auto_trigger": False},
        {"name": "CLOSING", "action_event": "get_continue", "to_state": "done", "auto_trigger": False},
        {"name": "prayers_done", "action_event": "quit_app", "to_state": "done", "auto_trigger": True},
    ]
    db_manager.persistence.load_states.return_value = state_data
    db_manager.app_params.past_prayer_display_count = 1
    db_manager.category_manager.categories = []
    db_manager.prayer_manager.get_unanswered_prayers.return_value = [prayer]
    # Mock PrayerSelector
    prayer_selector = Mock(spec=PrayerSelector)
    prayer_selector.select_past_prayers.return_value = [prayer]
    # Mock session
    session = Mock(spec=PrayerSession)
    session.past_prayer_prayed_count = 0  # Initialize as integer
    db_manager.session = session
    app_controller = AppController(db_manager, ui_manager)
    app_controller.prayer_selector = prayer_selector
    return app_controller

def test_get_past_prayers(app_controller):
    """Test get_past_prayers retrieves prayers and updates display_count."""
    prayer = Prayer(prayer="Test prayer", category="Other")
    app_controller.prayer_selector.select_past_prayers.return_value = [prayer]
    app_controller.ui_manager.get_response.side_effect = ['', 'n']
    result = app_controller.get_past_prayers()
    assert result == 'get_past_prayers'
    assert prayer.display_count == 1
    assert app_controller.db_manager.session.past_prayer_prayed_count == 1