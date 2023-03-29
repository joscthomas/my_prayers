# My Prayers Database Manager (Model of the MVC model)
#
# These objects are specific to the database technology the app uses
#
# this version uses pandas as the database

import pandas as pd
from mpo_model import PanelSet, Panel, PanelPgraph, \
    ControlTable, ControlTableRow

debug = True  # todo read this from parm file


class InitDatabase:
    #
    # the app database
    #
    # properties
    # df_all_panels: a pandas dataframe containing all panel data
    # df_all_prayers: a pandas dataframe containing all prayers
    #
    def __init__(self):  # initialize the database
        #
        # create pandas dataframe from panel data CSV
        self.df_all_panels = pd.read_csv('panels.csv')
        # self.df_all_panels = self.df_all_panels.set_index(['panel_set', 'panel', 'pgraph']).sort_index()
        # self.df_all_panels.sort_index(axis=1, inplace=True)
        if debug: print('Database __init__')
        if debug: print(self.df_all_panels.columns.tolist())
        if debug: print(f'df_all_panels: {self.df_all_panels}')
        # todo create pandas dataframe from prayer data CSV
        self.df_all_prayers = []


def create_panel_objects_from_database(db):
    #
    # a function to create:
    # 1. a PanelSet object (containing a list of child Panel objects)
    # 2. Panel objects (each containing a list of child PanelPgraph objects)
    # 3. PanelPgraph objects
    # 4. ControlTable objects
    #
    if debug: print('create_panel_set')
    panel_set_id = get_panel_set_id()
    if debug: print(f'panel_set_id: {panel_set_id}')
    # pattern: rslt_df = dataframe.loc[dataframe['Percentage'] > 80]
    if debug: print(f'db: {db.df_all_panels}')
    # select all panels for the prayer session
    df_panels = db.df_all_panels.loc[db.df_all_panels['panel_set'] ==
                                     int(panel_set_id)]
    if debug: print(f'df_panels: {df_panels}')
    if debug: print('iterating thru rows')
    last_panel = 1
    panel_list = []
    panel_pgraph_list = []
    control_table_row_list = []
    for row in df_panels.itertuples():  # iterate thru each row
        if debug: print(row.panel_set, row.panel_seq, row.pgraph_seq,
                        row.header, row.verse, row.text)
        assert len(row.text) > 0, \
            f'assert fail CreatePanelSet: a panel row has text = null'
        # create a PanelPgraph object
        panel_pgraph = PanelPgraph(row.pgraph_seq,
                                   row.header, row.verse, row.text)
        if debug: print(f'panel_pgraph: {panel_pgraph} {vars(panel_pgraph)}')
        if last_panel != row.panel_seq:  # change of panel_seq
            # create a Panel object
            panel = Panel(last_panel, panel_pgraph_list)
            if debug: print(f'Panel: {panel} {vars(panel)}')
            panel_list.append(panel)
            panel_pgraph_list = []
            # create a ControlTableRow
            current_state = panel_list[-1].pgraph_list[0].header
            if debug: print(f'last header: {current_state}')
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
            if debug: print(f'control_table_row: {control_table_row} '
                            f'{vars(control_table_row)}')
            last_panel = row.panel_seq
        panel_pgraph_list.append(panel_pgraph)  # save PanelPgraph in list
    # create last Panel object
    panel = Panel(last_panel, panel_pgraph_list)
    if debug: print(f'Panel: {panel} {vars(panel)}')
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
    if debug: print(f'control_table_row: {control_table_row} '
                    f'{vars(control_table_row)}')
    # create the PanelSet object
    panel_set = PanelSet(panel_list)
    if debug: print(f'PanelSet: {panel_set} {vars(panel_set)}')
    # reate the ControlTable object
    control_table = ControlTable(control_table_row_list)
    if debug: print(f'ControlTable: {control_table} {vars(control_table)}')
    return panel_set, control_table


def get_panel_set_id():
    # get the last panel displayed
    # [access the parms]
    # get the next panel to display
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
