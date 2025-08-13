# db_manager.py
# Handles data management and database interactions.

"""
This module manages data storage and retrieval for the My Prayers application, acting as the Model in MVC. It
handles loading and saving prayers, categories, panels, and session data using files (JSON for configs,
CSV for lists, pickle for objects). It includes managers for prayers, categories, and panels, with validation to
ensure data integrity. Beginners can see this as the 'filing cabinet' where the app stores and fetches information
reliably.
"""

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
    """
    Custom exception for database-related errors.

    Raised when file operations or data validation fail, like missing files or corrupt data.
    """


class PersistenceManager:
    """
    Handles file I/O operations for persistence (pickle, JSON, CSV).

    Manages reading and writing data to files for long-term storage.
    """

    def __init__(self, data_dir: str = "../data", pickle_file: str = "objects.pkl",
                 params_file: str = "params.json", categories_file: str = "categories.json",
                 states_file: str = "states.json"):
        """
        Initialize PersistenceManager with file paths.

        Args:
            data_dir (str): Directory for data files (defaults to '../data').
            pickle_file (str): File for storing objects (defaults to 'objects.pkl').
            params_file (str): File for app parameters (defaults to 'params.json').
            categories_file (str): File for category data (defaults to 'categories.json').
            states_file (str): File for state machine data (defaults to 'states.json').
        """
        self.data_dir: str = data_dir
        self.pickle_file: str = os.path.join(data_dir, pickle_file)
        self.params_file: str = os.path.join(data_dir, params_file)
        self.categories_file: str = os.path.join(data_dir, categories_file)
        self.states_file: str = os.path.join(data_dir, states_file)

    def load_pickle(self) -> Dict:
        """
        Load objects from the pickle file.

        Returns:
            Dict: Dictionary of stored objects (e.g., prayers, categories).

        Raises:
            DatabaseError: If the pickle file is missing or corrupt.
        """
        try:
            if not os.path.exists(self.pickle_file):
                return {}
            with open(self.pickle_file, "rb") as file:
                return pickle.load(file)
        except (pickle.UnpicklingError, EOFError) as e:
            logging.warning(f"Failed to load pickle file {self.pickle_file}: {e}. Falling back to empty dict.")
            return {}

    def save_pickle(self, objects: Dict) -> None:
        """
        Save objects to the pickle file.

        Args:
            objects (Dict): Dictionary of objects to save.

        Raises:
            DatabaseError: If saving to the pickle file fails.
        """
        try:
            os.makedirs(self.data_dir, exist_ok=True)  # Ensure data directory exists
            with open(self.pickle_file, "wb") as file:  # type: BinaryIO
                pickle.dump(objects, file)  # type: ignore
        except Exception as e:
            logging.error(f"Failed to save pickle file {self.pickle_file}: {e}")
            raise DatabaseError(f"Failed to save pickle file: {e}")

    @staticmethod
    def load_json(file_path: str) -> Dict:
        """
        Load data from a JSON file.

        Args:
            file_path (str): Path to the JSON file.

        Returns:
            Dict: The parsed JSON data.

        Raises:
            DatabaseError: If the JSON file is missing or invalid.
        """
        try:
            if not os.path.exists(file_path):
                raise DatabaseError(f"JSON file {file_path} not found")
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON file {file_path}: {e}")
            raise DatabaseError(f"Failed to parse JSON file: {e}")

    def save_json(self, file_path: str, data: Dict) -> None:
        """
        Save data to a JSON file.

        Args:
            file_path (str): Path to save the JSON file.
            data (Dict): Data to save.

        Raises:
            DatabaseError: If saving the JSON file fails.
        """
        try:
            os.makedirs(self.data_dir, exist_ok=True)  # Ensure data directory exists
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            logging.error(f"Failed to save JSON file {file_path}: {e}")
            raise DatabaseError(f"Failed to save JSON file: {e}")

    @staticmethod
    def load_csv(file_path: str) -> pd.DataFrame:
        """
        Load a CSV file into a pandas DataFrame.

        Args:
            file_path (str): Path to the CSV file.

        Returns:
            pd.DataFrame: The loaded data as a DataFrame.

        Raises:
            DatabaseError: If loading the CSV file fails.
        """
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
        """
        Load state transitions from states.json.

        Returns:
            List[Dict]: List of state data dictionaries.

        Raises:
            DatabaseError: If the states file is missing or invalid.
        """
        try:
            data = self.load_json(self.states_file)
            if not isinstance(data, list):
                raise DatabaseError("Invalid JSON format in states.json: Expected a list of states")
            return data
        except DatabaseError as e:
            logging.error(f"Failed to load states: {e}")
            raise


