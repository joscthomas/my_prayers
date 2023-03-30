"""
My Prayers Controller (Controller of the MVC model)

These objects manage the relationship between the user interface
   controller and the database controller.

MVC spreadsheet http://bit.ly/3jHdljS
MVC message sequence diagram http://bit.ly/3xj8hFa

"""

from mpo_model import ControlTable, ControlTableRow
from db_manager import InitDatabase, create_panel_objects_from_database, DbPrayer
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
        self.dbm = InitDatabase()
        # initialize user interface manager object
        self.uim = Display()
        # get panels data from database
        self.panel_set: object = None  # PanelSet object
        self.control_table:object = None  # ControlTable object
        self.panel_set, self.control_table = \
            create_panel_objects_from_database(self.dbm)
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
            for y in self.control_table.row_list:
                # find the ControlTableRow where
                if y.current_state == header:
                    if y.action_module == 'continue_prompt':
                        self.uim.continue_prompt()
                    elif y.action_module == 'get_new_prayers':
                        get_new_prayers()
                    else:
                        assert False, f'unexpected y.action_module ' \
                                      f'value: {y.action_module}'
                    if y.to_state_module == 'display_panel':
                        self.uim.display_panel(x)
                    elif y.to_state_module == 'get_old_prayers':
                        get_old_prayers()
                    elif y.to_state_module == 'quit_app':
                        quit_app()
                    else:
                        assert False, f'unexpected y.to_state_module ' \
                                      f'value: {y.to_state_module}'


def get_new_prayers():
    print('get_new_prayers')
    # get a prayer from the ui manager
    # ui manager returns a NewPrayer object
    # send the NewPrayer object to db manager to write it to the database

    new_prayer_list = []
    another_prayer = True
    while another_prayer:
        prayer = input('Enter prayer request (or return if done)\n').strip()
        if len(prayer) > 0:
            category = input('Category?\n').strip()
            # save the new prayer
            new_prayer = Prayer(prayer, category)
            new_prayer_list.append(new_prayer)
        else:
            another_prayer = False


def get_old_prayers():
    print('get_old_prayers')


def quit_app():
    print('quit_app')
    quit(0)


if __name__ == '__main__':
    app = App()
