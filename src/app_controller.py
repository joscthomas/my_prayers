# app_controller.py
# Coordinates between Model (AppDatabase, StateMachine) and View (AppDisplay).

from datetime import datetime, timedelta
import random
from typing import List, Optional
import logging

from mpo_model import Prayer, Category, Panel, AppParams, PrayerSession, State, StateMachine, ModelError
from db_manager import AppDatabase
from ui_manager import AppDisplay

class AppError(Exception):
    """Custom exception for application errors."""
    pass

class PrayerSelector:
    """Handles selection and filtering of prayers for display."""

    def __init__(self, db_manager: AppDatabase):
        self.db_manager = db_manager

    def select_past_prayers(self, days_back: int = 7, max_selections: int = 20) -> List[Prayer]:
        """Select a list of past prayers based on recent activity and categories."""
        current_date = datetime.now()
        start_date = current_date - timedelta(days=days_back)
        recent_prayers = [
            prayer for prayer in self.db_manager.prayer_manager.past_prayers
            if datetime.strptime(prayer.create_date, '%d-%b-%Y') >= start_date
        ]

        # Combine recent prayers and category-based prayer lists
        prayer_lists = [recent_prayers] + [cat.category_prayer_list for cat in
                                           self.db_manager.category_manager.weighted_categories]
        weights = [0.5] + [cat.category_weight for cat in self.db_manager.category_manager.weighted_categories]
        selected_prayers = set()

        for _ in range(max_selections):
            available_lists = [lst for lst in prayer_lists if lst]
            if not available_lists:
                break
            selected_list = random.choices(available_lists, weights[:len(available_lists)], k=1)[0]
            if selected_list:
                prayer = random.choice(selected_list)
                selected_prayers.add(prayer)
                selected_list.remove(prayer)

        return list(selected_prayers)

class SessionManager:
    """Manages prayer session data, such as streaks and counts."""

    def __init__(self, app_params: AppParams):
        self.app_params = app_params
        self.current_session = PrayerSession()
        self.update_streak()

    def update_streak(self):
        """Update the prayer streak based on the last prayer date."""
        current_date = datetime.now()
        try:
            last_prayer_date = datetime.strptime(self.app_params.last_prayer_date, '%d-%b-%Y')
            yesterday = current_date - timedelta(days=1)
            if yesterday.date() == last_prayer_date.date():
                self.app_params.prayer_streak += 1
            else:
                self.app_params.prayer_streak = 1
        except ValueError:
            self.app_params.prayer_streak = 1
        self.app_params.last_prayer_date = current_date.strftime('%d-%b-%Y')

class AppController:
    """Coordinates interactions between UI, database, and other components."""

    def __init__(self, states_file: str = "states.json"):
        self.db_manager = AppDatabase(states_file=states_file)
        self.ui_manager = AppDisplay()
        self.state_machine = self._initialize_state_machine()
        self.prayer_selector = PrayerSelector(self.db_manager)
        self.session_manager = SessionManager(self.db_manager.app_params)

    def _initialize_state_machine(self) -> StateMachine:
        """Initialize the state machine with data from AppDatabase."""
        try:
            state_data = self.db_manager.persistence.load_states()
            return StateMachine(state_data)
        except Exception as e:
            logging.error(f"Failed to initialize state machine: {e}")
            raise AppError(f"Failed to initialize state machine: {e}")

    def run(self):
        """Main application loop."""
        try:
            while self.state_machine.current_state and self.state_machine.current_state.name != "done":
                state = self.state_machine.current_state
                if state.auto_trigger == True:
                    # Auto-trigger states don't display a panel; execute action immediately
                    action = self.handle_state_action(state)
                    self.state_machine.transition(action)
                else:
                    # Display panel and handle user-driven action
                    panel = next((p for p in self.db_manager.panel_manager.panels if p.panel_header == state.name), None)
                    if not panel:
                        raise AppError(f"No panel found for state {state.name}")
                    self.ui_manager.display_panel(panel)
                    action = self.handle_state_action(state)
                    self.state_machine.transition(action)
        except (AppError, ModelError) as e:
            logging.error(f"Application error: {e}")
            self.quit()
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            self.quit()

    def handle_state_action(self, state: State) -> str:
        """Handle the action associated with the current state."""
        try:
            if state.action_event == 'get_continue':
                response = self.ui_manager.get_response('enter to continue ')
                if response == 'import':
                    self.handle_import()
                elif response == 'export':
                    self.db_manager.export()
                return 'get_continue'
            elif state.action_event == 'get_new_prayers':
                self.get_new_prayers()
                return 'get_new_prayers'
            elif state.action_event == 'get_past_prayers':
                self.get_past_prayers()
                return 'get_past_prayers'
            elif state.action_event == 'quit_app':
                self.quit()
                return 'quit_app'
            raise AppError(f"Unknown action event: {state.action_event}")
        except Exception as e:
            raise AppError(f"Error handling state {state.name}: {e}")

    def get_new_prayers(self):
        """Collect new prayers from the UI and save them to the database."""
        another_prayer = True
        while another_prayer:
            prayer, another_prayer = self.ui_manager.ui_get_new_prayer()
            if another_prayer and prayer is not None:
                try:
                    self.db_manager.create_prayer(prayer)
                    self.session_manager.current_session.new_prayer_added_count += 1
                except Exception as e:
                    logging.error(f"Failed to create prayer: {e}")
                    raise AppError(f"Error saving prayer: {e}")
            elif prayer is None and another_prayer:
                logging.warning("Received None prayer from ui_get_new_prayer")
                another_prayer = False

    def get_past_prayers(self):
        """Display past prayers selected by the PrayerSelector."""
        prayers = self.prayer_selector.select_past_prayers()
        display_num = self.db_manager.app_params.past_prayer_display_count
        for i in range(0, len(prayers), display_num):
            for prayer in prayers[i:i + display_num]:
                self.ui_manager.display_prayer(prayer)
                prayer.display_count += 1
                self.session_manager.current_session.past_prayer_prayed_count += 1
                response = self.ui_manager.get_response('"answered" or enter to continue ')
                if response == 'a':
                    answer, answer_date = self.ui_manager.get_answer(prayer)
                    prayer.answer = answer
                    prayer.answer_date = answer_date
                    self.session_manager.current_session.answered_prayer_count += 1
            if i + display_num < len(prayers):
                response = self.ui_manager.get_response('enter "more" or "done" ')
                if response.lower() in ('d', 'done'):
                    break

    def handle_import(self):
        """Placeholder for import logic."""
        # TODO: Implement import logic
        pass

    def quit(self):
        """Clean up and exit the application."""
        self.db_manager.close()
        self.ui_manager.close_ui()
        quit(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app = AppController()
    app.run()