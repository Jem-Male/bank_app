from flask import Flask, render_template, url_for, request, session, redirect
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash # для хеширование паролей
from config import SECRET_KEY
from database import get_all_users, create_user, get_user_by_info, get_user_by_id, create_transactions
import random

app = Flask(__name__)
# для сесии
app.secret_key = SECRET_KEY


@app.route('/', methods=['GET'])
def index():
    """главная страница"""
    return render_template('index.html', title='Главная - Банк')


@app.route('/users', methods=['GET'])
def get_users():
    """Страница со всеми пользователями"""
    data = get_all_users()
    if data == None:
        return f"Данных нет", 500
    return render_template('users.html', users=data, title='Пользователи')


@app.route('/register', methods=['GET','POST'])
def user_registration():
    """для создания нового пользоватеья + регистрация"""
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
        
        # 3. Собираем значения
        # Если в переменной email лежит None, в базу запишется NULL.
        # Если там "mail@mail.ru", запишется строка.
        # Генерацию карты тоже лучше вынести в переменную для читаемости.
        hashed_password = generate_password_hash(password)
        card_num = str(random.randint(100000000000, 999999999999))
        
        # создаем значения для values
        vals = (first_name, last_name, middle_name, hashed_password, phone, email, card_num)
        try:
            
            new_user_id = create_user(vals)
            if new_user_id is False:
                return f"Ошибка такой пользовател существует"
            
            session['user_id'] = new_user_id
            
            return redirect(url_for('profile'))
        
        except Error as e:
            
            return f"Ошибка sql - {e}"
        
    return render_template('register.html', title='Регистрация')


@app.route('/login', methods=['GET','POST'])
def user_login():
    """для входа в систему"""
    if request.method == 'POST':
        
        login_input = request.form.get('login_input')
        password = request.form.get('password')
        
        res = get_user_by_info(login_input, login_input)
        
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
         
    return render_template('login.html', invalid = 0)


@app.route('/me')
def profile():
    """Страница профиля"""
    
    # здесь мы пробуем получить сессию от пользователя
    # а именно пытаемся получить его id чтобы найти его в БД
    user_id = session.get('user_id') or None
    
    # если сессии нет опять перенаправляем его на страницу входа
    if user_id is None:
        return redirect(url_for('user_login'))
    
    res = get_user_by_id(user_id)
   
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
        return redirect(url_for('user_login'))
        
    return render_template('profile.html', user = res)


@app.route('/logout', methods=['POST'])
def logout():
    """функция для удаления сесии - т.е.: выход"""
    # удалить все сесии чтобы неболо сюрпризов
    session.clear()
    
    # после удаления сразу перенаправляем в повторный вход
    return redirect(url_for('user_login'))


@app.route('/transaction', methods=['GET','POST'])
def transaction():
    """Страница для транзакций"""
    
    if request.method == 'POST':
        user_id = session.get('user_id') or None
        
        if user_id:
            user = get_user_by_id(user_id)
            receiver_card = request.form.get('receiver_card')
            amount = request.form.get('amount')
            
            t = create_transactions(user['card_number'], receiver_card, amount)
            
            return render_template('transaction.html', user = user, t_rse = t)
        
        return f'Сессия истекла'
        
    # для начало получим id пользователя
    user_id = session.get('user_id') or None
    
    if user_id:
        user = get_user_by_id(user_id)
        return render_template('transaction.html', user=user, t_rse = 0)
        
    return redirect(url_for('user_login'))
    

@app.route('/test', methods=['GET'])
def get_request():
    """Просто тест"""
    print(request)
    return str(f" {request.base_url}, {request.headers}, {request.method}, {request.args}, {request.get_data()}")


if '__main__' == __name__:
    app.run(debug=True, host='0.0.0.0', port=5000)