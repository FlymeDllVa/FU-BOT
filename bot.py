# -*- coding: utf-8 -*-
import json
import io
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

class Bot:
	
	def __init__(self, token, group_id):
		self.vk_session = vk_api.VkApi(token = token)
		self.vk = self.vk_session.get_api()
		self.longpoll = VkBotLongPoll(self.vk_session, group_id)
		self.data = self.readData()
	
	def readData(self):
		try:
			with open('base/data.json', 'r') as file_data:
				return json.load(file_data)
		except Exception:
			print("Ошибка открытия базы")
			with open('base/data.json', 'w') as file_data:
				json.dump({}, file_data)
			return self.readData()
				
	def writeData(self):
		with io.open('base/data.json', 'w', encoding='utf8') as json_file:
			json.dump(self.data, json_file, ensure_ascii=False, indent=4, sort_keys=True)

	
	def check_status_user(self, user_id):
		user_id = str(user_id)
		if user_id in self.data:
			return self.data[user_id]["user_status"]
		else:
			self.data[user_id] = {
				"user_id": user_id,
				"user_status": "MENU",
				"user_group": None,
				"user_teacher": None
			}
			self.writeData()
			return self.data[user_id]["user_status"]
	
	def change_status_user(self, user_id, status):
		self.data[str(user_id)]["user_status"] = status
		self.writeData()
	
	def change_group(self, user_id, group_name):
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
		keyboard = VkKeyboard(one_time=True)

		keyboard.add_button('Мероприятия', color=VkKeyboardColor.NEGATIVE)
		keyboard.add_line()
		
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
		
		keyboard.add_button('Задать вопрос', color=VkKeyboardColor.PRIMARY)
		keyboard.add_line()
		
		keyboard.add_button('Настройки', color=VkKeyboardColor.DEFAULT)
		keyboard
		
		self.vk.messages.send (
				peer_id=user_id,
				random_id=get_random_id(),
				message='Выбери интересующий тебя пункт в меню',
				keyboard=keyboard.get_keyboard()
			)
		self.writeData()
	
	def message_find_menu(self, user_id, teacher):
		keyboard = VkKeyboard(one_time=True)
		
		keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)	
		keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT)
		keyboard.add_line()
		
		keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT)		
		keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT)
		keyboard.add_line()
		
		keyboard.add_button('Назад к меню', color=VkKeyboardColor.DEFAULT)
		self.vk.messages.send (
				peer_id=user_id,
				random_id=get_random_id(),
				message=f'Найденый преподаватель: {teacher[1]}\nВыберите промежуток',
				keyboard=keyboard.get_keyboard()
			)
		self.writeData()
		
	def message_settings(self, user_id):
		keyboard = VkKeyboard(one_time=True)

		if self.data[user_id]["user_group"] != None:
			keyboard.add_button('Выбрать группу', color=VkKeyboardColor.DEFAULT)
			keyboard.add_line()
		else:
			keyboard.add_button('Сменить группу', color=VkKeyboardColor.DEFAULT)
			keyboard.add_line()
		
		keyboard.add_button('Подписки на рассылки', color=VkKeyboardColor.NEGATIVE)	
		keyboard.add_line()
		
		keyboard.add_button('Назад к меню', color=VkKeyboardColor.DEFAULT)		
		
		self.vk.messages.send (
				peer_id=user_id,
				random_id=get_random_id(),
				message='Выберите пункт в настройках',
				keyboard=keyboard.get_keyboard()
			)
		self.writeData()
