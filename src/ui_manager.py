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
        self.last_panel = ''

    def display_panel(self, panel):
        """
        Display the PanelPgraph objects for a Panel.

        panel: a Panel object for displaying panels
        header: the header attribute of the PanelPgraph set
        """

        # iterate thru PanelPgraph objects associated with the Panel object
        for x in panel.pgraph_list:
            if x.header == x.header:  # true if not NaN (null)
                print(x.header, '\n')
                header = x.header
            print(textwrap.fill(x.text, 80))
            if x.verse == x.verse:  # false if NaN (null)
                print(x.verse, '\n')
            else:
                print('\n')
        return header

    def continue_prompt(self):
        """
        Get user input and go to the next step.
        """

        input('hit return to continue')