class PrayerManager:
    """
    Manages Prayer objects and their persistence.

    Handles loading, saving, and validating prayers in the database.
    """

    def __init__(self, persistence: PersistenceManager):
        """
        Initialize PrayerManager with a persistence manager.

        Args:
            persistence (PersistenceManager): Manager for file operations.
        """
        self.persistence: PersistenceManager = persistence
        self.prayers: List[Prayer] = []
        self.answered_prayers: List[Prayer] = []

    def load_prayers(self, prayers_file: str) -> None:
        """
        Load prayers from a CSV file.

        Args:
            prayers_file (str): Path to the CSV file with prayer data.

        Populates the prayers list and updates answered_prayers for unanswered prayers.
        """
        try:
            df = self.persistence.load_csv(os.path.join(self.persistence.data_dir, prayers_file))
            for _, row in df.iterrows():
                prayer = Prayer(
                    prayer=row['prayer'],
                    category=row['category'],
                    create_date=row.get('create_date'),
                    answer_date=row.get('answer_date'),
                    answer=row.get('answer'),
                    display_count=row.get('display_count', 0)
                )
                self.prayers.append(prayer)
                if prayer.answer_date is None:
                    self.answered_prayers.append(prayer)
        except Exception as e:
            logging.error(f"Failed to load prayers from {prayers_file}: {e}")
            raise DatabaseError(f"Failed to load prayers: {e}")

    def save_prayers(self, prayers_file: str) -> None:
        """
        Save prayers to a CSV file.

        Args:
            prayers_file (str): Path to save the CSV file.

        Raises:
            DatabaseError: If saving the CSV file fails.
        """
        try:
            data = []
            for prayer in self.prayers:
                data.append({
                    'prayer': prayer.prayer,
                    'category': prayer.category,
                    'create_date': prayer.create_date,
                    'answer_date': prayer.answer_date,
                    'answer': prayer.answer,
                    'display_count': prayer.display_count
                })
            df = pd.DataFrame(data)
            df.to_csv(os.path.join(self.persistence.data_dir, prayers_file), index=False)
        except Exception as e:
            logging.error(f"Failed to save prayers to {prayers_file}: {e}")
            raise DatabaseError(f"Failed to save prayers: {e}")

    def create_prayer(self, prayer: Prayer) -> None:
        """
        Add a new prayer to the prayers list.

        Args:
            prayer (Prayer): The prayer to add.

        Raises:
            DatabaseError: If the prayer is invalid.
        """
        if not isinstance(prayer, Prayer):
            raise DatabaseError("Invalid prayer object")
        self.prayers.append(prayer)
        if prayer.answer_date is None:
            self.answered_prayers.append(prayer)

    def get_unanswered_prayers(self) -> List[Prayer]:
        """
        Get all unanswered prayers.

        Returns:
            List[Prayer]: List of prayers with no answer date.
        """
        return [prayer for prayer in self.prayers if prayer.answer_date is None]

    def validate(self) -> bool:
        """
        Validate all prayers in the manager.

        Returns:
            bool: True if all prayers are valid, False otherwise.
        """
        for prayer in self.prayers:
            if not isinstance(prayer, Prayer) or not prayer.prayer:
                logging.error(f"Invalid prayer in manager: {prayer}")
                return False
        return True


