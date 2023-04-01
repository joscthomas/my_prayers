"""
My Prayers Controller (Controller of the MVC model)

These objects manage the relationship between the user interface
   controller and the database controller.

MVC spreadsheet http://bit.ly/3jHdljS
MVC message sequence diagram http://bit.ly/3xj8hFa

"""

from mpo_model import ControlTable, ControlTableRow
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
        self.control_table:object = None  # ControlTable object
        self.panel_set, self.control_table = \
            create_panel_objects_from_database(self.dbm)
        # the main loop of the app
        self.main_loop()


    def main_loop(self):
        """
        The main loop of the application.

        Display the first panel then
            use the ControlTable to drive what happens next
        """

        # loop to display each Panel
        for x in self.panel_set.panel_list:
            header = self.uim.display_panel(x)
            for ctr in self.control_table.row_list:
                # find the ControlTableRow (ctr) that matches the Panel
                #   (header of the first pgraph)
                # just displayed to determine what happens next
                if ctr.current_state == header:
                    if ctr.action_module == 'continue_prompt':
                        self.uim.continue_prompt()
                        # special commands
                        if self.uim.command == 'import':
                            self.dbm.import_database()
                        elif self.uim.command == 'export':
                            self.dbm.export_database()
                    elif ctr.action_module == 'get_new_prayers':
                        self.get_new_prayer()
                    else:
                        assert False, f'unexpected y.action_module ' \
                                      f'value: {ctr.action_module}'
                    # now another action
                    if ctr.to_state_module == 'display_panel':
                        self.uim.display_panel(x)
                    elif ctr.to_state_module == 'get_old_prayers':
                        self.get_old_prayers()
                    elif ctr.to_state_module == 'quit_app':
                        quit_app(self.uim, self.dbm)
                    else:
                        assert False, f'unexpected y.to_state_module ' \
                                      f'value: {ctr.to_state_module}'


    def get_new_prayer(self):
        """
        Get a prayer from the ui manager.

        UI manager returns a NewPrayer object.
        Send the NewPrayer object to db manager to write it to the database.
        """

        # call the ui manager to get a Prayer object
        # call the db manager to write the Prayer to the database
        another_prayer = True
        while another_prayer:
            prayer, another_prayer = self.uim.ui_get_new_prayer()
            if another_prayer:
                create_prayer(self.dbm, prayer)




    def get_old_prayers():
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
