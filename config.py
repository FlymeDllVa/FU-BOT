import os

# VK CONFIG
TOKEN = os.environ.get(
    'VK_TOKEN') or "97d0fb8a89e891819942c11c5ada66c40d7830b6eaf532e313d7cdd754d90f190fbbb4e3e71b91717e27d"
GROUP_ID = os.environ.get('VK_GROUP_ID') or "185809180"


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bot'
    SQLALCHEMY_DATABASE_URI = os.environ.get('VK_DB_URL') or 'postgresql://postgres:postgres@localhost:5432/bot'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_SETTINGS = {'wait_timeout': 30} if 'mysql' in SQLALCHEMY_DATABASE_URI else {}
    SQLALCHEMY_SETTINGS = {'pool_recycle': 600, 'pool_size': 30,
                           'pool_pre_ping': True} if 'mysql' in SQLALCHEMY_DATABASE_URI else {}
    # DB_SETTINGS = {'pool_recycle': 600} # MySQL
    # DB_SETTINGS = {'pool_size': 30, 'max_overflow': 10} # PostgeSQL
