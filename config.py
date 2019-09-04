import os

basedir = os.path.abspath(os.path.dirname(__file__))

# НАСТРОЙКИ СЕРВЕРА
SERVER_URL = "http://127.0.0.1:5000/"

# ИОП
LOGIN = ""
PASSWORD = ""

# VK CONFIG
TOKEN = ""
GROUP_ID = ""

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bot'
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:postgres@localhost:5432/bot"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
