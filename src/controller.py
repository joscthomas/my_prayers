"""
My Prayers Controller (Controller of the MVC model)

These objects manage the relationship between the user interface
   controller and the database controller.

MVC spreadsheet http://bit.ly/3jHdljS
MVC message sequence diagram http://bit.ly/3xj8hFa

"""

from mpo_model import StateTransitionTable, StateTransitionTableRow
from db_manager import AppDatabase, create_panel_objects_from_database, \
    create_prayer
from ui_manager import Display


class App:
    """
    The main loop of the application.

    dbm: database manager object
    uim: user interface manager object
    panel_set: PanelSet object (only one for the app)
    control_table: ControlTable object (only one for the app)

    """

    def __init__(self):
        """
        Initialize the app, perform other one-time setup operations,
        and start the main loop of the app.
        """

        # initialize database manager object
        self.dbm = AppDatabase()
        # initialize user interface manager object
        self.uim = Display()
        # get panels data and state transition table from database
        self.panel_set: object = None  # PanelSet object
        self.state_transition_table: object = None
        self.panel_set, self.state_transition_table = \
            create_panel_objects_from_database(self.dbm)
        assert check_panel_set(self.panel_set), \
            'panel set failure'
        assert check_state_transition_table(self.state_transition_table), \
            'state transition table failure'
        # the main loop of the app
        self.main_loop()

    def main_loop(self):
        """
        The main loop of the application.

        Display the first panel then
            use the StateTransitionTable to drive what happens next
        """

        # loop to display each Panel
        for p in self.panel_set.panel_list:
            panel_header = self.uim.display_panel(p)
            # loop to find the StateTransitionTableRow
            # that matches the Panel header to find the event
            # and the module to call that causes transition to occur
            for s in self.state_transition_table.row_list:
                if s.from_state == panel_header:
                    if s.action_event == 'get_continue':
                        self.uim.get_continue()
                        # special commands from the continue prompt
                        if self.uim.command == 'import':
                            self.dbm.import_database()
                        elif self.uim.command == 'export':
                            self.dbm.export_database()
                    elif s.action_event == 'get_new_prayers':
                        self.get_new_prayers()
                    elif s.action_event == 'get_old_prayers':
                        self.get_old_prayers()
                    elif s.action_event == 'quit_app':
                        quit_app(self.uim, self.dbm)
                    else:
                        assert False, f'unexpected s.action_event ' \
                                      f'value: {s.action_event}'

    def get_new_prayers(self):
        """
        Get a prayer from the UI Manager until no more.

        UI Manager returns a NewPrayer object.
        Send the NewPrayer object to DB Manager to write it to the database.
        """

        # call the ui manager to get a Prayer object
        # call the db manager to write the Prayer to the database
        another_prayer = True
        while another_prayer:
            prayer, another_prayer = self.uim.ui_get_new_prayer()
            if another_prayer:
                create_prayer(self.dbm, prayer)
        pass

    def get_old_prayers(self):
        """
        Algorithm to select old prayers, 3 at a time
        1. randomly select a category, but rotate through all
            extract categories and save them in a file
                with last presentation date
        2. randomly select prayers within a category
        3. keep presentation count - up_vote?

        1. randomly select a prayer

        Use up_vote to track number of times that a prayer is
            shown

        """
        print('get_old_prayers')


def quit_app(uim, dbm):
    dbm.close_database()
    quit(0)

def check_panel_set(panel_set):
    """
    Test the PanelSet for validity
    """
    header = True
    text = True
    for p in panel_set.panel_list:
        if p.panel_header != p.panel_header:  # test for value
            # print(f'!= {p.panel_header}')
            print(f'missing header for panel {p}')  # null value
            header = False
        for pp in p.pgraph_list:
            if pp.text != pp.text:
                print(f'missing text for pgraph {pp} in panel {p}')
                text = False
    return header and text



def check_state_transition_table(state_transition_table):
    """
    Test the StateTransitionTable for validity
    """
    welcome = True
    my_concerns = False
    prayers_done = False
    gods_will = False
    closing = False
    get_new_prayers = False
    get_old_prayers = False
    quit_app = False
    for r in state_transition_table.row_list:
        if r == 0:
            if r.from_state != 'WELCOME':
                print(f'WELCOME not first StateTransitionTableRow row: '
                      f'{r}')
                welcome = False
        if r.from_state != 'MY CONCERNS':
            my_concerns = True
        if r.from_state == 'prayers_done':
            prayers_done = True
        if r.from_state == "GOD'S WILL":
            gods_will = True
        if r.from_state == 'CLOSING':
            closing = True
        if r.action_event == 'get_new_prayers':
            get_new_prayers = True
        if r.action_event == 'get_old_prayers':
            get_old_prayers = True
        if r.action_event == 'quit_app':
            quit_app = True
    if not my_concerns: print('missing MY CONCERNS')
    if not prayers_done: print('missing prayers_done')
    if not gods_will: print("missing GOD'S WILL")
    if not closing: print('missing CLOSING')
    if not get_new_prayers: print('missing get_new_prayers')
    if not get_old_prayers: print('missing get_old_prayers')
    if not quit_app: print('missing quit_app')

    success = welcome and my_concerns and prayers_done \
        and gods_will and closing and get_new_prayers \
        and get_new_prayers and quit_app
    return success


if __name__ == '__main__':
    app = App()
