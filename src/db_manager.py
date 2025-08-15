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
        if data_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(project_root, "data")
        self.data_dir: str = data_dir
        self.pickle_file: str = os.path.join(data_dir, pickle_file)
        self.params_file: str = os.path.join(data_dir, params_file)
        self.categories_file: str = os.path.join(data_dir, categories_file)
        self.states_file: str = os.path.join(data_dir, states_file)

    def load_pickle(self) -> Dict[str, List[Any]]:
        """Load objects from the pickle file with validation."""
        try:
            if not os.path.exists(self.pickle_file):
                return {}
            with open(self.pickle_file, "rb") as file:
                data = pickle.load(file)
                # Validate Category_instances
                for category in data.get('Category_instances', []):
                    if not hasattr(category, 'category') or not hasattr(category, 'category_weight'):
                        logging.error(f"Invalid Category object in pickle: {category}")
                        raise DatabaseError("Loaded Category object missing required attributes")
                # Validate State_instances
                for state in data.get('State_instances', []):
                    if not isinstance(state, dict) or 'state' not in state or 'auto_trigger' not in state:
                        logging.error(f"Invalid State object in pickle: {state}")
                        raise DatabaseError("Loaded State object missing required fields")
                return data
        except (pickle.UnpicklingError, EOFError) as e:
            logging.error(f"Failed to unpickle {self.pickle_file}: {e}")
            raise DatabaseError(f"Failed to load pickle file: {e}")

    def save_pickle(self, objects: Dict) -> None:
        """Save objects to the pickle file."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.pickle_file, "wb") as file:  # type: BinaryIO
                pickle.dump(objects, file)  # type: ignore
        except Exception as e:
            logging.error(f"Failed to save pickle file {self.pickle_file}: {e}")
            raise DatabaseError(f"Failed to save pickle file: {e}")

    def load_json(self, file_path: str) -> Dict:
        """Load data from a JSON file."""
        file_path = os.path.join(self.data_dir, file_path) if not os.path.isabs(file_path) else file_path
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
        file_path = os.path.join(self.data_dir, file_path) if not os.path.isabs(file_path) else file_path
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            logging.error(f"Failed to save JSON file {file_path}: {e}")
            raise DatabaseError(f"Failed to save JSON file: {e}")

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load a CSV file into a pandas DataFrame."""
        file_path = os.path.join(self.data_dir, file_path) if not os.path.isabs(file_path) else file_path
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
        """Load state transitions from states.json with validation."""
        try:
            data = self.load_json(self.states_file)
            if not isinstance(data, list):
                raise DatabaseError("Invalid JSON format in states.json: Expected a list of states")
            for state in data:
                if not isinstance(state, dict) or 'state' not in state or 'auto_trigger' not in state:
                    raise DatabaseError(f"Invalid state in states.json: {state}")
            return data
        except DatabaseError as e:
            logging.error(f"Failed to load states: {e}")
            raise

    def load_app_params(self) -> AppParams:
        """Load application parameters from JSON, create default if missing."""
        try:
            params_data = self.load_json(self.params_file)
            return AppParams(**params_data)
        except DatabaseError as e:
            logging.warning(f"params.json not found or invalid: {e}, creating default")
            default_params = {"data_file_path": self.data_dir}
            self.save_json(self.params_file, default_params)
            return AppParams(**default_params)