class CategoryManager:
    """
    Manages Category objects and their persistence.

    Handles loading, saving, and validating categories in the database.
    """

    def __init__(self, persistence: PersistenceManager):
        """
        Initialize CategoryManager with a persistence manager.

        Args:
            persistence (PersistenceManager): Manager for file operations.
        """
        self.persistence: PersistenceManager = persistence
        self.categories: List[Category] = []

    def load_categories(self, categories_file: str) -> None:
        """
        Load categories from a JSON file.

        Args:
            categories_file (str): Path to the JSON file with category data.

        Raises:
            DatabaseError: If loading the categories fails.
        """
        try:
            data = self.persistence.load_json(os.path.join(self.persistence.data_dir, categories_file))
            for category_data in data.get('categories', []):
                category = Category(
                    category=category_data['name'],
                    count=category_data.get('count', 0),
                    weight=category_data.get('weight', 1)
                )
                self.categories.append(category)
        except Exception as e:
            logging.error(f"Failed to load categories from {categories_file}: {e}")
            raise DatabaseError(f"Failed to load categories: {e}")

    def save_categories(self) -> None:
        """
        Save categories to a JSON file.

        Raises:
            DatabaseError: If saving the categories fails.
        """
        try:
            categories_data = {
                'categories': [
                    {
                        'name': category.category,
                        'count': category.category_display_count,
                        'weight': category.category_weight
                    }
                    for category in self.categories
                ]
            }
            self.persistence.save_json(self.persistence.categories_file, categories_data)
        except Exception as e:
            logging.error(f"Failed to save categories: {e}")
            raise DatabaseError(f"Failed to save categories: {e}")

    def validate(self) -> bool:
        """
        Validate all categories in the manager.

        Returns:
            bool: True if all categories are valid, False otherwise.
        """
        for category in self.categories:
            if not isinstance(category, Category) or not category.category:
                logging.error(f"Invalid category in manager: {category}")
                return False
        return True


class PanelManager:
    """
    Manages Panel objects and their persistence.

    Handles loading, saving, and validating panels in the database.
    """

    def __init__(self, persistence: PersistenceManager):
        """
        Initialize PanelManager with a persistence manager.

        Args:
            persistence (PersistenceManager): Manager for file operations.
        """
        self.persistence: PersistenceManager = persistence
        self.panels: List[Panel] = []

    def load_panels(self, panels_file: str) -> None:
        """
        Load panels from a CSV file.

        Args:
            panels_file (str): Path to the CSV file with panel data.

        Raises:
            DatabaseError: If loading the panels fails.
        """
        try:
            df = self.persistence.load_csv(os.path.join(self.persistence.data_dir, panels_file))
            panel_dict = {}
            for _, row in df.iterrows():
                panel_set = row['panel_set']
                if panel_set not in panel_dict:
                    panel_dict[panel_set] = {
                        'header': row['header'],
                        'panel_seq': row['panel_seq'],
                        'pgraph_list': []
                    }
                panel_dict[panel_set]['pgraph_list'].append(
                    PanelPgraph(
                        pgraph_seq=row['pgraph_seq'],
                        verse=row.get('verse'),
                        text=row['text']
                    )
                )
            for panel_set, data in panel_dict.items():
                panel = Panel(
                    panel_seq=data['panel_seq'],
                    panel_header=data['header'],
                    pgraph_list=data['pgraph_list']
                )
                self.panels.append(panel)
        except Exception as e:
            logging.error(f"Failed to load panels from {panels_file}: {e}")
            raise DatabaseError(f"Failed to load panels: {e}")

    def validate(self) -> bool:
        """
        Validate all panels in the manager.

        Returns:
            bool: True if all panels are valid, False otherwise.
        """
        for panel in self.panels:
            if not isinstance(panel, Panel) or not panel.pgraph_list:
                logging.error(f"Invalid panel in manager: {panel}")
                return False
            for pgraph in panel.pgraph_list:
                if not isinstance(pgraph, PanelPgraph) or not pgraph.text:
                    logging.error(f"Invalid paragraph in panel: {pgraph}")
                    return False
        return True


