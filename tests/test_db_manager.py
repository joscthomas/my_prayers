# test_db_manager.py

import pytest
import pandas as pd
import pickle
import os
from unittest.mock import patch, mock_open, MagicMock
from typing import Dict, List, Any
from ..src.db_manager import PersistenceManager, PanelManager, PrayerManager, CategoryManager, AppDatabase, DatabaseError
from ..src.mpo_model import Prayer, Category, Panel, PanelPgraph, AppParams, PrayerSession

@pytest.fixture
def mock_persistence():
    return PersistenceManager(data_dir="test_data")

@pytest.fixture
def mock_app_database():
    with patch("my_prayers_project.src.db_manager.AppDatabase._load_params", return_value=AppParams({
        'id': '1', 'id_desc': 'App ID', 'app': 'My Prayers', 'app_desc': 'Prayer app',
        'install_path': '/app', 'install_path_desc': 'Install path',
        'data_file_path': '/data', 'data_file_path_desc': 'Data path',
        'past_prayer_display_count': 5, 'past_prayer_display_count_desc': 'Display count'
    })):
        db = MagicMock(spec=AppDatabase)
        db.app_params = AppParams({
            'id': '1', 'id_desc': 'App ID', 'app': 'My Prayers', 'app_desc': 'Prayer app',
            'install_path': '/app', 'install_path_desc': 'Install path',
            'data_file_path': '/data', 'data_file_path_desc': 'Data path',
            'past_prayer_display_count': 5, 'past_prayer_display_count_desc': 'Display count'
        })
        db.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)
        db.panel_manager = MagicMock(spec=PanelManager)
        db.panel_manager.panels = []
        db.prayer_manager = MagicMock(spec=PrayerManager)
        db.prayer_manager.prayers = []
        db.category_manager = MagicMock(spec=CategoryManager)
        db.category_manager.categories = []
        yield db

# PersistenceManager Tests
def test_persistence_manager_load_json_valid(mock_persistence):
    mock_data = {"categories": [{"name": "Personal", "weight": 2}]}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))), \
         patch("os.path.exists", return_value=True):
        result = mock_persistence.load_json("test.json")
    assert result == mock_data

def test_persistence_manager_load_json_invalid(mock_persistence):
    with patch("builtins.open", mock_open(read_data="invalid json")), \
         patch("os.path.exists", return_value=True):
        with pytest.raises(DatabaseError, match="Failed to parse JSON file"):
            mock_persistence.load_json("test.json")

def test_persistence_manager_load_json_not_exist(mock_persistence):
    with patch("os.path.exists", return_value=False):
        with pytest.raises(DatabaseError, match="JSON file test.json not found"):
            mock_persistence.load_json("test.json")

def test_persistence_manager_save_json(mock_persistence):
    mock_data = {"categories": [{"name": "Personal", "weight": 2}]}
    with patch("builtins.open", mock_open()) as mocked_file:
        mock_persistence.save_json("test.json", mock_data)
    mocked_file.assert_called_once_with("test.json", 'w', encoding='utf-8')
    mocked_file().write.assert_any_call(json.dumps(mock_data, indent=4))

def test_persistence_manager_load_pickle_valid(mock_persistence):
    mock_data = {'Prayer_instances': [Prayer("Test prayer", category="Personal")]}
    with patch("builtins.open", mock_open(read_data=pickle.dumps(mock_data))), \
         patch("os.path.exists", return_value=True):
        result = mock_persistence.load_pickle()
    assert len(result['Prayer_instances']) == len(mock_data['Prayer_instances'])
    assert result['Prayer_instances'][0].prayer == mock_data['Prayer_instances'][0].prayer
    assert result['Prayer_instances'][0].category == mock_data['Prayer_instances'][0].category

def test_persistence_manager_load_pickle_not_exist(mock_persistence):
    with patch("os.path.exists", return_value=False):
        result = mock_persistence.load_pickle()
    assert result == {}

