"""
My Prayers User Interface Manager (View of the MVC model)

These objects are specific to the user interface technology the app uses.

This version uses the print() statement for the user interface
"""

from mpo_model import Panel, PanelPgraph, Prayer, AppParms
import textwrap
from datetime import date
import readchar


class Display:
    """
    The intermediary between the user and the data

    last_panel:
    """

    def __init__(self):
        self.command = None

    def display_panel(self, panel):
        """
        Display the PanelPgraph objects for a Panel.

        panel: a Panel object for displaying panels
        header: the header attribute of the PanelPgraph set
        """

        header = None
        if panel.panel_header is not None:  # true if not NaN (null)
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
            else:  # x.verse false if NaN (null)
                print(x.verse, '\n')
        return header

    def get_response(self, prompt):
        """
        Get user input and go to the next step.
        """

        print(prompt, end='')
        response = readchar.readchar()
        # response = input(prompt)[0]
        if response == 'i' or 'e':
            self.command = response
        return response

    def ui_get_new_prayer(self):
        new_prayer: object = None
        another_prayer: bool = True
        prayer = input('Enter prayer request (or return if done)\n').strip()
        if len(prayer) > 0:
            category = input('Category?\n').strip()
            # save the new prayer
            today = date.today()
            today = today.strftime("%d-%b-%Y")
            new_prayer = Prayer(prayer, create_date=today,
                                answer_date=None, category=category,
                                answer=None, display_count=0)
        else:
            another_prayer = False
        return new_prayer, another_prayer

    def display_prayer(self, obj):
        print('\n', textwrap.fill(obj.prayer, 80), '\n')
