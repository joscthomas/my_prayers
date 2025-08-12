# db_manager.py
# Handles data management and database interactions.

import pandas as pd
import pickle
import json
import os
import random
from datetime import datetime, date
from typing import List, Optional, Dict
from typing import IO, BinaryIO
import logging

from mpo_model import Prayer, Category, Panel, PanelPgraph, AppParams, PrayerSession

class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass

class PersistenceManager:
    """Handles file I/O operations for persistence (pickle, JSON, CSV)."""

    def __init__(self, data_dir: str = "../data", pickle_file: str = "objects.pkl",
                 params_file: str = "params.json", categories_file: str = "categories.json",
                 states_file: str = "states.json"):
        self.data_dir: str = data_dir
        self.pickle_file: str = os.path.join(data_dir, pickle_file)
        self.params_file: str = os.path.join(data_dir, params_file)
        self.categories_file: str = os.path.join(data_dir, categories_file)
        self.states_file: str = os.path.join(data_dir, states_file)

    def load_pickle(self) -> Dict:
        """Load objects from the pickle file."""
        try:
            if not os.path.exists(self.pickle_file):
                return {}
            with open(self.pickle_file, "rb") as file:
                return pickle.load(file)
        except (pickle.UnpicklingError, EOFError) as e:
            logging.error(f"Failed to unpickle {self.pickle_file}: {e}")
            raise DatabaseError(f"Failed to load pickle file: {e}")

    def save_pickle(self, objects: Dict) -> None:
        """Save objects to the pickle file."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)  # Ensure data directory exists
            with open(self.pickle_file, "wb") as file:  # type: BinaryIO
                pickle.dump(objects, file)  # type: ignore
        except Exception as e:
            logging.error(f"Failed to save pickle file {self.pickle_file}: {e}")
            raise DatabaseError(f"Failed to save pickle file: {e}")

    @staticmethod
    def load_json(file_path: str) -> Dict:
        """Load data from a JSON file."""
        try:
            if not os.path.exists(file_path):
                raise DatabaseError(f"JSON file {file_path} not found")
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON file {file_path}: {e}")
            raise DatabaseError(f"Failed to parse JSON file: {e}")

    def save_json(self, file_path: str, data: Dict) -> None:
        """Save data to a JSON file."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)  # Ensure data directory exists
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            logging.error(f"Failed to save JSON file {file_path}: {e}")
            raise DatabaseError(f"Failed to save JSON file: {e}")

    @staticmethod
    def load_csv(file_path: str) -> pd.DataFrame:
        """Load a CSV file into a pandas DataFrame."""
        try:
            df = pd.read_csv(file_path)
            df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
            for col in df.columns:
                try:
                    df[col] = df[col].str.strip()
                except AttributeError:
                    pass
            return df
        except Exception as e:
            logging.error(f"Failed to load CSV file {file_path}: {e}")
            raise DatabaseError(f"Failed to load CSV file: {e}")

    def load_states(self) -> List[Dict]:
        """Load state transitions from states.json."""
        try:
            data = self.load_json(self.states_file)
            if not isinstance(data, list):
                raise DatabaseError("Invalid JSON format in states.json: Expected a list of states")
            return data
        except DatabaseError as e:
            logging.error(f"Failed to load states: {e}")
            raise