class AppDatabase:
    """
    Main database class coordinating all managers.

    Acts as the Model in MVC, managing data operations for prayers, categories, panels, and sessions.
    """

    def __init__(self, data_dir: str = "../data", states_file: str = "states.json"):
        """
        Initialize AppDatabase with managers and load initial data.

        Args:
            data_dir (str): Directory for data files (defaults to '../data').
            states_file (str): File for state machine data (defaults to 'states.json').
        """
        self.persistence: PersistenceManager = PersistenceManager(data_dir=data_dir, states_file=states_file)
        self.prayer_manager: PrayerManager = PrayerManager(self.persistence)
        self.category_manager: CategoryManager = CategoryManager(self.persistence)
        self.panel_manager: PanelManager = PanelManager(self.persistence)
        self.session: PrayerSession = None  # type: ignore
        self.app_params: AppParams = self._load_params()
        self._load_from_pickle()

    def _load_params(self) -> AppParams:
        """
        Load application parameters from JSON.

        Returns:
            AppParams: The loaded parameters.

        Raises:
            DatabaseError: If loading the params file fails.
        """
        try:
            params_data = self.persistence.load_json(self.persistence.params_file)
            return AppParams(params_data)
        except DatabaseError as e:
            logging.error(f"Failed to load parameters: {e}")
            raise

    def _load_from_pickle(self) -> None:
        """
        Load objects from pickle file, fallback to CSV/JSON if missing.

        Loads prayers, categories, and session data, or initializes defaults if the pickle file is missing.
        """
        if not os.path.exists(self.persistence.pickle_file):
            logging.info("Pickle file not found, loading from CSV and JSON")
            self.prayer_manager.load_prayers("prayers.csv")
            self.category_manager.load_categories("categories.json")
            self.panel_manager.load_panels("panels.csv")
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)  # Initialize
            # with defaults
            return
        data = self.persistence.load_pickle()
        if not data:
            logging.info("Empty pickle file, loading from CSV and JSON")
            self.prayer_manager.load_prayers("prayers.csv")
            self.category_manager.load_categories("categories.json")
            self.panel_manager.load_panels("panels.csv")
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)  # Initialize
            # with defaults
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
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)  # Initialize
            # with defaults

    def create_prayer(self, prayer: Prayer) -> None:
        """
        Add a new prayer to the database.

        Args:
            prayer (Prayer): The Prayer object to add.

        Updates the session's new prayer count.
        """
        self.prayer_manager.create_prayer(prayer)
        self.session.new_prayer_added_count += 1

    def save_prayer(self, prayer: Prayer) -> None:
        """
        Save a single prayer to the database.

        Args:
            prayer (Prayer): The Prayer object to save.

        Saves the prayer to the CSV file and updates the prayers list.
        """
        self.prayer_manager.create_prayer(prayer)
        self.prayer_manager.save_prayers("prayers.csv")

    def retrieve_prayer(self, prayer_text: str) -> Optional[Prayer]:
        """
        Retrieve a prayer by its text.

        Args:
            prayer_text (str): The text of the prayer to find.

        Returns:
            Optional[Prayer]: The matching Prayer object, or None if not found.
        """
        for prayer in self.prayer_manager.prayers:
            if prayer.prayer == prayer_text:
                return prayer
        return None

    def export(self) -> None:
        """
        Export prayers and panels to CSV (placeholder).

        Logs the export with a timestamp for tracking.
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        logging.info(f"Exporting database with timestamp {timestamp}")

    def close(self) -> None:
        """
        Persist all data to files.

        Saves prayers, categories, and session data to their respective files.
        """
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
        """
        Validate all database components.

        Returns:
            bool: True if all managers (prayer, category, panel) are valid, False otherwise.
        """
        return (
                self.panel_manager.validate() and
                self.prayer_manager.validate() and
                self.category_manager.validate()
        )

    def _validate_session(self) -> bool:
        """
        Validate the current prayer session.

        Returns:
            bool: True if the session is valid, False if issues are found.

        Logs warnings if no new or past prayers were processed.
        """
        logging.info(f"Session validation: new_prayer_added_count={self.session.new_prayer_added_count}, "
                     f"past_prayer_prayed_count={self.session.past_prayer_prayed_count}")
        if self.session.new_prayer_added_count == 0:
            logging.warning("No new prayers added in session")
        if self.session.past_prayer_prayed_count == 0:
            logging.warning("No past prayers prayed in session")
        return True