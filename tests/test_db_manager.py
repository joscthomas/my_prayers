# test_db_manager.py
# Tests db_manager

"""
This module tests the db_manager.py file with pytest. It verifies saving and retrieving prayers,
handling non-existent data, using temporary directories for isolated tests. Mocks simulate file setups,
and assertions check if data persists correctly. For beginners, this shows how to test data operations without
affecting real files.
"""

import json
import pytest
import pandas as pd
from db_manager import AppDatabase, DatabaseError
from mpo_model import Prayer, AppParams, PrayerSession


@pytest.fixture
def db_manager(tmpdir):
    """
    Create a new AppDatabase instance for testing.

    Args:
        tmpdir: Pytest fixture for a temporary directory.

    Returns:
        AppDatabase: A database instance with mock data files.

    Sets up temporary JSON, CSV, and state files for isolated testing.
    """
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
    """
    Test saving and retrieving a prayer in AppDatabase.

    Args:
        db_manager (AppDatabase): The database instance from the fixture.

    Verifies that a prayer can be saved and retrieved with correct attributes.
    """
    prayer = Prayer(prayer="Test prayer", category="Other")
    db_manager.save_prayer(prayer)
    retrieved = db_manager.retrieve_prayer(prayer.prayer)
    assert retrieved is not None
    assert retrieved.prayer == prayer.prayer
    assert retrieved.category == prayer.category
    assert retrieved.create_date == prayer.create_date


def test_load_params(db_manager):
    """
    Test loading application parameters in AppDatabase.

    Args:
        db_manager (AppDatabase): The database instance from the fixture.

    Verifies that AppParams are loaded correctly from the params.json file.
    """
    params = db_manager.app_params
    assert isinstance(params, AppParams)
    assert params.id == '1'
    assert params.app == 'My Prayers'
    assert params.past_prayer_display_count == 5


def test_create_prayer(db_manager):
    """
    Test creating a new prayer in AppDatabase.

    Args:
        db_manager (AppDatabase): The database instance from the fixture.

    Verifies that a prayer is added to the prayer manager and session count is updated.
    """
    prayer = Prayer(prayer="New prayer", category="Praise")
    db_manager.create_prayer(prayer)
    assert prayer in db_manager.prayer_manager.prayers
    assert db_manager.session.new_prayer_added_count == 1


def test_validate_db(db_manager):
    """
    Test AppDatabase validation.

    Args:
        db_manager (AppDatabase): The database instance from the fixture.

    Verifies that the database validates successfully with the provided mock data.
    """
    assert db_manager.validate() is True


def test_load_from_pickle_empty(db_manager, tmpdir):
    """
    Test loading from an empty or non-existent pickle file.

    Args:
        db_manager (AppDatabase): The database instance from the fixture.
        tmpdir: Pytest fixture for a temporary directory.

    Verifies that the database falls back to CSV/JSON loading when pickle is empty.
    """
    # Simulate empty pickle file
    with open(tmpdir.join("data/objects.pkl"), 'wb') as f:
        f.write(b"")
    db_manager._load_from_pickle()
    assert len(db_manager.prayer_manager.prayers) == 0
    assert len(db_manager.category_manager.categories) == 0
    assert isinstance(db_manager.session, PrayerSession)


def test_save_prayers_to_csv(db_manager, tmpdir):
    """
    Test saving prayers to a CSV file.

    Args:
        db_manager (AppDatabase): The database instance from the fixture.
        tmpdir: Pytest fixture for a temporary directory.

    Verifies that prayers are correctly saved to the CSV file.
    """
    prayer = Prayer(prayer="Saved prayer", category="Other")
    db_manager.prayer_manager.create_prayer(prayer)
    db_manager.prayer_manager.save_prayers("prayers.csv")
    df = pd.read_csv(tmpdir.join("data/prayers.csv"))
    assert len(df) == 1
    assert df.iloc[0]['prayer'] == "Saved prayer"
    assert df.iloc[0]['category'] == "Other"


def test_retrieve_nonexistent_prayer(db_manager):
    """
    Test retrieving a non-existent prayer.

    Args:
        db_manager (AppDatabase): The database instance from the fixture.

    Verifies that retrieving a prayer that doesn't exist returns None.
    """
    result = db_manager.retrieve_prayer("Non-existent prayer")
    assert result is None


def test_close_database(db_manager, tmpdir):
    """
    Test closing the database and saving data.

    Args:
        db_manager (AppDatabase): The database instance from the fixture.
        tmpdir: Pytest fixture for a temporary directory.

    Verifies that data is saved to pickle and JSON files upon closing.
    """
    prayer = Prayer(prayer="Test prayer", category="Other")
    db_manager.create_prayer(prayer)
    db_manager.close()
    assert tmpdir.join("data/objects.pkl").exists()
    assert tmpdir.join("data/categories.json").exists()
    assert tmpdir.join("data/params.json").exists()