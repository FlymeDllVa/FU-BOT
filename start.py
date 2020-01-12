from os import getenv

from app import start_app

config = dict(
    db_host=getenv("DB_HOST") or "localhost",
    db_port=int(getenv("DB_PORT") or "3306"),
    db_user=getenv("DB_USER") or "root",
    db_pass=getenv("DB_PASS") or "password",
    db_database=getenv("DB_DATABASE") or "bot",
    db_connect_timeout=int(getenv("DB_TIMEOUT") or "18000"),
    vk_token=getenv("VK_TOKEN") or "default-token",
    vk_group_id=getenv("GROUP_ID") or "default-group",
    debug=getenv("DEBUG") != "False",
)

if __name__ == "__main__":
    start_app(config)