class PanelManager:
    """Manages loading and validation of Panel and PanelPgraph objects."""

    def __init__(self, persistence: PersistenceManager, app_database: 'AppDatabase'):
        self.persistence: PersistenceManager = persistence
        self.app_params: AppParams = app_database.app_params
        self.session: PrayerSession = app_database.session
        self.state_data: List[Dict] = app_database.state_data
        self.panels: List[Panel] = []
        self.num_non_auto_trigger = len([s for s in self.state_data if not s.get('auto_trigger', False)])
        logging.info(f"PanelManager initialized with num_non_auto_trigger: {self.num_non_auto_trigger}")
        logging.info(f"PanelManager initialized with last_panel_set: {self.session.last_panel_set}")

    def load_panels(self, csv_file: str = "panels.csv") -> None:
        """Load panels from CSV and validate count per set."""
        csv_file = os.path.join(self.persistence.data_dir, csv_file)
        df = self.persistence.load_csv(csv_file)
        df = df.sort_values(by=['panel_set', 'panel_seq', 'pgraph_seq'])
        self.panel_sets = sorted(df['panel_set'].unique())
        self.all_panels = {}
        for ps in self.panel_sets:
            group = df[df['panel_set'] == ps]
            unique_panels = group['panel_seq'].unique()
            if len(unique_panels) != self.num_non_auto_trigger:
                raise DatabaseError(
                    f"Panel set {ps} has {len(unique_panels)} panels, expected {self.num_non_auto_trigger}.")
            panels = []
            current_panel = None
            for _, row in group.iterrows():
                if current_panel is None or current_panel.panel_seq != row['panel_seq']:
                    if current_panel:
                        panels.append(current_panel)
                    pgraph_list = []
                    current_panel = Panel(int(row['panel_seq']), row['header'], pgraph_list)
                pgraph = PanelPgraph(
                    int(row['pgraph_seq']),
                    None if pd.isna(row.get('verse')) else row.get('verse'),
                    None if pd.isna(row.get('text')) else row.get('text')
                )
                current_panel.pgraph_list.append(pgraph)
            if current_panel:
                panels.append(current_panel)
            self.all_panels[ps] = sorted(panels, key=lambda p: p.panel_seq)
        selected_panel_set = self._get_panel_set_id(df)
        self.panels = self.all_panels.get(selected_panel_set, [])
        logging.info(f"Selected panel set {selected_panel_set} with {len(self.panels)} panels")

    def _get_panel_set_id(self, df: pd.DataFrame) -> int:
        """Get the next panel set ID for the prayer session, rotating sequentially."""
        available_panel_sets = sorted(df['panel_set'].unique())
        if not available_panel_sets:
            raise DatabaseError("No panel sets found in CSV")
        logging.info(f"Available panel sets: {available_panel_sets}")
        logging.info(f"Initial last_panel_set: {self.session.last_panel_set}")
        last_panel_set = None
        if self.session.last_panel_set is not None:
            try:
                last_panel_set = int(self.session.last_panel_set)
                logging.info(f"Converted last_panel_set to int: {last_panel_set}")
                if last_panel_set not in available_panel_sets:
                    logging.warning(f"last_panel_set {last_panel_set} not in available panel sets, defaulting to None")
                    last_panel_set = None
            except (ValueError, TypeError) as e:
                logging.warning(f"Invalid last_panel_set '{self.session.last_panel_set}' due to {e}, defaulting to None")
                last_panel_set = None
        else:
            logging.info("last_panel_set is None")
        if last_panel_set is None:
            selected_panel_set = min(available_panel_sets)
            self.session.last_panel_set = str(selected_panel_set)
            logging.info(f"No valid last_panel_set, selected panel_set: {selected_panel_set}")
            return selected_panel_set
        for panel_set in available_panel_sets:
            if panel_set > last_panel_set:
                self.session.last_panel_set = str(panel_set)
                logging.info(f"Selected next panel_set: {panel_set}")
                return panel_set
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
        try:
            df = self.persistence.load_csv(csv_file)
            for row in df.itertuples():
                if not row.prayer:
                    logging.warning(f"Skipping prayer row with null prayer: {row}")
                    continue
                prayer = Prayer(
                    prayer=row.prayer,
                    category=row.category,
                    create_date=row.create_date,
                    answer_date=None if pd.isna(row.answer_date) else row.answer_date,
                    answer=None if pd.isna(row.answer) else row.answer,
                    display_count=0 if pd.isna(row.display_count) else int(row.display_count)
                )
                self.prayers.append(prayer)
            logging.info(f"Loaded {len(self.prayers)} prayers from {csv_file}")
        except DatabaseError as e:
            logging.error(f"Failed to load prayers: {e}")
            raise

    def create_prayer(self, prayer: Prayer) -> None:
        """Add a new prayer to the list and save to CSV."""
        self.prayers.append(prayer)
        self._save_prayers()

    def get_unanswered_prayers(self) -> List[Prayer]:
        """Return a list of unanswered prayers."""
        return [prayer for prayer in self.prayers if prayer.answer_date is None]

    def _save_prayers(self, csv_file: str = "prayers.csv") -> None:
        """Save prayers to CSV."""
        csv_file = os.path.join(self.persistence.data_dir, csv_file)
        try:
            prayers_data = [
                {
                    "prayer": prayer.prayer,
                    "category": prayer.category,
                    "create_date": prayer.create_date,
                    "answer_date": prayer.answer_date,
                    "answer": prayer.answer,
                    "display_count": prayer.display_count
                }
                for prayer in self.prayers
            ]
            df = pd.DataFrame(prayers_data)
            df.to_csv(csv_file, index=False)
            logging.info(f"Saved {len(self.prayers)} prayers to {csv_file}")
        except Exception as e:
            logging.error(f"Failed to save prayers to {csv_file}: {e}")
            raise DatabaseError(f"Failed to save prayers: {e}")

    def mark_prayer_answered(self, prayer_text: str, answer: str) -> None:
        """Mark a prayer as answered with the given answer text."""
        for prayer in self.prayers:
            if prayer.prayer == prayer_text:
                prayer.answer_date = date.today().strftime("%d-%b-%Y")
                prayer.answer = answer
                self._save_prayers()
                logging.info(f"Marked prayer '{prayer_text}' as answered with answer '{answer}'")
                return
        logging.warning(f"Prayer '{prayer_text}' not found for marking as answered")
        raise DatabaseError(f"Prayer '{prayer_text}' not found")

    def validate(self) -> bool:
        """Validate loaded prayers."""
        if not self.prayers:
            logging.warning("No prayers loaded")
        for prayer in self.prayers:
            if not prayer.prayer:
                logging.error(f"Invalid prayer with missing text: {prayer}")
                return False
            if not prayer.category:
                logging.error(f"Invalid prayer with missing category: {prayer}")
                return False
            if not prayer.create_date:
                logging.error(f"Invalid prayer with missing create_date: {prayer}")
                return False
        return True


