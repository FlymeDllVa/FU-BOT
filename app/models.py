import requests

from app.vk.src.portal import *
from app import db

"""
General Control Model
"""
class Model(object):

    """
    Users
    """
    def check_user(self, user_id):
        """
        Проверяет существование пользователя, если его нет создает
        :param user_id:
        :return user:
        """
        user = Users.query.filter(Users.user_id == str(user_id)).first()
        if user is None:
            user = Users(user_id=user_id, condition_menu=None)
            db.session.add(user)
            db.session.commit()
        return user

    def update_user_group(self, user, user_group):
        """
        Обновляет поле user_group
        :param user_group:
        :return user_group:
        """
        try:
            Users.query.filter_by(user_id=user.user_id).update({'user_group': user_group})
            db.session.commit()
            return user.user_id
        except Exception:
            return None

    def update_group_name(self, user, group_name):
        """
        Обновляет поле user_group
        :param user:
        :param group_name:
        :return:
        """
        if self.check_group(group_name) is not None:
            Users.query.filter_by(user_id=user.user_id).update({'user_group': group_name})
            db.session.commit()
            return group_name
        else:
            Users.query.filter_by(user_id=user.user_id).update({'user_group': None})
            db.session.commit()
            return None

    def update_condition_menu(self, user, condition_menu):
        """
        Обновляет поле condition_menu
        :param user_group:
        :return user_group:
        """
        try:
            Users.query.filter_by(user_id=user.user_id).update({'condition_menu': condition_menu})
            db.session.commit()
            return user.user_id
        except Exception:
            return None

    """
    Groups
    """

    def check_group(self, group_name):
        """
        Проверяет существует ли группа в базе
        :param group_name:
        :return:
        """
        group = Groups.query.filter(Groups.group_name == group_name).first()
        if group is not None:
            return group.group_id
        return None

    """
    Schedule
    """

    def update_schedule(self, user, days_update=13):
        """
        Обновляет расписание в базе данных
        :param user: данные user в базе данных
        :param days_update: на сколько дней вперед обновлять базу
        :return:
        """
        session = authorization(Config.LOGIN, Config.PASSWORD, max_attempt=3)
        if session is None: return None
        user_group_name = user.user_group
        user_group_id = self.check_group(user_group_name)
        today = (datetime.datetime.today() + datetime.timedelta(hours=0)).strftime('%d/%m/%Y')
        weekday = (datetime.datetime.today() + datetime.timedelta(hours=0)).weekday()
        for delta in range(days_update):
            day = (datetime.datetime.today() + datetime.timedelta(days=delta - weekday, hours=0)).strftime('%d/%m/%Y')
            data = parse_schedule(session.post('https://portal.fa.ru/Job/SearchAjax',
                                               data={'Date': today, 'DateBegin': day,
                                                     'DateEnd': day, 'JobType': 'GROUP',
                                                     'GroupId': user_group_id}).text, day, delta - 7)
            schedule = Schedule.query.filter_by(date=day, group_name=user_group_name).first()
            if schedule is not None:
                for object in range(len(schedule.objects)):
                    db.session.delete(schedule.objects[object])
            else:
                schedule = Schedule(date=day, group_name=user_group_name)
            for object in data:
                if object is not None:
                    schedule.objects.append(ScheduleObject(pair_time=object["pair_time"],
                                                           pair_name=object["pair_name"],
                                                           pair_type = object["pair_type"],
                                                           pair_location=object["pair_location"],
                                                           pair_teacher=object["pair_teacher"]))
            db.session.add(schedule)
        db.session.commit()
        return True


"""
DataBase Models
"""
class Users(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.String(64), index=True, unique=True)
    user_group = db.Column(db.String(64))
    condition_menu = db.Column(db.String(128))
    condition_teacher = db.Column(db.String(128))

class Groups(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    group_name = db.Column(db.String(64), index=True, unique=True)
    group_id = db.Column(db.Integer)

class Schedule(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date = db.Column(db.String(64))
    group_name = db.Column(db.String(64), index=True)


class ScheduleObject(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    pair_time = db.Column(db.String(256))
    pair_name = db.Column(db.String(256))
    pair_type = db.Column(db.String(256))
    pair_location = db.Column(db.String(256))
    pair_teacher = db.Column(db.String(256))

    schedule = db.relationship("Schedule", backref="objects")
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id', ondelete='CASCADE'))
