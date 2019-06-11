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
            return group.group_name
        return None

    """
    Schedule
    """

    def update_schedule(self, user, group):
        schedule = Schedule.query.filter_by(date="01/01/1999", group_name=group).first()
        if schedule is not None:
            for object in range(len(schedule.objects)):
                db.session.delete(schedule.objects[object])
            # TODO дописать, что делать когда база очистилась
        else:
            pass
            # TODO дописать, что делать если в базе нет расписания
        db.session.commit()


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
    time = db.Column(db.String(64))
    schedule = db.relationship("Schedule", backref="objects")
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id', ondelete='CASCADE'))
