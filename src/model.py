# code modeled after: 
# https://realpython.com/python-sqlite-sqlalchemy/#using-sqlite-to-persist-data # noqa
#
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

# This references the database file but I don't think we need it for the model
# engine = create_engine('sqlite:///db/mp.db')

Base = declarative_base()

class Prayer(Base):
    __tablename__ = 'prayer'
    prayer_id = Column(Integer, primary_key=True)
    prayer_text = Column(String)
    create_date = Column(String)
    answer_text = Column(String)
    answer_date = Column(String)
    display_count = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.category_id'))

class Category(Base):
    __tablename__ = 'category'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String)
    prayers = relationship('Prayer', backref=backref('prayer'))

class Message(Base):
    __tablename__ = 'message'
    message_id = Column(String, primary_key=True)
    component = Column(Integer, primary_key=True)
    pgraph = Column(Integer, primary_key=True)
    header = Column(String)
    verse = Column(String)
    message_text = Column(String)

class Parameters(Base):
    __tablename__='parameters'
    parm_id = Column(Integer, primary_key=True)
    actor_name = Column(String)
    first_date = Column(String)
    last_date = Column(String)
    access_count = Column(Integer)

