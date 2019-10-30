import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from config import Config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logger_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger_handler = logging.FileHandler(f'{__name__}_logging.log')
logger_handler.setLevel(logging.INFO)
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, **Config.DB_SETTINGS)

db = declarative_base()
session = scoped_session(sessionmaker(bind=engine))

from app import models
from app.workers import *

# db.metadata.drop_all(engine)
db.metadata.create_all(engine)
