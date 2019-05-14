import config
import datetime
import requests
import traceback
from lxml import html

def auth(login, password):
	"""
	Производит авторизацию на портале для дальнейших запросов
	:param login: Логин от ИОПа
	:param password: Пароль от ИОПа
	:return: Сессия с куки
	"""
	try:
		session = requests.session()
		session.post('https://portal.fa.ru/CoreAccount/LogOn', data={'Login': login, 'Pwd': password})
		return session
	except Exception as error:
		print(error)
		return auth(login, password)

### Find Teacher
def find_teacher(session, name):
	"""
	Ищет преподавателя по сессии
	:param session: Сессия от ИОПа
	:param name: ФИО преподавателя
	:return: Кортеж из ID преподавателя и ФИО
	"""
	response = session.post('https://portal.fa.ru/CoreUser/SearchDialogResultAjax',
						data={'Name': name, 'Roles': 16})
	response = response.json()
	if not response:
		return None
	else:
		return response[0]['id'], response[0]['name']

def parse_schedule_prepod(table, day, w):
	print(table)
	"""
	Функция для парсинга html таблицы в удобный для просмотра вид
	:param table: html-таблица
	:param day: datetime.strftime() объект для отображения даты
	:param w: День недели от 0 до 6
	:return: Строку, удобную для чтения
	"""
	response = ''
	table = html.fromstring(table)
	disciplines = table.xpath('//tr[@class="rowDisciplines"]')
	if not disciplines:
		return f'\n📅 {config.WEEKDAY[w]}, {day}\nНет пар\n'
	# date_block
	timestamp = table.xpath('//tr[@class="rowDate warning"]/td[@data-field="datetime"]/text()')[0].split()
	response += f'\n📅 {timestamp[1][1:-1]}, {timestamp[0]}\n\n'
	for disc in disciplines:
		# time_block
		time_block = disc.xpath('./td[@data-field="datetime"]/div/text()')
		response += '⏱{} - {}⏱\n'.format(*time_block[:2]) # TIME
		# discipline_block
		response += '{}\n'.format(disc.xpath('.//td[@data-field="discipline"]/text()')[0].strip())
		# type_block
		response += time_block[2] + '\n' if len(time_block) > 2 else ''
		# group_block
		response += 'Группа: ' + ','.join(disc.xpath('./td[@data-field="groups"]/span/text()')).strip() + '\n'
		# where_block
		response += 'Кабинет: ' + disc.xpath('./td[@data-field="tutors"]/div/div/i/text()')[0].strip()[:-1] + \
			   '\n' + disc.xpath('./td[@data-field="tutors"]/div/div/i/small/text()')[0].strip() + '\n\n'
	return response

def get_schedule_prepod(session, command, prepod):
	today = (datetime.datetime.today() + datetime.timedelta(hours=3)).strftime('%d/%m/%Y')
	if prepod is None:
		return
	if command.lower() == 'сегодня':
		return parse_schedule_prepod(session.post('https://portal.fa.ru/Job/SearchAjax',
																			 data={'Date': today, 'DateBegin': today, 'DateEnd': today,
																						 'JobType': 'TUTOR',
																						 'TutorId': prepod[0], 'Tutor': prepod[1]}).text, today,
													(datetime.datetime.today() + datetime.timedelta(hours=3)).weekday())
	elif command.lower() == 'завтра':
		tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1, hours=3)).strftime('%d/%m/%Y')
		return (parse_schedule_prepod(session.post('https://portal.fa.ru/Job/SearchAjax',
																				data={'Date': today, 'DateBegin': tomorrow, 'DateEnd': tomorrow,
																							'JobType': 'TUTOR',
																							'TutorId': prepod[0], 'Tutor': prepod[1]}).text, tomorrow,
												 (datetime.datetime.today() + datetime.timedelta(days=1, hours=3)).weekday()))
	elif command.lower() == 'эта неделя':
		weekday = (datetime.datetime.today() + datetime.timedelta(hours=3)).weekday()
		response = ''
		for delta in range(6):
				day = (datetime.datetime.today() + datetime.timedelta(days=delta - weekday, hours=3)).strftime(
						'%d/%m/%Y')
				response += (parse_schedule_prepod(session.post('https://portal.fa.ru/Job/SearchAjax',
																						data={'Date': today, 'DateBegin': day, 'DateEnd': day,
																									'JobType': 'TUTOR',
																									'TutorId': prepod[0], 'Tutor': prepod[1]}).text, day, delta))
		return response
	elif command.lower() == 'следующая неделя':
		weekday = (datetime.datetime.today() + datetime.timedelta(hours=3)).weekday()
		response = ''
		for delta in range(7, 13):
				day = (datetime.datetime.today() + datetime.timedelta(days=delta - weekday, hours=3)).strftime('%d/%m/%Y')
				response += (parse_schedule_prepod(session.post('https://portal.fa.ru/Job/SearchAjax',
																						data={'Date': today, 'DateBegin': day, 'DateEnd': day,
																									'JobType': 'TUTOR',
																									'TutorId': prepod[0], 'Tutor': prepod[1]}).text, day,
															 delta - 7))
	return response

