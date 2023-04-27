"""
Class model for the My Prayer objects.

This model is the interface between:
    1. the controller and the user interface manager
    2. the controller and the database manager
"""


class Prayer:
    """
    a prayer
    """

    # a list of all the Prayer objects
    all_prayers = []
    # a list of all the past (unanswered) prayers, a subset of all_prayers
    all_past_prayers = []
    # a list of the past prayers in display sequence
    unique_selected_prayers = []

    def __init__(self, prayer, create_date, answer_date,
                 category, answer, display_count):
        self.prayer = prayer
        self.create_date = create_date
        self.answer_date = answer_date
        self.category = category
        self.answer = answer
        self.display_count = display_count
        Prayer.all_prayers.append(self)


class Category:
    """
    a category to classify prayers
    """

    # list of all Category objects
    all_categories = []
    # list of Category objects with some repeats
    weighted_categories = []

    def __init__(self, category, count, weight):
        self.category = category
        self.category_display_count = count
        self.category_weight = weight
        self.category_prayer_list = []
        Category.all_categories.append(self)


# these objects are the blueprint for presentation
#   to the user for a prayer session

class Panel:
    """
    Data for display on the user interface. The parent of PanelPgraph.

    A Panel is the presentation of one screen with its composition
       of paragraphs

    panel_seq: sequence number of the Panel in the session display
    pgraph_list: a list of paragraph objects (PanelPgraph)
    """

    # list of all Panel objects
    all_panels = []

    def __init__(self, panel_seq, panel_header, pgraph_list):
        # a panel represents each display screen for a prayer session
        # a panel consists of multiple paragraphs
        self.panel_seq = panel_seq
        self.panel_header = panel_header
        self.pgraph_list = pgraph_list
        Panel.all_panels.append(self)


class PanelPgraph:
    """
    A paragraph of text for a Panel to display.

    panel: sequence number of the paragraph within the Panel
    header: the heading (short text) for the panel; indicates the PanelType
    text: a text line to display (long text)
    verse: the Bible book chapter:verse reference (optiona)
    """
    all_panel_pgraphs = []

    def __init__(self, pgraph_seq, verse, text):
        self.pgraph_seq = pgraph_seq
        self.verse = verse
        self.text = text
        PanelPgraph.all_panel_pgraphs.append(self)


class StateTransitionTable:
    """
    current_state: the current state of the ui
        (PanelPgraph header displayed, or module completed)
    action_module: the module to call to get user input for the current
       state (default: display_panel; otherwise special function module)
    to_state_module: the module to call to process user input
       and move to the next state
    to_state_panel: the header panel to pass to display_panel
    """

    all_rows = []

    def __init__(self, from_state, action_event, to_state):
        self.from_state = from_state
        self.action_event = action_event
        self.to_state = to_state
        StateTransitionTable.all_rows.append(self)


class AppParms:
    """
    global application parameters from parms.json
    """

    # the AppParms object
    app_parms = None

    def __init__(self, parms_dict):
        self.id = parms_dict[
            'id']
        self.id_desc = parms_dict[
            'id_desc']
        self.app = parms_dict[
            'app']
        self.app_desc = parms_dict[
            'app_desc']
        self.last_panel_set = parms_dict[
            'last_panel_set']
        self.last_panel_set_desc = parms_dict[
            'last_panel_set_desc']
        self.install_path = parms_dict[
            'install_path']
        self.install_path_desc = parms_dict[
            'install_path_desc']
        self.past_prayer_display_count = parms_dict[
            'past_prayer_display_count']
        self.past_prayer_display_count_desc = parms_dict[
            'past_prayer_display_count_desc']
        self.prayer_streak = parms_dict[
            'prayer_streak']
        self.prayer_streak_desc = parms_dict[
            'prayer_streak_desc']
        self.last_prayer_date = parms_dict[
            'last_prayer_date']
        self.last_prayer_date_desc = parms_dict[
            'last_prayer_date_desc']
        AppParms.app_parms = self
