from os import getenv

from app import start_app

config = dict(
    db_host=getenv('DB_HOST') or 'localhost',
    db_port=int(getenv('DB_PORT') or '3306'),
    db_user=getenv('DB_USER') or 'root',
    db_pass=getenv('DB_PASS') or 'password',
    db_database=getenv('DB_DATABASE') or 'bot',
    db_connect_timeout=int(getenv('DB_TIMEOUT') or '18000'),
    vk_token=getenv(
        'VK_TOKEN') or '97d0fb8a89e891819942c11c5ada66c40d7830b6eaf532e313d7cdd754d90f190fbbb4e3e71b91717e27d',
    vk_group_id=getenv('GROUP_ID') or '185809180',
)

if __name__ == '__main__':
    start_app(config)
