"""
My Prayers Controller (Controller of the MVC model)

These objects manage the relationship between the user interface
   controller and the database controller.

MVC spreadsheet http://bit.ly/3jHdljS
MVC message sequence diagram http://bit.ly/3xj8hFa

"""

from datetime import datetime, timedelta
import random
from mpo_model import Prayer, Category, Panel, StateTransitionTable, \
    AppParams, PrayerSession
from db_manager import AppDatabase, create_prayer
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

        # build state transition table from Panel objects
        self.build_state_transition_table()
        assert self.check_state_transition_table(
            StateTransitionTable.all_rows), \
            'state transition table failure'

        # track prayer session streak
        current_date = datetime.now()
        # subtract 1 days to get the yesterday's date
        yesterday = current_date - timedelta(days=1)
        pass
        if yesterday == datetime.strptime(
                AppParams.app_params.last_prayer_date, '%d-%b-%Y'):
            AppParams.app_params.prayer_streak += 1
        else:
            AppParams.app_params.prayer_streak = 1
        AppParams.app_params.last_prayer_date = \
            current_date.strftime('%d-%b-%Y')
        pass

        # the main loop of the app
        self.main_loop()

    def main_loop(self):
        """
        The main loop of the application.

        Display the first panel then
            the StateTransitionTable to drive what happens next
        """

        # loop to display each Panel in turn
        for pobj in Panel.all_panels:
            panel_header = self.uim.display_panel(pobj)
            # loop to find the StateTransitionTable row
            # that matches the Panel header to find the event
            # and the module to call that causes transition to occur
            for sobj in StateTransitionTable.all_rows:
                if sobj.from_state == panel_header:
                    match sobj.action_event:
                        case 'get_continue':
                            response = self.uim.get_response(
                                'enter to continue ')
                            # special commands from the continue prompt
                            match response:
                                case 'import':
                                    pass
                                    # deleting the pickle files
                                    # causes import to occur
                                case 'export':
                                    self.dbm.export_database()
                        case 'get_new_prayers':
                            self.get_new_prayers()
                        # case 'get_past_prayers':
                            self.get_past_prayers()
                        case 'quit_app':
                            self.quit_app(self.uim, self.dbm)
                        case _:
                            assert False, \
                                f'unexpected s.action_event ' \
                                f'value: {sobj.action_event}'

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
                self.dbm.create_prayer(self.dbm, prayer)
                PrayerSession.current_prayer_session.\
                    new_prayer_added_count += 1
        pass

    def get_past_prayers(self):
        """
        Algorithm to select past prayers
        1. randomly select a category, but rotate through all
            extract categories and save them in a file
            with last presentation date
        2. randomly select prayers within a category
        3. display_count tracks number of times that a prayer is
            shown

        repeat until done:
            - get old_prayer_display_count number of prayers
                from the database
            - send old_prayer_display_count number of prayers
                to the ui for display
        """
        # get a list of prayers from the last 7 days
        current_date = datetime.now()
        # subtract 7 days to get the start date
        start_date = current_date - timedelta(days=7)
        # create an empty list to hold recent prayers
        recent_prayers = []
        # loop through all_past_prayers and add recent prayers to the list
        for prayer in Prayer.all_past_prayers:
            prayer_date = datetime.strptime(prayer.create_date, '%d-%b-%Y')
            if prayer_date >= start_date:
                recent_prayers.append(prayer)
        pass

        # randomly select
        # create a list of lists of Prayer objects
        #   starting with the list of recent Prayer objects
        prayer_lists = []
        prayer_lists.append(recent_prayers)
        pass

        # add the Category prayer lists
        for category in Category.weighted_categories:
            prayer_lists.append(category.category_prayer_list)

        # gather a set of past prayers for presentation
        # get number of lists of prayer objects
        num_lists = len(prayer_lists)
        # number of times to loop
        num_selections = 20
        # to keep track of the selected prayers
        selected_prayers = []
        selected_set = set()
        pass
        for i in range(num_selections):
            # create a list of available indices for each prayer list
            available_indices = [j for j in range(num_lists)
                                 if len(prayer_lists[j]) > 0]
            pass
            # randomly select an index from the available indices
            #   for each prayer list
            selected_indices = []
            for j in available_indices:
                index = random.randrange(len(prayer_lists[j]))
                selected_indices.append(index)
                pass
            # get the selected prayer objects and add them to the
            #   selected_prayers list
            pass
            for j, index in zip(available_indices, selected_indices):
                if index < len(prayer_lists[j]):
                    prayer = prayer_lists[j][index]
                    # check if the prayer object has already been selected
                    if prayer not in selected_set:
                        # add the prayer object to the selected_prayers list and the selected_set
                        selected_prayers.append(prayer)
                        selected_set.add(prayer)
                    # remove the selected index from the prayer list
                    prayer_lists[j].pop(index)
            pass

        # Loop through the original list and add each element
        #   to the new list if it hasn't already been added
        Prayer.unique_selected_prayers = []
        for item in selected_prayers:
            if item not in Prayer.unique_selected_prayers:
                Prayer.unique_selected_prayers.append(item)

        # send the past prayers to the ui manager for display
        display_num = AppParams.app_params.past_prayer_display_count
        counter = 0
        prayer_count = len(Prayer.unique_selected_prayers)
        pass
        while counter < prayer_count:
            for i in range(counter,
                           min(counter + display_num, prayer_count)):
                pass
                self.uim.display_prayer(
                    Prayer.unique_selected_prayers[i])
                Prayer.unique_selected_prayers[i].display_count += 1
                PrayerSession.current_prayer_session.\
                    past_prayer_prayed_count += 1
                response = self.uim.get_response(
                    '"answered" or enter to continue ')
                if response == 'a':
                    self.uim.get_answer(
                        Prayer.unique_selected_prayers[i])
                    PrayerSession.current_prayer_session.\
                        answered_prayer_count += 1
            counter += display_num
            if counter >= prayer_count:
                break
            response = self.uim.get_response(
                'enter "more" or "done" ')
            if response.lower() == 'd':
                break
        pass

    @staticmethod
    def build_state_transition_table():
        """
        Examine Panel objects to build StateTransitionTable
        """
        # iterate through Panel objects
        last_stt_row = None
        for obj in Panel.all_panels:
            # when panel_seq changes, write the Panel and StateTransitionRow
            # create a StateTransitionTable row for the prior Panel
            # the default to_state for a Panel is header of next Panel
            # defaults
            action_event = 'get_continue'
            from_state = obj.panel_header
            to_state = None
            # special conditions to manage gathering and retrieving prayers
            if from_state == 'MY CONCERNS':
                action_event = 'get_new_prayers'
                to_state = 'prayers_done'
                StateTransitionTable(from_state,
                                     action_event,
                                     to_state)
                from_state = 'prayers_done'
                action_event = 'get_past_prayers'
                to_state = None
            if from_state == 'CLOSING':
                action_event = 'quit_app'
                to_state = 'done'
            # set prior StateTransitionTable row
            if obj.panel_seq > 1:
                last_stt_row.to_state = from_state
            last_stt_row = StateTransitionTable(from_state,
                                                action_event,
                                                to_state)
            pass
        return

    @staticmethod
    def check_state_transition_table(state_transition_table):
        """
        Test the StateTransitionTable for validity
        """
        welcome = True
        my_concerns = False
        prayers_done = False
        # gods_will = False
        closing = False
        get_new_prayers = False
        get_past_prayers = False
        quit_app = False
        for r in state_transition_table:
            if r == 0:
                if r.from_state != 'WELCOME':
                    print(f'WELCOME not first StateTransitionTableRow row: '
                          f'{r}')
                    welcome = False
            if r.from_state != 'MY CONCERNS':
                my_concerns = True
            if r.from_state == 'prayers_done':
                prayers_done = True
            # GOD'S WILL doesn't always follow MY CONCERNS
            #   and everything still seems to work okay
            # if r.from_state == "GOD'S WILL":
            #     gods_will = True
            if r.from_state == 'CLOSING':
                closing = True
            if r.action_event == 'get_new_prayers':
                get_new_prayers = True
            if r.action_event == 'get_past_prayers':
                get_past_prayers = True
            if r.action_event == 'quit_app':
                quit_app = True
        if not my_concerns: print('missing MY CONCERNS')
        if not prayers_done: print('missing prayers_done')
        # if not gods_will: print("missing GOD'S WILL")
        if not closing: print('missing CLOSING')
        if not get_new_prayers: print('missing get_new_prayers')
        if not get_past_prayers: print('missing display_past_prayers')
        if not quit_app: print('missing quit_app')

        success = welcome and my_concerns and prayers_done \
                  and closing and get_new_prayers \
                  and get_past_prayers and quit_app
        # and gods_will
        return success

    @staticmethod
    def quit_app(uim, dbm):
        dbm.close_database()
        uim.close_ui()
        quit(0)


if __name__ == '__main__':
    app = App()
