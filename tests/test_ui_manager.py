# test_ui_manager.py
# Tests ui_manager

"""
This module tests the ui_manager.py file with pytest and patches. It checks menu display, user input handling,
and output formatting, capturing printed text for verification. For those new to Python, this demonstrates testing
interactive console apps safely.
"""

import pytest
from unittest.mock import patch
from io import StringIO
from ui_manager import AppDisplay, UIError
from mpo_model import Panel, PanelPgraph, Prayer


@pytest.fixture
def app_display():
    """
    Create an AppDisplay instance for testing.

    Returns:
        AppDisplay: A new AppDisplay object with default settings.
    """
    return AppDisplay(max_line_width=80)


def test_display_panel(app_display):
    """
    Test AppDisplay.display_panel method.

    Args:
        app_display (AppDisplay): The AppDisplay instance from the fixture.

    Verifies that a panel's header and paragraphs are displayed correctly.
    """
    panel = Panel(
        panel_seq=1,
        panel_header="Test Panel",
        pgraph_list=[PanelPgraph(pgraph_seq=1, verse=None, text="This is a test paragraph.")]
    )
    with patch('sys.stdout', new=StringIO()) as fake_out:
        app_display.display_panel(panel)
        output = fake_out.getvalue()
        assert "Test Panel" in output
        assert "This is a test paragraph." in output
    assert app_display.last_panel == panel


def test_get_response(app_display):
    """
    Test AppDisplay.get_response method.

    Args:
        app_display (AppDisplay): The AppDisplay instance from the fixture.

    Verifies that user input is captured correctly.
    """
    with patch('builtins.input', return_value="test input"):
        response = app_display.get_response("Enter something: ")
        assert response == "test input"


def test_ui_get_new_prayer(app_display):
    """
    Test AppDisplay.ui_get_new_prayer method.

    Args:
        app_display (AppDisplay): The AppDisplay instance from the fixture.

    Verifies that a new prayer is created with valid input and the continue flag is set.
    """
    with patch('builtins.input', side_effect=["Test prayer", "Praise"]):
        prayer, continue_flag = app_display.ui_get_new_prayer()
        assert prayer.prayer == "Test prayer"
        assert prayer.category == "Praise"
        assert continue_flag is True


def test_display_prayer(app_display):
    """
    Test AppDisplay.display_prayer method.

    Args:
        app_display (AppDisplay): The AppDisplay instance from the fixture.

    Verifies that a prayer's text is displayed with proper formatting.
    """
    prayer = Prayer(prayer="This is a test prayer", category="Other")
    with patch('sys.stdout', new=StringIO()) as fake_out:
        app_display.display_prayer(prayer)
        output = fake_out.getvalue()
        assert "This is a test prayer" in output