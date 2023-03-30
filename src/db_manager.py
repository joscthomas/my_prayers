"""
My Prayers Database Manager (Model of the MVC model)

These objects are specific to the database technology the app uses.

This version uses pandas as the database.
"""

import pandas as pd
from mpo_model import PanelSet, Panel, PanelPgraph, \
    ControlTable, ControlTableRow


class InitDatabase:
    """
    The app database.

    properties
    df_all_panels: a pandas dataframe containing all panel data
    df_all_prayers: a pandas dataframe containing all prayers
    """

    def __init__(self):  # initialize the database
        #
        # create pandas dataframe from panel data CSV
        self.df_all_panels = pd.read_csv('panels.csv')
        # self.df_all_panels = self.df_all_panels.set_index(['panel_set', 'panel', 'pgraph']).sort_index()
        # self.df_all_panels.sort_index(axis=1, inplace=True)
        # todo create pandas dataframe from prayer data CSV
        self.df_all_prayers = []


def create_panel_objects_from_database(db):
    """
    A function to create:
    1. a PanelSet object (containing a list of child Panel objects)
    2. Panel objects (each containing a list of child PanelPgraph objects)
    3. PanelPgraph objects
    4. ControlTable objects
    """

    panel_set_id = get_panel_set_id()
    # pattern: rslt_df = dataframe.loc[dataframe['Percentage'] > 80]
    # select all panels for the prayer session
    df_panels = db.df_all_panels.loc[db.df_all_panels['panel_set'] ==
                                     int(panel_set_id)]
    last_panel = 1
    panel_list = []
    panel_pgraph_list = []
    control_table_row_list = []
    for row in df_panels.itertuples():  # iterate thru each row
        assert len(row.text) > 0, \
            f'assert fail CreatePanelSet: a panel row has text = null'
        # create a PanelPgraph object
        panel_pgraph = PanelPgraph(row.pgraph_seq,
                                   row.header, row.verse, row.text)
        if last_panel != row.panel_seq:  # change of panel_seq
            # create a Panel object
            panel = Panel(last_panel, panel_pgraph_list)
            panel_list.append(panel)
            panel_pgraph_list = []
            # create a ControlTableRow
            current_state = panel_list[-1].pgraph_list[0].header
            # special conditions to manage gathering and retrieving prayers
            if current_state == 'MY CONCERNS':  # panel for prayers
                action_module = 'get_new_prayers'
                to_state_module = 'get_old_prayers'
                to_state_panel = 'prayers done'
            elif current_state == "GOD'S WILL":  # panel after prayers
                action_module = 'continue_prompt'
                to_state_module = 'display_panel'
                to_state_panel = "GOD'S WILL"
                current_state = 'prayers done'
            else:  # default values
                action_module = 'continue_prompt'
                to_state_module = 'display_panel'
                to_state_panel = row.header
            control_table_row = ControlTableRow(current_state,
                                                action_module,
                                                to_state_module,
                                                to_state_panel)
            control_table_row_list.append(control_table_row)
            last_panel = row.panel_seq
        panel_pgraph_list.append(panel_pgraph)  # save PanelPgraph in list
    # create last Panel object
    panel = Panel(last_panel, panel_pgraph_list)
    panel_list.append(panel)
    # create last ControlTableRow object
    current_state = panel_list[-1].pgraph_list[0].header
    action_module = 'continue_prompt'
    to_state_module = 'quit_app'
    to_state_panel = None
    control_table_row = ControlTableRow(current_state,
                                        action_module,
                                        to_state_module,
                                        to_state_panel)
    control_table_row_list.append(control_table_row)
    # create the PanelSet object
    panel_set = PanelSet(panel_list)
    # reate the ControlTable object
    control_table = ControlTable(control_table_row_list)
    return panel_set, control_table


def get_panel_set_id():
    """
    Access ParmsTable to get a PanelSet for display.
    Rotate through the panel data for each prayer session.
    """

    # todo get and manage last panel_set_id from parm file
    return "20221204"


class DbPrayer:

    def __init__(self):
        pass

    def get_prayers(self, prayer_list):
        # algorithm to select a set of prayers from the database
        pass

    def write_prayer(self):
        # write a prayer to the database
        pass

    def update_prayer(self):
        # update a prayer in the database
        pass

    def delete_prayer(self):
        # delete a prayer in the database
        pass
