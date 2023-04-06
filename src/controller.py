"""
My Prayers Controller (Controller of the MVC model)

These objects manage the relationship between the user interface
   controller and the database controller.

MVC spreadsheet http://bit.ly/3jHdljS
MVC message sequence diagram http://bit.ly/3xj8hFa

"""

from mpo_model import StateTransitionTable, StateTransitionTableRow
from db_manager import AppDatabase, create_panel_objects_from_database, \
    create_prayer, read_prayer_set
from ui_manager import Display

class App():
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
        # get panels data from database
        self.panel_set: object = None  # PanelSet object
        self.state_transition_table: object = None
        self.panel_set, self.state_transition_table = \
            create_panel_objects_from_database(self.dbm)
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
                # else:
                #     assert False, f'unexpected s.from_state ' \
                #                   f'value: {s.from_state}'

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
    print('quit_app')
    dbm.close_database()
    quit(0)


if __name__ == '__main__':
    app = App()