def test_persistence_manager_save_pickle(mock_persistence):
    mock_data = {'Prayer_instances': [Prayer("Test prayer", category="Personal")]}
    with patch("builtins.open", mock_open()) as mocked_file:
        mock_persistence.save_pickle(mock_data)
    mocked_file.assert_called_once_with(mock_persistence.pickle_file, "wb")
    mocked_file().write.assert_called_once()

def test_persistence_manager_load_csv_valid(mock_persistence):
    mock_df = pd.DataFrame({"panel_seq": [1], "header": ["Test"], "text": ["Test text"]})
    with patch("pandas.read_csv", return_value=mock_df):
        result = mock_persistence.load_csv("panels.csv")
    assert result.equals(mock_df)

def test_persistence_manager_load_csv_invalid(mock_persistence):
    with patch("pandas.read_csv", side_effect=Exception("CSV error")):
        with pytest.raises(DatabaseError, match="Failed to load CSV file"):
            mock_persistence.load_csv("panels.csv")

# PanelManager Tests
def test_panel_manager_load_panels(mock_app_database):
    mock_df = pd.DataFrame({
        "panel_seq": [1, 1], "header": ["Test Panel", "Test Panel"],
        "pgraph_seq": [1, 2], "verse": ["John 3:16", None], "text": ["Text 1", "Text 2"],
        "panel_set": [1, 1]
    })
    with patch("my_prayers_project.src.db_manager.PersistenceManager.load_csv", return_value=mock_df):
        mock_app_database.panel_manager.load_panels()
    assert len(mock_app_database.panel_manager.panels) == 1
    assert mock_app_database.panel_manager.panels[0].panel_header == "Test Panel"
    assert len(mock_app_database.panel_manager.panels[0].pgraph_list) == 2

# PrayerManager Tests
def test_prayer_manager_load_prayers(mock_app_database):
    mock_df = pd.DataFrame({
        "prayer": ["Test prayer"], "category": ["Personal"], "create_date": ["01-Jan-2025"],
        "answer_date": [None], "answer": [None], "display_count": [0]
    })
    with patch("my_prayers_project.src.db_manager.PersistenceManager.load_csv", return_value=mock_df):
        mock_app_database.prayer_manager.load_prayers("prayers.csv")
    assert len(mock_app_database.prayer_manager.prayers) == 1
    assert mock_app_database.prayer_manager.prayers[0].prayer == "Test prayer"

def test_prayer_manager_create_prayer(mock_app_database):
    prayer = Prayer("Test prayer", category="Personal")
    mock_app_database.prayer_manager.create_prayer(prayer)
    assert prayer in mock_app_database.prayer_manager.prayers

# CategoryManager Tests
def test_category_manager_load_categories(mock_app_database):
    mock_data = {"categories": [{"name": "Personal", "weight": 2}]}
    with patch("my_prayers_project.src.db_manager.PersistenceManager.load_json", return_value=mock_data):
        mock_app_database.category_manager.load_categories("categories.json")
    assert len(mock_app_database.category_manager.categories) == 1
    assert mock_app_database.category_manager.categories[0].category == "Personal"

# AppDatabase Tests
def test_app_database_init(mock_app_database):
    assert isinstance(mock_app_database.app_params, AppParams)
    assert isinstance(mock_app_database.session, PrayerSession)
    assert isinstance(mock_app_database.panel_manager, PanelManager)
    assert isinstance(mock_app_database.prayer_manager, PrayerManager)
    assert isinstance(mock_app_database.category_manager, CategoryManager)

def test_app_database_create_prayer(mock_app_database):
    prayer = Prayer("Test prayer", category="Personal")
    mock_app_database.create_prayer(prayer)
    assert prayer in mock_app_database.prayer_manager.prayers
    assert mock_app_database.session.new_prayer_added_count == 1

def test_app_database_close(mock_app_database):
    with patch("my_prayers_project.src.db_manager.PersistenceManager.save_pickle") as mock_save_pickle:
        with patch("my_prayers_project.src.db_manager.PersistenceManager.save_json") as mock_save_json:
            mock_app_database.close()
    mock_save_pickle.assert_called_once()
    mock_save_json.assert_called()