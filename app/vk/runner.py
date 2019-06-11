import threading
import schedule

from config import Config
from app.vk_bot import vk_bot_main
from app.vk.src.bot import *
from app.workers import *

"""
Run Bot
"""
def start_bot():
    global bot
    print(" * BOT started")
    while True:
        try:
            vk_bot_main(bot)
        except Exception as error:
            print("ОШИБКА", error)
            time.sleep(1)

"""
Run Workers
"""
def start_worker():
    global bot
    print(" * CRON started")
    schedule.every().minute.at(":00").do(schedule_distribution)
    while True:
        schedule.run_pending()
        time.sleep(1)

"""
Run program
"""
bot = Bot(Config.TOKEN, Config.GROUP_ID)
for i in range(2):
    if i == 0: flow = threading.Thread(target=start_bot)
    if i == 1: flow = threading.Thread(target=start_worker)
    flow.start()