class PrayerManager:
    """Manages Prayer objects and their persistence."""

    def __init__(self, persistence: PersistenceManager):
        self.persistence: PersistenceManager = persistence
        self.prayers: List[Prayer] = []
        self.answered_prayers: List[Prayer] = []

    def load_prayers(self, prayers_file: str) -> None:
        """Load prayers from CSV file."""
        try:
            df = self.persistence.load_csv(os.path.join(self.persistence.data_dir, prayers_file))
            self.prayers = []
            for _, row in df.iterrows():
                prayer = Prayer(
                    prayer=row['prayer'],
                    category=row['category'],
                    create_date=row['create_date'],
                    answer_date=row.get('answer_date', None),
                    answer=row.get('answer', None),
                    display_count=int(row.get('display_count', 0))
                )
                self.prayers.append(prayer)
            self.answered_prayers = [prayer for prayer in self.prayers if prayer.answer_date is None]
            logging.info(f"Loaded {len(self.prayers)} prayers from {prayers_file}")
        except Exception as e:
            logging.warning(f"No prayers loaded: {e}")
            self.prayers = []
            self.answered_prayers = []

    def create_prayer(self, prayer: Prayer) -> None:
        """Add a new prayer to the list."""
        self.prayers.append(prayer)
        if prayer.answer_date is None:
            self.answered_prayers.append(prayer)
        logging.info(f"Created prayer: {prayer.prayer}")

    def save_prayers(self, prayers_file: str) -> None:
        """Save prayers to CSV file."""
        try:
            data = [
                {
                    'prayer': prayer.prayer,
                    'category': prayer.category,
                    'create_date': prayer.create_date,
                    'answer_date': prayer.answer_date,
                    'answer': prayer.answer,
                    'display_count': prayer.display_count
                }
                for prayer in self.prayers
            ]
            df = pd.DataFrame(data)
            df.to_csv(os.path.join(self.persistence.data_dir, prayers_file), index=False)
            logging.info(f"Saved {len(self.prayers)} prayers to {prayers_file}")
        except Exception as e:
            logging.error(f"Failed to save prayers: {e}")
            raise DatabaseError(f"Failed to save prayers: {e}")

    def get_unanswered_prayers(self) -> List[Prayer]:
        """Return list of unanswered prayers."""
        return self.answered_prayers

    def validate(self) -> bool:
        """Validate prayer data."""
        for prayer in self.prayers:
            if not prayer.prayer:
                logging.error(f"Invalid prayer with empty text: {prayer}")
                return False
            if not prayer.category:
                logging.error(f"Invalid prayer with empty category: {prayer}")
                return False
        return True

class CategoryManager:
    """Manages Category objects and their persistence."""

    def __init__(self, persistence: PersistenceManager, prayer_manager: PrayerManager):
        self.persistence: PersistenceManager = persistence
        self.prayer_manager: PrayerManager = prayer_manager
        self.categories: List[Category] = []

    def load_categories(self, categories_file: str) -> None:
        """Load categories from JSON file."""
        try:
            data = self.persistence.load_json(os.path.join(self.persistence.data_dir, categories_file))
            self.categories = []
            for cat_data in data.get('categories', []):
                category = Category(
                    category=cat_data['name'],
                    count=cat_data.get('count', 0),
                    weight=cat_data.get('weight', 1)
                )
                self.categories.append(category)
            self._assign_prayers_to_categories()
            logging.info(f"Loaded {len(self.categories)} categories from {categories_file}")
        except Exception as e:
            logging.error(f"Failed to load categories: {e}")
            raise DatabaseError(f"Failed to load categories: {e}")

    def _assign_prayers_to_categories(self) -> None:
        """Assign prayers to their respective categories."""
        for category in self.categories:
            category.category_prayer_list = [
                prayer for prayer in self.prayer_manager.prayers if prayer.category == category.category
            ]
            category.category_display_count = len(category.category_prayer_list)
            logging.debug(f"Assigned {len(category.category_prayer_list)} prayers to category {category.category}")

    def validate(self) -> bool:
        """Validate category data."""
        for category in self.categories:
            if not category.category:
                logging.error(f"Invalid category with empty name: {category}")
                return False
            # Allow empty prayer lists for testing purposes
            if not all(isinstance(prayer, Prayer) for prayer in category.category_prayer_list):
                logging.error(f"Invalid prayer in category {category.category}")
                return False
        return True

