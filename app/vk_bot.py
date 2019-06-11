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
    user = bot.model.check_user(str(event.obj.peer_id))

    if user.condition_menu == "MENU":
        """
        Главное меню
        """
        if message.lower() == "расписание":
            bot.model.update_condition_menu(user, "CHANGE_GROUP")
            bot.change_group_menu(user)
        elif message.lower() == "настройки":
            bot.model.update_condition_menu(user, "SETTINGS")
            bot.settings_menu(user)
        else:
            bot.main_menu(user)
    elif user.condition_menu == "SETTINGS":
        """
        Меню настроек
        """
        if message.lower() == "выбрать группу":
            bot.model.update_condition_menu(user, "CHANGE_GROUP")
            bot.change_group_menu(user)
        elif message.lower() == "назад к меню":
            bot.model.update_condition_menu(user, "MENU")
            bot.main_menu(user)
        else:
            bot.settings_menu(user)
    elif user.condition_menu == "CHANGE_GROUP":
        """
        Изменение группы пользователя
        """
        bot.update_group_name(user, message)
        bot.main_menu(user)
        bot.model.update_condition_menu(user, "MENU")
    else:
        bot.main_menu(user)
        bot.model.update_condition_menu(user, "MENU")


"""
Обработка сообщений в беседах
"""
def vk_bot_from_chat(bot, event):
    print(f"Сообщение в беседе {event.chat_id}")

