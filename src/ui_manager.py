"""
My Prayers User Interface Manager (View of the MVC model)

These objects are specific to the user interface technology the app uses.

This version uses the print() statement for the user interface
"""

from mpo_model import Panel, PanelPgraph, Prayer, AppParams
import textwrap
from datetime import date, datetime


class AppDisplay:
    """
    The intermediary between the user and the data

    last_panel:
    """

    def __init__(self):
        """
        Instantiate the UI display
        """
        pass

    def close_ui(self):
        """
        Close the UI
        """
        pass

    @staticmethod
    def display_panel(panel):
        """
        Display the PanelPgraph objects for a Panel.

        panel: a Panel object for displaying panels
        header: the header attribute of the PanelPgraph set
        """
        # display the header of the Panel
        header = None
        if panel.panel_header is not None:
            print('\n')
            print(panel.panel_header, '\n')
            header = panel.panel_header

        # iterate thru PanelPgraph objects associated with the Panel object
        pass
        for x in panel.pgraph_list:
            pass
            print(textwrap.fill(x.text, 80))
            if x.verse is not None:
                print('\n')
            else:
                print(x.verse, '\n')
        return header

    @staticmethod
    def get_response(prompt):
        """
        Get user input
        """
        response = input(prompt)
        return response

    @staticmethod
    def ui_get_new_prayer():
        new_prayer: object = None
        another_prayer: bool = True
        prayer = input('Enter prayer request (or return if done)\n').strip()
        if len(prayer) > 0:
            category = input('Category?\n').strip()
            # save the new prayer
            today = date.today()
            today = today.strftime("%d-%b-%Y")
            new_prayer = Prayer(prayer, create_date= today,
                                answer_date=None, category=category,
                                answer=None, display_count=0)
        else:
            another_prayer = False
        return new_prayer, another_prayer

    @staticmethod
    def get_answer(prayer):
        answer = input('how did God answer your prayer?')
        prayer.answer = answer
        # get the current date
        current_date = datetime.now()
        prayer.answer_date = current_date.strftime('%d-%b-%Y')
        pass

    @staticmethod
    def display_prayer(obj):
        print('\n', textwrap.fill(obj.prayer, 80), '\n')
