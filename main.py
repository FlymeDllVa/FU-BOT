import config
import vk_api
import time
from portal import auth, find_teacher, parse_schedule_prepod, get_schedule, get_schedule_prepod
from bot import Bot
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


def main(bot):
	print('Бот запустился')
	for event in bot.longpoll.listen():
		if event.type == VkBotEventType.MESSAGE_NEW:
			print(event.obj.peer_id)
			user_id = str(event.obj.peer_id)
			print('Новое сообщение:')
			print('Для меня от: ', end='')
			print(event.obj.peer_id)
			print('Текст:', event.obj.text)
			if bot.check_status_user(user_id) == "MENU":
				if event.obj.text.lower() == "сегодня":
					bot.vk.messages.send (
										peer_id=user_id,
										random_id=get_random_id(),
										message=get_schedule(auth(config.LOGIN, config.PASSWORD), "сегодня", bot.get_groupID(user_id)),
									)		
					bot.message_menu(user_id)
				elif event.obj.text.lower() == "завтра":
					bot.vk.messages.send (
										peer_id=user_id,
										random_id=get_random_id(),
										message=get_schedule(auth(config.LOGIN, config.PASSWORD), "завтра", bot.get_groupID(user_id)),
									)		
					bot.message_menu(user_id)
				elif event.obj.text.lower() == "эта неделя":
					bot.vk.messages.send (
										peer_id=user_id,
										random_id=get_random_id(),
										message=get_schedule(auth(config.LOGIN, config.PASSWORD), "эта неделя", bot.get_groupID(user_id)),
									)		
					bot.message_menu(user_id)
				elif event.obj.text.lower() == "следующая неделя":
					bot.vk.messages.send (
										peer_id=user_id,
										random_id=get_random_id(),
										message=get_schedule(auth(config.LOGIN, config.PASSWORD), "следующая неделя", bot.get_groupID(user_id)),
									)		
					bot.message_menu(user_id)
				elif event.obj.text.lower() == "поиск преподавателя":
					bot.vk.messages.send (
									peer_id=user_id,
									random_id=get_random_id(),
									message='Введите фамилию или ФИО преподавателя',
								)
					bot.change_status_user(user_id, "FIND_PREPOD")
				elif event.obj.text.lower() == "мероприятия":
					bot.vk.messages.send (
									peer_id=user_id,
									random_id=get_random_id(),
									message='Подробнее о грядущих мероприятих можно узнать по ссылке https://vk.com/finsst\nТак же вы можете подписаться на нашу рассылку по опредленным категориям\nДля того, что бы это сделать нажмите "Настройки" => "Рассылка"',
								)
					bot.message_menu(user_id)
				elif event.obj.text.lower() == "расписание":
					bot.vk.messages.send (
									peer_id=user_id,
									random_id=get_random_id(),
									message='Введите название вашей группы. Например: "ПИ18-1"',
								)
					bot.change_status_user(user_id, "CHANGE_GROUP")
				elif event.obj.text.lower() == "задать вопрос":
					bot.vk.messages.send (
									peer_id=user_id,
									random_id=get_random_id(),
									message='Добрый день! Напишите ваш вопрос и мы обязательно ответим на него\nДля выхода из чата напиште: "Выход"',
								)
					bot.change_status_user(user_id, "CHAT")
				elif event.obj.text.lower() == "настройки" or event.obj.text.lower() == "настроики":
					bot.change_status_user(user_id, "SETTINGS")
					bot.message_settings(user_id)
				else:
					bot.message_menu(user_id)
			### SETTINGS START
			elif bot.check_status_user(user_id) == "SETTINGS":
				if event.obj.text.lower() == "назад к меню":
					bot.change_status_user(user_id, "MENU")
					bot.message_menu(user_id)
				elif event.obj.text.lower() == "сменить группу" or event.obj.text.lower() == "выбрать группу":
					bot.change_status_user(user_id, "CHANGE_GROUP")
					bot.vk.messages.send (
									peer_id=user_id,
									random_id=get_random_id(),
									message='Введите название вашей группы. Например: "ПИ18-1"',
								)
				else:
					bot.message_settings(user_id)
			### SETTINGS END
			### CHAT START
			elif bot.check_status_user(user_id) == "CHAT":
				if event.obj.text.lower() == "выход" or event.obj.text.lower() == "0":
					bot.change_status_user(user_id, "MENU")
					bot.message_menu(user_id)
			### CHAT END
			### CHANGE_GROUP START
			elif bot.check_status_user(user_id) == "CHANGE_GROUP":
				bot.change_status_user(user_id, "MENU")
				group_name = event.obj.text
				if bot.change_group(user_id, group_name) != None:
					bot.vk.messages.send (
								peer_id=user_id,
								random_id=get_random_id(),
								message=f'Ваша группа изменена на: {group_name}',
							)
				else:
					bot.vk.messages.send (
								peer_id=user_id,
								random_id=get_random_id(),
								message=f'Не удалось найти {group_name}',
							)
				bot.message_menu(user_id)
			## CHANGE_GROUP END
			### FIND PREPOD START
			elif bot.check_status_user(user_id) == "FIND_PREPOD":
				session = auth(config.LOGIN, config.PASSWORD)
				teacher = find_teacher(session, event.obj.text)
				if teacher == None:
					bot.vk.messages.send (
									peer_id=user_id,
									random_id=get_random_id(),
									message='Преподаватель не найден',
								)
					bot.change_status_user(user_id, "MENU")
					bot.message_menu(user_id)
				else:
					bot.data[user_id]["user_teacher"] = teacher
					bot.change_status_user(user_id, "FIND_PREPOD_MENU")
					bot.message_find_menu(user_id, teacher)
			
			elif bot.check_status_user(user_id) == "FIND_PREPOD_MENU":
				bot.change_status_user(user_id, "MENU")
				command = event.obj.text
				if command.lower() == "сегодня" or command.lower() == "завтра" or command.lower() == "эта неделя" or command.lower() == "следующая неделя":
					session = auth(config.LOGIN, config.PASSWORD)
					teacher = bot.data[user_id]["user_teacher"]
					bot.vk.messages.send (
							peer_id=user_id,
							random_id=get_random_id(),
							message=get_schedule_prepod(session, command, teacher)
						)
					bot.data[user_id]["user_teacher"] = None
					bot.writeData()
					bot.message_menu(user_id)
				else:
					bot.data[user_id]["user_teacher"] = None
					bot.writeData()
					bot.message_menu(user_id)
			### FIND PREPOD END

		else:
			print(event.type)
			print()


if __name__ == '__main__':
	bot = Bot(config.TOKEN, config.GROUP_ID)
	while True:
		try: 
			main(bot)
		except Exception as error:
			print('error', error)
			time.sleep(1)
