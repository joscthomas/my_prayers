"""
My Prayers Database Manager (Model of the MVC model)

These objects are specific to the database technology the app uses.

This version uses pandas as the database.
"""

import pandas as pd
import os
import datetime
from mpo_model import PanelSet, Panel, PanelPgraph, \
    StateTransitionTable, StateTransitionTableRow


class AppDatabase:
    """
    The database for the application.

    properties
    df_all_panels: a pandas dataframe containing all panel data
    df_all_prayers: a pandas dataframe containing all prayers
    """

    # for storing and retrieving a pandas dataframe
    # https://stackoverflow.com/questions/17098654/how-to-reversibly-store-and-load-a-pandas-dataframe-to-from-disk

    def __init__(self):  # initialize the database
        #
        self.df_all_panels = []
        self.df_all_prayers = []
        # if no pickle files, load the dataframes from CSV
        if os.path.isfile('prayers.pkl') is False:
            self.import_database()
        else:
            # load dataframes from pickles
            self.df_all_prayers = pd.read_pickle('prayers.pkl')
            self.df_all_panels = pd.read_pickle('panels.pkl')
            pass

    def close_database(self):
        """

        """
        self.df_all_prayers = pd.to_pickle('prayers.pkl')
        self.df_all_panels = pd.to_pickle('panels.pkl')

    def import_database(self):
        """
        Read in a CSV file into a dataframe.
        """
        # create pandas dataframe from panel data CSV
        # columns: panel_set,panel_seq,pgraph_seq,header,verse,text
        self.df_all_panels = pd.read_csv('panels.csv')
        # create pandas datafram from prayer data CSV
        # columns: prayer,create_date,answer_date,category,up_vote
        self.df_all_prayers = pd.read_csv('prayers.csv')

    def export_database(self):
        """
        Create a CSV file from dataframe.
        """
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime("%Y%m%d%H%M%S")
        self.df_all_prayers.to_csv(f'prayers{timestamp}.csv')
        self.df_all_panels.to_csv(f'panels{timestamp}.csv')


def create_panel_objects_from_database(db):
    """
    A function to create:
    1. a PanelSet object (containing a list of child Panel objects)
    2. Panel objects (each containing a list of child PanelPgraph objects)
    3. PanelPgraph objects
    4. StateTransitionTableRow objects
    """

    panel_set_id = get_panel_set_id()
    # pattern: rslt_df = dataframe.loc[dataframe['Percentage'] > 80]
    # select all panels for the prayer session
    df_panels = db.df_all_panels.loc[db.df_all_panels['panel_set'] ==
                                     int(panel_set_id)]
    last_panel = 1
    panel_list = []
    save_panel_header = None
    panel_pgraph_list = []
    state_transition_table_row_list = []
    # a prayer session has one PanelSet
    # a PanelSet consists of many Panels (display screens)
    # a Panel (a screen) has many PanelPgraphs
    # the header for a panel is in the first row
    for row in df_panels.itertuples():  # iterate thru each row for Panel
        assert len(row.text) > 0, \
            f'assert fail CreatePanelSet: a panel row has text = null'
        # create a PanelPgraph object
        panel_pgraph = PanelPgraph(row.pgraph_seq,
                                   row.verse, row.text)
        panel_pgraph_list.append(panel_pgraph)  # save PanelPgraph in list
        # when panel_seq changes, write the Panel and StateTransitionRow
        #   for the prior Panel
        if last_panel != row.panel_seq:  # change of panel_seq
            # create a Panel object at the end of all its pgraphs
            panel = Panel(last_panel, save_panel_header, panel_pgraph_list)
            panel_list.append(panel)
            panel_pgraph_list = []
            # create a StateTransitionTableRow for the prior Panel
            # the default to_state for a Panel is header of next Panel
            to_state = row.header
            # other default
            action_event = 'continue_prompt'
            # special conditions to manage gathering and retrieving prayers
            if save_panel_header == 'MY CONCERNS':  # panel for prayers
                action_event = 'get_new_prayers'
                to_state = 'prayers done'
                # write the row
                state_transition_table_row = \
                    StateTransitionTableRow(save_panel_header,
                                            action_event,
                                            to_state)
                state_transition_table_row_list.append(state_transition_table_row)
                save_panel_header = 'prayers done'
                action_event = 'get_old_prayers'
                to_state = "GOD'S WILL"
            elif save_panel_header == 'CLOSE':
                action_event = 'quit_app'
                to_state = 'done'
            # set to_state in prior StateTransitionTableRow
            # last_state_transition_table_row.to_state = save_header
            # write the state transition row for the last panel
            state_transition_table_row = \
                StateTransitionTableRow(save_panel_header,
                                        action_event,
                                        to_state)
            state_transition_table_row_list.append(state_transition_table_row)
            last_state_transition_table_row = state_transition_table_row
            last_panel = row.panel_seq
        # save the Panel header
        if row.header == row.header:  # if not null (nan)
            save_panel_header = row.header  # save header for Panel
    # create last Panel object
    panel = Panel(last_panel, save_panel_header, panel_pgraph_list)
    panel_list.append(panel)
    # create last ControlTableRow object
    state_transition_table_row = \
        StateTransitionTableRow(save_panel_header,
                                action_event,
                                to_state)
    state_transition_table_row_list.append(state_transition_table_row)    # create the PanelSet object
    panel_set = PanelSet(panel_list)
    # create the StateTransitionTable object
    state_transition_table = StateTransitionTable(state_transition_table_row_list)
    return panel_set, state_transition_table


def get_panel_set_id():
    """
    Access ParmsTable to get a PanelSet for display.
    Rotate through the panel data for each prayer session.
    """

    # todo get and manage last panel_set_id from parm file
    return "20221204"


# class DbPrayer:
# columns: prayer,create_date,answer_date,category,up_vote

# def __init__(self):
#     pass

def read_prayer_set(self, prayer_list):
    # algorithm to select a set of prayers from the database
    pass


def create_prayer(db, prayer):
    # write a prayer to the database
    i = len(db.df_all_prayers)
    db.df_all_prayers.loc[i] = \
        [prayer.prayer,
         prayer.create_date,
         prayer.answer_date,
         prayer.category,
         None]
    x = True


def update_prayer(self):
    # update a prayer in the database
    pass


def delete_prayer(self):
    # delete a prayer in the database
    pass