class PanelManager:
    """Manages loading and validation of Panel and PanelPgraph objects."""

    def __init__(self, persistence: PersistenceManager, app_database: 'AppDatabase'):
        self.persistence: PersistenceManager = persistence
        self.app_params: AppParams = app_database.app_params
        self.session: PrayerSession = app_database.session
        self.panels: List[Panel] = []

    def load_panels(self, csv_file: str = "panels.csv") -> None:
        """Load panels from CSV and instantiate Panel objects."""
        csv_file = os.path.join(self.persistence.data_dir, csv_file)
        df = self.persistence.load_csv(csv_file)
        panel_set_id = self._get_panel_set_id(df)
        df_panels = df.loc[df['panel_set'] == int(panel_set_id)]

        last_panel_seq = 0
        panel_pgraph_list = []
        current_panel = None
        for row in df_panels.itertuples():
            if not row.text:
                raise DatabaseError(f"Panel row has null text: {row}")
            if last_panel_seq != row.panel_seq:
                if last_panel_seq > 0:
                    current_panel = Panel(last_panel_seq, current_panel.panel_header, panel_pgraph_list)
                    self.panels.append(current_panel)
                    panel_pgraph_list = []
                current_panel = Panel(row.panel_seq, row.header, [])
            verse = None if pd.isna(row.verse) else row.verse
            panel_pgraph = PanelPgraph(row.pgraph_seq, verse, row.text)
            panel_pgraph_list.append(panel_pgraph)
            last_panel_seq = row.panel_seq
        if current_panel:
            current_panel = Panel(last_panel_seq, current_panel.panel_header, panel_pgraph_list)
            self.panels.append(current_panel)
        logging.info(f"Loaded {len(self.panels)} panels from {csv_file}")

    def _get_panel_set_id(self, df: pd.DataFrame) -> int:
        """Get the next panel set ID for the prayer session."""
        last_panel_set = int(self.session.last_panel_set or 1)
        available_panel_sets = sorted(df['panel_set'].unique())
        if not available_panel_sets:
            raise DatabaseError("No panel sets found in CSV")
        # Find the next panel set
        for panel_set in available_panel_sets:
            if panel_set > last_panel_set:
                self.session.last_panel_set = str(panel_set)
                return panel_set
        # If no higher panel set, cycle to the lowest
        self.session.last_panel_set = str(min(available_panel_sets))
        return min(available_panel_sets)

    def validate(self) -> bool:
        """Validate loaded panels."""
        if not self.panels:
            logging.error("No panels loaded")
            return False
        for panel in self.panels:
            if not panel.panel_header:
                logging.error(f"Missing header for panel {panel}")
                return False
            for pgraph in panel.pgraph_list:
                if not pgraph.text:
                    logging.error(f"Missing text for pgraph {pgraph} in panel {panel}")
                    return False
        return True

