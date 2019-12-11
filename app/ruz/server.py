import logging
import datetime
from urllib.parse import quote

from marshmallow import ValidationError
import requests

from app.ruz.schemas import ScheduleSchema
from app.ruz.cache import timed_cache

SCHEDULE_SCHEMA = ScheduleSchema()

log = logging.getLogger(__name__)


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


@timed_cache(minutes=180)
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
    found_group = request.json()
    if found_group and found_group[0]['label'].strip().upper() == group_name:
        return Data(found_group[0]['id'])
    else:
        return Data.error('Not found')


@timed_cache(minutes=2)
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
    url = f"http://ruz.fa.ru/api/schedule/{type}/{id}?start={date_start.strftime('%Y.%m.%d')}" \
          f"&finish={date_end.strftime('%Y.%m.%d')}&lng=1"
    try:
        request = requests.get(url)
    except TimeoutError:
        return Data.error('Timeout error')
    request_json = request.json()
    try:
        res = SCHEDULE_SCHEMA.load({'pairs': request_json})
        return Data(res)
    except ValidationError as e:
        log.warning('Validation error in get_schedule for %s %s - %r', type, id, e)
        return Data.error('validation error')


@timed_cache(minutes=180)
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


def format_schedule(user, start_day: int = 0, days: int = 1, search: dict = None, date: datetime = None,
                    text: str = "") -> str or None:
    """
    Форматирует расписание к виду который отправляет бот

    :param text: начальная строка, к которой прибавляется расписание
    :param start_day: начальная дата в количестве дней от сейчас
    :param days: количество дней
    :param date: дата для расписания на любой один день
    :param search: запрос для поиска
    :param user:
    :return: строку расписания
    """
    if date is None:
        date_start = datetime.datetime.now() + datetime.timedelta(days=start_day)
        date_end = date_start + datetime.timedelta(days=days)
    else:
        date_start = date
        date_end = date
    if search is not None:
        schedule = get_schedule(search['id'], date_start, date_end,
                                type='lecturer' if search['type'] == 'teacher' else 'group')
    else:
        schedule = get_schedule(user.current_id, date_start, date_end,
                                type='lecturer' if user.role == 'teacher' else 'group')
    if schedule.has_error:
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
            selected_days = set()
            for lesson in sorted(schedule[text_date], key=lambda x: x['time_start']):
                if lesson['time_start'] in selected_days:
                    text += "\n"
                else:
                    text += f"\n⏱{lesson['time_start']} – {lesson['time_end']}⏱\n"
                    selected_days.add(lesson['time_start'])
                text += f"{lesson['name']}\n"
                if lesson['type']:
                    text += f"{lesson['type']}\n"
                if (search is not None or user.show_groups) and lesson['groups']:
                    if lesson['groups']:
                        text += "Группы: "
                        text += f"{', '.join(lesson['groups'])}\n"
                if search is not None:
                    if lesson['audience']:
                        text += f"Кабинет: {lesson['audience']}, "
                    text += f"{lesson['location']}"
                if user.current_name is not None and search is None:
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
