import asyncio
import logging
import time
from asyncio import Event, sleep

import schedule
from aiomisc.service.base import Service
from aiovk import TokenSession

from app.models import User, UserProxy
from .dependency import connection
from .bot import Bot
from .utils import constants as const

log = logging.getLogger(__name__)


class BotService(Service):
    __dependencies__ = ("db_write",)
    token: str
    group_id: str
    session: TokenSession
    db_write: connection

    async def start(self):
        self.session = TokenSession(access_token=self.token)
        bot = Bot(self.session, group_id=self.group_id, loop=self.loop, db=self.db_write)
        while True:
            await bot.main_loop()

    async def stop(self, exception=None):
        await self.session.close()


class BotSubscriptionService(Service):
    __dependencies__ = ("db_write",)
    token: str
    bot: Bot
    session: TokenSession
    db_write: connection
    exit_event: Event

    async def schedule_distribution(self):
        """
        Рассылает расписание пользователям
        """
        async with self.db_write() as conn:
            users = (UserProxy(user) for user in
                     await (
                         await conn.execute(
                             User.filter_by_time(time.strftime("%H:%M", time.localtime()))
                         )).fetchall())
        for user in users:
            if user.subscription_days is not None and user.subscription_days != const.CHANGES:
                if user.subscription_days == const.SUBSCRIPTION_TODAY:
                    await self.bot.send_schedule(user, days=1, text="Ваше расписание на сегодня\n\n")
                elif user.subscription_days == const.SUBSCRIPTION_TOMORROW:
                    await self.bot.send_schedule(user, start_day=1, days=1, text="Ваше расписание на завтра\n\n")
                elif user.subscription_days == const.SUBSCRIPTION_TODAY_TOMORROW:
                    await self.bot.send_schedule(user, days=2, text="Ваше расписание на сегодня и завтра\n\n")
                elif user.subscription_days == const.SUBSCRIPTION_WEEK:
                    await self.bot.send_schedule(user, days=7, text="Ваше расписание на 7 дней\n\n")
                elif user.subscription_days == const.SUBSCRIPTION_NEXT_WEEK:
                    await self.bot.send_schedule(user, start_day=7, days=7,
                                                 text="Ваше расписание на следующую неделю\n\n")

    async def start(self):
        self.exit_event = Event()
        self.session = TokenSession(access_token=self.token)
        self.bot = Bot.without_longpool(self.session)
        await self.schedule_distribution()

        schedule.every().minute.at(":00").do(
            asyncio.run_coroutine_threadsafe, self.schedule_distribution(), self.loop
        )
        while not self.exit_event.is_set():
            schedule.run_pending()
            await sleep(1)

    async def stop(self, exception=None):
        self.exit_event.set()
        await self.session.close()