class AppDatabase:
    """Coordinates database operations for the My Prayers application."""

    def __init__(self, data_dir: str = "../data", pickle_file: str = "objects.pkl",
                 params_file: str = "params.json", categories_file: str = "categories.json",
                 panels_file: str = "panels.csv", prayers_file: str = "prayers.csv",
                 states_file: str = "states.json"):
        self.persistence: PersistenceManager = PersistenceManager(data_dir, pickle_file, params_file,
                                                                  categories_file, states_file)
        self.app_params: AppParams = self._load_params()
        self.session: PrayerSession = PrayerSession()  # Moved before panel_manager
        self.prayer_manager: PrayerManager = PrayerManager(self.persistence)
        self.panel_manager: PanelManager = PanelManager(self.persistence, self)
        self.category_manager: CategoryManager = CategoryManager(self.persistence, self.prayer_manager)

        if os.path.exists(self.persistence.pickle_file):
            self._load_from_pickle()
        else:
            self.panel_manager.load_panels(panels_file)
            self.prayer_manager.load_prayers(prayers_file)
            self.category_manager.load_categories(categories_file)

        if not self.validate():
            raise DatabaseError("Database initialization failed")

    def _load_params(self) -> AppParams:
        """Load application parameters from JSON."""
        try:
            params_data = self.persistence.load_json(self.persistence.params_file)
            return AppParams(params_data)
        except DatabaseError as e:
            logging.error(f"Failed to load parameters: {e}")
            raise

    def _load_from_pickle(self) -> None:
        """Load objects from pickle file, fallback to CSV/JSON if missing."""
        if not os.path.exists(self.persistence.pickle_file):
            logging.info("Pickle file not found, loading from CSV and JSON")
            self.prayer_manager.load_prayers("prayers.csv")
            self.category_manager.load_categories("categories.json")
            self.panel_manager.load_panels("panels.csv")
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)  # Initialize with defaults
            return
        data = self.persistence.load_pickle()
        if not data:
            logging.info("Empty pickle file, loading from CSV and JSON")
            self.prayer_manager.load_prayers("prayers.csv")
            self.category_manager.load_categories("categories.json")
            self.panel_manager.load_panels("panels.csv")
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)  # Initialize with defaults
            return
        self.prayer_manager.prayers = data.get('Prayer_instances', [])
        # Validate Prayer objects
        for prayer in self.prayer_manager.prayers:
            if not hasattr(prayer, '_category'):
                logging.error(f"Invalid Prayer object missing _category: {prayer}")
                raise DatabaseError("Loaded Prayer object missing _category attribute")
        logging.info(f"Loaded {len(self.prayer_manager.prayers)} Prayer instances.")
        self.prayer_manager.answered_prayers = [prayer for prayer in self.prayer_manager.prayers if
                                               prayer.answer_date is None]
        logging.info(f"Computed {len(self.prayer_manager.answered_prayers)} unanswered Prayer instances.")
        self.category_manager.categories = data.get('Category_instances', [])
        logging.info(f"Loaded {len(self.category_manager.categories)} Category instances.")
        sessions = data.get('Session_instances', [])
        logging.info(f"Loaded {len(sessions)} Session instances.")
        if sessions:
            self.session = sessions[-1]
        else:
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)  # Initialize with defaults
        # Panels are loaded from CSV, not pickle
        self.panel_manager.load_panels()

    def create_prayer(self, prayer: Prayer) -> None:
        """Add a new prayer to the database."""
        self.prayer_manager.create_prayer(prayer)
        self.session.new_prayer_added_count += 1

    def save_prayer(self, prayer: Prayer) -> None:
        """Save a single prayer to the database."""
        self.prayer_manager.create_prayer(prayer)
        self.prayer_manager.save_prayers("prayers.csv")

    def retrieve_prayer(self, prayer_text: str) -> Optional[Prayer]:
        """Retrieve a prayer by its text."""
        for prayer in self.prayer_manager.prayers:
            if prayer.prayer == prayer_text:
                return prayer
        return None

    def export(self) -> None:
        """Export prayers and panels to CSV (placeholder)."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        logging.info(f"Exporting database with timestamp {timestamp}")

    def close(self) -> None:
        """Persist all data to files."""
        if not self._validate_session():
            raise DatabaseError("Session validation failed")

        # Update PrayerSession with last_prayer_date, prayer_streak, and last_panel_set
        self.session.last_prayer_date = date.today().strftime("%d-%b-%Y")
        self.session.prayer_streak = self.session.prayer_streak + 1 if self.session.prayer_streak else 1

        objects_to_pickle = {
            'Prayer_instances': self.prayer_manager.prayers,
            'Category_instances': self.category_manager.categories,
            'Session_instances': [self.session]
        }
        self.persistence.save_pickle(objects_to_pickle)

        categories_data = {
            "categories": [
                {
                    "name": category.category,
                    "weight": category.category_weight
                }
                for category in self.category_manager.categories
            ]
        }
        self.persistence.save_json(self.persistence.categories_file, categories_data)

        # Save AppParams without last_panel_set, prayer_streak, last_prayer_date
        params_data = {
            'id': self.app_params.id,
            'id_desc': self.app_params.id_desc,
            'app': self.app_params.app,
            'app_desc': self.app_params.app_desc,
            'install_path': self.app_params.install_path,
            'install_path_desc': self.app_params.install_path_desc,
            'data_file_path': self.app_params.data_file_path,
            'data_file_path_desc': self.app_params.data_file_path_desc,
            'past_prayer_display_count': self.app_params.past_prayer_display_count,
            'past_prayer_display_count_desc': self.app_params.past_prayer_display_count_desc
        }
        self.persistence.save_json(self.persistence.params_file, params_data)

    def validate(self) -> bool:
        """Validate all database components."""
        return (
            self.panel_manager.validate() and
            self.prayer_manager.validate() and
            self.category_manager.validate()
        )

    def _validate_session(self) -> bool:
        """Validate the current prayer session."""
        logging.info(f"Session validation: new_prayer_added_count={self.session.new_prayer_added_count}, "
                     f"past_prayer_prayed_count={self.session.past_prayer_prayed_count}")
        if self.session.new_prayer_added_count == 0:
            logging.warning("No new prayers added in session")
        if self.session.past_prayer_prayed_count == 0:
            logging.warning("No past prayers prayed in session")
        return True