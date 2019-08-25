import requests
import json
import datetime

from config import *


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


def get_schedule(group_name: str) -> dict or None:
    """
    Запрашивает расписание у сервера

    :param group_name:
    :return:
    """

    session = requests.session()
    request = session.post(f"{SERVER_URL}api/v1/schedule/group", json={"group_name": group_name}, timeout=2)
    if not request.status_code == 200:
        return None
    return request.json()


def format_schedule(group_name: str, start_day: int = 0, days: int = 1) -> str or None:
    """
    Форматирует расписание к виду который отправляет бот

    :param start_day:
    :param group_name:
    :param days:
    :return:
    """

    schedule = get_schedule(group_name)
    if schedule is None:
        return None

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
                if lesson['audience']:
                    text += f"Где: {lesson['audience']}\n"
                teachers = format_name(lesson['teachers'])
                if teachers:
                    text += f"Кто: {teachers}"
                text += "\n"
        else:
            text += f"Нет пар\n"
        text += "\n"
        date += datetime.timedelta(days=1)
    return text

