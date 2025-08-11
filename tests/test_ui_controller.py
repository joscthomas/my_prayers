# test_ui_manager
# Test ui_manager

import pytest
from unittest.mock import patch
from ..src.ui_manager import AppDisplay

@pytest.fixture
def ui_manager():
    """Fixture to create a new AppDisplay instance."""
    return AppDisplay()

@patch('builtins.input', return_value='1')
def test_display_menu_valid_choice(mock_input, ui_manager):
    """Test display_menu returns valid user choice."""
    result = ui_manager.get_user_input()
    assert result == '1'
    mock_input.assert_called_once()

def test_display_menu_output(capsys, ui_manager):
    """Test display_menu prints expected menu options."""
    ui_manager.display_menu()
    captured = capsys.readouterr()
    assert "1. Create new prayer" in captured.out