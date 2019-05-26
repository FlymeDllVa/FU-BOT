# -*- coding: utf-8 -*-
import json
import io
import vk_api
import time
import config
import requests
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

class Distribution:

	def __init__(self):
		pass
	
	def add_person_in_newsletter(self, userd_id, newsletters_list, token = config.TOKEN_DISTRIBUTION):
		requests.put(f"https://broadcast.vkforms.ru/api/v2/list/{newsletters_list}?token={token}"  , json = {"list":{"to_add":[userd_id]}})
	
	def delete_person_in_newsletter(self, userd_id, newsletters_list, token = config.TOKEN_DISTRIBUTION):
		requests.put(f"https://broadcast.vkforms.ru/api/v2/list/{newsletters_list}?token={token}"  , json = {"list":{"to_delete":[userd_id]}})

class Logger:
	
	def __init__(self):
		pass
	
	def writeLogs(self, data, fileName):
		with open(fileName, 'a', encoding='utf8') as file_name:
			print(data, file=file_name)
		
	def print_info_logs(self, data):
		self.writeLogs(f"{time.asctime()} | {str(data)}", "logs/info.log")
		print(data)
	
	def print_error_logs(self, data):
		self.print_info_logs(data)
		self.writeLogs(f"{time.asctime()} | {str(data)}", "logs/errors.log")
		print(data)

class Bot(Distribution, Logger):
	
	def __init__(self, token, group_id):
		self.vk_session = vk_api.VkApi(token = token)
		self.vk = self.vk_session.get_api()
		self.longpoll = VkBotLongPoll(self.vk_session, group_id)
		self.data = self.readData()
		self.statistics = self.readStatistics()
	
	# Statistics
	def add_statistics_requests(self):
		self.statistics["requests"] = self.statistics["requests"] + 1
		self.writeStatistics()

	def add_statistics_people(self, people):
		self.statistics["people"] = people
		self.writeStatistics()

	def readStatistics(self):
		try:
			with open('statistics.json', 'r') as file_data:
				return json.load(file_data)
		except Exception:
			with open('statistics.json', 'w') as file_data:
				json.dump({ "requests": 0, "people": 0 }, file_data)
			return self.readStatistics()
	
	def writeStatistics(self):
		with io.open('base/statistics.json', 'w', encoding='utf8') as json_file:
			json.dump(self.statistics, json_file, ensure_ascii=False, indent=4, sort_keys=True)
	
	# Data
	def readData(self):
		try:
			with open('base/data.json', 'r') as file_data:
				return json.load(file_data)
		except Exception:
			self.print_error_logs("Ошибка открытия базы")
			with open('base/data.json', 'w') as file_data:
				json.dump({}, file_data)
			return self.readData()
				
	def writeData(self):
		with io.open('base/data.json', 'w', encoding='utf8') as json_file:
			json.dump(self.data, json_file, ensure_ascii=False, indent=4, sort_keys=True)
	
	def check_status_user(self, user_id):
		self.add_statistics_people(len(self.data))
		user_id = str(user_id)
		if user_id in self.data:
			return self.data[user_id]["user_status"]
		else:
			self.data[user_id] = {
				"user_id": user_id,
				"user_status": "FIRST_START",
				"user_group": None,
				"user_teacher": None
			}
			self.writeData()
			return self.data[user_id]["user_status"]
	
	def change_status_user(self, user_id, status):
		self.data[str(user_id)]["user_status"] = status
		self.writeData()
	
	def change_group(self, user_id, group_name):
		group_name = group_name.upper()
		with open('base/groups.json', 'r') as file_data:
			data = json.load(file_data)
			if group_name in data:
				self.data[str(user_id)]["user_group"] = group_name
				return data[group_name]
			else:
				self.data[str(user_id)]["user_group"] = None
				return None
			self.writeData()
	
	def get_groupID(self, user_id):
		group_name = self.data[str(user_id)]["user_group"]
		with open('base/groups.json', 'r') as file_data:
			data = json.load(file_data)
			if group_name in data:
				return data[group_name]
			else:
				return None
	
	def message_menu(self, user_id):		
		keyboard = VkKeyboard()

#		keyboard.add_button('Мероприятия', color=VkKeyboardColor.NEGATIVE)
#		keyboard.add_line()
		
		if self.data[user_id]["user_group"] != None:
			keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)	
			keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT)
			keyboard.add_line()
			
			keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT)		
			keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT)
			keyboard.add_line()
		else:
			keyboard.add_button('Расписание', color=VkKeyboardColor.DEFAULT)
			keyboard.add_line()	
		
		keyboard.add_button('Поиск преподавателя', color=VkKeyboardColor.POSITIVE)
		keyboard.add_line()

		# if self.data[user_id]["user_group"] != None:
		# 	keyboard.add_button('⬇️ Сегодня', color=VkKeyboardColor.POSITIVE)	
		# 	keyboard.add_button('➡️ Завтра', color=VkKeyboardColor.DEFAULT)
		# 	keyboard.add_line()
			
		# 	keyboard.add_button('⏬ Эта неделя', color=VkKeyboardColor.DEFAULT)		
		# 	keyboard.add_button('⏩ Следующая неделя', color=VkKeyboardColor.DEFAULT)
		# 	keyboard.add_line()
		# else:
		# 	keyboard.add_button('📅 Расписание', color=VkKeyboardColor.DEFAULT)
		# 	keyboard.add_line()	
		
		# keyboard.add_button('🔍 Поиск преподавателя', color=VkKeyboardColor.POSITIVE)
		# keyboard.add_line()
		
