from flask import url_for, redirect, session
# Из за того что в декораторе есть функция wrapper и она одинакова для всех в во flask файле
# по этому чтоб не путать flask одинаковыми переменными делаем именно это
# Без @wraps:
# Flask смотрит в код и видит:
# Роут /profile ведет к функции wrapper.
# Роут /settings ведет к функции wrapper.
# Итог: Конфликт имён. Flask падает с ошибкой, потому что для него это как две переменные с одинаковым названием в одном месте.
# С @wraps(f):
# Когда декоратор обрабатывает profile, он превращает wrapper в profile.
# Когда декоратор обрабатывает settings, он превращает второй wrapper в settings.
# Итог: Flask доволен, у каждой ручки свое уникальное имя, хотя код проверки внутри один и тот же.
from functools import wraps

def login_required(func):    

    @wraps(func)
    def wrapper(*args, **kwargs):

        if 'user_id' is not session:
            
            return redirect(url_for('user_login'))
        
        return func(*args, **kwargs)
    
    return wrapper