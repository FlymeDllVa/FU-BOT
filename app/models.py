import logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, Boolean, create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from _mysql_connector import MySQLInterfaceError

from app.utils.constants import CHANGES
from config import Config

metadata = MetaData()

db = declarative_base(metadata=metadata)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, **Config.SQLALCHEMY_SETTINGS, connect_args=Config.DB_SETTINGS)
session = scoped_session(sessionmaker(bind=engine))

log = logging.getLogger(__name__)


# db.metadata.drop_all(engine)
# db.metadata.create_all(engine)


class User(db):
    __tablename__ = "vk_users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    role = Column(String(256), default=None)
    update = Column(String(256), default="1.0")
    current_name = Column(String(256), default=None)
    current_id = Column(Integer, default=None)
    schedule_day_date = Column(String(256), default=None)
    found_id = Column(Integer, default=None)
    found_name = Column(String(256), default=None)
    found_type = Column(String(256), default=None)
    subscription_time = Column(String(256), default=None)
    subscription_days = Column(String(256), default=None)
    subscription_group = Column(String(256), default=None)
    show_location = Column(Boolean, default=False)
    show_groups = Column(Boolean, default=False)

    @classmethod
    def filter_by_time(cls, time: str) -> list:
        """
        Ищет всех пользователей с временем подписки time

        :param time:
        :return:
        """

        try:
            res = session.query(cls).filter_by(subscription_time=time).all()
            return res
        except MySQLInterfaceError as e:
            log.warning('Error in subscription %r', e)
            return []

    @classmethod
    def search_user(cls, id: int) -> 'User':
        """
        Ищет пользователя в базе по id

        :param id:
        :return:
        """

        user = session.query(cls).filter_by(id=id).first()
        if user:
            return user
        user = cls(id=id)
        session.add(user)
        session.commit()
        return user

    @classmethod
    def update_user(cls, user: 'User', **data) -> 'User':
        """
        Обновляет поля пользователя поданные как kwargs

        :param user:
        :param data:
        :return:
        """

        for key, value in data['data'].items():
            if hasattr(user, key):
                setattr(user, key, value)
        session.commit()
        return user

    def cancel_changes(self):
        if self.current_name == CHANGES:
            self.current_name = None
        elif self.found_name == CHANGES and self.found_id == 0:
            self.found_name = None
            self.found_type = None
        elif self.subscription_days == CHANGES:
            self.subscription_days = None
        elif self.schedule_day_date == CHANGES:
            self.schedule_day_date = None
        session.commit()
