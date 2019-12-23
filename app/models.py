import logging

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, Boolean, MetaData, case

from app.utils.constants import CHANGES

metadata = MetaData()
db = declarative_base(metadata=metadata)

log = logging.getLogger(__name__)


class User(db):
    __tablename__ = "vk_users"
    __table__: sa.sql.schema.Table

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
    def filter_by_time(cls, time: str) -> sa.sql:
        """
        Ищет всех пользователей с временем подписки time

        :param time:
        :return:
        """
        return sa.select([
            cls.id,
            cls.current_id,
            cls.role
        ]).where(cls.subscription_time == time)

    @classmethod
    def search_user(cls, id: int) -> sa.sql:
        """
        Ищет пользователя в базе по id

        :param id:
        :return:
        """
        return sa.select(['*']).select_from(cls.__table__).where(cls.id == id)

    @classmethod
    def add_user(cls, id: int) -> sa.sql:
        return cls.__table__.insert().values([
            dict(id=id)
        ])

    @classmethod
    def update_user(cls, id: int, **data) -> sa.sql:
        """
        Обновляет поля пользователя поданные как kwargs

        :param user:
        :param data:
        :return:
        """
        return cls.__table__.update().values(**data).where(cls.id == id)

    @classmethod
    def cancel_changes(cls, id: int):
        return cls.__table__.update().values(
            case(
                [
                    (cls.current_name == CHANGES, None),
                    (cls.found_name == CHANGES, None),
                    (cls.subscription_days == CHANGES, None),
                    (cls.schedule_day_date == CHANGES, None),
                ]
            )).where(cls.id == id)


class DBResultProxy:
    _table: tuple
    _fields: dict

    def __init__(self, result):
        self._fields = {k: result.get(k, None) for k in self._table}

    def __getattr__(self, item):
        return self._fields[item]


class UserProxy(DBResultProxy):
    _table = tuple([i.name for i in User.__table__.columns])
