# My Prayers Controller (Controller of the MVC model)
#
# These objects manage the relationship between the user interface
#   controller and the database controller
#
# Initialize upon Run message from OS
#
# Main loop (until user ends program)
#   Send awaiting command message to UI Controller
#   Process command
#
#
# MVC spreadsheet http://bit.ly/3jHdljS
# MVC message sequence diagram http://bit.ly/3xj8hFa
#

from mpo_model import ControlTable, ControlTableRow
from db_manager import InitDatabase, create_panel_objects_from_database, DbPrayer
from ui_manager import Display

debug = True  # todo read this from parm file

class App():
    # the main loop of the application
    # upon startup,
    # who instantiates the Panel object?
    # the DB Manager populates the Panel object with data 
    # send a message to the DB Manager to create a Panel object
    # do so by invoking a method for the DB Manager object

    def __init__(self):
        # initialize
        self.dbm = InitDatabase()  # initialize database manager object
        self.uim = Display()  # initialize user interface manager object
        # get panels data from database
        self.panel_set, self.control_table = \
            create_panel_objects_from_database(self.dbm)
        # display the panels
        #
        # loop to display each panel
        # at the end of each panel display
        # prompt for next panel or collect input (as appropriate);
        #   this needs to be driven by the data;
        #   types of input: 1. next panel (no data collection)
        #       2. collect data for persisting to the database (a prayer)
        for x in self.panel_set.panel_list:
            if debug: print(f'\npanel_set.panel_list: {self.panel_set.panel_list}')
            if debug: print(f'panel: {x} {vars(x)}')
            header = self.uim.display_panel(x)
            # find the ControlTableRow where
            for y in self.control_table.row_list:
                if debug: print(f'control_table.row_list: '
                                f'{self.control_table.row_list} ')
                if debug: print(f'control_table.row: {vars(y)}')
                if y.current_state == header:
                    # perhaps a way to do this:
                    # https://www.danielmorell.com/blog/dynamically-calling-functions-in-python-safely
                    print(f'header: {header} calling {y.action_module}')
                    # print(f'globals: {globals()}')
                    # func = globals()[y.action_module]
                    # self.uim.func()
                    if y.action_module == 'continue_prompt':
                        next = self.uim.continue_prompt()
                    elif y.action_module == 'get_new_prayers':
                        get_new_prayers()
                    else:
                        print(f'unexpected y.action_module value: '
                              f'{y.action_module}')
                    if y.to_state_module == 'display_panel':
                        self.uim.display_panel(x)
                    elif y.to_state_module == 'get_old_prayers':
                        get_old_prayers()
                    elif y.to_state_module == 'quit_app':
                        quit_app()
                    else:
                        print(f'unexpected y.to_state_module value: '
                              f'{y.to_state_module}')


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
