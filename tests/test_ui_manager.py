# test_ui_manager.py

import pytest
from unittest.mock import patch
from ..src.ui_manager import AppDisplay, UIError
from ..src.mpo_model import Prayer, Panel, PanelPgraph

@pytest.fixture
def app_display():
    return AppDisplay(max_line_width=80)

# AppDisplay Tests
def test_app_display_display_panel(app_display):
    pgraph = PanelPgraph(pgraph_seq=1, verse="John 3:16", text="Test text")
    panel = Panel(panel_seq=1, panel_header="Test Panel", pgraph_list=[pgraph])
    with patch("builtins.print") as mock_print:
        app_display.display_panel(panel)
    assert app_display.last_panel == panel
    mock_print.assert_called()

def test_app_display_get_response(app_display):
    with patch("builtins.input", return_value="test input"):
        response = app_display.get_response("Enter input: ")
    assert response == "test input"

def test_app_display_ui_get_new_prayer_valid(app_display):
    with patch("builtins.input", side_effect=["Test prayer", "Personal"]):
        prayer, another = app_display.ui_get_new_prayer()
    assert prayer.prayer == "Test prayer"
    assert prayer.category == "Personal"
    assert another is True

def test_app_display_ui_get_new_prayer_empty(app_display):
    with patch("builtins.input", side_effect=["", ""]):
        prayer, another = app_display.ui_get_new_prayer()
    assert prayer is None
    assert another is False

def test_app_display_get_answer(app_display):
    prayer = Prayer("Test prayer", category="Personal")
    with patch("builtins.input", return_value="Answered"):
        answer, date_str = app_display.get_answer(prayer)
    assert answer == "Answered"
    assert date_str == prayer.create_date

def test_app_display_display_prayer(app_display):
    prayer = Prayer("Test prayer", category="Personal")
    with patch("builtins.print") as mock_print:
        app_display.display_prayer(prayer)
    mock_print.assert_called_with("\nTest prayer\n")