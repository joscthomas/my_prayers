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
'''

# Standard library imports
import logging

# Third party imports

# Local application imports

# define functions


# define the main function
def main():
    """The main or top level module of the My Prayers application.

    Call the following primary functions for this application.
    """

    # logging set up
    logging.basicConfig(
        filename='app.log', filemode='w',
        format='%(asctime)s : %(name)s : %(levelname)s : %(message)s',
        level=logging.DEBUG, force=True)
    logging.debug('Logging level is DEBUG')
    app_debug=True

    db_setup(app_debug)
    welcome(app_debug)
    honor_God(app_debug)
    manage_prayers(app_debug)
    Gods_will(app_debug)
    db_close(app_debug)


def welcome(app_debug):
    if app_debug==True:
        logging.debug('Function : welcome')

    return "welcome"


def honor_God(app_debug):
    if app_debug==True:
        logging.debug('Function : honor_God')

    return "honor_God"


def manage_prayers(app_debug):
    if app_debug==True:
        logging.debug('Function : manage_prayers')

    return "manage_prayers"


def Gods_will(app_debug):
    if app_debug==True:
        logging.debug('Function : Gods_will')    

    return "Gods_will"


def db_setup(app_debug):
    if app_debug==True:
        logging.debug('Function : db.setup')

    return 'db_setup'


def db_close(app_debug):
    if app_debug==True:
        logging.debug('Function : db.close')

    return 'db_close'


if __name__ == '__main__':
    main()
