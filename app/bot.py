import threading
import json

from vk_api.bot_longpoll import VkBotEventType
from app.models import User
import app.utils.constants as const


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

    user = User.search_user(event.obj.peer_id)
    payload = json.loads(getattr(event.obj, 'payload', '{}')) if 'payload' in event.obj else {}
    message = event.obj.text
    message_lower = message.lower()

    if message_lower == ("начать" or "start" or "сброс") or payload.get('command', '') == 'start':
        bot.send_schedule_menu(user)
    elif const.PAYLOAD_MENU in payload:
        menu = payload[const.PAYLOAD_MENU]
        if menu == const.MENU_MAIN:
            bot.send_schedule_menu(user)
        elif menu == const.MENU_SCHEDULE:
            bot.send_schedule_menu(user)
        elif menu == const.MENU_SCHEDULE_SHOW:
            bot.send_schedule(user, start_day=payload[const.PAYLOAD_START_DAY], days=payload[const.PAYLOAD_DAYS])
        elif menu == const.MENU_SCHEDULE_SHOW_ONE:
            bot.send_one_day_schedule(user)
        elif menu == const.MENU_SEARCH_TEACHER:
            bot.send_search_teacher(user)
        elif menu == const.MENU_TEACHER:
            bot.send_teacher(user, payload)
        elif menu == const.MENU_SCHEDULE_FOUND:
            bot.send_teacher_schedule(user, start_day=payload[const.PAYLOAD_START_DAY],
                                      days=payload[const.PAYLOAD_DAYS])
        elif menu == const.MENU_SETTINGS:
            bot.send_settings_menu(user)
        elif menu == const.MENU_SET_SETTINGS:
            bot.show_groups_or_location(user, payload[const.PAYLOAD_TYPE])
        elif menu == const.MENU_CHANGE_GROUP:
            bot.send_choice_group(user)
        elif menu == const.MENU_SUBSCRIBE:
            bot.subscribe_schedule(user)
        elif menu == const.MENU_UNSUBSCRIBE:
            bot.unsubscribe_schedule(user)
        elif menu == const.MENU_UPDATE_SUBSCRIPTION:
            bot.update_subscribe_day(user, payload[const.PAYLOAD_TYPE])
        elif menu == const.MENU_CANCEL:
            user.cancel_changes()
            bot.send_schedule_menu(user)
        elif menu == const.MENU_CHOOSE_ROLE:
            bot.set_role(user, payload[const.PAYLOAD_ROLE])
        elif menu == const.MENU_GET_CALENDAR:
            bot.send_calendar(user, payload["army"])
        elif menu == const.MENU_SET_TEACHER:
            bot.set_teacher(user, payload)
        elif menu == const.MENU_SEARCH:
            bot.search(user)
        elif menu == const.MENU_SEARCH_GROUP:
            bot.search_group(user)
        else:
            bot.send_schedule_menu(user)
    elif const.PAYLOAD_MENU not in payload:
        if user.current_name == const.CHANGES:
            if user.role == const.ROLE_STUDENT:
                bot.send_check_group(user, message_lower)
            else:
                bot.search_teacher_to_set(user, message_lower)
        elif user.found_name == const.CHANGES and user.found_id == 0:
            if user.found_type == const.ROLE_TEACHER:
                bot.search_teacher_schedule(user, message_lower)
            else:
                bot.search_check_group(user, message_lower)
        elif user.subscription_days == const.CHANGES:
            bot.update_subscribe_time(user, message_lower)
        elif user.schedule_day_date == const.CHANGES:
            bot.send_day_schedule(user, message_lower)
        elif message == "📅":
            bot.chose_calendar(user)
        else:
            bot.send_schedule_menu(user)


def vk_bot_answer_unread(bot):
    unread = bot.vk.messages.getConversations(filter='unread', count=25)

    for conversation in unread['items']:
        # -- Если вдруг понадобится --
        # payload = json.loads(conversation['last_message']['payload']) if 'payload' in conversation[
        #     'last_message'] else {}
        user = conversation['last_message']['peer_id']
        try:
            # TODO решить что писать людям
            user = User.search_user(user)
            bot.send_schedule_menu(user)
        except Exception:
            bot.vk.messages.markAsRead(peer_id=user)


def vk_bot_from_chat(bot, event):
    """
    Обработка сообщений в беседах

    :param bot:
    :param event:
    :return:
    """

    print(f"Сообщение в беседе {event.chat_id}")
    # TODO Дописать функцианал для бесед
