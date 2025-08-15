# db_manager.py

import pandas as pd
import pickle
import json
import os
import random
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from typing import IO, BinaryIO
import logging

from mpo_model import Prayer, Category, Panel, PanelPgraph, AppParams, PrayerSession


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass


class PersistenceManager:
    """Handles file I/O operations for persistence (pickle, JSON, CSV)."""

    def __init__(self, data_dir: str = None, pickle_file: str = "objects.pkl",
                 params_file: str = "params.json", categories_file: str = "categories.json",
                 states_file: str = "states.json"):
        # Set data_dir to project_root/data if not provided
        if data_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(project_root, "data")
        self.data_dir: str = data_dir
        self.pickle_file: str = os.path.join(data_dir, pickle_file)
        self.params_file: str = os.path.join(data_dir, params_file)
        self.categories_file: str = os.path.join(data_dir, categories_file)
        self.states_file: str = os.path.join(data_dir, states_file)

    def load_pickle(self) -> Dict[str, List[Any]]:
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


class PanelManager:
    """Manages loading and validation of Panel and PanelPgraph objects."""

    def __init__(self, persistence: PersistenceManager, app_database: 'AppDatabase'):
        self.persistence: PersistenceManager = persistence
        self.app_params: AppParams = app_database.app_params
        self.session: PrayerSession = app_database.session
        self.panels: List[Panel] = []
        logging.info(f"PanelManager initialized with last_panel_set: {self.session.last_panel_set}")

    def load_panels(self, csv_file: str = "panels.csv") -> None:
        """Load panels from CSV and instantiate Panel objects."""
        csv_file = os.path.join(self.persistence.data_dir, csv_file)
        df = self.persistence.load_csv(csv_file)
        logging.info(f"Before _get_panel_set_id last_panel_set: {self.session.last_panel_set}")
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
        logging.info(f"Loaded {len(self.panels)} panels from {csv_file} with panel_set {panel_set_id}")

    def _get_panel_set_id(self, df: pd.DataFrame) -> int:
        """Get the next panel set ID for the prayer session, rotating sequentially."""
        available_panel_sets = sorted(df['panel_set'].unique())
        if not available_panel_sets:
            raise DatabaseError("No panel sets found in CSV")
        logging.info(f"Available panel sets: {available_panel_sets}")

        # Log the initial state of last_panel_set
        logging.info(f"Initial last_panel_set: {self.session.last_panel_set}")

        # Check if last_panel_set exists and is valid
        last_panel_set = None
        if self.session.last_panel_set is not None:
            try:
                last_panel_set = int(self.session.last_panel_set)
                logging.info(f"Converted last_panel_set to int: {last_panel_set}")
                # Verify if last_panel_set is in available_panel_sets
                if last_panel_set not in available_panel_sets:
                    logging.warning(f"last_panel_set {last_panel_set} not in available panel sets, defaulting to None")
                    last_panel_set = None
            except (ValueError, TypeError) as e:
                logging.warning(f"Invalid last_panel_set '{self.session.last_panel_set}' due to {e}, defaulting to None")
                last_panel_set = None
        else:
            logging.info("last_panel_set is None")

        # If no valid last_panel_set, select the first panel set
        if last_panel_set is None:
            selected_panel_set = min(available_panel_sets)
            self.session.last_panel_set = str(selected_panel_set)
            logging.info(f"No valid last_panel_set, selected panel_set: {selected_panel_set}")
            return selected_panel_set

        # Find the next panel set greater than last_panel_set
        for panel_set in available_panel_sets:
            if panel_set > last_panel_set:
                self.session.last_panel_set = str(panel_set)
                logging.info(f"Selected next panel_set: {panel_set}")
                return panel_set

        # If no panel set is greater, cycle to the first panel set
        selected_panel_set = min(available_panel_sets)
        self.session.last_panel_set = str(selected_panel_set)
        logging.info(f"Cycled to first panel_set: {selected_panel_set}")
        return selected_panel_set

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


