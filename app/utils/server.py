import requests
import datetime
from urllib.parse import quote

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


def date_name(date: datetime) -> str:
    """
    Определяет день недели по дате

    :param date:
    :return:
    """

    return ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][date.weekday()]


def get_group(group_name: str) -> Data:
    """
    Запрашивает группу у сервера

    :param group_name:
    :return: id группы в Data
    """
    try:
        request = requests.get(f"http://ruz.fa.ru/api/search?term={quote(group_name)}&type=group", timeout=2)
    except requests.exceptions.ReadTimeout:
        return Data.error('Timeout error')
    found_group = request.json()[0]
    if found_group['label'].strip().upper() == group_name:
        return Data(found_group['id'])
    else:
        return Data.error('Not found')


def get_schedule(id: str, date_start: datetime = None, date_end: datetime = None, type: str = 'group') -> Data:
    """
    Запрашивает расписание у сервера

    :param id:
    :param date_start:
    :param date_end:
    :param type: 'group' 'lecturer'
    :return: {'dd.mm.yyyy': {'time_start': , 'time_end': , 'name': , 'type': , 'groups': , 'audience': , 'location': ,
                             'teachers_name': }}
    """
    if not date_start:
        date_start = datetime.datetime.today()
    if not date_end:
        date_end = datetime.datetime.today() + datetime.timedelta(days=1)
    request = requests.get(f"http://ruz.fa.ru/api/schedule/{type}/{id}?start={date_start.strftime('%Y.%m.%d')}&"
                           f"finish={date_end.strftime('%Y.%m.%d')}&lng=1")
    request_json = request.json()
    res = {}
    for i in request_json:
        res.setdefault(datetime.datetime.strptime(i['date'], '%Y.%m.%d').strftime('%d.%m.%Y'), []).append(
            dict(time_start=i['beginLesson'], time_end=i['endLesson'], name=i['discipline'], type=i['kindOfWork'],
                 groups=i['stream'], audience=i['auditorium'], location=i['building'], teachers_name=i['lecturer']
                 )
        )
    return Data(res)


def get_teacher(teacher_name: str) -> list or None:
    """
    Поиск преподователя

    :param teacher_name:
    :return: [(id, name), ...]
    """
    try:
        request = requests.get(f"http://ruz.fa.ru/api/search?term={quote(teacher_name)}&type=lecturer", timeout=2)
    except requests.exceptions.ReadTimeout:
        return Data.error('Timeout error')
    teachers = [(i['id'], i['label']) for i in request.json() if i['id']]
    return Data(teachers)


def format_schedule(user, start_day: int = 0, days: int = 1, teacher: dict = None, date: datetime = None,
                    text: str = "") -> str or None:
    """
    Форматирует расписание к виду который отправляет бот

    :param text: начальная строка, к которой прибавляется расписание
    :param start_day: начальная дата в количестве дней от сейчас
    :param days: количество дней
    :param date: дата для расписания на любой один день
    :param teacher: id преподователя
    :param user:
    :return: строку расписания
    """
    if date is None:
        date_start = datetime.datetime.now() + datetime.timedelta(days=start_day)
        date_end = date_start + datetime.timedelta(days=days)
    else:
        date_start = date
        date_end = date
    if teacher is not None:
        schedule = get_schedule(teacher['id'], date_start, date_end,
                                type='lecturer' if teacher['type'] == 'teacher' else 'group')
    else:
        schedule = get_schedule(user.current_id, date_start, date_end)
        if schedule in ('Connection error', 'Server error', 'Not found', 'Refreshes', 'Error'):
            return schedule
    if schedule is None:
        return None
    else:
        schedule = schedule.data
    if date is None:
        date = datetime.datetime.today()
        date += datetime.timedelta(days=start_day)
    for _ in range(days):
        text_date = date.strftime('%d.%m.%Y')
        text += f"📅 {date_name(date)}, {text_date}\n"
        if text_date in schedule:
            for lesson in sorted(schedule[text_date], key=lambda x: x['time_start']):
                text += f"\n⏱{lesson['time_start']} – {lesson['time_end']}⏱\n"
                text += f"{lesson['name']}\n"
                if lesson['type']:
                    text += f"{lesson['type']}\n"
                if (teacher is not None or user.show_groups) and lesson['groups']:
                    if len(lesson['groups'].split(', ')) > 1:
                        text += "Группы: "
                    else:
                        text += "Группа: "
                    text += f"{lesson['groups']}\n"
                if teacher is not None:
                    if lesson['audience']:
                        text += f"Кабинет: {lesson['audience']}, "
                    text += f"{lesson['location']}"
                if user.current_name is not None and teacher is None:
                    if lesson['audience']:
                        text += f"Где: {lesson['audience']}"
                    if user.show_location is True and lesson['location'] is not None:
                        text += f", {lesson['location']}\n"
                    else:
                        text += "\n"
                    if "teachers_name" in lesson:
                        text += f"Кто: {lesson['teachers_name']}"
                text += "\n"
        else:
            text += f"Нет пар\n"
        text += "\n"
        date += datetime.timedelta(days=1)
    return text
