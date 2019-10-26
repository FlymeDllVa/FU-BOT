from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from app.models import User
import app.utils.constants as const


class Keyboards:
    @staticmethod
    def empty_keyboard() -> str:
        """
        Возвращает пустую клавиатуру

        :return:
        """

        return VkKeyboard().get_empty_keyboard()

    @staticmethod
    def choose_role():
        keyboard = VkKeyboard()
        keyboard.add_button('Студент', payload={const.PAYLOAD_MENU: const.MENU_CHOOSE_ROLE,
                                                const.PAYLOAD_ROLE: const.ROLE_STUDENT})
        keyboard.add_line()
        keyboard.add_button('Преподователь', payload={const.PAYLOAD_MENU: const.MENU_CHOOSE_ROLE,
                                                      const.PAYLOAD_ROLE: const.ROLE_TEACHER})
        return keyboard.get_keyboard()

    @staticmethod
    def schedule_menu(user: User) -> str:
        """
        Возвращает клавиатуру главного меню

        :param user:
        :return:
        """

        keyboard = VkKeyboard()

        keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE,
                            payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE_SHOW, const.PAYLOAD_START_DAY: 0,
                                     const.PAYLOAD_DAYS: 1})
        keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE_SHOW, const.PAYLOAD_START_DAY: 1,
                                     const.PAYLOAD_DAYS: 1})
        keyboard.add_line()
        keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE_SHOW, const.PAYLOAD_START_DAY: -1,
                                     const.PAYLOAD_DAYS: 7})
        keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE_SHOW, const.PAYLOAD_START_DAY: -2,
                                     const.PAYLOAD_DAYS: 7})
        keyboard.add_line()
        keyboard.add_button('Расписание на определенный день', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE_SHOW_ONE})
        keyboard.add_line()
        keyboard.add_button('Поиск', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_SEARCH})
        keyboard.add_line()
        # keyboard.add_button('← Назад', color=VkKeyboardColor.PRIMARY, payload={const.PAYLOAD_MENU: const.MENU_MAIN})
        keyboard.add_button('Настройки', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_SETTINGS})

        return keyboard.get_keyboard()

    @staticmethod
    def search_menu() -> str:
        keyboard = VkKeyboard()
        keyboard.add_button('Расписание группы', payload={const.PAYLOAD_MENU: const.MENU_SEARCH_GROUP})
        keyboard.add_line()
        keyboard.add_button('Расписание преподователя', payload={const.PAYLOAD_MENU: const.MENU_SEARCH_TEACHER})
        keyboard.add_line()
        keyboard.add_button('← Назад', color=VkKeyboardColor.PRIMARY, payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE})
        return keyboard.get_keyboard()

    @staticmethod
    def settings_menu(user: User) -> str:
        """
        Возвращает клавиатуру настроек

        :param user:
        :return:
        """

        keyboard = VkKeyboard()
        keyboard.add_button('Выбрать группу' if user.current_name is None else 'Изменить информацию о себе',
                            color=VkKeyboardColor.DEFAULT, payload={const.PAYLOAD_MENU: const.MENU_CHANGE_GROUP})
        keyboard.add_line()
        keyboard.add_button('Группы в расписании',
                            color=VkKeyboardColor.POSITIVE if user.show_groups else VkKeyboardColor.NEGATIVE,
                            payload={const.PAYLOAD_MENU: const.MENU_SET_SETTINGS,
                                     const.PAYLOAD_TYPE: const.SETTINGS_TYPE_GROUPS})
        keyboard.add_button('Корпус в расписании',
                            color=VkKeyboardColor.POSITIVE if user.show_location else VkKeyboardColor.NEGATIVE,
                            payload={const.PAYLOAD_MENU: const.MENU_SET_SETTINGS,
                                     const.PAYLOAD_TYPE: const.SETTINGS_TYPE_LOCATION})
        keyboard.add_line()

        if (user.subscription_days is None or user.subscription_days == const.CHANGES) and user.current_name:
            keyboard.add_button('Подписаться на расписание', color=VkKeyboardColor.DEFAULT,
                                payload={const.PAYLOAD_MENU: const.MENU_SUBSCRIBE})
            keyboard.add_line()
        else:
            if user.subscription_days is not None and user.subscription_days != const.CHANGES and user.current_name:
                if user.current_name:
                    keyboard.add_button('Изменить подписку на расписание', color=VkKeyboardColor.DEFAULT,
                                        payload={const.PAYLOAD_MENU: const.MENU_SUBSCRIBE})
                    keyboard.add_line()
                keyboard.add_button('Отписаться от подписки на расписание', color=VkKeyboardColor.DEFAULT,
                                    payload={const.PAYLOAD_MENU: const.MENU_UNSUBSCRIBE})
                keyboard.add_line()
        keyboard.add_button('← Назад', color=VkKeyboardColor.PRIMARY, payload={const.PAYLOAD_MENU: const.MENU_CANCEL})

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

        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY, payload={const.PAYLOAD_MENU: const.MENU_CANCEL})

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
                            payload={const.PAYLOAD_MENU: const.MENU_UPDATE_SUBSCRIPTION,
                                     const.PAYLOAD_TYPE: const.SUBSCRIPTION_TODAY})
        keyboard.add_line()
        keyboard.add_button('Следующий день', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_UPDATE_SUBSCRIPTION,
                                     const.PAYLOAD_TYPE: const.SUBSCRIPTION_TOMORROW})
        keyboard.add_line()
        keyboard.add_button('Текущий и следующий день', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_UPDATE_SUBSCRIPTION,
                                     const.PAYLOAD_TYPE: const.SUBSCRIPTION_TODAY_TOMORROW})
        keyboard.add_line()
        keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_UPDATE_SUBSCRIPTION,
                                     const.PAYLOAD_TYPE: const.SUBSCRIPTION_WEEK})
        keyboard.add_line()
        keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_UPDATE_SUBSCRIPTION,
                                     const.PAYLOAD_TYPE: const.SUBSCRIPTION_NEXT_WEEK})
        keyboard.add_line()
        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY, payload={const.PAYLOAD_MENU: const.MENU_CANCEL})

        return keyboard.get_keyboard()

    @staticmethod
    def found_list(found_list: list, to_set: bool = False, found_type: str = const.ROLE_TEACHER) -> str:
        """
        Возвращает клавиатуру для выбора преподавателя

        :param found_list:
        :param to_set:
        :param found_type:
        :return:
        """

        keyboard = VkKeyboard()

        for item in found_list[:9]:
            keyboard.add_button(item[1], color=VkKeyboardColor.DEFAULT,
                                payload={const.PAYLOAD_MENU: const.MENU_SET_TEACHER if to_set else const.MENU_TEACHER,
                                         const.PAYLOAD_FOUND_ID: item[0],
                                         const.PAYLOAD_FOUND_NAME: item[1],
                                         "found_type": found_type})
            keyboard.add_line()
        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY, payload={const.PAYLOAD_MENU: const.MENU_CANCEL})

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
                            payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE_FOUND, const.PAYLOAD_START_DAY: 0,
                                     const.PAYLOAD_DAYS: 1})
        keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE_FOUND, const.PAYLOAD_START_DAY: 1,
                                     const.PAYLOAD_DAYS: 1})
        keyboard.add_line()
        keyboard.add_button('Сегодня и завтра', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE_FOUND, const.PAYLOAD_START_DAY: 0,
                                     const.PAYLOAD_DAYS: 2})
        keyboard.add_line()
        keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE_FOUND, const.PAYLOAD_START_DAY: 0,
                                     const.PAYLOAD_DAYS: 7})
        keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT,
                            payload={const.PAYLOAD_MENU: const.MENU_SCHEDULE_FOUND, const.PAYLOAD_START_DAY: 7,
                                     const.PAYLOAD_DAYS: 7})
        keyboard.add_line()
        keyboard.add_button('Отмена', color=VkKeyboardColor.PRIMARY, payload={const.PAYLOAD_MENU: const.MENU_CANCEL})

        return keyboard.get_keyboard()
