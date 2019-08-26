import vk_api
import datetime

from app.utils.keyboards import Keyboards
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from app.utils.server import get_schedule, get_teacher, format_schedule
from app.models import User


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
    Методы первой настройки настройка
    """

    def start_menu(self, user: User) -> User:
        """
        Отправляет пользователю стартовое меню

        :param user:
        :return:
        """

        # TODO дописать определение дня
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Добрый день!\nХотите выбрать вашу группу?",
            keyboard=self.keyboard.start_menu()
        )
        return user

    def error_data(self, user: User, message: str = "Пожайлуста, выберите пункт из меню") -> User:
        """
        В случае ошибки введенных данных просит повторить

        :param message:
        :param user:
        :return:
        """

        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message=message,
        )
        return user

    """
    Методы главного меню
    """

    def main_menu(self, user: User, message: str = "Выберите интересующий пункт в меню") -> User:
        """
        Отправляет пользователю главное меню

        :param message: сообщение если требуется, или None
        :param user:
        :return:
        """

        if message:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=message,
                keyboard=self.keyboard.main_menu(user)
            )
        else:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                keyboard=self.keyboard.main_menu(user)
            )
        return user

    """
    Методы поиска группы
    """

    def choice_group(self, user: User) -> User:
        """
        Отправляет пользователю сообщение о том, что для смены группы трубется ее написать

        :param user:
        :return:
        """

        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Напишите название группы, расписание которой требуется получить\n\nНапример «ПИ18-1»",
            keyboard=self.keyboard.empty_keyboard()
        )
        return user

    def check_group(self, user: User, group_name: str) -> User or None:
        """
        Проверяет существует ли группа

        :param user:
        :param group_name:
        :return:
        """
        group_name = group_name.strip().replace(" ", "").upper()
        schedule = get_schedule(group_name)
        if schedule is None:
            return None
        else:
            return User.change_group_name(user, group_name)

    def change_group(self, user: User, change: bool = False) -> User:
        """
        Отправляет сообщение о успешной смене группы

        :param change:
        :param user:
        :return:
        """

        if change is False:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Не удалось изменить группу",
            )
            User.update_user(user, data=dict(group_name=None))
        elif change is True:
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Группа успешно изменена на {user.group_name}",
            )
        return user

    """
    Методы расписания
    """

    def send_schedule(self, user: User, start_day: int = 0, days: int = 1) -> User or None:
        """
        Отсылает пользователю расписание

        :param start_day:
        :param user:
        :param days:
        :return:
        """

        if not user.group_name:
            self.main_menu(user=user, message="Пожайлуста, выберите пункт из меню")
            return user
        schedule = format_schedule(group_name=user.group_name, start_day=start_day, days=days)
        if schedule is None:
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

    def settings(self, user: User) -> User:
        """
        Отсылает пользователю меню настроек

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

    def subscribe_error(self, user: User) -> User:
        user = User.update_user(user=user,
                                data=dict(subscription_time=None, subscription_group=None, subscription_days=None))
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Подписка на расписание отменена",
        )
        return user

    def subscribe_schedule(self, user: User) -> User:
        """
        Отправляет время для подписки на расписание

        :param user:
        :return:
        """

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
        except Exception:
            self.subscribe_error(user)
            return None

    def update_subscribe_day(self, user: User, day: str) -> User or None:
        """
        Отправляет день для подписки на расписание

        :param day:
        :param user:
        :return:
        """

        if day in ("текущий день", "следующий день", "текущий и следующий день", "эта неделя", "следующая неделя"):
            if day == "текущий день":
                user = User.update_user(user=user, data=dict(subscription_days="ТЕКУЩИЙ"))
            elif day == "следующий день":
                user = User.update_user(user=user, data=dict(subscription_days="СЛЕДУЮЩИЙ"))
            elif day == "текущий и следующий день":
                user = User.update_user(user=user, data=dict(subscription_days="ТЕКУЩИЙ_И_СЛЕДУЮЩИЙ"))
            elif day == "эта неделя":
                user = User.update_user(user=user, data=dict(subscription_days="ТЕКУЩАЯ_НЕДЕЛЯ"))
            elif day == "следующая неделя":
                user = User.update_user(user=user, data=dict(subscription_days="СЛЕДУЮЩАЯ_НЕДЕЛЯ"))
            else:
                return None
            if day == "эта неделя":
                day = "эту неделю"
            if day == "следующая неделя":
                day = "следующую неделю"
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f'Вы подписались на раписание группы {user.subscription_group}\nТеперь каждый день вы будете '
                f'получать расписание в {user.subscription_time} на {day}',
            )
        return user

    """
    Поиск преподавателя
    """

    def search_teacher(self, user: User) -> User:
        """
        Отправляет сообщение с просьбой ввести ФИО преподавателя

        :param user:
        :return:
        """
        self.vk.messages.send(
            peer_id=user.id,
            random_id=get_random_id(),
            message="Введите фамилию или ФИО преподавателя",
            keyboard=self.keyboard.empty_keyboard()
        )
        return user

    def search_teacher_schedule(self, user: User, teacher_name: str) -> User or None:
        teacher = get_teacher(teacher_name)
        if isinstance(teacher, dict):
            User.update_user(user=user, data=dict(found_teacher_id=teacher['id'], found_teacher_name=teacher['name']))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Найденный преподаватель: {teacher['name']}\nВыберите промежуток",
                keyboard=self.keyboard.find_teacher_menu(user)
            )
            return user
        else:
            User.update_user(user=user, data=dict(found_teacher_id=None, found_teacher_name=None))
            self.vk.messages.send(
                peer_id=user.id,
                random_id=get_random_id(),
                message=f"Преподаватель не найден",
            )
            return None

    def send_teacher_schedule(self, user: User, start_day: int = 0, days: int = 1) -> User or None:
        """
        Отсылает пользователю расписание преподавателя

        :param start_day:
        :param user:
        :param days:
        :return:
        """

        schedule = format_schedule(start_day=start_day, days=days, teacher=dict(id=user.found_teacher_id,
                                                                                name=user.found_teacher_name))
        User.update_user(user=user, data=dict(found_teacher_id=None, found_teacher_name=None))
        if schedule is None:
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
