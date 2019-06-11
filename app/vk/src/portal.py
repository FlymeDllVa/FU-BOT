import requests
import datetime

from lxml import html
from config import Config

def authorization(login, password, max_attempt=1, attempt=0):
    """
	Производит авторизацию на портале для дальнейших запросов
	:param login: Логин от ИОПа
	:param password: Пароль от ИОПа
    :max_attempt: Макмальное количество попыток авторизации
    :attempt: Счетчик попыток авторизации
	:return: Сессия с куки или None
	"""
    if attempt >= max_attempt: return None
    try:
        session = requests.session()
        session.post('https://portal.fa.ru/CoreAccount/LogOn', data={'Login': login, 'Pwd': password})
        return session
    except Exception:
        attempt+=1
        print(f"Ошибка авторизации на ИОП ${attempt}")
        authorization(login, password, attempt=attempt)

def teacher_search(session, teacher_name):
    """
	Ищет преподавателя по сессии
	:param session: Сессия от ИОПа
	:param teacher_name: ФИО преподавателя
	:return: Кортеж из ID преподавателя и ФИО
	"""
    response = session.post('https://portal.fa.ru/CoreUser/SearchDialogResultAjax', data={'Name': teacher_name, 'Roles': 16}).json()
    if not response:
        return None
    else:
        return response[0]['id'], response[0]['name']

# def get_schedule(session, group_id):
#     today = (datetime.datetime.today() + datetime.timedelta(hours=0)).strftime('%d/%m/%Y')
#     weekday = (datetime.datetime.today() + datetime.timedelta(hours=0)).weekday()
#     for delta in range(13):
#         day = (datetime.datetime.today() + datetime.timedelta(days=delta - weekday, hours=0)).strftime('%d/%m/%Y')
#         data = parse_schedule(session.post('https://portal.fa.ru/Job/SearchAjax',
#                                                  data={'Date': today, 'DateBegin': day,
#                                                        'DateEnd': day, 'JobType': 'GROUP', 'GroupId': group_id}).text,
#                                     day,
#                                     delta - 7)


def parse_schedule(table, day, w):
    """
    Функция для парсинга html таблицы в удобный для просмотра вид
    :param table: html-таблица
    :param day: datetime.strftime() объект для отображения даты
    :param w: День недели от 0 до 6
    :return: Строку, удобную для чтения
    """
    response = []
    table = html.fromstring(table)
    disciplines = table.xpath('//tr[@class="rowDisciplines"]')
    # Если нет пар
    if not disciplines:
        return [None]
    timestamp = table.xpath('//tr[@class="rowDate warning"]/td[@data-field="datetime"]/text()')[0].split()

    # 📅
    day_name = timestamp[1][1:-1]
    date = timestamp[0]
    for disc in disciplines:
        time_block = disc.xpath('./td[@data-field="datetime"]/div/text()')

        pair_time = f'{time_block[0]} - {time_block[1]}'.strip()
        pair_name = disc.xpath('.//td[@data-field="discipline"]/text()')[0].strip()
        pair_type = (time_block[2] + '\n' if len(time_block) > 2 else '').strip()
        pair_location = ', '.join(
            [i.strip()[:-1].strip() for i in disc.xpath('./td[@data-field="tutors"]/div/div/i/text()') if
             i.strip()[:-1] != '']).strip()
        if pair_location:
            pair_teacher = ', '.join(
                disc.xpath('./td[@data-field="tutors"]/div/button[@type="button"]/text()')).replace(" , ", ", ").strip()
        else:
            pair_location = None
            pair_teacher = None

        response.append(
            {"pair_time": pair_time, "pair_name": pair_name, "pair_type": pair_type, "pair_location": pair_location,
             "pair_teacher": pair_teacher})

    return response