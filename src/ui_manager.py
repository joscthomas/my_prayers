# ui_manager.py

import logging
from typing import Tuple, Optional
from datetime import date
import textwrap

from mpo_model import Panel, PanelPgraph, Prayer, AppParams


class UIError(Exception):
    """Custom exception for UI-related errors."""
    pass


class AppDisplay:
    """Manages the user interface for the My Prayers application (View in MVC)."""

    def __init__(self, max_line_width: int = 80):
        """Initialize the UI with configuration."""
        self.max_line_width: int = max_line_width
        self.last_panel: Optional[Panel] = None
        logging.info("AppDisplay initialized")

    def close_ui(self) -> None:
        """Clean up and close the UI."""
        logging.info("Closing UI")
        # Placeholder for future cleanup (e.g., closing a GUI window)
        pass

    def display_panel(self, panel: Panel) -> str:
        """Display a Panel and its PanelPgraph objects."""
        if not isinstance(panel, Panel):
            logging.error(f"Invalid panel object: {panel}")
            raise UIError("Panel object is invalid")
        if not panel.panel_header:
            logging.warning(f"Panel header is empty for panel {panel.panel_seq}")

        # Display header
        header = panel.panel_header or "Untitled Panel"
        if header != "prayers_done":
            print(f"\n{header}\n")

        # Display paragraphs
        for pgraph in panel.pgraph_list:
            if not isinstance(pgraph, PanelPgraph):
                logging.error(f"Invalid PanelPgraph object: {pgraph}")
                raise UIError("Invalid PanelPgraph in panel")
            if not pgraph.text:
                logging.warning(f"Empty text in PanelPgraph {pgraph.pgraph_seq}")
                continue
            print(textwrap.fill(pgraph.text, self.max_line_width))
            if pgraph.verse is not None:
                print(f"\n{pgraph.verse}\n")
            else:
                print("\n")

        self.last_panel = panel
        return header

    @staticmethod
    def get_response(prompt: str) -> str:
        """Get user input with the given prompt."""
        try:
            response = input(prompt).strip()
            logging.debug(f"User input: {response}")
            return response
        except KeyboardInterrupt:
            logging.info("User interrupted input")
            raise UIError("Input interrupted by user")

    @staticmethod
    def ui_get_new_prayer() -> Tuple[Optional[Prayer], bool]:
        """Collect a new prayer from the user."""
        try:
            prayer_text = input("Enter prayer request (or return if done)\n").strip()
            if not prayer_text:
                logging.debug("No prayer entered, ending prayer input")
                return None, False

            category = input("Category?\n").strip()
            if not category:
                logging.warning("Empty category provided, using default 'General'")
                category = "General"

            today = date.today().strftime("%d-%b-%Y")
            prayer = Prayer(
                prayer=prayer_text,
                create_date=today,
                answer_date=None,
                category=category,
                answer=None,
                display_count=0
            )
            logging.info(f"New prayer created: {prayer_text} (Category: {category})")
            return prayer, True
        except Exception as e:
            logging.error(f"Error collecting new prayer: {e}")
            raise UIError(f"Failed to create prayer: {e}")

    @staticmethod
    def get_answer(prayer: Prayer) -> Tuple[str, str]:
        """Collect an answer for a prayer and return the answer and date."""
        if not isinstance(prayer, Prayer):
            logging.error(f"Invalid prayer object: {prayer}")
            raise UIError("Invalid prayer object")

        try:
            answer = input("How did God answer your prayer?\n").strip()
            if not answer:
                logging.warning("Empty answer provided")
                raise UIError("Prayer answer cannot be empty")

            current_date = date.today().strftime("%d-%b-%Y")
            logging.info(f"Answer recorded for prayer '{prayer.prayer}': {answer}")
            return answer, current_date
        except KeyboardInterrupt:
            logging.info("User interrupted answer input")
            raise UIError("Answer input interrupted by user")

    def display_prayer(self, prayer: Prayer) -> None:
        """Display a prayer's text."""
        if not isinstance(prayer, Prayer):
            logging.error(f"Invalid prayer object: {prayer}")
            raise UIError("Invalid prayer object")
        if not prayer.prayer:
            logging.warning("Empty prayer text")
            return
        print(f"\n{textwrap.fill(prayer.prayer, self.max_line_width)}\n")
        logging.debug(f"Displayed prayer: {prayer.prayer} {prayer.create_date} {prayer.category}")