class PrayerManager:
    """Manages loading, creation, and validation of Prayer objects."""

    def __init__(self, persistence: PersistenceManager):
        self.persistence: PersistenceManager = persistence
        self.prayers: List[Prayer] = []

    def load_prayers(self, csv_file: str = "prayers.csv") -> None:
        """Load prayers from CSV and instantiate Prayer objects."""
        csv_file = os.path.join(self.persistence.data_dir, csv_file)
        df = self.persistence.load_csv(csv_file)
        for row in df.itertuples():
            # Read display_count from CSV if available, default to 0 if missing or invalid
            display_count = 0
            if hasattr(row, 'display_count') and not pd.isna(row.display_count):
                try:
                    display_count = int(row.display_count)
                    if display_count < 0:
                        display_count = 0
                        logging.warning(
                            f"Invalid display_count {row.display_count} for prayer '{row.prayer}', setting to 0")
                except (ValueError, TypeError):
                    logging.warning(
                        f"Invalid display_count {row.display_count} for prayer '{row.prayer}', setting to 0")
            prayer = Prayer(
                prayer=row.prayer,
                create_date=row.create_date,
                answer_date=None if pd.isna(row.answer_date) else row.answer_date,
                category=row.category,
                answer=None if pd.isna(row.answer) else row.answer,
                display_count=display_count
            )
            self.prayers.append(prayer)

    def create_prayer(self, prayer: Prayer) -> None:
        """Add a new prayer to the in-memory database."""
        if not isinstance(prayer, Prayer):
            raise DatabaseError(f"Invalid prayer object: {prayer}")
        self.prayers.append(prayer)
        logging.info(f"Created prayer: {prayer.prayer}")

    def get_unanswered_prayers(self) -> List[Prayer]:
        """Return a list of unanswered prayers."""
        return [prayer for prayer in self.prayers if prayer.answer_date is None]

    def validate(self) -> bool:
        """Validate loaded prayers."""
        if not self.prayers:
            logging.warning("No prayers loaded")
            return True  # Allow empty prayer list for initial setup
        return True


class CategoryManager:
    """Manages loading, weighting, and validation of Category objects."""

    def __init__(self, persistence: PersistenceManager, prayer_manager: PrayerManager):
        self.persistence: PersistenceManager = persistence
        self.prayer_manager: PrayerManager = prayer_manager
        self.categories: List[Category] = []
        self.weighted_categories: List[Category] = []

    def load_categories(self, json_file: str = "categories.json") -> None:
        """Load categories from JSON and instantiate Category objects."""
        json_file = os.path.join(self.persistence.data_dir, json_file)
        try:
            data = self.persistence.load_json(json_file)
            json_categories = []
            for c in data.get('categories', []):
                category = Category(c['name'], count=0, weight=c['weight'])  # Set count to 0
                self.categories.append(category)
                json_categories.append(c['name'])

            prayer_categories = set(prayer.category for prayer in self.prayer_manager.get_unanswered_prayers())
            unique_categories = [c for c in prayer_categories if c not in json_categories]
            for c in unique_categories:
                self.categories.append(Category(category=c, count=0, weight=1))

            for category in self.categories:
                category.category_prayer_list = [
                    prayer for prayer in self.prayer_manager.get_unanswered_prayers()
                    if prayer.category == category.category
                ]

            self.weighted_categories = []
            for category in self.categories:
                for _ in range(category.category_weight):
                    self.weighted_categories.append(category)
            self.weighted_categories.extend(self.categories)
            random.shuffle(self.weighted_categories)
        except DatabaseError as e:
            logging.error(f"Failed to load categories: {e}")
            raise

    def validate(self) -> bool:
        """Validate loaded categories."""
        prayer_count = sum(len(category.category_prayer_list) for category in self.categories)
        if prayer_count == 0:
            logging.error("No prayers in category prayer lists")
            return False
        if not self.prayer_manager.prayers:
            logging.error("No prayers loaded")
            return False
        if not self.prayer_manager.get_unanswered_prayers():
            logging.error("No unanswered prayers loaded")
            return False
        if not os.path.exists(self.persistence.categories_file):
            logging.error("No categories.json file")
            return False
        return True


