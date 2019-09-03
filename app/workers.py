import schedule
import time

from threading import Thread

from app.bot import vk_bot_main, vk_bot_answer_unread
from app.utils.vk import *
from config import *


def start_bot():
    """
    Запускат бота

    :return:
    """
    global bot
    print(" * BOT started")
    # TODO мож в другой поток бахнуть
    vk_bot_answer_unread(bot)
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
        if user.subscription_days is not None and user.subscription_days != "CHANGES":
            if user.subscription_days == "today":
                bot.send_schedule(user, days=1, text="Ваше расписание на сегодня\n")
            elif user.subscription_days == "tomorrow":
                bot.send_schedule(user, start_day=1, days=1, text="Ваше расписание на завтра\n")
            elif user.subscription_days == "today_and_tomorrow":
                bot.send_schedule(user, days=2, text="Ваше расписание на два дня\n")
            elif user.subscription_days == "this_week":
                bot.send_schedule(user, days=7, text="Ваше расписание на 7 дней вперед\n")
            elif user.subscription_days == "next_week":
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
