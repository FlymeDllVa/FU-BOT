import os

basedir = os.path.abspath(os.path.dirname(__file__))

# НАСТРОЙКИ СЕРВЕРА
SERVER_URL = "http://127.0.0.1:5000/"
CALENDAR_LINK = lambda group: f'http://84.201.185.101/api/v1/schedule/{group}/calendar.ics'

# ИОП
LOGIN = ""
PASSWORD = ""

# VK CONFIG
TOKEN = "80144b9aad54d7e52486556322002512cfb9b0091fe30530258648532b75324c75330b80a77d2aa46b77e"
current_id = "174550671"


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bot'
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:postgres@localhost:5432/bot"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
