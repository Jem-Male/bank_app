from flask import Flask, render_template, url_for, request, session, redirect
import mysql.connector
from mysql.connector import Error
import time
from werkzeug.security import generate_password_hash, check_password_hash # для хеширование паролей
from config import MYSQL_CONFIG, SECRET_KEY
import random

app = Flask(__name__)
app.secret_key = SECRET_KEY


def get_db():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    
    except Error as e:
        print("Ошибка соединения: {e}")
        return None
    


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', title='Главная - Банк')


@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db()
    if conn is None:
        return f"Ошибка к подключению БД", 500
    try:
        # dictionary=True ставим ЗДЕСЬ. Это настройка "пальца", а не "телефона"
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM users')
        data = cur.fetchall()
        
        # Данные получили, курсор больше не нужен
        cur.close()
        
        # Закрываем соединение, чтобы не висело в Process List
        conn.close()
        
        return redirect(url_for('user_login')) # теперь после регистрации пользователя перенаправляют на страницу входа
    
    except Error as e:
        return f"Ошибка при выполнении запроса: {e}", 500


@app.route('/register', methods=['GET','POST'])
def user_registration():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        middle_name = request.form.get('middle_name')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # 1. Получаем Email
        # Если поле пустое, .get() вернет пустую строку ''. 
        # Конструкция (A or B) вернет B, если A пустое.
        # То есть email станет None, если пользователь ничего не ввел.
        email = request.form.get('email') or None
        
        # логируем регистрированного пользователя в ком.строку
        print(f"новые данные: {first_name}, {phone}")
        
        # 2. Создаем SQL запрос
        # Обрати внимание: мы ВСЕГДА пишем `email` и `%s`.
        # Мы не меняем текст запроса.
        sql_into = """
            INSERT INTO users
            (first_name, last_name, middle_name, password, phone, card_number, email) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        # 3. Собираем значения
        # Если в переменной email лежит None, в базу запишется NULL.
        # Если там "mail@mail.ru", запишется строка.
        # Генерацию карты тоже лучше вынести в переменную для читаемости.
        hashed_password = generate_password_hash(password)
        card_num = str(random.randint(100000000000, 999999999999))
        
        # создаем значения для values
        vals = (first_name, last_name, middle_name, hashed_password, phone, card_num, email)
        
        try:
            # создаем соединения и курсор для работы с БД
            conn = get_db()
            cur = conn.cursor()
            
            # 4. Выполняем
            cur.execute(sql_into, vals)
            
            # сохраняем и закрываем соединения
            conn.commit()
            cur.close()
            conn.close()
            
            return f"Вставка прошла успешно"
        
        
        except Error as e:
            return f"Ошибка sql - {e}"
            
    return render_template('register.html', title='Регистрация')


@app.route('/login', methods=['GET','POST'])
def user_login():
    if request.method == 'POST':
        
        login_input = request.form.get('login_input')
        password = request.form.get('password')
        
        try:
            conn = get_db()
            cur = conn.cursor(dictionary=True)
            
            sql_select = """
            SELECT last_name, id, password, phone, email from users
            WHERE (email = %s or phone = %s) and is_deleted = 0;
            """
            
            value = (login_input, login_input)
            cur.execute(sql_select, value)
            
            res = cur.fetchone()
            
            cur.close()
            conn.close()
            
            # если пользователь не найден - создаем флаг с ошибкой
            # так удобнее создавать ошибки и явно указывать что не так
            # и лишь в конце дать готовый ответ со страницой
            if res is None:
                invalid = 'Такого пользователя нет'
                
            # check_password_hash() - медот для проверки пароля
            # сперва хэш потом то что ввел пользователь
            elif check_password_hash(res['password'], password):
                
                # тут создается session по его id
                session['user_id'] = res['id'] 
                return redirect(url_for('profile'))
            
            else:
                invalid = 'Неверный пароль'
            
            return render_template('login.html', invalid = invalid)
        
        except Error as e:
            return f"ошибка - {e}"
         
    return render_template('login.html', invalid = 0)


@app.route('/me')
def profile():
    """Страница профиля"""
    
    # здесь мы пробуем получить сессию от пользователя
    # а именно пытаемся получить его id чтобы найти его в БД
    user_id = session.get('user_id')
    
    # если сессии нет опять перенаправляем его на страницу входа
    if user_id is None:
        
        return redirect(url_for('user_login'))
    try:
        # танцы с бубнами ради подключения к БД чтобы получить пользователя по его id
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        
        sql_select = """
        SELECT id, last_name, middle_name, password, phone, email , card_number, balance from users
        WHERE id = %s and is_deleted = 0;
        """
        
        value = (user_id,)
        cur.execute(sql_select, value)
        res = cur.fetchone()
        cur.close()
        conn.close()
        
    except Error as e:
        return f"ошибка подключения к БД - {e}"
    
    # если такого пользователя нет или же он уже удален - (is_deleted = 1, True)
    # то мы удаляем его протухшие куки
    # ведь уже тут он смог пройти проверку на наличия session
    if res is None:
        
        # удаляем через метод pop() 
        # но если все же у метода не получится найти user_id session то просто возвращает None
        # то етсь мягкое удаление
        session.pop('user_id', None)
        # как бы мы говорим - удалить! = ничего
        # метод такой - оке, "удали ничего"
        
    return render_template('profile.html', user = res)

@app.route('/test', methods=['GET'])
def get_request():
    print(request)
    return str(f" {request.base_url}, {request.headers}, {request.method}, {request.args}, {request.get_data()}")


if '__main__' == __name__:
    app.run(debug=True, host='0.0.0.0', port=5000)