import os

basedir = os.path.abspath(os.path.dirname(__file__))

# НАСТРОЙКИ СЕРВЕРА
CALENDAR_LINK = lambda group: f'http://84.201.185.101/api/v1/schedule/{group}/calendar.ics'

# VK CONFIG
TOKEN = "97d0fb8a89e891819942c11c5ada66c40d7830b6eaf532e313d7cdd754d90f190fbbb4e3e71b91717e27d"
GROUP_ID = "185809180"


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bot'
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:postgres@localhost:5432/bot"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_SETTINGS = {}
    # DB_SETTINGS = {pool_recycle=600} # MySQL
    # DB_SETTINGS = {pool_size=30, max_overflow=10} # PostgeSQL
