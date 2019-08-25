import threading

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from app.models import User


def vk_bot_main(bot):
    """
    Запускает лонгпул и передает event в отдельном потоке

    :param bot:
    :return:
    """
    for event in bot.longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_user:
                flow = threading.Thread(target=vk_bot_from_user, args=(bot, event,))
                flow.start()
            elif event.from_chat:
                flow = threading.Thread(target=vk_bot_from_chat, args=(bot, event,))
                flow.start()
            else:
                print(event)


def vk_bot_from_user(bot, event):
    """
    Обработывает сообщения пользователей

    :param bot:
    :param event:
    :return:
    """

    message = event.obj.text
    message_lower = message.lower()
    user = User.search_user(event.obj.peer_id)

    if message_lower == ("начать" or "start" or "сброс") or user.position == "START":
        bot.start_menu(User.change_position(user, "START_GROUP"))

    # Стартовое меню
    elif user.position == "START_GROUP":
        if message_lower == "да":
            bot.choice_group(User.change_position(user, "GROUP_CHOICE"))
        elif message_lower == "нет":
            bot.main_menu(User.change_position(user, "MAIN_MENU"))
        else:
            bot.error_data(user)

    # Главное меню
    elif user.position == "MAIN_MENU":
        if message_lower == "расписание":
            bot.choice_group(User.change_position(user, "GROUP_CHOICE"))
        elif message_lower == "сегодня":
            bot.send_schedule(user, days=1)
        elif message_lower == "завтра":
            bot.send_schedule(user, start_day=1, days=1)
        elif message_lower == "эта неделя":
            bot.send_schedule(user, days=7)
        elif message_lower == "следующая неделя":
            bot.send_schedule(user, start_day=7, days=7)
        elif message_lower == "поиск преподавателя":
            # TODO Дописать поиск преподавателя
            pass
        elif message_lower == "настройки":
            bot.settings(User.change_position(user, "SETTINGS"))
        else:
            bot.main_menu(user=user, message="Пожайлуста, выберите пункт из меню")

    # Смена группы
    elif user.position == "GROUP_CHOICE":
        db_user = bot.check_group(user, message)
        if db_user:
            user = bot.change_group(db_user, True)
        else:
            user = bot.change_group(user, False)
        user = User.change_position(user, "MAIN_MENU")
        bot.main_menu(user=user)

    # Настройки
    elif user.position == "SETTINGS":
        if message_lower in ("изменить группу", "выбрать группу"):
            bot.choice_group(User.change_position(user, "GROUP_CHOICE"))
        elif message_lower in ("подписаться на расписание", "изменить подписку на расписание"):
            bot.subscribe_schedule(User.change_position(user, "SUBSCRIBE_TIME"))
        elif message_lower == "отписаться от подписки на расписание":
            bot.main_menu(User.change_position(bot.subscribe_error(user), "MAIN_MENU"))
        elif message_lower in ("назад", "◀️ назад"):
            bot.main_menu(User.change_position(user, "MAIN_MENU"))

    # Подписка на расписание
    elif user.position == "SUBSCRIBE_TIME":
        if message_lower in ("отмена", "меню", "назад", "◀️ назад"):
            user = bot.subscribe_error(user)
            bot.main_menu(User.change_position(user, "MAIN_MENU"))
        else:
            if bot.update_subscribe_time(user, message_lower):
                User.change_position(user, "SUBSCRIBE_DAY")
            else:
                bot.subscribe_schedule(bot.error_data(user, message="Напишите время или выберите из меню"))

    elif user.position == "SUBSCRIBE_DAY":
        if message_lower in ("отмена", "меню", "назад", "◀️ назад"):
            user = bot.subscribe_error(user)
            bot.main_menu(User.change_position(user, "MAIN_MENU"))
        if bot.update_subscribe_day(user, message_lower):
            bot.main_menu(User.change_position(user, "MAIN_MENU"))
        else:
            bot.error_data(user, message="Выберите промежуток в меню")


def vk_bot_from_chat(bot, event):
    """
    Обработка сообщений в беседах

    :param bot:
    :param event:
    :return:
    """

    print(f"Сообщение в беседе {event.chat_id}")
    # TODO Дописать функцианал для бесед


