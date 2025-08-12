# test_db_manager
# Tests db_manager

import json
import pytest
from ..src.db_manager import AppDatabase
from ..src.mpo_model import Prayer

@pytest.fixture
def db_manager(tmpdir):
    """Fixture to create a new AppDatabase instance for testing."""
    data_dir = tmpdir.mkdir("data")
    params_data = {
        'id': '1',
        'id_desc': 'ID',
        'app': 'My Prayers',
        'app_desc': 'Prayer app',
        'install_path': '/path',
        'install_path_desc': 'Install path',
        'data_file_path': '/data',
        'data_file_path_desc': 'Data path',
        'past_prayer_display_count': 5,
        'past_prayer_display_count_desc': 'Count'
    }
    params_file = data_dir / "params.json"
    with open(params_file, 'w') as f:
        json.dump(params_data, f)
    categories_file = data_dir / "categories.json"
    with open(categories_file, 'w') as f:
        json.dump({"categories": []}, f)
    panels_file = data_dir / "panels.csv"
    with open(panels_file, 'w') as f:
        f.write("panel_set,header,panel_seq,pgraph_seq,verse,text\n1,Test,1,1,,Test text\n")
    prayers_file = data_dir / "prayers.csv"
    with open(prayers_file, 'w') as f:
        f.write("prayer,category,create_date\n")
    states_file = data_dir / "states.json"
    with open(states_file, 'w') as f:
        json.dump([], f)
    return AppDatabase(data_dir=str(data_dir))

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