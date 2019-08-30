import requests
import json
import datetime

from config import *


class Data:
    """
    Объект данных, полученных с портала
    """

    data: any
    has_error: bool
    error_text: str

    def __init__(self, data: any, has_error: bool = False, error: str = None) -> None:
        self.data = data
        self.has_error = has_error
        self.error_text = error

    @classmethod
    def error(cls, error: str) -> 'Data':
        return cls(data={}, has_error=True, error=error)


def date_name(date: datetime):
    """
    Определяет день недели по дате

    :param date:
    :return:
    """

    return ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][date.weekday()]


def format_name(lesson: list):
    """
    Возравращает форматированную строку имен

    :param lesson:
    :return:
    """
    names = list()
    for teacher in lesson:
        teacher_name = str()
        if "surname" in teacher:
            if teacher["surname"] is not None:
                teacher_name += teacher['surname']
        if "firstname" in teacher:
            if teacher["firstname"] is not None:
                teacher_name += " " + teacher['firstname']
        if "patronymic" in teacher:
            if teacher["patronymic"] is not None:
                teacher_name += " " + teacher['patronymic']
        names.append(teacher_name)
    return ', '.join(names)


def get_group(group_name: str) -> str or dict:
    """
    Запрашивает группу у сервера

    :param group_name:
    :return:
    """

    session = requests.session()
    try:
        request = session.post(f"{SERVER_URL}api/v1/group", json={"group_name": group_name}, timeout=2)
    except requests.exceptions.ReadTimeout:
        return Data.error('Timeout error')
    if request.status_code == 523:
        return Data.error('Connection error')
    elif request.status_code == 500:
        return Data.error('Server error')
    elif request.status_code == 400:
        return Data.error('Not found')
    elif not request.status_code == 200:
        return Data.error('Error')
    request_json = request.json()
    if "group_update" in request_json:
        return Data(request_json)
    else:
        return Data.error('Connection error')


def get_schedule(group_name: str, date: datetime = None) -> dict or None:
    """
    Запрашивает расписание у сервера

    :param date:
    :param group_name:
    :return:
    """
    session = requests.session()
    if date is None:
        json_obj = {"group_name": group_name}
    elif date:
        json_obj = {"group_name": group_name, "date": date.strftime('%d.%m.%Y')}
    else:
        return None
    try:
        request = session.post(f"{SERVER_URL}api/v1/schedule/group", json=json_obj, timeout=5)
    except requests.exceptions.ReadTimeout:
        return None
    if not request.status_code == 200:
        return None
    return request.json()


def get_teacher_schedule(teacher: dict):
    """
    Запрашивает расписание преподавателя у сервера

    :param teacher:
    :return:
    """

    session = requests.session()
    try:
        request = session.post(f"{SERVER_URL}api/v1/schedule/teacher",
                               json={"id": teacher['id'], "name": teacher['name']}, timeout=10)
    except requests.exceptions.ReadTimeout:
        return None
    if not request.status_code == 200:
        return None
    return request.json()


def get_teacher(teacher_name: str) -> dict or None:
    """
    Запрашивает расписание у сервера

    :param teacher_name:
    :return:
    """

    session = requests.session()
    try:
        request = session.post(f"{SERVER_URL}api/v1/teacher", json={"name": teacher_name}, timeout=5)
    except requests.exceptions.ReadTimeout:
        return "timeout"
    if not request.status_code == 200:
        return None
    request = request.json()
    if request is not None:
        if len(request) > 0:
            return request
    return None


def format_schedule(user, start_day: int = 0, days: int = 1, teacher: dict = None, date: str = None) -> str or None:
    """
    Форматирует расписание к виду который отправляет бот

    :param date:
    :param teacher:
    :param start_day:
    :param user:
    :param days:
    :return:
    """

    if teacher is not None:
        schedule = get_teacher_schedule(teacher)
    elif date is not None:
        schedule = get_schedule(user.group_name, date)
    else:
        schedule = get_schedule(user.group_name)
        if schedule is not None:
            if schedule["has_error"] is False:
                schedule = schedule["data"]
            else:
                if schedule["error"] == "Update schedule":
                    return schedule["error"]
                else:
                    return "error"
    if schedule is None:
        return None
    if date is None:
        date = datetime.datetime.today()
        date += datetime.timedelta(days=start_day)
    text = str()
    for _ in range(days):
        text_date = date.strftime('%d.%m.%Y')
        text += f"📅 {date_name(date)}, {text_date}\n"
        if text_date in schedule:
            for lesson in schedule[text_date]:
                text += f"\n⏱{lesson['time_start']} – {lesson['time_end']}⏱\n"
                text += f"{lesson['name']}\n"
                if lesson['type']:
                    text += f"{lesson['type']}\n"
                if teacher is not None or user.show_groups is True:
                    if len(lesson['groups'].split(', ')) > 1:
                        text += "Группы: "
                    else:
                        text += "Группы: "
                    text += f"{lesson['groups']}\n"
                if teacher is not None:
                    if lesson['audience']:
                        text += f"Кабинет: {lesson['audience']}, "
                    text += f"{lesson['location']}"
                if user.group_name is not None and teacher is None:
                    if lesson['audience']:
                        text += f"Где: {lesson['audience']}"
                    if user.show_location is True and lesson['location'] is not None:
                        text += f", {lesson['location']}\n"
                    else:
                        text += "\n"
                    teachers = format_name(lesson['teachers'])
                    if teachers:
                        text += f"Кто: {teachers}"
                text += "\n"
        else:
            text += f"Нет пар\n"
        text += "\n"
        date += datetime.timedelta(days=1)
    return text
