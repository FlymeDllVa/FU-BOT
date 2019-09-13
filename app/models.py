from app import db, session
from sqlalchemy import Integer, String, Column, Boolean


class User(db):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    role = Column(String, default=None)
    update = Column(String, default="1.0")
    current_name = Column(String, default=None)
    current_id = Column(Integer, default=None)
    schedule_day_date = Column(String, default=None)
    found_id = Column(Integer, default=None)
    found_name = Column(String, default=None)
    found_type = Column(String, default=None)
    subscription_time = Column(String, default=None)
    subscription_days = Column(String, default=None)
    subscription_group = Column(String, default=None)
    show_location = Column(Boolean, default=False)
    show_groups = Column(Boolean, default=False)

    @classmethod
    def filter_by_time(cls, time):
        """
        Ищет всех пользователей с временем подписки time

        :param time:
        :return:
        """

        return session.query(cls).filter_by(subscription_time=time).all()

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
        if self.current_name == "CHANGES":
            self.current_name = None
        elif self.found_name == "CHANGES" and self.found_id == 0:
            self.found_name = None
            self.found_type = None
        elif self.subscription_days == "CHANGES":
            self.subscription_days = None
        elif self.schedule_day_date == "CHANGES":
            self.schedule_day_date = None
        session.commit()
