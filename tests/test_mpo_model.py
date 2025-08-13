# test_mpo_model.py

import pytest
from datetime import date
from typing import List, Dict, Optional
from ..src.mpo_model import Prayer, Category, Panel, PanelPgraph, AppParams, PrayerSession, State, StateMachine, ModelError

# Prayer Tests
def test_prayer_constructor_valid():
    prayer = Prayer(prayer="Test prayer", category="Personal")
    assert prayer.prayer == "Test prayer"
    assert prayer.category == "Personal"
    assert prayer.create_date == date.today().strftime("%d-%b-%Y")
    assert prayer.answer_date is None
    assert prayer.answer is None
    assert prayer.display_count == 0

def test_prayer_constructor_invalid_empty_prayer():
    with pytest.raises(ModelError, match="Prayer text cannot be empty"):
        Prayer(prayer="", category="Personal")

def test_prayer_constructor_invalid_none_category():
    with pytest.raises(ModelError, match="Category cannot be None"):
        Prayer(prayer="Test prayer", category=None)

def test_prayer_set_answer():
    prayer = Prayer(prayer="Test prayer", category="Personal")
    prayer.answer = "Answered"
    assert prayer.answer == "Answered"
    prayer.answer_date = "01-Jan-2025"
    assert prayer.answer_date == "01-Jan-2025"

def test_prayer_set_display_count_invalid():
    prayer = Prayer(prayer="Test prayer", category="Personal")
    with pytest.raises(ModelError, match="Display count cannot be negative"):
        prayer.display_count = -1

# Category Tests
def test_category_constructor_valid():
    category = Category(category="Personal", count=5, weight=2)
    assert category.category == "Personal"
    assert category.category_display_count == 5
    assert category.category_weight == 2
    assert category.category_prayer_list == []

def test_category_constructor_invalid_empty():
    with pytest.raises(ModelError, match="Category name cannot be empty"):
        Category(category="")

def test_category_constructor_invalid_negative_count():
    with pytest.raises(ModelError, match="Category count cannot be negative"):
        Category(category="Personal", count=-1)

def test_category_constructor_invalid_low_weight():
    with pytest.raises(ModelError, match="Category weight must be at least 1"):
        Category(category="Personal", weight=0)

def test_category_set_display_count_valid():
    category = Category(category="Personal")
    category.category_display_count = 10
    assert category.category_display_count == 10

def test_category_set_display_count_invalid():
    category = Category(category="Personal")
    with pytest.raises(ModelError, match="Category display count cannot be negative"):
        category.category_display_count = -1

# Panel Tests
def test_panel_constructor_valid():
    pgraph = PanelPgraph(pgraph_seq=1, verse="John 3:16", text="Test text")
    panel = Panel(panel_seq=1, panel_header="Test Panel", pgraph_list=[pgraph])
    assert panel.panel_seq == 1
    assert panel.panel_header == "Test Panel"
    assert panel.pgraph_list == [pgraph]

def test_panel_constructor_invalid_negative_seq():
    pgraph = PanelPgraph(pgraph_seq=1, verse="John 3:16", text="Test text")
    with pytest.raises(ModelError, match="Panel sequence cannot be negative"):
        Panel(panel_seq=-1, panel_header="Test Panel", pgraph_list=[pgraph])

def test_panel_constructor_invalid_empty_header():
    pgraph = PanelPgraph(pgraph_seq=1, verse="John 3:16", text="Test text")
    with pytest.raises(ModelError, match="Panel header cannot be empty"):
        Panel(panel_seq=1, panel_header="", pgraph_list=[pgraph])

def test_panel_constructor_invalid_pgraph_type():
    with pytest.raises(ModelError, match="All items in pgraph_list must be PanelPgraph objects"):
        Panel(panel_seq=1, panel_header="Test Panel", pgraph_list=["Invalid"])

# PanelPgraph Tests
def test_panel_pgraph_constructor_valid():
    pgraph = PanelPgraph(pgraph_seq=1, verse="John 3:16", text="Test text")
    assert pgraph.pgraph_seq == 1
    assert pgraph.verse == "John 3:16"
    assert pgraph.text == "Test text"

def test_panel_pgraph_constructor_invalid_negative_seq():
    with pytest.raises(ModelError, match="Paragraph sequence cannot be negative"):
        PanelPgraph(pgraph_seq=-1, verse="John 3:16", text="Test text")

def test_panel_pgraph_constructor_invalid_empty_text():
    with pytest.raises(ModelError, match="Paragraph text cannot be empty"):
        PanelPgraph(pgraph_seq=1, verse="John 3:16", text="")

