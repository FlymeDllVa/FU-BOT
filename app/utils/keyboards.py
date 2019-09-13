from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from app.models import User
from config import *


class Keyboards:
    @staticmethod
    def empty_keyboard() -> str:
        """
        Возвращает пустую клавиатуру

        :return:
        """

        return VkKeyboard().get_empty_keyboard()

    @staticmethod
    def main_menu():
        """
        Возвращает главное меню

        :return:
        """

        keyboard = VkKeyboard()

        keyboard.add_button('Расписание', color=VkKeyboardColor.DEFAULT, payload={"menu": "schedule"})
        keyboard.add_line()
        keyboard.add_vkapps_button(label="Мероприятия", app_id=6819359, owner_id=-int(current_id), hash="send_events")
        keyboard.add_line()
        keyboard.add_vkapps_button(label="Рассылка событий", app_id=5748831, owner_id=-int(current_id),
                                   hash="send_distributions")

        return keyboard.get_keyboard()

    @staticmethod
    def schedule_menu(user: User) -> str:
        """
        Возвращает клавиатуру главного меню

        :param user:
        :return:
        """

        keyboard = VkKeyboard()

        if user.group_name is None or user.group_name == "CHANGES":
            keyboard.add_button('Выбрать группу', color=VkKeyboardColor.DEFAULT, payload={"menu": "change_group"})
            keyboard.add_line()
        else:
            keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE,
                                payload={"menu": "schedule_show", "start_day": 0, "days": 1})
            keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT,
                                payload={"menu": "schedule_show", "start_day": 1, "days": 1})
            keyboard.add_line()

            keyboard.add_button('Сегодня и завтра', color=VkKeyboardColor.DEFAULT,
                                payload={"menu": "schedule_show", "start_day": 0, "days": 2})
            keyboard.add_line()

            keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT,
                                payload={"menu": "schedule_show", "start_day": -1, "days": 7})
            keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT,
                                payload={"menu": "schedule_show", "start_day": -2, "days": 7})
            keyboard.add_line()

            keyboard.add_button('Расписание на определенный день', color=VkKeyboardColor.DEFAULT,
                                payload={"menu": "schedule_one_day"})
            keyboard.add_line()

        keyboard.add_button('Поиск преподавателя', color=VkKeyboardColor.DEFAULT, payload={"menu": "search_teacher"})
        keyboard.add_line()

        keyboard.add_button('← Назад', color=VkKeyboardColor.PRIMARY, payload={"menu": "main"})
        keyboard.add_button('≡ Настройки', color=VkKeyboardColor.DEFAULT, payload={"menu": "settings"})

        return keyboard.get_keyboard()

    @staticmethod
    def settings_menu(user: User) -> str:
        """
        Возвращает клавиатуру настроек

        :param user:
        :return:
        """

        keyboard = VkKeyboard()

        if user.group_name is None:
            keyboard.add_button('Выбрать группу', color=VkKeyboardColor.DEFAULT, payload={"menu": "change_group"})
            keyboard.add_line()
        else:
            keyboard.add_button('Изменить группу', color=VkKeyboardColor.DEFAULT, payload={"menu": "change_group"})
            keyboard.add_line()

        if user.show_groups is False:
            keyboard.add_button('Группы в расписании', color=VkKeyboardColor.NEGATIVE, payload={"menu": "show_groups"})
        else:
            keyboard.add_button('Группы в расписании', color=VkKeyboardColor.POSITIVE, payload={"menu": "show_groups"})
        if user.show_location is False:
            keyboard.add_button('Корпус в расписании', color=VkKeyboardColor.NEGATIVE,
                                payload={"menu": "show_location"})
        else:
            keyboard.add_button('Корпус в расписании', color=VkKeyboardColor.POSITIVE,
                                payload={"menu": "show_location"})
        keyboard.add_line()

        if (user.subscription_days is None or user.subscription_days == "CHANGES") and user.current_name:
            keyboard.add_button('Подписаться на расписание', color=VkKeyboardColor.DEFAULT,
                                payload={"menu": "subscribe_to_newsletter"})
            keyboard.add_line()
        else:
            if user.subscription_days is not None and user.subscription_days != "CHANGES" and user.current_name:
                if user.current_name:
                    keyboard.add_button('Изменить подписку на расписание', color=VkKeyboardColor.DEFAULT,
                                        payload={"menu": "subscribe_to_newsletter"})
                    keyboard.add_line()
                keyboard.add_button('Отписаться от подписки на расписание', color=VkKeyboardColor.DEFAULT,
                                    payload={"menu": "unsubscribe_to_newsletter"})
                keyboard.add_line()

        keyboard.add_button('← Назад', color=VkKeyboardColor.PRIMARY, payload={"menu": "cancel"})

        return keyboard.get_keyboard()

    @staticmethod
    def subscribe_to_schedule_start_menu(user: User) -> str:
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

        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY, payload={"menu": "cancel"})

        return keyboard.get_keyboard()

    @staticmethod
    def subscribe_to_schedule_day_menu(user: User) -> str:
        """
        Возвращает клавиатуру для выбора дня рассылки

        :param user:
        :return:
        """
        keyboard = VkKeyboard()

        keyboard.add_button('Текущий день', color=VkKeyboardColor.DEFAULT,
                            payload={"menu": "subscribe_to_newsletter_today"})
        keyboard.add_line()
        keyboard.add_button('Следующий день', color=VkKeyboardColor.DEFAULT,
                            payload={"menu": "subscribe_to_newsletter_tomorrow"})
        keyboard.add_line()
        keyboard.add_button('Текущий и следующий день', color=VkKeyboardColor.DEFAULT,
                            payload={"menu": "subscribe_to_newsletter_today_and_tomorrow"})
        keyboard.add_line()
        keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT,
                            payload={"menu": "subscribe_to_newsletter_this_week"})
        keyboard.add_line()
        keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT,
                            payload={"menu": "subscribe_to_newsletter_next_week"})
        keyboard.add_line()
        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY, payload={"menu": "cancel"})

        return keyboard.get_keyboard()

    @staticmethod
    def teachers_menu(teachers: list) -> str:
        """
        Возвращает клавиатуру для выбора преподавателя

        :param teachers:
        :return:
        """

        keyboard = VkKeyboard()

        for teacher in teachers[:9]:
            keyboard.add_button(teacher[1], color=VkKeyboardColor.DEFAULT, payload={"menu": "teachers",
                                                                                    "found_teacher_id": teacher[0],
                                                                                    "found_teacher_name": teacher[1]})
            keyboard.add_line()
        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY, payload={"menu": "cancel"})

        return keyboard.get_keyboard()

    @staticmethod
    def find_schedule_menu(user: User) -> str:
        """
        Возвращает клавиатуру для выбора даты
        :param user:
        :return:
        """

        keyboard = VkKeyboard()
        keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE,
                            payload={"menu": "teacher_schedule_show", "start_day": 0, "days": 1})
        keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT,
                            payload={"menu": "teacher_schedule_show", "start_day": 1, "days": 1})
        keyboard.add_line()
        keyboard.add_button('Сегодня и завтра', color=VkKeyboardColor.DEFAULT,
                            payload={"menu": "teacher_schedule_show", "start_day": 0, "days": 2})
        keyboard.add_line()
        keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT,
                            payload={"menu": "teacher_schedule_show", "start_day": 0, "days": 7})
        keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT,
                            payload={"menu": "teacher_schedule_show", "start_day": 7, "days": 7})
        keyboard.add_line()

        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY,
                            payload={"menu": "cancel"})

        return keyboard.get_keyboard()

    @staticmethod
    def chose_calendar():
        """
        Возвращает выбор типа календаря

        :return:
        """

        keyboard = VkKeyboard()

        keyboard.add_button('С военкой', color=VkKeyboardColor.DEFAULT, payload={"menu": "get_calendar", "army": True})
        keyboard.add_line()
        keyboard.add_button('Без военки', color=VkKeyboardColor.DEFAULT,
                            payload={"menu": "get_calendar", "army": False})
        keyboard.add_line()
        keyboard.add_button('Расписание', color=VkKeyboardColor.PRIMARY, payload={"menu": "schedule"})

        return keyboard.get_keyboard()
