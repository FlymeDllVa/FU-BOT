import logging
from threading import Thread

from app import models
from app.workers import start_bot, start_workers
from app.utils.vk import Bot
from config import TOKEN, GROUP_ID

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(asctime)-15s - %(message)s')
log = logging.getLogger(__name__)


def start_app():
    bot = Bot(TOKEN, GROUP_ID)
    bot_flow = Thread(target=start_bot, args=(bot,))
    workers_flow = Thread(target=start_workers, args=(bot,))
    bot_flow.start()
    workers_flow.start()
