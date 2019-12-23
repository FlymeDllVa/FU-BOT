# TODO Сделать рассылку
# import schedule
# import time
# import logging
#
# from .bot import vk_bot_main, vk_bot_answer_unread
# from .models import User
# from .utils import constants as const
#
# log = logging.getLogger(__name__)
# schedule_log = logging.getLogger('schedule')
# schedule_log.setLevel(logging.WARNING)
#
#
# def schedule_distribution(bot):
#     """
#     Рассылает расписание пользователям
#
#     :param bot:
#     :return:
#     """
#
#     for user in User.filter_by_time(time.strftime("%H:%M", time.localtime())):
#         if user.subscription_days is not None and user.subscription_days != const.CHANGES:
#             if user.subscription_days == const.SUBSCRIPTION_TODAY:
#                 bot.send_schedule(user, days=1, text="Ваше расписание на сегодня\n\n")
#             elif user.subscription_days == const.SUBSCRIPTION_TOMORROW:
#                 bot.send_schedule(user, start_day=1, days=1, text="Ваше расписание на завтра\n\n")
#             elif user.subscription_days == const.SUBSCRIPTION_TODAY_TOMORROW:
#                 bot.send_schedule(user, days=2, text="Ваше расписание на сегодня и завтра\n\n")
#             elif user.subscription_days == const.SUBSCRIPTION_WEEK:
#                 bot.send_schedule(user, days=7, text="Ваше расписание на 7 дней\n\n")
#             elif user.subscription_days == const.SUBSCRIPTION_NEXT_WEEK:
#                 bot.send_schedule(user, start_day=7, days=7, text="Ваше расписание на следующую неделю\n\n")
#
#
# def start_workers(bot):
#     """
#     Запускает работников
#
#     :return:
#     """
#     log.info(" * CRON started")
#     schedule.every().minute.at(":00").do(schedule_distribution, bot=bot)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
