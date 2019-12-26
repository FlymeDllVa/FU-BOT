import logging

from aiomisc.service.base import Service
from aiovk import TokenSession

from .dependency import connection
from .bot import Bot

log = logging.getLogger(__name__)


class BotService(Service):
    __dependencies__ = ("db_write",)
    token: str
    group_id: str
    session: TokenSession
    db_write: connection

    async def start(self):
        self.session = TokenSession(access_token=self.token)
        bot = Bot(self.session, self.group_id, loop=self.loop, db=self.db_write)
        while True:
            await bot.main_loop()

    async def stop(self, exception=None):
        await self.session.close()
