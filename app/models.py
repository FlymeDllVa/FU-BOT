from app import db, session
from sqlalchemy import Integer, String, Column


class User(db):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    update = Column(String, default="1.0")
    position = Column(String, default="START")
    group_name = Column(String, default=None)
    found_teacher_id = Column(Integer, default=None)
    found_teacher_name = Column(String, default=None)
    subscription_time = Column(String, default=None)
    subscription_days = Column(String, default=None)
    subscription_group = Column(String, default=None)

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
    def change_position(cls, user: 'User', position: str) -> 'User':
        """
        Изменяет расположения человека в меню в базе

        :param user:
        :param position:
        :return:
        """

        user.position = position
        session.commit()
        return user

    @classmethod
    def change_group_name(cls, user: 'User', group_name: str) -> 'User':
        """
        Изменяет название группы человека в базе

        :param user:
        :param group_name:
        :return:
        """

        user.group_name = group_name
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
