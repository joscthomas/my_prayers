# app_controller.py
# Coordinates between Model (db_manager) and View (ui_manager).

import logging
from datetime import datetime, date
import random
from typing import List, Optional
from datetime import timedelta
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
        self.displayed_prayers: set = set()  # Track prayers displayed in this session

    def reset_session(self):
        """Reset displayed prayers for a new session."""
        self.displayed_prayers.clear()

    def select_past_prayers(self, max_selections: int, current_weight: int) -> List[Prayer]:
        """Select unanswered prayers from previous sessions, prioritizing lowest display count with random selection."""
        today = date.today().strftime("%d-%b-%Y")
        # Get unanswered prayers from previous sessions
        eligible_prayers = [
            prayer for prayer in self.db_manager.prayer_manager.get_unanswered_prayers()
            if prayer.create_date != today and prayer.prayer not in self.displayed_prayers
        ]
        if not eligible_prayers:
            logging.warning("No eligible past unanswered prayers found")
            return []

        # Group prayers by category weight
        weight_groups = {}
        for prayer in eligible_prayers:
            category = next(
                (cat for cat in self.db_manager.category_manager.categories if cat.category == prayer.category), None)
            weight = category.category_weight if category else 1
            weight_groups.setdefault(weight, []).append(prayer)

        # Sort each weight group by display_count and group by display_count
        selected_prayers = []
        remaining_selections = max_selections
        weight = current_weight

        while remaining_selections > 0 and weight >= 1:
            if weight in weight_groups and weight_groups[weight]:
                # Sort prayers by display_count (ascending)
                weight_groups[weight].sort(key=lambda p: p.display_count)
                # Group prayers by display_count
                display_count_groups = {}
                for prayer in weight_groups[weight]:
                    display_count_groups.setdefault(prayer.display_count, []).append(prayer)

                # Select from the lowest display_count group
                if display_count_groups:
                    lowest_display_count = min(display_count_groups.keys())
                    available_prayers = display_count_groups[lowest_display_count]
                    num_to_select = min(remaining_selections, len(available_prayers))
                    # Randomly select from prayers with the lowest display_count
                    prayers = random.sample(available_prayers, num_to_select)
                    selected_prayers.extend(prayers)
                    # Update displayed prayers and remove selected prayers from weight group
                    for prayer in prayers:
                        self.displayed_prayers.add(prayer.prayer)
                        weight_groups[weight].remove(prayer)
                    remaining_selections -= num_to_select
            weight -= 1  # Move to the next lower weight group

        return selected_prayers[:max_selections]

class SessionManager:
    """Manages prayer session data, such as streaks and counts."""

    def __init__(self, session: PrayerSession):
        self.session = session
        self.update_streak()

    def update_streak(self):
        """Update the prayer streak based on the last prayer date."""
        current_date = datetime.now()
        try:
            last_prayer_date = datetime.strptime(self.session.last_prayer_date, '%d-%b-%Y')
            yesterday = current_date - timedelta(days=1)
            if yesterday.date() == last_prayer_date.date():
                self.session.prayer_streak += 1
            else:
                self.session.prayer_streak = 1
        except (ValueError, TypeError):
            self.session.prayer_streak = 1
        self.session.last_prayer_date = current_date.strftime('%d-%b-%Y')

class AppController:
    """Coordinates interactions between UI, database, and other components."""

    def __init__(self, states_file: str = "states.json"):
        self.db_manager = AppDatabase(states_file=states_file)
        self.ui_manager = AppDisplay()
        self.state_machine = self._initialize_state_machine()
        self.prayer_selector = PrayerSelector(self.db_manager)
        self.session_manager = SessionManager(self.db_manager.session)

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
            self.prayer_selector.reset_session()  # Clear displayed prayers at start
            while self.state_machine.current_state and self.state_machine.current_state.name != "done":
                state = self.state_machine.current_state
                if state.auto_trigger:
                    action = self.handle_state_action(state)
                    self.state_machine.transition(action)
                else:
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
                response = self.ui_manager.get_response('Press Enter to continue: ')
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
                    self.session_manager.session.new_prayer_added_count += 1
                except Exception as e:
                    logging.error(f"Failed to create prayer: {e}")
                    raise AppError(f"Error saving prayer: {e}")
            elif prayer is None and another_prayer:
                logging.warning("Received None prayer from ui_get_new_prayer")
                another_prayer = False

    def get_past_prayers(self):
        """Display past prayers one at a time and allow marking as answered."""
        display_num = self.db_manager.app_params.past_prayer_display_count
        current_weight = 10  # Start with the highest weight
        continue_displaying = True

        while continue_displaying:
            prayers = self.prayer_selector.select_past_prayers(max_selections=display_num, current_weight=current_weight)
            if not prayers:
                self.ui_manager.display_panel(
                    Panel(0, "No Past Prayers", [PanelPgraph(0, None, "No unanswered past prayers available.")])
                )
                break

            for prayer in prayers:
                self.ui_manager.display_prayer(prayer)
                prayer.display_count += 1
                self.session_manager.session.past_prayer_prayed_count += 1
                response = self.ui_manager.get_response(
                    'How was this prayer answered? (Enter answer or press Enter to skip): '
                )
                if response.strip():  # Non-empty response indicates an answer
                    prayer.answer = response
                    prayer.answer_date = date.today().strftime("%d-%b-%Y")
                    self.session_manager.session.answered_prayer_count += 1
                    # Remove from answered_prayers since it's now answered
                    if prayer in self.db_manager.prayer_manager.answered_prayers:
                        self.db_manager.prayer_manager.answered_prayers.remove(prayer)

            if len(prayers) == display_num:
                response = self.ui_manager.get_response(
                    f'Display another set of {display_num} prayers? (y/n): '
                )
                continue_displaying = response.lower() in ('y', 'yes')
                current_weight = (current_weight - 1) if current_weight > 1 else 10  # Cycle to next weight
            else:
                continue_displaying = False

        return 'get_past_prayers'

    def handle_import(self):
        """Placeholder for import logic."""
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