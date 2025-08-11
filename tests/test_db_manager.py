# test_db_manager
# Tests db_manager

import pytest
from ..src.db_manager import AppDatabase
from ..src.mpo_model import Prayer

@pytest.fixture
def db_manager():
    """Fixture to create a new AppDatabase instance for testing."""
    return AppDatabase()

def test_save_prayer(db_manager):
    """Test saving and retrieving a prayer in AppDatabase."""
    prayer = Prayer(prayer="Test prayer", category="Other")
    db_manager.save_prayer(prayer)
    retrieved = db_manager.retrieve_prayer(prayer.prayer)
    assert retrieved.prayer == prayer.prayer
    assert retrieved.category == prayer.category
    assert retrieved.create_date == prayer.create_date

def test_retrieve_nonexistent_prayer(db_manager):
    """Test retrieving a prayer that doesn't exist returns None."""
    result = db_manager.retrieve_prayer("Nonexistent prayer")
    assert result is None