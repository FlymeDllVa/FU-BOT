import logging

from aiomisc import entrypoint

from app import models
from app.dependency import config_dependency
from app.services import BotService

log = logging.getLogger(__name__)


def start_app(config: dict):
    config_dependency(config)
    with entrypoint(
            BotService(
                token=config['vk_token'],
                group_id=config['vk_group_id']),
            log_level=logging.DEBUG if config['debug'] else logging.INFO
    ) as loop:
        log.info('Bot started')
        loop.run_forever()
