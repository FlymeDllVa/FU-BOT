import vk_api

from app.models import Model
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

class Keyboards():

    def __init__(self):
        pass

    def main_menu(self, user):
        """
        Клавитатура главного меню
        :param user:
        :return:
        """

        keyboard = VkKeyboard()

        if user.user_group == None:
            keyboard.add_button('Расписание', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()
        else:
            keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()

            keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()

        keyboard.add_button('Поиск преподавателя', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()

        keyboard.add_button('Написать нам', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('Настройки', color=VkKeyboardColor.DEFAULT)

        return keyboard.get_keyboard()

    def settings_menu(self, user):
        """
        Клавиатура настроек
        :param user:
        :return:
        """

        keyboard = VkKeyboard()

        keyboard.add_button('Выбрать группу', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()

        keyboard.add_button('Назад к меню', color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()

