from asyncio import TimeoutError
import datetime
import logging
from urllib.parse import quote

from marshmallow import ValidationError
from aiohttp import ClientSession, ClientError
from ujson import loads

from app.ruz.schemas import ScheduleSchema

# from app.ruz.cache import timed_cache

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
    def error(cls, error: str) -> "Data":
        return cls(data={}, has_error=True, error=error)


def date_name(date: datetime) -> str:
    """
    Определяет день недели по дате

    :param date:
    :return:
    """

    return [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ][date.weekday()]


# @timed_cache(minutes=180)
async def get_group(group_name: str) -> Data:
    """
    Запрашивает группу у сервера

    :param group_name:
    :return: id группы в Data
    """
    try:
        async with ClientSession() as client:
            request = await client.get(
                f"https://ruz.fa.ru/api/search?term={quote(group_name)}&type=group",
                timeout=2,
            )
            found_group = await request.json(loads=loads)
    except (ClientError, TimeoutError, ValueError):
        return Data.error("Timeout error")
    if found_group and found_group[0]["label"].strip().upper() == group_name:
        return Data(found_group[0]["id"])
    else:
        return Data.error("Not found")


# @timed_cache(minutes=2)
async def get_schedule(
    id: int, date_start: datetime = None, date_end: datetime = None, type: str = "group"
) -> Data:
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
    url = (
        f"https://ruz.fa.ru/api/schedule/{type}/{id}?start={date_start.strftime('%Y.%m.%d')}"
        f"&finish={date_end.strftime('%Y.%m.%d')}&lng=1"
    )
    try:
        async with ClientSession() as client:
            request = await client.get(url)
            request_json = await request.json(loads=loads)
    except (ClientError, TimeoutError, ValueError):
        return Data.error("Timeout error")
    try:
        res = SCHEDULE_SCHEMA.load({"pairs": request_json})
        return Data(res)
    except ValidationError as e:
        log.warning("Validation error in get_schedule for %s %s - %r", type, id, e)
        return Data.error("validation error")


# @timed_cache(minutes=180)
async def get_teacher(teacher_name: str) -> list or None:
    """
    Поиск преподователя

    :param teacher_name:
    :return: [(id, name), ...]
    """
    try:
        async with ClientSession() as client:
            request = await client.get(
                f"https://ruz.fa.ru/api/search?term={quote(teacher_name)}&type=person",
                timeout=2,
            )
            request_json = await request.json(loads=loads)
    except (ClientError, TimeoutError, ValueError):
        return Data.error("Timeout error")
    teachers = [(i["id"], i["label"]) for i in request_json if i["id"]]
    return Data(teachers)


async def default_link_formatter(link): return link


async def format_schedule(
    id: int,
    type: str,
    start_day: int = 0,
    days: int = 1,
    show_groups: bool = False,
    show_location: bool = False,
    text: str = "",
    link_formatter: callable = default_link_formatter
) -> str or None:
    """
    Форматирует расписание к виду который отправляет бот

    :param show_location:
    :param show_groups:
    :param id:
    :param type:
    :param text: начальная строка, к которой прибавляется расписание
    :param start_day: начальная дата в количестве дней от сейчас
    :param days: количество дней
    :param link_formatter: функция для обработки строк с сылками
    :return: строку расписания
    """
    date_start = datetime.datetime.now() + datetime.timedelta(days=start_day)
    date_end = date_start + datetime.timedelta(days=days)
    schedule = await get_schedule(
        id, date_start, date_end, type="person" if type == "teacher" else "group"
    )
    if schedule.has_error:
        return None
    else:
        schedule = schedule.data
    date = datetime.datetime.today()
    date += datetime.timedelta(days=start_day)
    for _ in range(days):
        text_date = date.strftime("%d.%m.%Y")
        text += f"📅 {date_name(date)}, {text_date}\n"
        if text_date in schedule:
            selected_days = set()
            for lesson in sorted(schedule[text_date], key=lambda x: x["time_start"]):
                if lesson["time_start"] in selected_days:
                    text += "\n"
                else:
                    text += f"\n⏱{lesson['time_start']} – {lesson['time_end']}⏱\n"
                    selected_days.add(lesson["time_start"])
                text += f"{lesson['name']}\n"
                if lesson["type"]:
                    text += f"{lesson['type']}\n"
                if show_groups and lesson["groups"]:
                    if lesson["groups"]:
                        text += "Группы: "
                        text += f"{', '.join(lesson['groups'])}\n"
                if lesson["audience"]:
                    text += f"Где: {lesson['audience']}"
                if show_location and lesson["location"] is not None:
                    text += f", {lesson['location']}\n"
                else:
                    text += "\n"
                text += f"Кто: {lesson['teachers_name']}\n"
                if lesson["note"]:
                    text += f'Примечание: {lesson["note"]}\n'
                if lesson["url1"]:
                    text += lesson['url1_description'] + ": " + await link_formatter(lesson['url1']) + "\n"
                if lesson["url2"]:
                    text += lesson['url2_description'] + ": " + await link_formatter(lesson['url2']) + "\n"
        else:
            text += f"Нет пар\n"
        text += "\n"
        date += datetime.timedelta(days=1)
    return text
