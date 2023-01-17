from sqlalchemy import create_engine  # and_, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func  # asc, desc,

import logging

from ..src.model import Category, Prayer, Message  # Parameters
from ..src import my_prayers


def test_app():
    ''' Test the model-view-controller my_prayer app

    '''
    # logging set up
    logging.basicConfig(
        filename='app_test.log', filemode='w',
        format='%(asctime)s : %(name)s : %(levelname)s : %(message)s',
        level=logging.DEBUG, force=True)
    logging.debug('test_app : Logging level is TEST DEBUG')

    # create the database, if necessary
    db_connection = my_prayers.db_setup()
    assert db_connection is not None
    logging.debug('db_connection : %s', db_connection)

    #
    # Connect to the database using SQLAlchemy
    #
    # TODO I do not really understand this implementation but I think it is
    # a better solution then what follows
    '''
    with resources.path(
        "mp_project.db", "mp.db"
    ) as sqlite_filepath:
        engine = create_engine(f"sqlite:///{sqlite_filepath}")
    '''
    engine = create_engine('sqlite:///db/mp.db')
    #
    # create the Session class from SQLAlchemy
    Session = sessionmaker()
    # bind the Session to the engine
    Session.configure(bind=engine)
    # create the session instance, used to communicate with SQLAlchemy
    session = Session()

    # TODO start with an empty database

    # put some data in the database
    populate_db(session)

    # test the model by retrieving and getting data
    categories = get_categories(session)
    for row in categories:
        logging.debug((
            f'Category: {row.category_name}, total : {row.total_categories}'
            )
        )

    prayers = get_prayers(session)
    for row in prayers:
        logging.debug((
            f'Prayer: {row.prayer_text}, total : {row.total_prayers}'
            )
        )

    messages = get_messages(session)
    for row in messages:
        logging.debug((
            f'Message: {row.message_text}, total : {row.total_messages}'
            )
        )

    # delete the data
    result = session.query(Category).one()
    session.delete(result)
    result = session.query(Prayer).one()
    session.delete(result)
    result = session.query(Message).one()
    session.delete(result)
    session.commit()

    # see https://realpython.com/python-sqlite-sqlalchemy/#working-with-sqlalchemy-and-python-objects # noqa

    return


def populate_db(session):

    category = Category(category_name='test category 1')
    session.add(category)

    prayer = Prayer(prayer_text='test prayer 1', create_date='2022-01-15',
            category_id=1)
    session.add(prayer)

    message = Message(message_id='2022-12-04', component=1, pgraph=1,
            header='WELCOME', message_text='test message 1')
    session.add(message)

    # Commit to the database
    session.commit()

    return


def get_categories(session):
    """Get a list of category objects sorted by category name"""
    return (
        session.query(
            Category.category_name,
            func.count(Category.category_name).label("total_categories")
            )
        .order_by(Category.category_name).all()
        )


def get_prayers(session):
    """Get a list of prayer objects sorted by create_date"""
    return (
        session.query(
            Prayer.prayer_text,
            func.count(Prayer.prayer_text).label("total_prayers")
            )
        .order_by(Prayer.create_date).all()
        )


def get_messages(session):
    """Get a list of message objects sorted by primary keys"""
    return (
        session.query(
            Message.message_text,
            func.count(Message.message_text).label("total_messages")
            )
        .order_by(Message.message_id, Message.component, Message.pgraph)
        .all()
        )


if __name__ == '__main__':
    test_app()
