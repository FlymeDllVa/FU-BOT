import schedule
import time

from threading import Thread

from app.bot import vk_bot_main
from app.models import User
from app.utils.vk import *
from config import *


def start_bot():
    """
    Запускат бота

    :return:
    """
    global bot
    print(" * BOT started")
    while True:
        try:
            vk_bot_main(bot)
        except Exception as error:
            print("ОШИБКА", error)
            time.sleep(1)


def schedule_distribution(bot):
    """
    Рассылает расписание пользователям

    :param bot:
    :return:
    """

    for user in User.filter_by_time(time.strftime("%H:%M", time.localtime())):
        if user.subscription_days == "ТЕКУЩИЙ":
            bot.send_schedule(user, days=1)
        elif user.subscription_days == "СЛЕДУЮЩИЙ":
            bot.send_schedule(user, start_day=1, days=1)
        elif user.subscription_days == "ТЕКУЩИЙ_И_СЛЕДУЮЩИЙ":
            bot.send_schedule(user, days=2)
        elif user.subscription_days == "ТЕКУЩАЯ_НЕДЕЛЯ":
            bot.send_schedule(user, days=7)
        elif user.subscription_days == "СЛЕДУЮЩАЯ_НЕДЕЛЯ":
            bot.send_schedule(user, start_day=7, days=7)


def start_workers():
    """
    Запускает работников

    :return:
    """
    global bot
    print(" * CRON started")
    schedule.every().minute.at(":00").do(schedule_distribution, bot=bot)
    while True:
        schedule.run_pending()
        time.sleep(1)


"""
Run program
"""
bot = Bot(TOKEN, GROUP_ID)
bot_flow = Thread(target=start_bot)
workers_flow = Thread(target=start_workers)
bot_flow.start()
workers_flow.start()
