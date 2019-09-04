import threading
import json

from vk_api.bot_longpoll import VkBotEventType
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

    user = User.search_user(event.obj.peer_id)
    payload = json.loads(getattr(event.obj, 'payload', '{}')) if 'payload' in event.obj else {}
    message = event.obj.text
    message_lower = message.lower()

    if message_lower == ("начать" or "start" or "сброс") or payload.get('command', '') == 'start':
        bot.send_main_menu(user)
    elif "menu" in payload:
        menu = payload["menu"]
        if menu == "main":
            bot.send_main_menu(user)
        elif menu == "schedule":
            bot.send_schedule_menu(user)
        elif menu == "schedule_show":
            bot.send_schedule(user, start_day=payload["start_day"], days=payload["days"])
        elif menu == "schedule_one_day":
            bot.send_one_day_schedule(user)
        elif menu == "search_teacher":
            bot.send_search_teacher(user)
        elif menu == "teachers":
            bot.send_teacher(user, payload)
        elif menu == "teacher_schedule_show":
            bot.send_teacher_schedule(user, start_day=payload["start_day"], days=payload["days"])
        elif menu == "settings":
            bot.send_settings_menu(user)
        elif menu == "show_groups" or menu == "show_location":
            bot.show_groups_or_location(user, payload["menu"])
        elif menu == "change_group":
            bot.send_choice_group(user)
        elif menu == "subscribe_to_newsletter":
            bot.subscribe_schedule(user)
        elif menu == "unsubscribe_to_newsletter":
            bot.unsubscribe_schedule(user)
        elif menu in ("subscribe_to_newsletter_today", "subscribe_to_newsletter_tomorrow",
                      "subscribe_to_newsletter_today_and_tomorrow", "subscribe_to_newsletter_this_week",
                      "subscribe_to_newsletter_next_week"):
            bot.update_subscribe_day(user, menu)
        elif menu == "cancel":
            user.cancel_changes()
            bot.send_main_menu(user)
        else:
            bot.send_main_menu(user)
    elif "menu" not in payload:
        if user.group_name == "CHANGES":
            bot.send_check_group(user, message_lower)
        elif user.found_teacher_name == "CHANGES" and user.found_teacher_id == 0:
            bot.search_teacher_schedule(user, message_lower)
        elif user.subscription_days == "CHANGES":
            bot.update_subscribe_time(user, message_lower)
        elif user.schedule_day_date == "CHANGES":
            bot.send_day_schedule(user, message_lower)
        else:
            bot.send_main_menu(user)


def vk_bot_answer_unread(bot):
    unread = bot.vk.messages.getConversations(filter='unread', count=25)

    # TODO разобраться с этим костылем
    class UserSimple:
        def __init__(self, id):
            self.id = id

    for conversation in unread['items']:
        # -- Если вдруг понадобится --
        # payload = json.loads(conversation['last_message']['payload']) if 'payload' in conversation[
        #     'last_message'] else {}
        user = conversation['last_message']['peer_id']
        try:
            # TODO решить что писать людям
            bot.send_main_menu(UserSimple(user))
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