class AppDatabase:
    """Coordinates database operations for the My Prayers application."""

    def __init__(self, data_dir: str = None, pickle_file: str = "objects.pkl",
                 params_file: str = "params.json", categories_file: str = "categories.json",
                 panels_file: str = "panels.csv", prayers_file: str = "prayers.csv",
                 states_file: str = "states.json"):
        # Set data_dir to project_root/data if not provided
        if data_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(project_root, "data")
        self.persistence: PersistenceManager = PersistenceManager(data_dir, pickle_file, params_file,
                                                                  categories_file, states_file)
        self.app_params: AppParams = self._load_params()
        # Initialize session after loading from pickle to avoid overwriting
        self.session: PrayerSession = None
        self.prayer_manager: PrayerManager = PrayerManager(self.persistence)
        self.panel_manager: PanelManager = None
        self.category_manager: CategoryManager = CategoryManager(self.persistence, self.prayer_manager)

        if os.path.exists(self.persistence.pickle_file):
            self._load_from_pickle()
        else:
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)
            self.panel_manager = PanelManager(self.persistence, self)
            self.prayer_manager.load_prayers(prayers_file)
            self.category_manager.load_categories(categories_file)
            self.panel_manager.load_panels(panels_file)

        logging.info(f"After initialization last_panel_set: {self.session.last_panel_set}")
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
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)
            self.panel_manager = PanelManager(self.persistence, self)
            self.prayer_manager.load_prayers("prayers.csv")
            self.category_manager.load_categories("categories.json")
            self.panel_manager.load_panels("panels.csv")
            return
        data = self.persistence.load_pickle()
        if not data:
            logging.info("Empty pickle file, loading from CSV and JSON")
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)
            self.panel_manager = PanelManager(self.persistence, self)
            self.prayer_manager.load_prayers("prayers.csv")
            self.category_manager.load_categories("categories.json")
            self.panel_manager.load_panels("panels.csv")
            return
        self.prayer_manager.prayers = data.get('Prayer_instances', [])
        # Validate Prayer objects
        for prayer in self.prayer_manager.prayers:
            if not hasattr(prayer, '_category'):
                logging.error(f"Invalid Prayer object missing _category: {prayer}")
                raise DatabaseError("Loaded Prayer object missing _category attribute")
        logging.info(f"Loaded {len(self.prayer_manager.prayers)} Prayer instances.")
        sessions = data.get('Session_instances', [])
        logging.info(f"Loaded {len(sessions)} Session instances.")
        if sessions:
            self.session = sessions[-1]
            logging.info(f"Loaded session last_panel_set: {self.session.last_panel_set}")
        else:
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)
        # Initialize panel_manager after session is loaded
        self.panel_manager = PanelManager(self.persistence, self)
        # Panels are loaded from CSV, not pickle
        logging.info(f"Before load_panels() last_panel_set: {self.session.last_panel_set}")
        self.panel_manager.load_panels()

    def create_prayer(self, prayer: Prayer) -> None:
        """Add a new prayer to the database."""
        self.prayer_manager.create_prayer(prayer)
        self.session.new_prayer_added_count += 1

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
        logging.info(f"Saving last_panel_set: {self.session.last_panel_set}")

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
                     f"past_prayer_prayed_count={self.session.past_prayer_prayed_count}, "
                     f"last_panel_set={self.session.last_panel_set}")
        if self.session.new_prayer_added_count == 0:
            logging.warning("No new prayers added in session")
        if self.session.past_prayer_prayed_count == 0:
            logging.warning("No past prayers prayed in session")
        return True