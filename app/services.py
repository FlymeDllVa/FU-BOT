import asyncio
import logging
import time
from asyncio import Event, sleep, TimeoutError

import schedule
from aiomisc.service.base import Service
from aiovk import TokenSession
from aiovk.drivers import HttpDriver
from aiohttp import ClientError
from ujson import loads

from app.models import User, UserProxy
from .dependency import connection
from .bot import Bot
from .utils import constants as const

log = logging.getLogger(__name__)


class FixedDriver(HttpDriver):
    async def json(self, url, params, timeout=None):
        try:
            if url.split("/")[-1] == "messages.send":
                async with self.session.post(
                    url, data=params, timeout=timeout or self.timeout
                ) as response:
                    return await response.json(loads=loads)
            async with self.session.get(
                url, params=params, timeout=timeout or self.timeout
            ) as response:
                return await response.json(loads=loads)
        except (ClientError, TimeoutError):
            log.warning("Vk Timeout error on url %s", url)
            await sleep(5)
            return await self.json(url, params, timeout)

    async def get_text(self, url, params, timeout=None):
        try:
            async with self.session.get(url, params=params, timeout=timeout or self.timeout) as response:
                return response.status, await response.text()
        except (ClientError, TimeoutError):
            log.warning("Vk Timeout error on url %s", url)
            await sleep(5)
            return await self.get_text(url, params, timeout)


class BotService(Service):
    __dependencies__ = ("db_write",)
    token: str
    group_id: str
    session: TokenSession
    db_write: connection

    async def start(self):
        self.session = TokenSession(access_token=self.token, driver=FixedDriver())
        bot = Bot(
            self.session, group_id=self.group_id, loop=self.loop, db=self.db_write
        )
        self.loop.create_task(bot.vk_bot_answer_unread())
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
            users = (
                UserProxy(user)
                for user in await (
                    await conn.execute(
                        User.filter_by_time(time.strftime("%H:%M", time.localtime()))
                    )
                ).fetchall()
            )
        for user in users:
            if (
                user.subscription_days is not None
                and user.subscription_days != const.CHANGES
            ):
                if user.subscription_days == const.SUBSCRIPTION_TODAY:
                    await self.bot.send_schedule(
                        user, days=1, text="Ваше расписание на сегодня\n\n"
                    )
                elif user.subscription_days == const.SUBSCRIPTION_TOMORROW:
                    await self.bot.send_schedule(
                        user, start_day=1, days=1, text="Ваше расписание на завтра\n\n"
                    )
                elif user.subscription_days == const.SUBSCRIPTION_TODAY_TOMORROW:
                    await self.bot.send_schedule(
                        user, days=2, text="Ваше расписание на сегодня и завтра\n\n"
                    )
                elif user.subscription_days == const.SUBSCRIPTION_WEEK:
                    await self.bot.send_schedule(
                        user, days=7, text="Ваше расписание на 7 дней\n\n"
                    )
                elif user.subscription_days == const.SUBSCRIPTION_NEXT_WEEK:
                    await self.bot.send_schedule(
                        user,
                        start_day=7,
                        days=7,
                        text="Ваше расписание на следующую неделю\n\n",
                    )

    async def start(self):
        self.exit_event = Event()
        self.session = TokenSession(access_token=self.token, driver=FixedDriver())
        self.bot = Bot.without_longpool(self.session, loop=self.loop, db=self.db_write)

        logging.getLogger("schedule").setLevel(logging.WARNING)

        def distribution():
            asyncio.run_coroutine_threadsafe(self.schedule_distribution(), self.loop)

        schedule.every().minute.at(":00").do(distribution)
        while not self.exit_event.is_set():
            schedule.run_pending()
            await sleep(1)

    async def stop(self, exception=None):
        self.exit_event.set()
        await self.session.close()
