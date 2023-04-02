"""
Class model for the My Prayer objects.

This model is the interface between:
    1. the controller and the user interface manager
    2. the controller and the database manager
"""

from datetime import date


class Prayer:

    def __init__(self, prayer, category):
        self.prayer = prayer
        today = date.today()
        today = today.strftime("%d-%b-%Y")
        self.create_date = today
        self.answer_date = None
        self.category = category
        self.up_vote = None
    # columns: prayer,create_date,answer_date,category,up_vote


    def save_new_prayers(self, prayer_list):
        #
        pass

    def get_prayer(self):
        return


    def update_prayers(self, prayers):
        pass

class NewPrayers:
    new_prayer_list = []

    def __init__(self, prayer_list):
        self.new_prayer_list = prayer_list

class PrayerList:
    # collect a set of prayers for presentation

    def __init__(self, prayers):
        # a list of Prayer objects
        print(f'type:{type(prayers)}')
        self.prayer_list = prayers


# these objects are the blueprint for text to present
#   to the user for a prayer session

class PanelSet:
    """
    A list of panels to display for a PrayerSession; a panel is one screen.

    panel_list: a list of Panel objects
    """

    def __init__(self, panel_list):
        self.panel_list = panel_list


class Panel:
    """
    Data for display on the user interface. The parent of PanelPgraph.

    A Panel is the presentation of one screen with its composition
       of paragraphs

    panel_seq: sequence number of the Panel in the session display
    pgraph_list: a list of paragraph objects (PanelPgraph)
    """

    def __init__(self, panel_seq, panel_header, pgraph_list):
        # a panel represents each display screen for a prayer session
        # a panel consists of multiple paragraphs
        self.panel_seq = panel_seq
        self.panel_header = panel_header
        self.pgraph_list = pgraph_list


class PanelPgraph:
    """
    A paragraph of text for a Panel to display.

    panel: sequence number of the paragraph within the Panel
    header: the heading (short text) for the panel; indicates the PanelType
    text: a text line to display (long text)
    verse: the Bible book chapter:verse reference (optiona)
    """

    def __init__(self, pgraph_seq, verse, text):
        self.pgraph_seq = pgraph_seq
        self.verse = verse
        self.text = text

class StateTransitionTable:
    """
    Parent of StateTransitionTableRow.

    row_list: a list of StateTransitionTableRow objects
    """

    def __init__(self, row_list):
        self.row_list = row_list


class StateTransitionTableRow:
    """
    current_state: the current state of the ui
        (PanelPgraph header displayed, or module completed)
    action_module: the module to call to get user input for the current
       state (default: display_panel; otherwise special function module)
    to_state_module: the module to call to process user input
       and move to the next state
    to_state_panel: the header panel to pass to display_panel
    """

    def __init__(self, from_state, action_event, to_state):
        self.from_state = from_state
        self.action_event = action_event
        self.to_state = to_state
        # self.to_state_panel = to_state_panel
