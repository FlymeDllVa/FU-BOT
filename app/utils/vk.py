import urllib.parse
import vk_api
import datetime

from app.utils.keyboards import Keyboards
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.utils import get_random_id
from app.utils.server import get_group, get_teacher, format_schedule
from app.models import User
from config import CALENDAR_LINK


class Bot:
    """
    Конструкторуирует бота
    """

    def __init__(self, token: str, group_id: int):
        """
        Главный конструктор бота

        :param token: токен группы ВК
        :param group_id: id группы ВК
        """

        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.keyboard = Keyboards

    """
    Главное меню
    """

    def send_main_menu(self, user: User) -> User:
        """
        Отправляет пользователю главное меню
        :param user:
        :return:
        """

        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Выберите пункт из меню",
            keyboard=self.keyboard.main_menu()
        )

        return user

    """
    Меню расписания
    """

    def send_schedule_menu(self, user: User) -> User:
        """
        Отправляет меню расписания

        :param user:
        :return:
        """
        if user.group_name is None:
            self.send_choice_group(user)
        else:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message="Выберите пункт из меню",
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
                message="Ошибка получения расписания. Обратитесь к администрации",
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

        user = User.update_user(user, data=dict(schedule_day_date="CHANGES"))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Напишите дату, что бы получить ее расписание\n\nНапример «01.10.2019» или «01.10»",
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
                message=f"Неправильная дата",
                keyboard=self.keyboard.schedule_menu(user)
            )
            return user
        schedule = format_schedule(user=user, date=date)
        if schedule is None:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Не удалось найти расписание на {date.strftime('%d.%m.%Y')}",
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

        :param user:
        :return:
        """

        user = User.update_user(user, data=dict(group_name="CHANGES"))

        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Напишите название группы, расписание которой требуется получить\n\nНапример «ПИ18-1»",
            keyboard=self.keyboard.empty_keyboard()
        )

        return user

    def send_check_group(self, user: User, group_name: str) -> None or User:
        """
        Проверяет существует ли группа

        :param user:
        :param group_name:
        :return:
        """

        group_name = group_name.strip().replace(" ", "").upper()
        group = get_group(group_name)
        if group.has_error is False:
            user = User.update_user(user, data=dict(group_name=group_name))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Группа изменана на «{group_name}»",
                keyboard=self.keyboard.schedule_menu(user)
            )
            return user
        else:
            if group.error_text == "Refreshes":
                user = User.update_user(user, data=dict(group_name=group_name))
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message=f"Группа изменана на «{group_name}»\nДля работы расписания потребуется время на обновление",
                    keyboard=self.keyboard.schedule_menu(user)
                )
                return user
            user = User.update_user(user, data=dict(group_name=None))
            if group.error_text == "Connection error":
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message="Информационно образовательного портал не доступен. Попробуйте позже",
                    keyboard=self.keyboard.schedule_menu(user)
                )
            elif group.error_text == "Timeout error":
                group = get_group(group_name)
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message=f"Не удалось сменить группу. Попробуйте позже",
                    keyboard=self.keyboard.schedule_menu(user)
                )
            elif group.error_text == "Not found":
                user = User.update_user(user, data=dict(group_name=None))
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message=f"Группа «{group_name}» не существует",
                    keyboard=self.keyboard.schedule_menu(user)
                )
                return user
            elif group.error_text == "Error" or group.error_text == "Server error":
                user = User.update_user(user, data=dict(group_name=None))
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message=f"Не удалось найти группу «{group_name}». Попробуйте позже",
                    keyboard=self.keyboard.schedule_menu(user)
                )
                return user

    """
    Поиск преподавателя
    """

    def send_search_teacher(self, user: User) -> User:
        """
        Отправляет сообщение с просьбой ввести ФИО преподавателя

        :param user:
        :return:
        """

        user = User.update_user(user, data=dict(found_teacher_id=0, found_teacher_name="CHANGES"))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Введите фамилию или ФИО преподавателя",
            keyboard=self.keyboard.empty_keyboard()
        )
        return user

    def search_teacher_schedule(self, user: User, teacher_name: str) -> User or None:
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Ищем преподавателя",
        )
        teachers = get_teacher(teacher_name)
        if teachers == "timeout":
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message="Не удалось подключиться к информационно образовательному порталу. Попробуйте позже",
                keyboard=self.keyboard.schedule_menu(user)
            )
        elif teachers:
            if len(teachers) == 1:
                user = User.update_user(user=user, data=dict(found_teacher_id=teachers[0][0],
                                                             found_teacher_name=teachers[0][1]))
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message=f"Найденный преподаватель: {teachers[0][1]}\nВыберите промежуток",
                    keyboard=self.keyboard.find_teacher_menu(user)
                )
            else:
                self.vk.messages.send(
                    peer_id=user.id,
                    random_id=get_random_id(),
                    message="Выберите нужного преподавателя",
                    keyboard=self.keyboard.teachers_menu(teachers)
                )
                return user
        else:
            User.update_user(user=user, data=dict(found_teacher_id=None, found_teacher_name=None))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Преподаватель не найден",
                keyboard=self.keyboard.schedule_menu(user)
            )
            return None

    def send_teacher(self, user, payload):
        """
        Отправляет меню с выбором промежутка расписания для пользователя

        :param user:
        :param payload:
        :return:
        """
        if "found_teacher_id" in payload and "found_teacher_name" in payload:
            user = User.update_user(user=user, data=dict(found_teacher_id=payload["found_teacher_id"],
                                                         found_teacher_name=payload["found_teacher_name"]))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Выберите промежуток",
                keyboard=self.keyboard.find_teacher_menu(user)
            )
        else:
            User.update_user(user=user, data=dict(found_teacher_id=None, found_teacher_name=None))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Не удалось найти пользователя",
                keyboard=self.keyboard.schedule_menu(user)
            )

    def send_teacher_schedule(self, user: User, start_day: int = 0, days: int = 1) -> User or None:
        """
        Отсылает пользователю расписание преподавателя

        :param start_day:
        :param user:
        :param days:
        :return:
        """

        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Ищем расписание",
        )

        schedule = format_schedule(user, start_day=start_day, days=days, teacher=dict(id=user.found_teacher_id,
                                                                                      name=user.found_teacher_name))
        User.update_user(user=user, data=dict(found_teacher_id=None, found_teacher_name=None))
        if schedule is None:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message="Не удалось получить расписание",
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

        :param user:
        :param act_type:
        :return:
        """

        if act_type == "show_groups":
            if user.show_groups is False:
                user = User.update_user(user=user, data=dict(show_groups=True))
                message = "Список групп будет отображаться в раписании"
            else:
                user = User.update_user(user=user, data=dict(show_groups=False))
                message = "Список групп не будет отображаться в раписании"
        elif act_type == "show_location":
            if user.show_location is False:
                user = User.update_user(user=user, data=dict(show_location=True))
                message = "Список корпусов будет отображаться в раписании"
            else:
                user = User.update_user(user=user, data=dict(show_location=False))
                message = "Список корпусов не будет отображаться в раписании"
        else:
            message = "Ошибка"
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

        :param user:
        :return:
        """

        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Выберите в меню, что требуется настроить",
            keyboard=self.keyboard.settings_menu(user)
        )
        return user

    """
    Подписка на расписание
    """

    def unsubscribe_schedule(self, user: User) -> User:
        """
        Отправляет время для подписки на расписание

        :param user:
        :return:
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

        :param user:
        :return:
        """

        user = User.update_user(user=user, data=dict(subscription_time="CHANGES",
                                                     subscription_group="CHANGES",
                                                     subscription_days="CHANGES"))
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

        :param user:
        :param time:
        :return:
        """
        try:
            time = datetime.datetime.strptime(time, "%H:%M").strftime("%H:%M")
        except ValueError:
            pass
        user = User.update_user(user=user, data=dict(subscription_time=time,
                                                     subscription_group=user.group_name))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=f"Формируем расписания для группы {user.group_name} в {time}\nВыберите период, на который вы "
            f"хотите получать расписание",
            keyboard=self.keyboard.subscribe_to_schedule_day_menu(user)
        )
        return user

    def update_subscribe_day(self, user: User, menu: str) -> User or None:
        """
        Отправляет день для подписки на расписание

        :param menu:
        :param user:
        :return:
        """

        if menu == "subscribe_to_newsletter_today":
            subscription_days = "today"
            day = "сегодня"
        elif menu == "subscribe_to_newsletter_tomorrow":
            subscription_days = "tomorrow"
            day = "завтра"
        elif menu == "subscribe_to_newsletter_today_and_tomorrow":
            subscription_days = "today_and_tomorrow"
            day = "текущий и следующий день"
        elif menu == "subscribe_to_newsletter_this_week":
            subscription_days = "this_week"
            day = "текущую неделю"
        elif menu == "subscribe_to_newsletter_next_week":
            subscription_days = "next_week"
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
            message="Инструкции пока тут нет, но она должна потом появиться. "
                    "\nДля гугла вставлять сюда: https://calendar.google.com/calendar/r/settings/addbyurl",
            keyboard=self.keyboard.chose_calendar()
        )
        return user

    def send_calendar(self, user: User, army: bool):
        link = CALENDAR_LINK(
            urllib.parse.quote(user.group_name)) + f'?army={1 if army else 0}&address={1 if user.show_location else 0}'
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=f"Ссылка на календарь для подписки: {link}",
            keyboard=self.keyboard.schedule_menu(user)
        )
        return user
