# db_manager.py
# Handles loading of data files (JSON, CSV, etc.) for the Model.

import pandas as pd
import pickle
import json
import os
import random
from datetime import datetime
from typing import List, Optional, Dict
import logging

from mpo_model import Prayer, Category, Panel, PanelPgraph, AppParams, PrayerSession

class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass

class PersistenceManager:
    """Handles file I/O operations for persistence (pickle, JSON, CSV)."""

    def __init__(self, pickle_file: str = "objects.pkl", params_file: str = "params.json",
                 categories_file: str = "categories.json", states_file: str = "states.json"):
        self.pickle_file = pickle_file
        self.params_file = params_file
        self.categories_file = categories_file
        self.states_file = states_file

    def load_pickle(self) -> dict:
        """Load objects from the pickle file."""
        try:
            if not os.path.exists(self.pickle_file):
                return {}
            with open(self.pickle_file, "rb") as file:
                return pickle.load(file)
        except (pickle.UnpicklingError, EOFError) as e:
            logging.error(f"Failed to unpickle {self.pickle_file}: {e}")
            raise DatabaseError(f"Failed to load pickle file: {e}")

    def save_pickle(self, objects: dict):
        """Save objects to the pickle file."""
        try:
            with open(self.pickle_file, "wb") as file:
                pickle.dump(objects, file)
        except Exception as e:
            logging.error(f"Failed to save pickle file {self.pickle_file}: {e}")
            raise DatabaseError(f"Failed to save pickle file: {e}")

    def load_json(self, file_path: str) -> dict:
        """Load data from a JSON file."""
        try:
            if not os.path.exists(file_path):
                raise DatabaseError(f"JSON file {file_path} not found")
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON file {file_path}: {e}")
            raise DatabaseError(f"Failed to parse JSON file: {e}")

    def save_json(self, file_path: str, data: dict):
        """Save data to a JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            logging.error(f"Failed to save JSON file {file_path}: {e}")
            raise DatabaseError(f"Failed to save JSON file: {e}")

    def load_csv(self, file_path: str) -> pd.DataFrame:
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

    def __init__(self, persistence: PersistenceManager, app_params: AppParams):
        self.persistence = persistence
        self.app_params = app_params
        self.panels: List[Panel] = []

    def load_panels(self, csv_file: str = "panels.csv"):
        """Load panels from CSV and instantiate Panel objects."""
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
                    # Create Panel with accumulated pgraph_list
                    current_panel = Panel(last_panel_seq, current_panel.panel_header, panel_pgraph_list)
                    self.panels.append(current_panel)
                    panel_pgraph_list = []
                # Initialize new Panel with empty pgraph_list for now
                current_panel = Panel(row.panel_seq, row.header, [])
            # Convert NaN verse to None
            verse = None if pd.isna(row.verse) else row.verse
            panel_pgraph = PanelPgraph(row.pgraph_seq, verse, row.text)
            panel_pgraph_list.append(panel_pgraph)
            last_panel_seq = row.panel_seq
        if current_panel:
            # Create final Panel with its pgraph_list
            current_panel = Panel(last_panel_seq, current_panel.panel_header, panel_pgraph_list)
            self.panels.append(current_panel)
        logging.info(f"Loaded {len(self.panels)} panels from {csv_file}")

    def _get_panel_set_id(self, df: pd.DataFrame) -> int:
        """Get the next panel set ID for the prayer session."""
        last_panel_set = int(self.app_params.last_panel_set or 1)
        try:
            next_panel_set_row = df[df.panel_set > last_panel_set].iloc[0]
        except IndexError:
            next_panel_set_row = df[df.panel_set > 1].iloc[0]
        panel_set_id = next_panel_set_row.panel_set
        self.app_params.last_panel_set = str(panel_set_id)
        return panel_set_id

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
        self.persistence = persistence
        self.prayers: List[Prayer] = []
        self.past_prayers: List[Prayer] = []
        self.unique_selected_prayers: List[Prayer] = []

    def load_prayers(self, csv_file: str = "prayers.csv"):
        """Load prayers from CSV and instantiate Prayer objects."""
        df = self.persistence.load_csv(csv_file)
        for row in df.itertuples():
            prayer = Prayer(
                prayer=row.prayer,
                create_date=row.create_date,
                answer_date=row.answer_date,
                category=row.category,
                answer=row.answer,
                display_count=0
            )
            self.prayers.append(prayer)
            if pd.isna(row.answer_date):
                self.past_prayers.append(prayer)

    def create_prayer(self, prayer: Prayer):
        """Add a new prayer to the in-memory database."""
        if not isinstance(prayer, Prayer):
            raise DatabaseError(f"Invalid prayer object: {prayer}")
        self.prayers.append(prayer)
        if pd.isna(prayer.answer_date):
            self.past_prayers.append(prayer)
        logging.info(f"Created prayer: {prayer.prayer}")

    def validate(self) -> bool:
        """Validate loaded prayers."""
        if not self.prayers:
            logging.error("No prayers loaded")
            return False
        return True

class CategoryManager:
    """Manages loading, weighting, and validation of Category objects."""

    def __init__(self, persistence: PersistenceManager, prayer_manager: PrayerManager):
        self.persistence = persistence
        self.prayer_manager = prayer_manager
        self.categories: List[Category] = []
        self.weighted_categories: List[Category] = []

    def load_categories(self, json_file: str = "categories.json"):
        """Load categories from JSON and instantiate Category objects."""
        try:
            data = self.persistence.load_json(json_file)
            json_categories = []
            for c in data.get('categories', []):
                category = Category(c['name'], c['display_count'], c['weight'])
                self.categories.append(category)
                json_categories.append(c['name'])

            prayer_categories = set(prayer.category for prayer in self.prayer_manager.past_prayers)
            unique_categories = [c for c in prayer_categories if c not in json_categories]
            for c in unique_categories:
                self.categories.append(Category(category=c, count=0, weight=1))

            for category in self.categories:
                category.category_prayer_list = [
                    prayer for prayer in self.prayer_manager.past_prayers
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
        if not self.prayer_manager.past_prayers:
            logging.error("No past prayers loaded")
            return False
        if not os.path.exists(self.persistence.categories_file):
            logging.error("No categories.json file")
            return False
        return True

class AppDatabase:
    """Coordinates database operations for the My Prayers application."""

    def __init__(self, pickle_file: str = "objects.pkl", params_file: str = "params.json",
                 categories_file: str = "categories.json", panels_file: str = "panels.csv",
                 prayers_file: str = "prayers.csv", states_file: str = "states.json"):
        self.persistence = PersistenceManager(pickle_file, params_file, categories_file, states_file)
        self.app_params = self._load_params()
        self.prayer_manager = PrayerManager(self.persistence)
        self.panel_manager = PanelManager(self.persistence, self.app_params)
        self.category_manager = CategoryManager(self.persistence, self.prayer_manager)
        self.session = PrayerSession()

        if os.path.exists(pickle_file):
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

    def _load_from_pickle(self):
        """Load objects from pickle file."""
        data = self.persistence.load_pickle()
        if not data:
            return
        self.prayer_manager.prayers = data.get('Prayer_instances', [])
        self.prayer_manager.past_prayers = data.get('Prayer_past_instances', [])
        self.prayer_manager.unique_selected_prayers = data.get('Prayer_unique_selected_prayers', [])
        self.panel_manager.panels = data.get('Panel_instances', [])
        self.category_manager.categories = data.get('Category_instances', [])
        sessions = data.get('Session_instances', [])
        if sessions:
            self.session = sessions[-1]

    def create_prayer(self, prayer: Prayer):
        """Add a new prayer to the database."""
        self.prayer_manager.create_prayer(prayer)
        self.session.new_prayer_added_count += 1

    def export(self):
        """Export prayers and panels to CSV (placeholder)."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        logging.info(f"Exporting database with timestamp {timestamp}")

    def close(self):
        """Persist all data to files."""
        if not self._validate_session():
            raise DatabaseError("Session validation failed at close")

        objects_to_pickle = {
            'Prayer_instances': self.prayer_manager.prayers,
            'Prayer_past_instances': self.prayer_manager.past_prayers,
            'Prayer_unique_selected_prayers': self.prayer_manager.unique_selected_prayers,
            'Category_instances': self.category_manager.categories,
            'Panel_instances': self.panel_manager.panels,
            'Session_instances': [self.session]
        }
        self.persistence.save_pickle(objects_to_pickle)

        categories_data = {
            "categories": [
                {
                    "name": category.category,
                    "display_count": category.category_display_count,
                    "weight": category.category_weight
                }
                for category in self.category_manager.categories
            ]
        }
        self.persistence.save_json(self.persistence.categories_file, categories_data)

        params_data = {
            'id': self.app_params._id,
            'id_desc': self.app_params._id_desc,
            'app': self.app_params._app,
            'app_desc': self.app_params._app_desc,
            'last_panel_set': self.app_params._last_panel_set,
            'last_panel_set_desc': self.app_params._last_panel_set_desc,
            'install_path': self.app_params._install_path,
            'install_path_desc': self.app_params._install_path_desc,
            'past_prayer_display_count': self.app_params._past_prayer_display_count,
            'past_prayer_display_count_desc': self.app_params._past_prayer_display_count_desc,
            'prayer_streak': self.app_params._prayer_streak,
            'prayer_streak_desc': self.app_params._prayer_streak_desc,
            'last_prayer_date': self.app_params._last_prayer_date,
            'last_prayer_date_desc': self.app_params._last_prayer_date_desc
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