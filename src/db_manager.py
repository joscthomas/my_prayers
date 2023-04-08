"""
My Prayers Database Manager (Model of the MVC model)

These objects are specific to the database technology the app uses.

This version uses pandas as the database.
"""

import pandas as pd
import json
import os
import datetime
from mpo_model import PanelSet, Panel, PanelPgraph, \
    StateTransitionTable, StateTransitionTableRow, AppParms


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
        # get the app parameters
        self.app_parms = get_app_parms()

    def import_database(self):
        """
        Read in a CSV file into a dataframe.
        """
        # create pandas dataframe from panel data CSV
        # columns: panel_set,panel_seq,pgraph_seq,header,verse,text
        self.df_all_panels = pd.read_csv('panels.csv')
        # create pandas dataframe from prayer data CSV
        # columns: prayer,create_date,answer_date,category,present_count
        self.df_all_prayers = pd.read_csv('prayers.csv')

    def export_database(self):
        """
        Create a CSV file from dataframe.
        """
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime("%Y%m%d%H%M%S")
        self.df_all_prayers.to_csv(f'prayers{timestamp}.csv')
        self.df_all_panels.to_csv(f'panels{timestamp}.csv')

    def close_database(self):
        """
        Close the database files
        """
        self.df_all_prayers.to_pickle('prayers.pkl')
        self.df_all_panels.to_pickle('panels.pkl')
        # save the JSON application parameter file
        dict = vars(self.app_parms)
        file = open('parms.json', 'w')
        json.dump(dict, file, indent=4)
        file.close()


def create_panel_objects_from_database(db):
    """
    A function to create:
    1. a PanelSet object (containing a list of child Panel objects)
    2. Panel objects (each containing a list of child PanelPgraph objects)
    3. PanelPgraph objects
    4. StateTransitionTableRow objects
    """

    panel_set_id = get_panel_set_id(db.df_all_panels, db.app_parms)
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
    # a Panel has many PanelPgraphs
    # the header for a Panel is in the first row
    for row in df_panels.itertuples():  # iterate through each Panel row
        assert len(row.text) > 0, \
            f'assert fail CreatePanelSet: a panel row has text = null'
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
            action_event = 'get_continue'
            # special conditions to manage gathering and retrieving prayers
            if save_panel_header == 'MY CONCERNS':  # panel for prayers
                action_event = 'get_new_prayers'
                to_state = 'prayers_done'
                # write the row
                state_transition_table_row = \
                    StateTransitionTableRow(save_panel_header,
                                            action_event,
                                            to_state)
                state_transition_table_row_list.append(state_transition_table_row)
                save_panel_header = 'prayers_done'
                action_event = 'get_old_prayers'
                to_state = "GOD'S WILL"
            # set to_state in prior StateTransitionTableRow
            # last_state_transition_table_row.to_state = save_header
            # write the state transition row for the last panel
            state_transition_table_row = \
                StateTransitionTableRow(save_panel_header,
                                        action_event,
                                        to_state)
            state_transition_table_row_list.append(state_transition_table_row)
            # last_state_transition_table_row = state_transition_table_row
            last_panel = row.panel_seq
        # create a PanelPgraph object
        panel_pgraph = PanelPgraph(row.pgraph_seq,
                                   row.verse, row.text)
        panel_pgraph_list.append(panel_pgraph)  # save PanelPgraph in list
        # save the Panel header
        if row.header == row.header:  # if not null (nan)
            save_panel_header = row.header  # save header for Panel
    # create last Panel object
    panel = Panel(last_panel, save_panel_header, panel_pgraph_list)
    panel_list.append(panel)
    # create last StateTransitionTableRow object
    if save_panel_header != 'CLOSING':
        assert False, f'expected last panel header of CLOSING'
    action_event = 'quit_app'
    to_state = 'done'
    state_transition_table_row = \
        StateTransitionTableRow(save_panel_header,
                                action_event,
                                to_state)
    state_transition_table_row_list.append(state_transition_table_row)  # create the PanelSet object
    panel_set = PanelSet(panel_list)
    # create the StateTransitionTable object
    state_transition_table = StateTransitionTable(state_transition_table_row_list)
    return panel_set, state_transition_table


def get_panel_set_id(df_all_panels, app_parms):
    """
    Access AppParms to get the next PanelSet for display.
    Rotate through the panel data for each prayer session.
    """
    # find the panel set id that is next (first one greater than last one)
    next_panel_set_row = df_all_panels[df_all_panels.panel_set
                                       > int(app_parms.last_panel_set)].iloc[0]
    panel_set_id = next_panel_set_row.panel_set
    # save the current session panel_set_id as the last_panel_set in AppParms
    app_parms.last_panel_set = str(panel_set_id)
    pass
    return panel_set_id


def get_app_parms():
    """
    Get the application parameters from the JSON file
    """
    # Open JSON file
    file = open('parms.json')
    # returns JSON object as a dictionary
    data = json.load(file)
    app_parms = AppParms(data['id'], data['app'], data['last_panel_set'])
    # Close file
    file.close()
    return app_parms


# class DbPrayer:
# columns: prayer,create_date,answer_date,category,present_count

# def __init__(self):
#     pass

def read_prayer_set(self, prayer_list):
    # algorithm to select a set of prayers from the database
    pass


def create_prayer(db, prayer):
    # write a prayer to the database
    i = len(db.df_all_prayers)
    present_count = 0
    answer = None
    db.df_all_prayers.loc[i] = \
        [prayer.prayer,
         prayer.create_date,
         prayer.answer_date,
         prayer.category,
         prayer.answer,
         present_count]
    x = True


def update_prayer(self):
    # update a prayer in the database
    pass


def delete_prayer(self):
    # delete a prayer in the database
    pass
