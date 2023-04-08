"""
My Prayers User Interface Manager (View of the MVC model)

These objects are specific to the user interface technology the app uses.

This version uses the print() statement for the user interface
"""

from mpo_model import Panel, PanelPgraph, Prayer, NewPrayers
import textwrap


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
        if panel.panel_header == panel.panel_header:  # true if not NaN (null)
            print('\n')
            print(panel.panel_header, '\n')
            header = panel.panel_header
        # iterate thru PanelPgraph objects associated with the Panel object
        for x in panel.pgraph_list:
            print(textwrap.fill(x.text, 80))
            if x.verse == x.verse:  # false if NaN (null)
                print(x.verse, '\n')
            else:
                print('\n')
        return header

    def get_continue(self):
        """
        Get user input and go to the next step.
        """
        response = input('hit return to continue')
        if response == 'import' or 'export':
            self.command = response


    def ui_get_new_prayer(self):
        new_prayer: object = None
        another_prayer: bool = True
        prayer = input('Enter prayer request (or return if done)\n').strip()
        if len(prayer) > 0:
            category = input('Category?\n').strip()
            # save the new prayer
            new_prayer = Prayer(prayer, category)
        else:
            another_prayer = False
        return new_prayer, another_prayer

