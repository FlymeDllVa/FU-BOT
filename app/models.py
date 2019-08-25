from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    update = db.Column(db.String, default="1.0")
    position = db.Column(db.String, default="START")
    group_name = db.Column(db.String, default=None)
    subscription_time = db.Column(db.String, default=None)
    subscription_days = db.Column(db.String, default=None)
    subscription_group = db.Column(db.String, default=None)

    @classmethod
    def filter_by_time(cls, time):
        """
        Ищет всех пользователей с временем подписки time

        :param time:
        :return:
        """

        return cls.query.filter_by(subscription_time=time).all()

    @classmethod
    def search_user(cls, id):
        """
        Ищет пользователя в базе по id

        :param id:
        :return:
        """

        user = cls.query.filter_by(id=id).first()
        if user:
            return user
        user = cls(id=id)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def change_position(cls, user, position):
        """
        Изменяет расположения человека в меню в базе

        :param user:
        :param position:
        :return:
        """

        user.position = position
        db.session.commit()
        return user

    @classmethod
    def change_group_name(cls, user, group_name):
        """
        Изменяет название группы человека в базе

        :param user:
        :param group_name:
        :return:
        """

        user.group_name = group_name
        db.session.commit()
        return user

    @classmethod
    def update_user(cls, user, **data):
        """
        Обновляет поля пользователя поданные как kwargs

        :param user:
        :param data:
        :return:
        """

        for key, value in data['data'].items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return user

