import requests

def authorization(login, password, max_attempt = 1, attempt = 0):
    """
	Производит авторизацию на портале для дальнейших запросов
	:param login: Логин от ИОПа
	:param password: Пароль от ИОПа
    :max_attempt: Максимальное количество попыток авторизации
    :attempt: Счетчик попыток авторизации
	:return: Сессия с куки или None
	"""
    if attempt >= max_attempt: return None
    try:
        return requests.session().post('https://portal.fa.ru/CoreAccount/LogOn', data={'Login': login, 'Pwd': password})
    except Exception:
        attempt += 1
        print(f"Ошибка авторизации на ИОП ${attempt}")
        authorization(login, password, attempt=attempt)

def teacher_search(session, teacher_name):
    """
	Ищет преподавателя по сессии
	:param session: Сессия от ИОПа
	:param teacher_name: ФИО преподавателя
	:return: Кортеж из ID преподавателя и ФИО
	"""
    response = session.post('https://portal.fa.ru/CoreUser/SearchDialogResultAjax', data={'Name': teacher_name, 'Roles': 16}).json()
    if not response:
        return None
    else:
        return response[0]['id'], response[0]['name']

