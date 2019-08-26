import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from config import Config

engine = sqlalchemy.create_engine(Config.SQLALCHEMY_DATABASE_URI, connect_args={'check_same_thread': False})
db = declarative_base()
session = scoped_session(sessionmaker(bind=engine))

from app import models
from app.workers import *

# db.metadata.drop_all()
db.metadata.create_all(engine)
