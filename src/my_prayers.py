'''
Manage a list of prayers by allowing CRUD operations.
Modeled after YouVersion's Pray Now function.
1. Present a welcome message.
2. Present a message that honors God.
3. Present a message that invites praying for your concerns and an
    Add Prayer button.
4. Upon clicking the Add Prayer button, present a dialog to collect and
    save a prayer. Include a button to add another prayer.
5. When no more prayers to add, present prayers from the prayer list 3 at
    a time with a Show More button. Repeat.
6. When the Show More button is not clicked, then present a message that
    invites God's will to be done.
7. Present a closing message.

“Code tells you how; Comments tell you why.”
— Jeff Atwood (aka Coding Horror)
'''

# Standard library imports
import logging
import os

# Third party imports

# Local application imports

# define functions


# define the main function
def main():
    '''The main or top level module of the My Prayers application.

    Call the following primary functions for this application.
    '''

    # logging set up
    logging.basicConfig(
        filename='app.log', filemode='w',
        format='%(asctime)s : %(name)s : %(levelname)s : %(message)s',
        level=logging.DEBUG, force=True)
    logging.debug('Logging level is DEBUG')
    app_debug = True

    # main line
    db_connection = db_setup(app_debug)
    # temporary null op so db_connection is referenced
    if db_connection is False:
        pass

    welcome(app_debug)
    honor_God(app_debug)
    manage_prayers(app_debug)
    Gods_will(app_debug)
    db_close(app_debug)


def welcome(app_debug):
    if app_debug is True:
        logging.debug('Function : welcome')

    return "welcome"


def honor_God(app_debug):
    if app_debug is True:
        logging.debug('Function : honor_God')

    return "honor_God"


def manage_prayers(app_debug):
    if app_debug is True:
        logging.debug('Function : manage_prayers')

    return "manage_prayers"


def Gods_will(app_debug):
    if app_debug is True:
        logging.debug('Function : Gods_will')

    return "Gods_will"


def db_setup(app_debug):
    ''' Function that Sets up an SQL database for prayers and support data.

    *input arguments*
    app_debug : bool
        true turns on debug logging
    *returns*
    db_connection : obj
        name of database object if creation successful, null if not
    '''

    if app_debug is True:
        logging.debug('Function : db_setup')

    # Using SQLite DBMS
    import sqlite3
    from sqlite3 import Error

    # FIXIT What if the database already sexist?

    # create a connection to a SQLite database for a file
    # in the current project (maybe install?) directory
    # TODO collect db_file for app setup parameter
    db_file = 'db/mp.db'        # name of database file
    db_connection = None        # initialize
    setup_db_tables = False     # initialize

    if app_debug is True:
        logging.debug('db file exists : %s', os.path.isfile(db_file))

    # test for a new database file; if so, setup database tables
    if os.path.isfile(db_file) is False:
        setup_db_tables = True

    try:
        db_connection = sqlite3.connect(db_file)
    except Error as e:
        logging.error('SQLite error upon database creation ', e)
#        print(e)
#    finally:
#        if conn:
#            conn.close()

    if app_debug is True:
        logging.info('Created SQLite database file: %s', db_file)
        logging.info('SQLite database version %s', sqlite3.version)
        logging.debug('db_connection : %s', db_connection)
        logging.debug('db file exists : %s', os.path.isfile(db_file))
        logging.debug('setup_db_tables : %s', setup_db_tables)

    if setup_db_tables is not True:     # new database file, create tables
        create_db_tables(app_debug)

    return db_connection


def create_db_tables(app_debug):
    ''' Execute SQL statements to create datbase tables for the app

    *input arguments*
    app_debug : bool
        true turns on debug logging
    *returns*
    db_connection : obj
        name of database object if creation successful, null if not
    '''

    if app_debug is True:
        logging.debug('Function : create_db_tables')

    return


def db_close(app_debug):
    if app_debug is True:
        logging.debug('Function : db.close')

    return 'db_close'


if __name__ == '__main__':
    main()
