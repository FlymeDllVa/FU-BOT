
import vk_api
import datetime
import threading

from app.models import Model
from app.vk.src.logger import Logger
from app.vk.src.portal import date_name
from app.vk.src.keyboards import Keyboards
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

class Bot:
    """

    Конструкторуирует бота

    """

    def __init__(self, token, group_id):
        self.vk_session = vk_api.VkApi(token = token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.model = Model()
        self.keyboard = Keyboards()

    def test(self):
        print("tests")

    """
    Отправка сообщений
    """
    def main_menu(self, user):
        """
        Отправляет пользователю главное меню
        :param user:
        :return:
        """
        self.vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            message='Выберите интересующий вас пункт меню',
            keyboard=self.keyboard.main_menu(user)
        )

    def settings_menu(self, user):
        """
        Отправляет пользователю меню настроек
        :param user:
        :return:
        """
        self.vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            message='Выберите интересующий вас пункт меню',
            keyboard=self.keyboard.settings_menu(user)
        )

    def change_group_menu(self, user):
        """
        Отправляет сообщение, которое информирует о способе изменения группы
        :param user:
        :return:
        """
        self.vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            message='Введите название вашей группы\nНапример: "ПИ18-1"',
            keyboard=VkKeyboard().get_empty_keyboard(),
        )

    def find_teacher_start(self, user):
        """
        Отправляет сообщение, котороее информирует о том, что необходимо ввести преподавателя
        :param user:
        :return:
        """
        self.vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            message='Введите фамилию или ФИО преподавателя',
            keyboard=VkKeyboard().get_empty_keyboard(),
        )

    """
    Функцианальные методы
    """

    def get_schedule(self, user, day):
        """
        Получает текст расписания из базы данных и отправляет пользователю его вместе с меню
        :param user: данные user из базы данных
        :param day: название дня, когда требуется получить расписание
        :return:
        """
        if day == "сегодня" or day == "завтра":
            if day == "сегодня":
                date = datetime.datetime.today() + datetime.timedelta(hours=0)
            elif day == "завтра":
                date =(datetime.datetime.today() + datetime.timedelta(days=1, hours=0))
            day = date.strftime('%d/%m/%Y')
            data = self.model.get_schedule(user, day)
            if data is None:
                self.vk.messages.send(
                    peer_id=user.user_id,
                    random_id=get_random_id(),
                    message="Не удалось получить расписание, попробуйте позже",
                )
            elif data == []:
                response = f"📅 {date_name(date)}, {day}\nНет пар"
            elif data is not None:
                response = [f"📅 {date_name(date)}, {day}"]
                for object in data:
                    if object.pair_location is None:
                        pair_location = ""
                    else:
                        pair_location = f"\nГде: {object.pair_location}"
                    if object.pair_teacher is None:
                        pair_teacher = ""
                    else:
                        pair_teacher = f"\nКто: {object.pair_teacher}"
                    if object.pair_type == "Экзамен":
                        pair_type = f"\n❗ ️Экзамен ❗️"
                    else:
                        pair_type = f"\n{object.pair_type}"
                    response.append(f"⏱{object.pair_time}⏱\n{object.pair_name}{pair_type}{pair_location}{pair_teacher}")
                response = '\n\n'.join(response)
            self.vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message=response,
            )
        elif day == "следующая неделя" or day == "эта неделя":
            if day == "эта неделя":
                weekrange = range(6)
            elif day == "следующая неделя":
                weekrange = range(7, 13)
            weekday = (datetime.datetime.today() + datetime.timedelta(hours=0)).weekday()
            response = []
            for delta in weekrange:
                date = (datetime.datetime.today() + datetime.timedelta(days=delta - weekday, hours=0))
                day = date.strftime('%d/%m/%Y')
                data = self.model.get_schedule(user, day)
                if data is None:
                    self.vk.messages.send(
                        peer_id=user.user_id,
                        random_id=get_random_id(),
                        message="Не удалось получить расписание, попробуйте позже",
                    )
                elif data == []:
                    response.append(f"\n📅 {date_name(date)}, {day}\nНет пар")
                elif data is not None:
                    response.append(f"\n📅 {date_name(date)}, {day}")
                    for object in data:
                        if object.pair_location is None:
                            pair_location = ""
                        else:
                            pair_location = f"\nГде: {object.pair_location}"
                        if object.pair_teacher is None:
                            pair_teacher = ""
                        else:
                            pair_teacher = f"\nКто: {object.pair_teacher}"
                        if object.pair_type == "Экзамен":
                            pair_type = f"\n❗ ️Экзамен ❗️"
                        else:
                            pair_type = f"\n{object.pair_type}"
                        response.append(" ")
                        response.append(
                            f"⏱{object.pair_time}⏱\n{object.pair_name}{pair_type}{pair_location}{pair_teacher}")
            response_text = ""
            for object in response:
                response_text += object + "\n"
            self.vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message=response_text,
            )
        self.main_menu(user)


    def update_group_name(self, user, message):
        """
        Обновляет группу пользователя, при этом делая запрос расписания с ИОПа
        :param user:
        :param message:
        :return:
        """
        message = message.upper().replace(" ", "")
        group_model = self.model.update_group_name(user, message)
        if group_model is not None:
            if self.model.get_schedule(user, (datetime.datetime.today() + datetime.timedelta(hours=0)).strftime('%d/%m/%Y')) is None:
                self.vk.messages.send(
                    peer_id=user.user_id,
                    random_id=get_random_id(),
                    message="Ищем вашу группу...",
                )
                if self.model.update_schedule(user) == True:
                    message = f'Ваша группа успешно изменена на "{message}"'
                else:
                    message = f'Не удалось изменить группу на "{message}"'
                self.vk.messages.send(
                    peer_id=user.user_id,
                    random_id=get_random_id(),
                    message=message,
                )
            else:
                self.vk.messages.send(
                    peer_id=user.user_id,
                    random_id=get_random_id(),
                    message=f'Ваша группа успешно изменена на "{message}"',
                )
        else:
            self.vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message=f'Не удалось изменить группу на "{message}"',
            )

    def find_teacher(self, user, teacher_name):
        self.vk.messages.send(
            peer_id=user.user_id,
            random_id=get_random_id(),
            message='Ищем преподавателя...',
            keyboard=VkKeyboard().get_empty_keyboard(),
        )
        teacher = self.model.find_teacher(user, teacher_name)
        if teacher is not None:
            keyboard = VkKeyboard()

            keyboard.add_button('Сегодня', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('Завтра', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()

            keyboard.add_button('Эта неделя', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('Следующая неделя', color=VkKeyboardColor.DEFAULT)
            keyboard.add_line()

            keyboard.add_button('Назад к меню', color=VkKeyboardColor.PRIMARY)
            self.vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message=f'Найденный преподаватель: {teacher[1]}\nВыберите промежуток',
                keyboard=keyboard.get_keyboard()
            )
            self.model.update_condition_teacher(user, teacher[0])
            return teacher
        else:
            self.vk.messages.send (
				peer_id=user.user_id,
				random_id=get_random_id(),
				message='Преподаватель не найден',
			)
            self.model.update_condition_teacher(user, None)
            return None


