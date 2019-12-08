import threading
import json
import logging

from vk_api.bot_longpoll import VkBotEventType

from app.models import User
import app.utils.constants as const

logger = logging.getLogger(__name__)


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
                logger.warning('unexpected event in bot - %s', event)


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
        if menu in const.MENUS_LIST:
            getattr(bot, menu)(user, payload=payload)
        else:
            logger.warning('unexpected payload %s , user %s', payload, user.id)
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
            logger.info('%s asked for calendar for group %s', user.id, user.current_name)
            bot.chose_calendar(user)
        else:
            bot.send_schedule_menu(user)


def vk_bot_answer_unread(bot):
    unread = bot.vk.messages.getConversations(filter='unread', count=25)
    logger.info('Answering %s unread messages', unread.get('unread_count', 0))
    for conversation in unread['items']:
        # -- Если вдруг понадобится --
        # payload = json.loads(conversation['last_message']['payload']) if 'payload' in conversation[
        #     'last_message'] else {}
        user = conversation['last_message']['peer_id']
        try:
            # TODO решить что писать людям
            user = User.search_user(user)
            bot.send_schedule_menu(user)
        except Exception as e:
            logger.warning('Exception in unread: user %s for %s', user, e)
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
