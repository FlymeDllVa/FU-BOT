
import vk_api

from app.models import Model
from app.vk.src.logger import Logger
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
    """
    Функцианальные методы
    """

    def update_group_name(self, user, message):
        message = message.upper().replace(" ", "")
        if self.model.update_group_name(user, message) is not None:

            self.vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message=f'Ваша группа успешно изменена на "{message}"',
            )
        else:
            self.vk.messages.send(
                peer_id=user.user_id,
                random_id=get_random_id(),
                message=f'Не удалось изменить группу на "{message.upper()}"',
            )