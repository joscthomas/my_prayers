# test_app_controller
# Test app_controller

import pytest
from unittest.mock import Mock
from ..app_controller import AppController
from ..mpo_model import Prayer

@pytest.fixture
def app_controller():
    """Fixture to create a mocked AppController instance."""
    db_manager = Mock()
    ui_manager = Mock()
    return AppController(db_manager, ui_manager)

def test_get_past_prayers(app_controller):
    """Test get_past_prayers retrieves prayers and updates display_count."""
    prayer = Prayer(prayer="Test prayer", category="Other")
    app_controller.db_manager.get_past_prayers.return_value = [prayer]
    result = app_controller.get_past_prayers()
    assert len(result) == 1
    assert result[0].prayer == prayer.prayer
    assert result[0].display_count == 1