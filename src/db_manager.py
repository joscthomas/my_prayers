"""
My Prayers Database Manager (Model of the MVC model)

These objects are specific to the database technology the app uses.

This version uses pandas as the database.
"""

import pandas as pd
import pickle
import json
import os
import datetime
import random
from mpo_model import Prayer, Category, Panel, PanelPgraph, \
    AppParams, PrayerSession


class AppDatabase:
    """
    The database for the application.

    properties
    df_all_panels: a pandas dataframe containing all panel data
    df_all_prayers: a pandas dataframe containing all prayers
    """

    def __init__(self):  # initialize the database
        # placeholder variables for values established later
        self.df_all_panels = []
        self.df_all_prayers = []
        self.prayer_list_categories = []
        self.category_objects = []
        self.all_categories_index = 0  # points at next in all_categories

        # get the application parameters
        self.get_app_params()
        assert self.check_app_parameters(AppParams.app_params), \
            'app parameters failure'
        pass

        # if present, open pickle file for reading in binary mode
        #   and unpickle the objects
        if os.path.isfile('objects.pkl'):
            self.unpickle_objects()
        else:
            # load Panel dataframe from CSV
            self.import_panels()
            # load prayer dataframe from CSV
            self.import_prayers()
            # instantiate a PrayerSession object
            #   for the current prayer session
            PrayerSession.current_prayer_session = PrayerSession()
        pass
        # build category list for past prayers
        self.get_categories()
        pass

        assert self.check_panel_set(), \
            'panel set load failure'
        pass
        assert self.check_prayers(), \
            'prayer load failure'
        assert self.check_prayer_categories(), \
            'prayer categories load failure'
        assert self.check_prayer_sessions(), \
            'prayer session load failure'
        pass

    @staticmethod
    def unpickle_objects():
        with open("objects.pkl", "rb") as file:
            unpickled_objects = pickle.load(file)

        # extract the classes from the unpickled dictionary
        Prayer = unpickled_objects['Prayer']
        # Category = unpickled_objects['Category']
        Panel = unpickled_objects['Panel']
        PanelPgraph = unpickled_objects['PanelPgraph']
        PrayerSession = unpickled_objects['PrayerSession']
        # unpickle the objects
        prayer_instances = unpickled_objects['Prayer_instances']
        past_prayer_instances = unpickled_objects['Prayer_past_instances']
        unique_selected_prayers = \
            unpickled_objects['Prayer_unique_selected_prayers']
        # category_instances = unpickled_objects['Category_instances']
        panel_instances = unpickled_objects['Panel_instances']
        panel_pgraph_instances = unpickled_objects['PanelPgraph_instances']
        session_instances = unpickled_objects['Session_instances']
        pass

        # initialize class attributes
        Prayer.all_prayers = prayer_instances
        Prayer.all_past_prayers = past_prayer_instances
        Prayer.unique_selected_prayers = unique_selected_prayers
        Panel.all_panels = panel_instances
        PanelPgraph.all_panel_pgraphs = panel_pgraph_instances
        PrayerSession.prayer_session_list = session_instances
        # the prior PrayerSession object is the last one in the list
        PrayerSession.prior_prayer_session = \
            session_instances[len(PrayerSession.prayer_session_list)]
        # instantiate a PrayerSession object for the current prayer session
        PrayerSession.current_prayer_session = PrayerSession()
        pass

        # for obj in Prayer.all_prayers:
        #     print(f'Prayer object address: {id(obj)}',)
        #     for attr_name, attr_value in vars(obj).items():
        #         print(f"{attr_name}: {attr_value}")
        #
        # pass

    def import_panels(self):
        """
        Read the panel CSV file into a pandas dataframe then instantiate
        Panel objects

        columns: panel_set,panel_seq,pgraph_seq,header,verse,text
        """
        # read the CSV file into the dataframe
        self.df_all_panels = pd.read_csv('panels.csv')
        # strip tabs, CRs, and LFs
        self.df_all_panels.replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""],
            regex=True, inplace=True)
        # strip leading and trailing spaces in all fields
        for col in self.df_all_panels.columns:
            try:
                self.df_all_panels[col] = \
                    self.df_all_panels[col].str.strip()
            except AttributeError:
                pass

        # instantiate Panel objects
        self.instantiate_panel_objects(self.df_all_panels)

        # delete the dataframe
        del self.df_all_panels
        pass

    def import_prayers(self):
        """
        Read the prayer CSV file into a pandas dataframe then instantiate
        Prayer objects

        columns: prayer,create_date,answer_date,category,present_count
        """
        # read the CSV file into the dataframe
        self.df_all_prayers = pd.read_csv('prayers.csv')
        # strip tabs, CRs, and LFs
        self.df_all_prayers.replace(
            to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""],
            regex=True, inplace=True)
        # strip leading and trailing spaces in all fields
        for col in self.df_all_prayers.columns:
            try:
                self.df_all_prayers[col] = \
                    self.df_all_prayers[col].str.strip()
            except AttributeError:
                pass

        # create Prayer objects
        pass
        for row in self.df_all_prayers.itertuples():
            prayer = Prayer(row.prayer, row.create_date, row.answer_date,
                            row.category, row.answer, display_count=0)
            if pd.isna(row.answer_date):
                Prayer.all_past_prayers.append(prayer)
        pass

        # delete the dataframe
        del self.df_all_prayers
        pass

    @staticmethod
    def export_database():
        """
        Create a CSV file from dataframe.
        """
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime("%Y%m%d%H%M%S")
        # todo convert set of Prayer and Panel objects to CSV
        # self.df_all_prayers.to_csv(f'prayers{timestamp}.csv')
        # self.df_all_panels.to_csv(f'panels{timestamp}.csv')

    @staticmethod
    def close_database(self):
        """
        Persist the database files
        """
        # check
        assert self.check_prayer_sessions_at_close(), \
            'prayer session check failure at close'
        # create a dictionary containing the objects to be pickled
        objects_to_pickle = {
            'Prayer': Prayer,
            'Category': Category,
            'Panel': Panel,
            'PanelPgraph': PanelPgraph,
            'PrayerSession': PrayerSession,
            'Prayer_instances': Prayer.all_prayers,
            'Prayer_past_instances': Prayer.all_past_prayers,
            'Prayer_unique_selected_prayers':
                Prayer.unique_selected_prayers,
            'Category_instances': Category.all_categories,
            'Panel_instances': Panel.all_panels,
            'PanelPgraph_instances': PanelPgraph.all_panel_pgraphs,
            'Session_instances': PrayerSession.prayer_session_list
        }
        pass

        # open a file for writing in binary mode and pickle the objects
        with open("objects.pkl", "wb") as file:
            pickle.dump(objects_to_pickle, file)

        # save the JSON category file
        data = {"categories": []}
        for category in Category.all_categories:
            data["categories"].append({
                "name": category.category,
                "display_count": category.category_display_count,
                "weight": category.category_weight
            })
        with open("categories.json", "w") as outfile:
            json.dump(data, outfile, indent=4)

        # save the JSON application parameter file
        parameters_dictionary = vars(AppParams.app_params)
        with open('params.json', 'w') as file:
            json.dump(parameters_dictionary, file, indent=4)

    @staticmethod
    def instantiate_panel_objects(df_all_panels):
        """
        instantiate:
        1. Panel objects (each containing a list of child PanelPgraph objects)
        2. PanelPgraph objects
        """
        # identify the panel set for this prayer session
        panel_set_id = get_panel_set_id(df_all_panels)
        # get all panels for the prayer session
        df_panels = df_all_panels.loc[df_all_panels['panel_set'] ==
                                      int(panel_set_id)]
        last_panel_seq = 0
        panel_pgraph_list = []
        # a prayer session has a set of Panel objects (display screens)
        # a Panel has many PanelPgraph objects (text for display screen)
        # the header for a Panel is in the first row
        for row in df_panels.itertuples():  # iterate through each Panel row
            assert len(row.text) > 0, \
                f'assert fail create Panel: a panel row has text = null'
            if last_panel_seq != row.panel_seq:
                # new panel when panel_seq changes
                if last_panel_seq > 0:  # not the first time through
                    # set panel pgraph list for previous panel
                    panel.pgraph_list = panel_pgraph_list
                    panel_pgraph_list = []
                # instantiate a new Panel object
                panel = Panel(row.panel_seq, row.header, pgraph_list=[])
            # instantiate a PanelPgraph object
            panel_pgraph = PanelPgraph(row.pgraph_seq,
                                       row.verse, row.text)
            panel_pgraph_list.append(panel_pgraph)
            last_panel_seq = row.panel_seq
            pass
        panel.pgraph_list = panel_pgraph_list
        pass
        return

    @staticmethod
    def get_app_params():
        """
        Get the application parameters from the JSON file
        """
        # Open JSON file
        with open('params.json') as file:
            data = json.load(file)
        AppParams(data)
        pass
        return

    @staticmethod
    def create_prayer(db, prayer):
        # write a prayer to the database
        #
        # since all app data is in memory and not persisted until
        #   the app ends, there is nothing to persist/write at this point;
        #   when data is stored in a database then change this method
        #   to write to the database
        #
        # add the prayer to the end of the prayer dataframe
        # i = len(db.df_all_prayers)
        # present_count = 0
        # answer = None
        # db.df_all_prayers.loc[i] = \
        #     [prayer.prayer,
        #      prayer.create_date,
        #      prayer.answer_date,
        #      prayer.category,
        #      prayer.answer,
        #      present_count]
        pass

    def update_prayer(self):
        # update a prayer in the database
        pass

    @staticmethod
    def get_categories():
        """
        Instantiate Category objects
        1. Get the persisted categories
        2. Get from past prayers any categories not persisted
        3. Instantiate Category objects for categories
        4. Store in each Category object a list of prayers for the category
        5. Weight some categories by repeating them
        6. Randomize the list of weighted categories
        """
        # retrieve the persisted list of categories
        with open('categories.json') as file:
            data = json.load(file)

        # instantiate a Category object for each category in the JSON file
        json_categories = []
        for c in data['categories']:
            c_obj = Category(c['name'], c['display_count'], c['weight'])
            json_categories.append(c['name'])
        pass

        # get a list of prayer categories from the list of past prayers
        prayer_list_categories = set(obj.category for obj
                                     in Prayer.all_past_prayers)
        pass

        # get the categories in prayer_list that are not in the JSON file
        unique_categories = [item for item in prayer_list_categories
                             if item not in json_categories]
        pass

        # instantiate the Category objects
        for c in unique_categories:
            # print(c)
            obj = Category(category=c, count=0, weight=1)
        pass

        # collect a list of Prayer objects for each Category
        for cobj in Category.all_categories:
            prayer_category = cobj.category
            prayers = [prayer for prayer in Prayer.all_past_prayers
                       if prayer.category == prayer_category]
            cobj.category_prayer_list = prayers
        pass

        # weight categories by repeating them in the list
        Category.weighted_categories = []
        pass
        for co in Category.all_categories:
            # print(co, co.category, co.category_weight)
            n = co.category_weight - 1
            for i in range(0, n):
                # print(co.category)
                Category.weighted_categories.append(co)
                pass
            pass
        pass
        Category.weighted_categories = Category.weighted_categories \
                                       + Category.all_categories
        pass

        # randomize the list of category objects
        random.shuffle(Category.weighted_categories)
        pass

    @staticmethod
    def check_panel_set():
        """
        Test the loading of the Panel objects for validity
        """
        pickle_panel_list = []  # fix this
        pickle_load = True
        if len(pickle_panel_list) > 0:
            # loaded from pickle file
            if Panel.all_panels != pickle_panel_list:
                print('panel pickle load failure')
                pickle_load = False
        pass
        if len(Panel.all_panels) <= 0:
            print('all_panels empty')
            header = False
            text = False
        else:
            header = True
            text = True
            for p in Panel.all_panels:
                if p.panel_header is None:
                    print(f'missing header for panel {p}')
                    header = False
                for pp in p.pgraph_list:
                    if pp.text is None:
                        print(f'missing text for pgraph {pp} in panel {p}')
                        text = False
        success = header and text and pickle_load
        return success

    @staticmethod
    def check_prayers():
        """
        Test the loading of the Prayer objects for validity
        """
        pickle_prayer_list = []  # fix this
        pickle_load = True
        if len(pickle_prayer_list) > 0:
            # loaded from pickle file
            if Prayer.all_prayers != pickle_prayer_list:
                print('prayer pickle load failure')
                pickle_load = False
        pass
        all_prayers = True
        if len(Prayer.all_prayers) <= 0:
            all_prayers = False
            print('all_prayers empty')

        success = all_prayers and pickle_load
        return success

    @staticmethod
    def check_app_parameters(parameters):
        """
        Test the app parameters for validity
        """
        last_panel_set = True
        if parameters.last_panel_set != parameters.last_panel_set:
            last_panel_set = False
        install_path = True
        if parameters.install_path != parameters.install_path:
            install_path = False
        past_prayer_display_count = True
        if parameters.past_prayer_display_count != \
                parameters.past_prayer_display_count:
            past_prayer_display_count = False

        success = last_panel_set and install_path and past_prayer_display_count
        return success

    @staticmethod
    def check_prayer_categories():
        category_prayers = True
        prayer_count = 0
        for obj in Category.all_categories:
            prayer_count = prayer_count + len(obj.category_prayer_list)
        if prayer_count == 0:
            print('category_prayer_lists empty')
            category_prayers = False
        if len(Prayer.all_prayers) > 0:
            all_prayers = True
        else:
            all_prayers = False
            print('all_prayers empty')
        if len(Prayer.all_past_prayers) > 0:
            past_prayers = True
        else:
            past_prayers = False
            print('all_past_prayers empty')

        if not os.path.isfile('categories.json'):
            print('no categories.json file')

        success = category_prayers and all_prayers and past_prayers \
                  and os.path.isfile('categories.json')
        return success

    @staticmethod
    def check_prayer_sessions():
        """
        Test the loading of the PrayerSession objects for validity
        """
        # check for PrayerSession object
        session_object = True
        if len(PrayerSession.prayer_session_list) <= 0:
            print('prayer_session_list empty')
            session_object = False
        # if no past session object, expect length of session list to be 1
        if PrayerSession.prior_prayer_session is None:
            if len(PrayerSession.prayer_session_list) != 1:
                print('expected a single PrayerSession object')
                session_object = False
        else:
            if len(PrayerSession.prayer_session_list) <= 1:
                print('expected multiple PrayerSession objects')
                session_object = False
        #
        success = session_object
        return success

    @staticmethod
    def check_prayer_sessions_at_close():
        # expect that a prayer session adds at least one prayer
        prayers_added = True
        if PrayerSession.current_prayer_session. \
                new_prayer_added_count == 0:
            print('no prayers added')
            prayers_added = False
        # expect that a prayer session adds at least one prayer
        prayers_prayed = True
        if PrayerSession.current_prayer_session. \
                past_prayer_prayed_count == 0:
            print('no prayers prayed')
            prayers_prayed = False
        pass
        success = prayers_added and prayers_prayed
        return success


def get_panel_set_id(df_all_panels):
    """
    Access AppParams to get the next PanelSet for display.
    Rotate through the panel data for each prayer session.
    """
    # find the panel set id that is next (first one greater than last one)
    last_panel_set = AppParams.app_params.last_panel_set
    try:
        next_panel_set_row = df_all_panels[df_all_panels.panel_set
                                           > int(last_panel_set)].iloc[0]
    except IndexError:
        # Handle the case where no row with panel_set greater than
        #   the last_panel_set is found by resetting to the first row
        next_panel_set_row = df_all_panels[df_all_panels.panel_set
                                           > int(1)].iloc[0]
    panel_set_id = next_panel_set_row.panel_set
    # save the current session panel_set_id
    #   as the last_panel_set in AppParams
    AppParams.app_params.last_panel_set = str(panel_set_id)
    pass
    return panel_set_id
