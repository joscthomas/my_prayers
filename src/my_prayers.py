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
import sqlite3
from sqlite3 import Error

# Local application imports

# define constants
APP_DEBUG = True

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
    if APP_DEBUG is True:
        logging.debug('Logging level is DEBUG')
#    app_debug = True

    # main line
    db_connection = db_setup()
    welcome(db_connection)
    honor_God(db_connection)
    manage_prayers(db_connection)
    Gods_will(db_connection)
    db_close(db_connection)

    return


def welcome(db_connection):
    if APP_DEBUG is True:
        logging.debug('Function : welcome')

    return "welcome"


def honor_God(db_connection):
    if APP_DEBUG is True:
        logging.debug('Function : honor_God')

    return "honor_God"


def manage_prayers(db_connection):
    if APP_DEBUG is True:
        logging.debug('Function : manage_prayers')

    return "manage_prayers"


def Gods_will(db_connection):
    if APP_DEBUG is True:
        logging.debug('Function : Gods_will')

    return "Gods_will"


def db_setup():
    ''' Set up an SQL database for prayers and support data.

    *input arguments*
    *returns*
        db_connection : obj ; database object if successful, null if not
    '''

    if APP_DEBUG is True:
        logging.debug('Function : db_setup')

    # create a connection to a SQLite database file
    # TODO in the current project (maybe install?) directory
    # TODO collect db_file for app setup parameter
    db_file = 'db/mp.db'        # name of database file

    db_connection = None        # initialize
    setup_db_tables = False     # initialize

    if APP_DEBUG is True:
        logging.debug('db file exists : %s', os.path.isfile(db_file))

    # test for a new database file;
    # only setup database file with tables if they do not already exist
    if os.path.isfile(db_file) is False:
        setup_db_tables = True

    db_connection = create_connection(db_file)

    if APP_DEBUG is True:
        logging.debug('Created SQLite database file: %s', db_file)
        logging.debug('SQLite database version %s', sqlite3.version)
        logging.debug('db_connection : %s', db_connection)
        logging.debug('db file exists : %s', os.path.isfile(db_file))
        logging.debug('setup_db_tables : %s', setup_db_tables)

    if setup_db_tables is True:     # new database file, create tables
        create_db_tables(db_connection)

    return db_connection


def create_connection(db_file):
    ''' Create a database connection to the SQLite database

    *input parameters*
        db_file : str ; database file name
    *return*
        conn : obj ; Connection object or None
    '''

    # import sqlite3
    # from sqlite3 import Error

    db_connection = None    # initialize

    try:
        db_connection = sqlite3.connect(db_file)
    except Error as e:
        logging.error('SQLite error upon database creation %s', e)

    return db_connection


def create_db_tables(db_connection):
    ''' Execute SQL statements to create datbase tables for the app

    *input arguments*
        db_connection : obj ; database object if successful, null if not
    *returns*
        null
    Database design diagram : http://bit.ly/3FyXESA
    '''

    if APP_DEBUG is True:
        logging.debug('Function : create_db_tables')

    # prayer_id : unique identifer set by sqlite
    # prayer_text : a prayer request
    # create_date : date a prayer was created
    # answer_text : the answer to the prayer request
    # answer_date : date a prayer was answered
    # category_id : points at the category name for the prayer
    # display_count : number of times a prayer presented
    # (dates stored as ISO8601 strings : "YYYY-MM-DD HH:MM:SS.SSS"
    sql_string = ('''CREATE TABLE IF NOT EXISTS prayer
        (prayer_id integer PRIMARY KEY,
        prayer_text text NOT NULL,
        create_date text NOT NULL,
        answer_text text,
        answer_date text,
        category_id integer,
        display_count integer,
        FOREIGN KEY (category_id)
        REFERENCES category (category_id)
        );''')
    if APP_DEBUG is True:
        logging.debug('prayer : %s', sql_string)
    create_table(db_connection, sql_string)

    # category_id : unique identifier set by sqlite
    # category_name : a category of a prayer request
    sql_string = ('''CREATE TABLE IF NOT EXISTS category
        (category_id integer PRIMARY KEY,
        category_name text NOT NULL
        );''')
    create_table(db_connection, sql_string)

    # message_id : unique identifier set by sqlite
    # header : a label at the top of the page
    # seq : one up sequence number identifying a header component
    # pgraph : one up sequence number identifying a paragraph
    # verse : bible reference book, chapter, verse or null (not a verse)
    # message : the text of the message
    sql_string = ('''CREATE TABLE IF NOT EXISTS message
        (message_id integer,
        header text,
        seq integer,
        pgraph integer,
        verse text,
        message text NOT NULL,
        PRIMARY KEY (message_id, header, seq, pgraph)
        );''')
    create_table(db_connection, sql_string)

    # status_id : unique identifier assigned by sqlite
    # message_count : number of times for a prayer session
    sql_string = ('''CREATE TABLE IF NOT EXISTS status
        (status_id integer PRIMARY KEY,
        message_count integer NOT NULL
        );''')
    create_table(db_connection, sql_string)

    return


def create_table(db_connection, create_table_sql):
    """ create a table from the create_table_sql statement

    *input arguments*
        db_connection : obj ; database connection object
        create_table_sql : str ; a CREATE TABLE sql statement
    *return*
        null
    """

    # import sqlite3
    from sqlite3 import Error

    try:
        c = db_connection.cursor()
        c.execute(create_table_sql)
    except Error as e:
        logging.error('SQLite error upon table creation %s', e)

    return


def db_close(db_connection):
    if APP_DEBUG is True:
        logging.debug('Function : db_close')

    return 'db_close'


if __name__ == '__main__':
    main()