def parse_schedule(table, day, w):
	"""
	Функция для парсинга html таблицы в удобный для просмотра вид
	:param table: html-таблица
	:param day: datetime.strftime() объект для отображения даты
	:param w: День недели от 0 до 6
	:return: Строку, удобную для чтения
	"""
	response = ''
	table = html.fromstring(table)
	disciplines = table.xpath('//tr[@class="rowDisciplines"]')
	if not disciplines:
		return f'\n📅 {config.WEEKDAY[w]}, {day}\nНет пар\n'
	# date_block
	timestamp = table.xpath('//tr[@class="rowDate warning"]/td[@data-field="datetime"]/text()')[0].split()
	response += f'\n📅 {timestamp[1][1:-1]}, {timestamp[0]}\n\n'
	for disc in disciplines:
		# time_block
		time_block = disc.xpath('./td[@data-field="datetime"]/div/text()')
		response += '⏱{} - {}⏱\n'.format(*time_block[:2]) # TIME
		# discipline_block
		response += '{}\n'.format(disc.xpath('.//td[@data-field="discipline"]/text()')[0].strip())
		# type_block
		response += time_block[2] + '\n' if len(time_block) > 2 else ''
		# where_block
		prepod = ', '.join([i.strip()[:-1].strip() for i in disc.xpath('./td[@data-field="tutors"]/div/div/i/text()') if i.strip()[:-1] != ''])
		if prepod:
			response += 'Где: ' +  prepod + "\n"
			# group_block
			response += 'Кто: ' + ', '.join(disc.xpath('./td[@data-field="tutors"]/div/button[@type="button"]/text()')).replace(" , ", ", ") + '\n\n'
		
	return response

def get_schedule(session, command, groupID):
	today = (datetime.datetime.today() + datetime.timedelta(hours=3)).strftime('%d/%m/%Y')
	if groupID is None:
		return
	if command.lower() == 'сегодня':
		return parse_schedule(session.post('https://portal.fa.ru/Job/SearchAjax',
																			 data={'Date': today, 'DateBegin': today,
																			  'DateEnd': today, 'JobType': 'GROUP', 'GroupId': groupID}).text, today,
													(datetime.datetime.today() + datetime.timedelta(hours=3)).weekday())
	elif command.lower() == 'завтра':
		tomorrow = (datetime.datetime.today() + datetime.timedelta(days=1, hours=3)).strftime('%d/%m/%Y')
		return (parse_schedule(session.post('https://portal.fa.ru/Job/SearchAjax',
																				data={'Date': today, 'DateBegin': tomorrow,
																				 'DateEnd': tomorrow, 'JobType': 'GROUP', 'GroupId': groupID}).text, tomorrow,
												 (datetime.datetime.today() + datetime.timedelta(days=1, hours=3)).weekday()))
	elif command.lower() == 'эта неделя':
		weekday = (datetime.datetime.today() + datetime.timedelta(hours=3)).weekday()
		response = ''
		for delta in range(6):
				day = (datetime.datetime.today() + datetime.timedelta(days=delta - weekday, hours=3)).strftime(
						'%d/%m/%Y')
				response += (parse_schedule(session.post('https://portal.fa.ru/Job/SearchAjax',
																						data={'Date': today, 'DateBegin': day,
																						 'DateEnd': day, 'JobType': 'GROUP', 'GroupId': groupID}).text, day, delta))
		return response
	elif command.lower() == 'следующая неделя':
		weekday = (datetime.datetime.today() + datetime.timedelta(hours=3)).weekday()
		response = ''
		for delta in range(7, 13):
				day = (datetime.datetime.today() + datetime.timedelta(days=delta - weekday, hours=3)).strftime('%d/%m/%Y')
				response += (parse_schedule(session.post('https://portal.fa.ru/Job/SearchAjax',
																						data={'Date': today, 'DateBegin': day,
																						 'DateEnd': day, 'JobType': 'GROUP', 'GroupId': groupID}).text, day,
															 delta - 7))
	return response






