from flask import Flask, render_template, url_for, request
import mysql.connector
from mysql.connector import Error
import time
from config import MYSQL_CONFIG
import random

app = Flask(__name__)

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
def get_user():
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
        
        return render_template('users.html', users=data, title='Пользователи')
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
        
        # логируем регистрированного пользователя в ком.строку
        print(f"новые данные: {first_name}, {phone}")
        
        # создаем соединения и курсор для работы с БД
        conn = get_db()
        cur = conn.cursor()
        
        # значения для вставки в mysql - список для того что бы была возможность адаптивности
        sql_values = [first_name, last_name, middle_name, password, phone, random.randint(100000000000, 999999999999)]
        
        # есть ли почта? да создаем поле и дданные, нет оставляем все пустым
        if email:
            s = ', %s'
            sql_values.append(email)
            e = ', `email`'
        else:
            s = ''
            e= ''
        
        # создаем запрос добавления без данных
        sql_into = f"""
        INSERT INTO users(`first_name`, `last_name`, `middle_name`, `password`, `phone`, `card_number`{e}) 
        VALUES (%s, %s, %s, %s, %s, %s{s});
        """
        
        # вставляем данные
        cur.execute(sql_into, tuple(sql_values))
        
        # сохраняем и закрываем соединения
        conn.commit()
        cur.close()
        conn.close()
        
        return f"Вставка прошла успешно"
            
    return render_template('register.html', title='Регистрация')


@app.route('/test', methods=['GET'])
def get_request():
    print(request)
    return str(f" {request.base_url}, {request.headers}, {request.method}, {request.args}, {request.get_data()}")


if '__main__' == __name__:
    app.run(debug=True, host='0.0.0.0', port=5000)