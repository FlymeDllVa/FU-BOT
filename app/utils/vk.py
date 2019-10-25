import vk_api
import datetime

from app.utils.keyboards import Keyboards
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.utils import get_random_id
from app.utils.server import get_group, get_teacher, format_schedule
from app.models import User
import app.utils.constants as const
import app.utils.strings as strings


class Bot:
    """
    Конструкторуирует бота
    """

    def __init__(self, token: str, current_id: int):
        """
        Главный конструктор бота

        :param token: токен группы ВК
        :param current_id: id группы ВК
        """

        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, current_id)
        self.keyboard = Keyboards

    """
    Меню расписания
    """

    def send_schedule_menu(self, user: User) -> User:
        """
        Отправляет меню расписания
        """
        if user.current_name is None or user.role is None:
            self.send_choice_group(user)
        else:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.CHOOSE_MENU,
                keyboard=self.keyboard.schedule_menu(user)
            )
        return user

    def send_schedule(self, user: User, start_day: int = 0, days: int = 1, text: str = "") -> User or None:
        """
        Отсылает пользователю расписание

        :param text:
        :param start_day: -1 - начало этой недели, -2 - начало следующей
        :param user:
        :param days:
        :return:
        """
        if start_day == -1:
            start_day = -datetime.datetime.now().isoweekday() + 1
        elif start_day == -2:
            start_day = 7 - datetime.datetime.now().isoweekday() + 1
        schedule = format_schedule(user, start_day=start_day, days=days, text=text)
        if schedule == "'Connection error'":
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message="Не удалось подключиться с информационно образовательному порталу",
            )
            return None
        elif schedule == "Not found":
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message="Расписание не найдено",
            )
            return None
        elif schedule == "Refreshes":
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message="Расписание обновляется. Попробуйте позже",
            )
            return None
        elif schedule == "Error":
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message="Ошибка получения расписания. Попробуйте заново выбрать группу в настройках или "
                        "обратитесь к администрации",
            )
            return None
        elif schedule is None:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message="Не удалось получить расписание",
            )
            return None
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=schedule,
        )
        return user

    def send_one_day_schedule(self, user: User) -> User:
        """
        Отправляет пользователю предложение написать дату

        :param user:
        :return:
        """

        user = User.update_user(user, data=dict(schedule_day_date=const.CHANGES))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=strings.WRITE_DATE,
            keyboard=self.keyboard.empty_keyboard()
        )
        return user

    def send_day_schedule(self, user: User, date: str) -> User:
        """
        Отправляет расписание на 1 день

        :param user:
        :param date:
        :return:
        """

        user = User.update_user(user, data=dict(schedule_day_date=None))
        try:
            if len(date.split(".")) == 3:
                date = datetime.datetime.strptime(date, '%d.%m.%Y')
            elif len(date.split(".")) == 2:
                date = datetime.datetime.strptime(f"{date}.{datetime.datetime.now().year}", '%d.%m.%Y')
            else:
                raise ValueError
        except ValueError:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.INCORRECT_DATE,
                keyboard=self.keyboard.schedule_menu(user)
            )
            return user
        schedule = format_schedule(user=user, date=date)
        if schedule is None:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.CANT_FIND_SCHEDULE_BY_DATE.format(date.strftime('%d.%m.%Y')),
                keyboard=self.keyboard.schedule_menu(user)
            )
            return user
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=schedule,
            keyboard=self.keyboard.schedule_menu(user)
        )
        return user

    def send_choice_group(self, user: User) -> User:
        """
        Отправляет пользователю сообщение о том, что для смены группы трубется ее написать
        """

        user = User.update_user(user, data=dict(current_name=const.CHANGES, role=None))
        return self.change_role(user)

    def send_check_group(self, user: User, group_name: str) -> None or User:
        """
        Проверяет существует ли группа
        """

        group_name = group_name.strip().replace(" ", "").upper()
        group = get_group(group_name)
        if group.has_error is False:
            user = User.update_user(user, data=dict(current_name=group_name, current_id=group.data))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.GROUP_CHANGED_FOR.format(group_name),
                keyboard=self.keyboard.schedule_menu(user)
            )
            return user
        else:
            user = User.update_user(user, data=dict(current_name=None))
            self.send_group_error(user, group_name, group.error_text)

    def send_group_error(self, user: User, group_name: str, error: str):
        if error == "Timeout error":
            # group = get_group(group_name)
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Не удалось сменить группу. Попробуйте позже",
                keyboard=self.keyboard.schedule_menu(user)
            )
        elif error == "Not found":
            user = User.update_user(user, data=dict(current_name=None))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Группа «{group_name}» не существует",
                keyboard=self.keyboard.schedule_menu(user)
            )
            return user

    def search_check_group(self, user: User, group_name: str) -> None or User:
        """
        Проверяет существует ли группа

        :param user:
        :param group_name:
        :return:
        """

        group_name = group_name.strip().replace(" ", "").upper()
        group = get_group(group_name)
        if group.has_error is False:
            user = User.update_user(user, data=dict(found_name=group_name, found_id=group.data))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.GROUP.format(group_name),
                keyboard=self.keyboard.find_schedule_menu(user)
            )
            return user
        else:
            user = User.update_user(user, data=dict(found_name=None))
            self.send_group_error(user, group_name, group.error_text)

    """
    Поиск преподавателя
    """

    def send_search_teacher(self, user: User) -> User:
        """
        Отправляет сообщение с просьбой ввести ФИО преподавателя

        :param user:
        :return:
        """

        user = User.update_user(user, data=dict(found_id=0, found_name=const.CHANGES, found_type=const.ROLE_TEACHER))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=strings.WRITE_TEACHER,
            keyboard=self.keyboard.empty_keyboard()
        )
        return user

    def search_teacher_schedule(self, user: User, teacher_name: str) -> User or None:
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=strings.SEARCHING_FOR_TEACHER,
        )
        teachers = get_teacher(teacher_name)
        if teachers.has_error:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message="Не удалось подключиться к информационно образовательному порталу. Попробуйте позже",
                keyboard=self.keyboard.schedule_menu(user)
            )
        elif teachers.data:
            teachers = teachers.data
            if len(teachers) == 1:
                user = User.update_user(user=user, data=dict(found_id=teachers[0][0],
                                                             found_name=teachers[0][1]))
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message=strings.FOUND_TEACHER.format(teachers[0][1]) + '\n' + strings.CHOOSE_TIMEDELTA,
                    keyboard=self.keyboard.find_schedule_menu(user)
                )
            else:
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message=strings.CHOOSE_CURRENT_TEACHER,
                    keyboard=self.keyboard.found_list(teachers)
                )
                return user
        else:
            User.update_user(user=user, data=dict(found_id=None, found_name=None, found_type=None))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.TEACHER_NOT_FOUND,
                keyboard=self.keyboard.schedule_menu(user)
            )
            return None

    def search_teacher_to_set(self, user: User, teacher_name: str) -> User or None:
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=strings.SEARCHING,
        )
        teachers = get_teacher(teacher_name)
        if teachers.has_error:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message="Не удалось подключиться к информационно образовательному порталу. Попробуйте позже",
                keyboard=self.keyboard.schedule_menu(user)
            )
        elif teachers.data:
            teachers = teachers.data
            if len(teachers) == 1:
                user = User.update_user(user=user, data=dict(current_id=teachers[0][0],
                                                             current_name=teachers[0][1]))
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message=strings.FOUND_TEACHER.format(teachers[0][1]) + '\n' + strings.CHOOSE_TIMEDELTA,
                    keyboard=self.keyboard.schedule_menu(user)
                )
            else:
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message=strings.CHOOSE_CURRENT_TEACHER,
                    keyboard=self.keyboard.found_list(teachers, to_set=True)
                )
                return user
        else:
            User.update_user(user=user, data=dict(found_id=None, found_name=None, found_type=None))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.TEACHER_NOT_FOUND,
                keyboard=self.keyboard.schedule_menu(user)
            )
            return None

    def set_teacher(self, user, payload):
        user = User.update_user(user=user, data=dict(current_id=payload[const.PAYLOAD_FOUND_ID],
                                                     current_name=payload[const.PAYLOAD_FOUND_NAME]))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=strings.FOUND_TEACHER.format(payload[const.PAYLOAD_FOUND_NAME]),
            keyboard=self.keyboard.schedule_menu(user)
        )

    def send_teacher(self, user, payload: dict):
        """
        Отправляет меню с выбором промежутка расписания для пользователя
        """
        if const.PAYLOAD_FOUND_ID in payload and const.PAYLOAD_FOUND_NAME in payload:
            user = User.update_user(user=user, data=dict(found_id=payload[const.PAYLOAD_FOUND_ID],
                                                         found_name=payload[const.PAYLOAD_FOUND_NAME]))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.CHOOSE_TIMEDELTA,
                keyboard=self.keyboard.find_schedule_menu(user)
            )
        else:
            User.update_user(user=user, data=dict(found_id=None, found_name=None, found_type=None))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.CANT_FIND_USER,
                keyboard=self.keyboard.schedule_menu(user)
            )

    def send_teacher_schedule(self, user: User, start_day: int = 0, days: int = 1) -> User or None:
        """
        Отсылает пользователю расписание преподавателя
        """

        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=strings.SEARCHING,
        )

        schedule = format_schedule(user, start_day=start_day, days=days, teacher=dict(id=user.found_id,
                                                                                      name=user.found_name,
                                                                                      type=user.found_type))
        User.update_user(user=user, data=dict(found_id=None, found_name=None, found_type=None))
        if schedule is None:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.CANT_GET_SCHEDULE,
                keyboard=self.keyboard.schedule_menu(user)
            )
            return None
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=schedule,
            keyboard=self.keyboard.schedule_menu(user)
        )
        return user

    """
    Меню настроек
    """

    def show_groups_or_location(self, user: User, act_type: str) -> User:
        """
        Обновляет поля
        """

        if act_type == const.SETTINGS_TYPE_GROUPS:
            if user.show_groups is False:
                user = User.update_user(user=user, data=dict(show_groups=True))
                message = "Список групп будет отображаться в раписании"
            else:
                user = User.update_user(user=user, data=dict(show_groups=False))
                message = "Список групп не будет отображаться в раписании"
        elif act_type == const.SETTINGS_TYPE_LOCATION:
            if user.show_location is False:
                user = User.update_user(user=user, data=dict(show_location=True))
                message = "Список корпусов будет отображаться в раписании"
            else:
                user = User.update_user(user=user, data=dict(show_location=False))
                message = "Список корпусов не будет отображаться в раписании"
        else:
            message = strings.ERROR
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=message,
            keyboard=self.keyboard.settings_menu(user)
        )
        return user

    def send_settings_menu(self, user: User) -> User:
        """
        Отправляет меню настроек
        """

        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=strings.WHAT_TO_SET,
            keyboard=self.keyboard.settings_menu(user)
        )
        return user

    """
    Подписка на расписание
    """

    def unsubscribe_schedule(self, user: User) -> User:
        """
        Отправляет время для подписки на расписание
        """

        user = User.update_user(user=user, data=dict(subscription_time=None,
                                                     subscription_group=None,
                                                     subscription_days=None))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=f'Вы отписались от рассылки расписания',
            keyboard=self.keyboard.schedule_menu(user)
        )
        return user

    def subscribe_schedule(self, user: User) -> User:
        """
        Отправляет время для подписки на расписание
        """

        user = User.update_user(user=user, data=dict(subscription_time=const.CHANGES,
                                                     subscription_group=const.CHANGES,
                                                     subscription_days=const.CHANGES))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Напишите или выберите время в которое хотите получать раписание\n\nНапример: «12:35»",
            keyboard=self.keyboard.subscribe_to_schedule_start_menu(user)
        )
        return user

    def update_subscribe_time(self, user: User, time: str) -> User or None:
        """
        Обновляет время для подписки на расписание
        """
        try:
            time = datetime.datetime.strptime(time, "%H:%M").strftime("%H:%M")
        except ValueError:
            user = User.update_user(user=user, data=dict(subscription_days=None,
                                                         subscription_time=None,
                                                         subscription_group=None))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=strings.INCORRECT_DATE_FORMAT,
                keyboard=self.keyboard.schedule_menu(user)
            )
            return user
        user = User.update_user(user=user, data=dict(subscription_time=time,
                                                     subscription_group=user.current_name))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=f"Формируем расписания для группы {user.current_name} в {time}\nВыберите период, на который вы "
                    f"хотите получать расписание",
            keyboard=self.keyboard.subscribe_to_schedule_day_menu(user)
        )
        return user

    def update_subscribe_day(self, user: User, menu: str) -> User or None:
        """
        Отправляет день для подписки на расписание
        """

        if menu == const.SUBSCRIPTION_TODAY:
            subscription_days = const.SUBSCRIPTION_TODAY
            day = "сегодня"
        elif menu == const.SUBSCRIPTION_TOMORROW:
            subscription_days = const.SUBSCRIPTION_TOMORROW
            day = "завтра"
        elif menu == const.SUBSCRIPTION_TODAY_TOMORROW:
            subscription_days = const.SUBSCRIPTION_TODAY_TOMORROW
            day = "текущий и следующий день"
        elif menu == const.SUBSCRIPTION_WEEK:
            subscription_days = const.SUBSCRIPTION_WEEK
            day = "текущую неделю"
        elif menu == const.SUBSCRIPTION_NEXT_WEEK:
            subscription_days = const.SUBSCRIPTION_NEXT_WEEK
            day = "следующую неделю"
        else:
            user = User.update_user(user=user, data=dict(subscription_time=None,
                                                         subscription_group=None,
                                                         subscription_days=None))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f'Не удалось добавить в рассылку расписания',
                keyboard=self.keyboard.schedule_menu(user)
            )
            return None
        user = User.update_user(user=user, data=dict(subscription_days=subscription_days))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=f'Вы подписались на раписание группы {user.subscription_group}\nТеперь каждый день в '
                    f'{user.subscription_time} вы будете получать расписание на {day}',
            keyboard=self.keyboard.schedule_menu(user)
        )
        return user

    def chose_calendar(self, user: User):
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Инструкция по добавлению подписки"
                    "\nДля iPhone"
                    "\nНастройки ▶ Почта, Контакты, Календарь ▶ Добавить учетную запись ▶ Другое ▶ Добавить подписной "
                    "календарь ▶ вставить адрес календаря "
                    "\n\nДля Android"
                    "\nВставить адрес календаря в https://calendar.google.com/calendar/r/settings/addbyurl ▶ Открыть "
                    "(скачать) Google Календарь ▶ Настройки ▶ FU Schedule ▶ Синхронизация\n\n\n"
                    "Ссылка на календарь для подписки: http://null.com 😥",
            keyboard=self.keyboard.schedule_menu(user)
        )
        return user

    def change_role(self, user: User):
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=strings.WELCOME,
            keyboard=self.keyboard.choose_role()
        )
        return user

    def set_role(self, user: User, role: str):
        message = strings.GROUP_EXAMPLE if role == const.ROLE_STUDENT else strings.TEACHER_EXAMPLE
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=message,
            keyboard=self.keyboard.empty_keyboard()
        )
        User.update_user(user=user, data=dict(current_name=const.CHANGES, role=role))
        return user

    def search(self, user):
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=strings.WHAT_TO_FIND,
            keyboard=self.keyboard.search_menu()
        )
        return user

    def search_group(self, user):
        User.update_user(user=user, data=dict(found_id=0, found_name=const.CHANGES, found_type=const.ROLE_STUDENT))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=strings.WRITE_GROUP,
            keyboard=self.keyboard.empty_keyboard()
        )
        return user