# AppParams Tests
def test_app_params_valid():
    params_dict = {
        'id': '1', 'id_desc': 'App ID', 'app': 'My Prayers', 'app_desc': 'Prayer app',
        'install_path': '/app', 'install_path_desc': 'Install path',
        'data_file_path': '/data', 'data_file_path_desc': 'Data path',
        'past_prayer_display_count': 5, 'past_prayer_display_count_desc': 'Display count'
    }
    params = AppParams(params_dict)
    assert params.id == '1'
    assert params.data_file_path == '/data'
    assert params.past_prayer_display_count == 5

def test_app_params_missing_keys():
    params_dict = {'id': '1', 'id_desc': 'App ID'}
    with pytest.raises(ModelError, match="Missing required parameters"):
        AppParams(params_dict)

# PrayerSession Tests
def test_prayer_session_constructor():
    session = PrayerSession(last_prayer_date="01-Jan-2025", prayer_streak=3, last_panel_set="1")
    assert session.last_prayer_date == "01-Jan-2025"
    assert session.prayer_streak == 3
    assert session.last_panel_set == "1"
    assert session.new_prayer_added_count == 0
    assert session.past_prayer_prayed_count == 0
    assert session.answered_prayer_count == 0

def test_prayer_session_set_negative_counts():
    session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)
    with pytest.raises(ModelError, match="New prayer added count cannot be negative"):
        session.new_prayer_added_count = -1
    with pytest.raises(ModelError, match="Past prayer prayed count cannot be negative"):
        session.past_prayer_prayed_count = -1
    with pytest.raises(ModelError, match="Answered prayer count cannot be negative"):
        session.answered_prayer_count = -1
    with pytest.raises(ModelError, match="Prayer streak cannot be negative"):
        session.prayer_streak = -1

# State Tests
def test_state_constructor_valid():
    state = State(name="WELCOME", action_event="get_continue", to_state="HONOR GOD", auto_trigger=True)
    assert state.name == "WELCOME"
    assert state.action_event == "get_continue"
    assert state.to_state == "HONOR GOD"
    assert state.auto_trigger is True

def test_state_constructor_invalid_empty_name():
    with pytest.raises(ModelError, match="State name cannot be empty"):
        State(name="", action_event="get_continue")

def test_state_constructor_invalid_empty_action():
    with pytest.raises(ModelError, match="Action event cannot be empty"):
        State(name="WELCOME", action_event="")

# StateMachine Tests
def test_state_machine_init_valid():
    states_data = [
        {"name": "WELCOME", "action_event": "get_continue", "to_state": "HONOR GOD", "auto_trigger": False},
        {"name": "HONOR GOD", "action_event": "get_continue", "to_state": "MY CONCERNS", "auto_trigger": False},
        {"name": "MY CONCERNS", "action_event": "get_new_prayers", "to_state": "prayers_done", "auto_trigger": False},
        {"name": "prayers_done", "action_event": "get_past_prayers", "to_state": "GOD'S WILL", "auto_trigger": False},
        {"name": "GOD'S WILL", "action_event": "get_continue", "to_state": "CLOSING", "auto_trigger": False},
        {"name": "CLOSING", "action_event": "quit_app", "to_state": "done", "auto_trigger": False}
    ]
    state_machine = StateMachine(states_data)
    assert state_machine.current_state.name == "WELCOME"
    assert state_machine.validate() is True

def test_state_machine_init_empty():
    with pytest.raises(ModelError, match="States data cannot be empty"):
        StateMachine([])

def test_state_machine_validate():
    states_data = [
        {"name": "WELCOME", "action_event": "get_continue", "to_state": "HONOR GOD"},
        {"name": "HONOR GOD", "action_event": "get_continue", "to_state": "done"}
    ]
    state_machine = StateMachine(states_data)
    assert state_machine.validate() is False  # Missing required states and actions

def test_state_machine_transition_valid():
    states_data = [
        {"name": "WELCOME", "action_event": "get_continue", "to_state": "HONOR GOD"},
        {"name": "HONOR GOD", "action_event": "get_continue", "to_state": "done"}
    ]
    state_machine = StateMachine(states_data)
    state_machine.transition("get_continue")
    assert state_machine.current_state.name == "HONOR GOD"

def test_state_machine_transition_invalid():
    states_data = [
        {"name": "WELCOME", "action_event": "get_continue", "to_state": "HONOR GOD"},
        {"name": "HONOR GOD", "action_event": "get_continue", "to_state": "done"}
    ]
    state_machine = StateMachine(states_data)
    with pytest.raises(ModelError, match="No valid transition"):
        state_machine.transition("invalid_action")