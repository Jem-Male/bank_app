from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import select, or_ # Нужно для условия "ИЛИ"
import random
from decimal import Decimal
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY
from models import db, User, Transaction
from auth_utils import login_required
from DAO import get_all_users, get_user_for_evidence

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY

db.init_app(app)

with app.app_context():
    db.create_all() 
    print("БД подключена и таблицы проверены.")


@app.route('/')
def index():
    return render_template('index.html', title='Главная - Банк')


@app.route('/users')
def get_users():
    users_list = get_all_users()
    print(type(users_list))
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
        existing_user = get_user_for_evidence(phone=phone, email=email)
        
        print(existing_user)
        
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
        elif user:
            msg = "Неверный пароль"
        else:
            msg = "Неверный логин или пароль"

    return render_template('login.html', invalid=msg)


@app.route('/me')
@login_required
def profile():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)

   # если пользователю больше не существует
    if not user:
        session.clear()
        return redirect(url_for('user_login'))

    return render_template('profile.html', user=user)


@app.route('/transaction', methods=['GET','POST'])
@login_required
def transaction():
    
    msg = None
    succ = None
    user_id = session.get('user_id')    
    
    if request.method == 'POST' and user_id:
        
        send_user = db.session.get(User, user_id)
        r_user = request.form.get('r_card')
        revecide_user = User.query.filter_by(card_number = r_user).first()
        amount = request.form.get('amount')
        
        if not revecide_user:
            msg = "получатель не найден"
        elif r_user == send_user.card_number:
            msg = "средства нельзя отправлять самому себе"
        else:
            try:
                amount = Decimal(amount)
                if amount <=0:
                    msg = "отправляемая сумма не может быть отрицательной"
                    return render_template('transaction.html', user=send_user, message = msg, success = succ)
                elif amount > send_user.balance:
                    msg = "недостаточоно средств"
                    return render_template('transaction.html', user=send_user, message = msg, success = succ)
            except:
                msg = "Ошибка ввода"
                return render_template('transaction.html', user=send_user, message = msg, success = succ)
            
            try:
                send_user.balance -= amount
                revecide_user.balance += amount
                
                new_transaction = Transaction(
                    send_card = send_user.card_number,
                    receiver_card = revecide_user.card_number,
                    amount = amount
                )
                db.session.add(new_transaction)
                db.session.commit()
                msg = "Средства былы успешно переведены"
                succ = True
            except:
                db.session.rollback()
                msg = "Ошибка перевода"                
    
        return render_template('transaction.html', user=send_user, message = msg, success = succ)
    
    
    user = db.session.get(User, user_id)
    return render_template('transaction.html', user=user, message = msg, success = succ)  
    

@app.route('/history', methods=['GET'])
@login_required
def history():
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    # сделай так чтобы бэкенд получал все данные, а jinja2 сама 
    # все рассартирует по типам транзакции: отправленные, полученное, отмененые
    # transaction = select(Transaction).where(or_(Transaction.receiver_card==user.card_number, Transaction.send_card==user.card_number))
    # pushTransactions = Transaction.query.filter_by(send_card=user.card_number, status='success').all()
    # pullTransactions = Transaction.query.filter_by(receiver_card=user.card_number, status='success').all()
    
    transaction = db.session.scalars(select(Transaction).where(
        or_(
            Transaction.receiver_card==user.card_number, 
            Transaction.send_card==user.card_number
            )
        )).all() # новая запись

    return render_template('history_tr.html', transaction = transaction, user = user, arr = None) # переделай страницу под новое 
    
    # добавь чтобы было видно поступления
    # pullTransactions - то что получено
    # pushtransactions - то что отправленно
    # либо сделай чуть лучше: проверяй 
    # {% if tr.sender_card == user.card_number %}
    #     <h3 style="color: red;">- {{ tr.amount }} (Исходящий)</h3>
    #     <span>Кому: {{ tr.receiver_card }}</span>
    #     <br>
    #     <!-- Кнопку отмены показываем ТОЛЬКО для исходящих -->
    #     <a href="{{url_for('cancellation', tr_id=tr.id)}}" style="color: grey;">Отменить перевод</a>

    # <!-- Иначе (если получатель Я) -->
    # {% else %}
    #     <h3 style="color: green;">+ {{ tr.amount }} (Входящий)</h3>
    #     <span>От кого: {{ tr.sender_card }}</span>
    # {% endif %}
    


@app.route('/cancellation/<int:tr_id>', methods=['GET', 'POST'])
@login_required
def cancellation(tr_id):
    msg = None
    transaction = Transaction.query.filter_by(id = tr_id, status = "success").first()
    user = db.session.get(User, session.get('user_id'))
    if not user or not transaction:
        transaction = None
        msg = "Ошибка"
        user = None
    elif user.card_number != transaction.send_card:
        transaction = None
        user = None
        msg = "Ошибка: доступ запрещен" 
    elif request.method == 'POST':
        password = request.form.get('pass')
        amount = transaction.amount
        revecide_user = User.query.filter(User.card_number == transaction.receiver_card, User.balance > amount).first()
        if not revecide_user:
            res = False
            msg = "Отмена невозможна: средства уже использованы получателем или заблокированы"
            user = None
            transaction = None
        elif check_password_hash(user.password, password):
            try:
                user.balance += amount
                revecide_user.balance -= amount
                
                transaction.status = "Refund"
                
                db.session.commit()
                res = "Отмена прошла успешно"
                user = None
                transaction = None
            except:
                db.session.rollback()
                res = False
                msg = "Ошибка перевода"
                user = None
                transaction = None
            return render_template('cancellation.html', tr = transaction, res = res, msg = msg, us = user)
        else:
            msg = "Ошибка пароля"
            
    return render_template('cancellation.html', tr = transaction, res = False, msg = msg, us = user)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('user_login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')