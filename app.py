# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_ # Нужно для условия "ИЛИ"
import random

# Наши новые файлы
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import db, User

app = Flask(__name__)

# --- Настройка ---
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY

# Инициализация БД
db.init_app(app)

# Создание таблиц при запуске
with app.app_context():
    db.create_all() 
    # SQLAlchemy посмотрит на models.py и создаст таблицу users в MySQL, если её нет.
    print("БД подключена и таблицы проверены.")

# --- Маршруты ---

@app.route('/')
def index():
    return render_template('index.html', title='Главная - Банк')

@app.route('/users')
def get_users():
    # СТАРЫЙ КОД: cursor.execute('SELECT * FROM users')
    # НОВЫЙ КОД:
    users_list = User.query.all() 
    return render_template('users.html', users=users_list, title='Пользователи')

@app.route('/register', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'POST':
        # Сбор данных из формы
        fname = request.form.get('first_name')
        lname = request.form.get('last_name')
        mname = request.form.get('middle_name')
        phone = request.form.get('phone')
        email = request.form.get('email') or None # Пустая строка превращается в None
        raw_password = request.form.get('password')

        # Проверка: есть ли такой пользователь?
        # SELECT * FROM users WHERE phone = ... OR email = ...
        existing_user = User.query.filter(
            or_(User.phone == phone, User.email == email)
        ).first()

        if existing_user:
            return "Пользователь с таким телефоном или почтой уже есть!"

        # Генерация данных
        hashed_pw = generate_password_hash(raw_password)
        card_num = str(random.randint(1000000000000000, 9999999999999999)) # 16 цифр

        # Создание объекта (НОВАЯ МАГИЯ ✨)
        new_user = User(
            first_name=fname,
            last_name=lname,
            middle_name=mname,
            phone=phone,
            email=email,
            password=hashed_pw,
            card_number=card_num,
            balance=0 # Начальный баланс
        )

        try:
            db.session.add(new_user) # "Добавь в список задач"
            db.session.commit()      # "Выполни SQL запрос INSERT"
            
            # Авто-логин
            session['user_id'] = new_user.id
            return redirect(url_for('profile'))
            
        except Exception as e:
            db.session.rollback() # Если ошибка - отменяем
            return f"Ошибка регистрации: {e}"

    return render_template('register.html', title='Регистрация')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    msg = None
    if request.method == 'POST':
        login_input = request.form.get('login_input')
        password = request.form.get('password')

        # Поиск пользователя (Email ИЛИ Phone)
        # SELECT * FROM users WHERE (email=input OR phone=input) AND is_deleted=False
        user = User.query.filter(
            or_(User.email == login_input, User.phone == login_input),
            User.is_deleted == False
        ).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('profile'))
        else:
            msg = "Неверный логин или пароль"

    return render_template('login.html', invalid=msg)

@app.route('/me')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_login'))

    # Получение пользователя по ID (новый синтаксис SQLAlchemy 2.0)
    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return redirect(url_for('user_login'))

    return render_template('profile.html', user=user)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('user_login'))

if __name__ == '__main__':
    app.run(debug=True)