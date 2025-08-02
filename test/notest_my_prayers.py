'''
Purpose: module for testing using pytest

To run this test from the command shell
1. cd \\Users\\jcthomas\\Documents\\JCT Documents\\Python\\my_prayers_project
2. pytest
'''

# Standard library imports
# import sys
# import pytest
import logging
from datetime import date


# Third party imports


# Local application imports
# from local_module import local_class
# from local_package import local_function
# from package(directory).module import function
from ..src import my_prayers


def test_main():

    # logging set up
    logging.basicConfig(
        filename='app_test.log', filemode='w',
        format='%(asctime)s : %(name)s : %(levelname)s : %(message)s',
        level=logging.DEBUG, force=True)
    logging.debug('test_my_prayers : Logging level is TEST DEBUG')

    # module_filename.function
    # TODO the following seems superflous since the error checking is
    # in the function; how do I test?
    db_connection = my_prayers.db_setup()
    assert db_connection is not None
    logging.debug('db_connection : %s', db_connection)

    check_db(db_connection)

    assert my_prayers.welcome(db_connection) == 'welcome'
    assert my_prayers.honor_God(db_connection) == 'honor_God'
    assert my_prayers.manage_prayers(db_connection) == 'manage_prayers'
    assert my_prayers.Gods_will(db_connection) == 'Gods_will'
    assert my_prayers.db_close(db_connection) == 'db_close'

    return


def check_db(db_connection):
    ''' Test that the database has been successfully created

    Test each table by:
        1. Set up columns and values for each table
        2. Call function that performs some basic operations on each table
        3. Delete each table
    '''

    logging.debug('module : check_db : db_connection : %s', db_connection)

    # check each table in turn
    # (see create_db_tables in my_prayers.py for table definition)

    table_name = 'category'
    table_cols = 'category'
    col_values = '"test category 1"'
    check_table(db_connection, table_name, table_cols, col_values)

    table_name = 'prayer'
    table_cols = 'prayer_text, create_date, category_id'
    col_values = '"test prayer 1", "' + str(date.today()) + '", 1'
    check_table(db_connection, table_name, table_cols, col_values)

    table_name = 'message'
    table_cols = 'message_id, component, pgraph, header, verse, message_text'
    col_values = '"2022-12-04", 1, 1, "WELCOME", "","test message 1"'
    check_table(db_connection, table_name, table_cols, col_values)

    # Delete all rows for each table in turn
    # Delete prayer first because of FK constraint on category
    table_name = 'prayer'
    del_table_rows(db_connection, table_name)

    table_name = 'category'
    del_table_rows(db_connection, table_name)

    # Delete message first
    table_name = 'message'
    del_table_rows(db_connection, table_name)

    return


def check_table(db_connection, table_name, table_cols, col_values):
    ''' Check that a table can be operated on

    Test each table by:
    1. Check that no rows exist
    2. Insert a row
    3. Retrieve the row

    *input args*
        db_connection : obj ; sql database
        table_name : str ; name of table to check
        table_cols : str ; table columns for insert
        col_values : str ; values for table columns
    *returns*
        null
    '''

    logging.debug(('check_table : table_name=%s : table_cols=%s\
        : col_values=%s'), table_name, table_cols, col_values)

    cursor = db_connection.cursor()
    # 1. Check that no rows exist
    sql_string = 'SELECT * FROM ' + table_name
    logging.debug('sql_string=%s', sql_string)
    cursor.execute(sql_string)
    rows = cursor.fetchall()
    assert len(rows) == 0
    logging.debug('start : table=%s : rows=%s', table_name, len(rows))

    # 2. Insert a row
    sql_string = ('INSERT INTO ' + table_name + ' (' + table_cols +
                  ') VALUES (' + col_values + ')')
    logging.debug('sql_string=%s', sql_string)
    db_connection.execute(sql_string)
    db_connection.commit()

    # 3. Retrieve the row
    sql_string = 'SELECT * FROM ' + table_name
    cursor.execute(sql_string)
    rows = cursor.fetchall()
    assert len(rows) == 1
    logging.debug('insert step : table=%s : rows=%s', table_name, len(rows))
    for row in rows:
        logging.debug('table=%s : row=%s', table_name, row)

    return


def del_table_rows(db_connection, table_name):
    ''' Delete all rows in a table

    *input args*
        db_connection : obj ; sql database
        table_name : str ; name of table to check
    *returns*
        null
    '''
    logging.debug('delete step : table=%s', table_name)

    cursor = db_connection.cursor()
    sql_string = 'DELETE FROM ' + table_name
    cursor.execute(sql_string)
    db_connection.commit()

    sql_string = 'SELECT * FROM ' + table_name
    cursor.execute(sql_string)
    rows = cursor.fetchall()
    assert len(rows) == 0

    return


if __name__ == '__main__':
    test_main()
