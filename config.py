import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ИОП
    LOGIN=""
    PASSWORD=""
    WEEKDAY = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    # VK CONFIG
    TOKEN=""
    GROUP_ID=""


class Flask_Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bot'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'bot.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    