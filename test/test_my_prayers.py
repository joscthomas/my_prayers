'''
Purpose: main module for testing using pytest
'''

# Standard library imports
# import sys
# import pytest
import logging

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
        level=logging.DEBUG, force = True)
    logging.debug('Logging level is TEST DEBUG')
    app_debug = True

    # module_filename.function
    assert my_prayers.db_setup(app_debug) == 'db_setup'
    assert my_prayers.welcome(app_debug) == 'welcome'
    assert my_prayers.honor_God(app_debug) == 'honor_God'
    assert my_prayers.manage_prayers(app_debug) == 'manage_prayers'
    assert my_prayers.Gods_will(app_debug) == 'Gods_will'
    assert my_prayers.db_close(app_debug) == 'db_close'


if __name__ == '__main__':
    test_main()