class CategoryManager:
    """Manages loading and validation of Category objects."""

    def __init__(self, persistence: PersistenceManager, prayer_manager: PrayerManager):
        self.persistence: PersistenceManager = persistence
        self.prayer_manager: PrayerManager = prayer_manager
        self.categories: List[Category] = []
        self.weighted_categories: List[Category] = []

    def load_categories(self, json_file: str = "categories.json") -> None:
        """Load categories from JSON if not already loaded from pickle."""
        if self.categories:
            logging.info("Categories already loaded from pickle, skipping JSON load")
            return
        json_file = os.path.join(self.persistence.data_dir, json_file)
        try:
            data = self.persistence.load_json(json_file)
            json_categories = []
            for c in data.get('categories', []):
                category = Category(c['name'], count=0, weight=c['weight'])
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
        if data_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(project_root, "data")
        self.persistence: PersistenceManager = PersistenceManager(data_dir, pickle_file, params_file,
                                                                 categories_file, states_file)
        self.app_params: AppParams = self.persistence.load_app_params()
        self.prayer_manager: PrayerManager = PrayerManager(self.persistence)
        self.category_manager: CategoryManager = CategoryManager(self.persistence, self.prayer_manager)
        self.session: Optional[PrayerSession] = None
        self.panel_manager: Optional[PanelManager] = None
        self.state_data: List[Dict] = []

        if os.path.exists(self.persistence.pickle_file):
            data = self.persistence.load_pickle()
            self.prayer_manager.prayers = data.get('Prayer_instances', [])
            self.category_manager.categories = data.get('Category_instances', [])
            self.state_data = data.get('State_instances', [])
            sessions = data.get('Session_instances', [])
            self.session = sessions[-1] if sessions else PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)
            for prayer in self.prayer_manager.prayers:
                if not hasattr(prayer, '_category'):
                    logging.error(f"Invalid Prayer object missing _category: {prayer}")
                    raise DatabaseError("Loaded Prayer object missing _category attribute")
            for category in self.category_manager.categories:
                if not hasattr(category, 'category'):
                    logging.error(f"Invalid Category object missing category: {category}")
                    raise DatabaseError("Loaded Category object missing category attribute")
            logging.info(f"Loaded {len(self.prayer_manager.prayers)} Prayer instances, {len(self.category_manager.categories)} Category instances, {len(self.state_data)} State instances")
        else:
            self.session = PrayerSession(last_prayer_date=None, prayer_streak=0, last_panel_set=None)
            self.prayer_manager.load_prayers(prayers_file)
            self.category_manager.load_categories(categories_file)
            self.state_data = self.persistence.load_states()
        self.panel_manager = PanelManager(self.persistence, self)
        self.panel_manager.load_panels(panels_file)
        logging.info(f"After initialization last_panel_set: {self.session.last_panel_set}")
        if not self.validate():
            raise DatabaseError("Database initialization failed")

    def _load_from_pickle(self) -> None:
        """Deprecated: Use PersistenceManager.load_pickle directly."""
        pass

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
        self.session.last_prayer_date = date.today().strftime("%d-%b-%Y")
        self.session.prayer_streak = self.session.prayer_streak + 1 if self.session.prayer_streak else 1
        logging.info(f"Saving last_panel_set: {self.session.last_panel_set}")
        logging.info(f"Saving {len(self.state_data)} State instances")
        objects_to_pickle = {
            'Prayer_instances': self.prayer_manager.prayers,
            'Category_instances': self.category_manager.categories,
            'Session_instances': [self.session],
            'State_instances': self.state_data
        }
        self.persistence.save_pickle(objects_to_pickle)

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