#		keyboard.add_button('Задать вопрос', color=VkKeyboardColor.PRIMARY)
#		keyboard.add_line()
		
		keyboard.add_button('Написать нам', color=VkKeyboardColor.DEFAULT)
		keyboard.add_button('Настройки', color=VkKeyboardColor.DEFAULT)
		keyboard
		
		self.vk.messages.send (
				peer_id=user_id,
				random_id=get_random_id(),
				message='Выбери интересующий тебя пункт в меню',
				keyboard=keyboard.get_keyboard()
			)
		self.writeData()
	
	"""
	FIRST_START
	"""
	def message_distribution_start(self, user_id):		
		keyboard = VkKeyboard()

		keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
		keyboard.add_line()
		keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
		
		self.vk.messages.send (
				peer_id=user_id,
				random_id=get_random_id(),
				message='Привет!\nПрежде чем начать работу с ботом, предлаегаем вам подписаться на рассылку собыйтий, которые происходят в университете\n\nХотите подписаться прямо сейчас?',
				keyboard=keyboard.get_keyboard()
			)
		self.writeData()

	def create_clear_newsletter(self, user_id):
		self.data[str(user_id)].update({"user_newsletter": {item: False for item in config.DISTRIBUTION.keys()}})
		[self.delete_person_in_newsletter(user_id, config.DISTRIBUTION[item]) for item in self.data[str(user_id)]["user_newsletter"].keys()]
		self.writeData()

	def check_newsletter(self, user_id, data):
		if data in self.data[str(user_id)]["user_newsletter"]:
			if self.data[str(user_id)]["user_newsletter"][data] == False:
				self.data[str(user_id)]["user_newsletter"][data] = True
				self.add_person_in_newsletter(user_id, config.DISTRIBUTION[data])
			elif self.data[str(user_id)]["user_newsletter"][data] == True:
				self.data[str(user_id)]["user_newsletter"][data] = False
				self.delete_person_in_newsletter(user_id, config.DISTRIBUTION[data])
		self.writeData()

	def newsSubscription(self, user_id):
		keyboard = VkKeyboard()
		
		if self.data[str(user_id)]["user_newsletter"]["научные конференции"] == True:
			keyboard.add_button('Научные конференции', color=VkKeyboardColor.POSITIVE)
		else:
			keyboard.add_button('Научные конференции', color=VkKeyboardColor.DEFAULT)
		keyboard.add_line()
		
		if self.data[str(user_id)]["user_newsletter"]["культурно-массовые мероприятия"] == True:
			keyboard.add_button('Культурно-массовые мероприятия', color=VkKeyboardColor.POSITIVE)
		else:
			keyboard.add_button('Культурно-массовые мероприятия', color=VkKeyboardColor.DEFAULT)
		keyboard.add_line()

		if self.data[str(user_id)]["user_newsletter"]["спорт"] == True:
			keyboard.add_button('Спорт', color=VkKeyboardColor.POSITIVE)
		else:
			keyboard.add_button('Спорт', color=VkKeyboardColor.DEFAULT)
		keyboard.add_line()

		keyboard.add_button('Перейти к меню', color=VkKeyboardColor.PRIMARY)
		
		self.vk.messages.send (
				peer_id=user_id,
				random_id=get_random_id(),
				message='Выберите новости, на которые хотите подписаться',
				keyboard=keyboard.get_keyboard()
			)
		self.writeData()
	
	def message_find_menu(self, user_id, teacher):
		keyboard = VkKeyboard()
		
		keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)	
		keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT)
		keyboard.add_line()
		
		keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT)		
		keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT)
		keyboard.add_line()
		
		keyboard.add_button('Назад к меню', color=VkKeyboardColor.PRIMARY)
		self.vk.messages.send (
				peer_id=user_id,
				random_id=get_random_id(),
				message=f'Найденый преподаватель: {teacher[1]}\nВыберите промежуток',
				keyboard=keyboard.get_keyboard()
			)
		self.writeData()
		
	def message_settings(self, user_id):
		keyboard = VkKeyboard()

		if self.data[user_id]["user_group"] != None:
			keyboard.add_button('Выбрать группу', color=VkKeyboardColor.DEFAULT)
			keyboard.add_line()
		else:
			keyboard.add_button('Сменить группу', color=VkKeyboardColor.DEFAULT)
			keyboard.add_line()
		
		keyboard.add_button('Подписки на рассылки', color=VkKeyboardColor.DEFAULT)	
		keyboard.add_line()
		
		keyboard.add_button('Назад к меню', color=VkKeyboardColor.PRIMARY)		
		
		self.vk.messages.send (
				peer_id=user_id,
				random_id=get_random_id(),
				message='Выберите пункт в настройках',
				keyboard=keyboard.get_keyboard()
			)
		self.writeData()
