import threading

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

"""
Запуск лонгпула и передача event на обработку в отдельном потоке
"""
def vk_bot_main(bot):
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

"""
Обработка сообщений пользователей
"""
def vk_bot_from_user(bot, event):

    message = event.obj.text
    message_lower = message.lower()
    user = bot.model.check_user(str(event.obj.peer_id))

    if user.condition_menu == "MENU":
        """
        Главное меню
        """
        if message_lower in ["расписание"]:
            bot.model.update_condition_menu(user, "CHANGE_GROUP")
            bot.change_group_menu(user)
        elif message_lower in ["сегодня", "завтра", "следующая неделя", "эта неделя"]:
            flow = threading.Thread(target=bot.get_schedule, args=(user, message_lower,))
            flow.start()
        elif message_lower in ["поиск преподавателя"]:
            bot.model.update_condition_menu(user, "FIND_TEACHER_START")
            bot.find_teacher_start(user)
        elif message_lower in ["написать нам"]:
            bot.model.update_condition_menu(user, "CHAT")
        elif message_lower in ["настройки"]:
            bot.model.update_condition_menu(user, "SETTINGS")
            bot.settings_menu(user)
        else:
            bot.main_menu(user)

    elif user.condition_menu == "FIND_TEACHER_START":
        if bot.find_teacher(user, message) is not None:
            bot.model.update_condition_menu(user, "FIND_TEACHER")
        else:
            bot.model.update_condition_menu(user, "MENU")
            bot.main_menu(user)

    elif user.condition_menu == "FIND_TEACHER":
        if message_lower in ["сегодня", "завтра", "следующая неделя", "эта неделя"]:
            pass
            # TODO Дописать
        else:
            bot.model.update_condition_teacher(user, None)
            bot.model.update_condition_menu(user, "MENU")
            bot.main_menu(user)

    elif user.condition_menu == "CHAT":
        pass
        # TODO дописать

    elif user.condition_menu == "SETTINGS":
        """
        Меню настроек
        """
        if message_lower == "выбрать группу":
            bot.model.update_condition_menu(user, "CHANGE_GROUP")
            bot.change_group_menu(user)
        elif message_lower == "назад к меню":
            bot.model.update_condition_menu(user, "MENU")
            bot.main_menu(user)
        else:
            bot.settings_menu(user)

    elif user.condition_menu == "CHANGE_GROUP":
        """
        Изменение группы пользователя
        """
        bot.model.update_condition_menu(user, "MENU")
        bot.update_group_name(user, message)
        bot.main_menu(user)

    else:
        bot.main_menu(user)
        bot.model.update_condition_menu(user, "MENU")


"""
Обработка сообщений в беседах
"""
def vk_bot_from_chat(bot, event):
    print(f"Сообщение в беседе {event.chat_id}")

