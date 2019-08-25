import vk_api

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from config import *

class Keyboards:

    @classmethod
    def empty_keyboard(cls):
        """
        Возвращает пустую клавиатуру

        :return:
        """

        return VkKeyboard().get_empty_keyboard()

    @classmethod
    def start_menu(cls):
        """
        Возвращает клавиатуру стартового меню

        :return:
        """

        keyboard = VkKeyboard()

        keyboard.add_button('Да', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Нет', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_vkapps_button(app_id=5748831, owner_id=-int(GROUP_ID), label="Рассылка", hash="sendKeyboard")

        return keyboard.get_keyboard()

    @classmethod
    def main_menu(cls, user):
        """
        Возвращает клавиатуру главного меню

        :param user:
        :return:
        """

        keyboard = VkKeyboard()

        if user.group_name is None:
            keyboard.add_button('Расписание', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()
        else:
            keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()

            keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()

        keyboard.add_button('Поиск преподавателя', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()

        keyboard.add_button('Настройки', color=VkKeyboardColor.DEFAULT)

        return keyboard.get_keyboard()

    @classmethod
    def settings_menu(cls, user):
        """
        Возвращает клавиатуру настроек

        :param user:
        :return:
        """

        keyboard = VkKeyboard()

        if user.group_name is None:
            keyboard.add_button('Выбрать группу', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()
        else:
            keyboard.add_button('Изменить группу', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()

        if user.subscription_days is None and user.group_name:
            keyboard.add_button('Подписаться на расписание', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()
        else:
            if user.subscription_days:
                if user.group_name:
                    keyboard.add_button('Изменить подписку на расписание', color=VkKeyboardColor.DEFAULT)
                    keyboard.add_line()
                keyboard.add_button('Отписаться от подписки на расписание', color=VkKeyboardColor.DEFAULT)
                keyboard.add_line()

        keyboard.add_button('◀️ Назад', color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()

    @classmethod
    def subscribe_to_schedule_start_menu(cls, user):
        """
        Возвращает клавиатуру подписки на расписание

        :param user:
        :return:
        """
        keyboard = VkKeyboard()

        keyboard.add_button('7:00', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('7:30', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('8:00', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('9:00', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('9:30', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('10:00', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('20:00', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('21:00', color=VkKeyboardColor.DEFAULT)
        keyboard.add_button('22:00', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()

        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()

    @classmethod
    def subscribe_to_schedule_day_menu(cls, user):
        """
        Возвращает клавиатуру для выбора дня рассылки

        :param user:
        :return:
        """
        keyboard = VkKeyboard()

        keyboard.add_button('Текущий день', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Следующий день', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Текущий и следующий день', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()

    @classmethod
    def find_teacher_menu(self, user):
        """
        Возвращает клавиатуру для выбора даты
        :param user:
        :return:
        """

        keyboard = VkKeyboard()

        keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Сегодня и завтра', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()

        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY)

        return keyboard.get_keyboard()
