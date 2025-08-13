# test_app_controller.py

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timedelta
from typing import List
from ..src.app_controller import PrayerSelector, SessionManager, AppController, AppError
from ..src.mpo_model import Prayer, Category, PrayerSession, State, StateMachine, AppParams
from ..src.db_manager import AppDatabase

@pytest.fixture
def mock_db():
    db = MagicMock(spec=AppDatabase)
    db.app_params = AppParams({
        'id': '1', 'id_desc': 'App ID', 'app': 'My Prayers', 'app_desc': 'Prayer app',
        'install_path': '/app', 'install_path_desc': 'Install path',
        'data_file_path': '/data', 'data_file_path_desc': 'Data path',
        'past_prayer_display_count': 2, 'past_prayer_display_count_desc': 'Display count'
    })
    db.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)
    return db

@pytest.fixture
def prayer_selector(mock_db):
    return PrayerSelector(mock_db)

@pytest.fixture
def session_manager(mock_db):
    return SessionManager(mock_db.session)

# PrayerSelector Tests
def test_prayer_selector_select_past_prayers(prayer_selector, mock_db):
    prayer1 = Prayer("Prayer 1", category="Personal", create_date="01-Jan-2025")
    prayer2 = Prayer("Prayer 2", category="Family", create_date="01-Jan-2025")
    mock_db.prayer_manager.get_unanswered_prayers.return_value = [prayer1, prayer2]
    mock_db.category_manager.categories = [Category("Personal", weight=2), Category("Family", weight=1)]
    prayers = prayer_selector.select_past_prayers(max_selections=2, current_weight=2)
    assert len(prayers) <= 2
    assert all(p in [prayer1, prayer2] for p in prayers)

def test_prayer_selector_reset_session(prayer_selector):
    prayer_selector.displayed_prayers.add("Prayer 1")
    prayer_selector.reset_session()
    assert len(prayer_selector.displayed_prayers) == 0

# SessionManager Tests
def test_session_manager_update_streak(session_manager):
    session_manager.session.last_prayer_date = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
    session_manager.update_streak()
    assert session_manager.session.prayer_streak == 2
    assert session_manager.session.last_prayer_date == datetime.now().strftime("%d-%b-%Y")

# AppController Tests
def test_app_controller_handle_state_action_get_continue(mock_db):
    app_controller = AppController()
    app_controller.ui_manager = MagicMock()
    state = State(name="WELCOME", action_event="get_continue", to_state="HONOR GOD")
    with patch.object(app_controller.ui_manager, "get_response", return_value=""):
        action = app_controller.handle_state_action(state)
    assert action == "get_continue"

def test_app_controller_get_new_prayers(mock_db):
    app_controller = AppController()
    app_controller.ui_manager = MagicMock()
    app_controller.ui_manager.ui_get_new_prayer.return_value = (Prayer("Test prayer", category="Personal"), True)
    app_controller.get_new_prayers()
    mock_db.create_prayer.assert_called_once()
    assert mock_db.session.new_prayer_added_count == 1

def test_app_controller_get_past_prayers(mock_db):
    app_controller = AppController()
    app_controller.ui_manager = MagicMock()
    app_controller.prayer_selector = MagicMock()
    prayer = Prayer("Test prayer", category="Personal")
    app_controller.prayer_selector.select_past_prayers.return_value = [prayer]
    app_controller.ui_manager.get_response.side_effect = ["", "y"]
    app_controller.get_past_prayers()
    assert prayer.display_count == 1
    assert mock_db.session.past_prayer_prayed_count == 1

def test_app_controller_quit(mock_db):
    app_controller = AppController()
    app_controller.ui_manager = MagicMock()
    with pytest.raises(SystemExit):
        app_controller.quit()
    mock_db.close.assert_called_once()
    app_controller.ui_manager.close_ui.assert_called_once()