"""

В файле хранятся функции, которые использует cron

"""

import time

def schedule_distribution():
    # TODO дописать функцию
    print(time.strftime("%H:%M", time.localtime()))