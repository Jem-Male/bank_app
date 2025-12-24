import mysql.connector
from mysql.connector import Error
from config import MYSQL_CONFIG

def get_conn():
    """создание подключения"""
    # Функция только создает объект, не подавляя ошибку
    return mysql.connector.connect(**MYSQL_CONFIG)


def get_all_users():
    """получаем всех пользователей"""    
    # инициализируем переменную
    # Если ошибка произойдет на самом первом этапе (внутри try), переменная conn не будет создана.
    # Программа "упадет" не из-за базы данных, а из-за попытки закрыть то, чего не существует - finally
    conn = None
    try:
        conn = get_conn()
        with conn.cursor(dictionary=True) as cur: # with открывает cursor и сам же её закрывает так как использует метод close(), благодаря этому код чуть меньше
            cur.execute('SELECT id, first_name, last_name, card_number, balance FROM users')
            
            return cur.fetchall()
        
    except Error as e:
        print("Ошибка - {e}")
        return None
    
    finally: # всегда будет закрывать соединения в не зависимости от try, except
        if conn: # для проверки существоввания самого подключения, не вызовет ошибку так как он проверяет прежде чем закрыть, а то он будет закрывать ничего: none.close()
            conn.close()


def create_user(values):
    """создать пользователя по его данным"""
    conn = None
    try:
        conn = get_conn()
        
        with conn.cursor() as cur:
            sql_into = "SELECT id FROM users WHERE phone = %s or email = %s;"
            val = values[4:6]
            cur.execute(sql_into, val)
            res = cur.fetchall()
            if res:
                print("Пользователь уже сузествует")
                return False
        
            sql_into = """
            INSERT INTO users
            (first_name, last_name, middle_name, password, phone, email, card_number) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            print(sql_into)
            cur.execute(sql_into, values)
            id = cur.lastrowid
            conn.commit()
            return id
    
    except Error as e:
        print(f"ошибка вставки - {e}")
        return None
    
    finally:
        if conn:
            conn.close()


def get_user_by_info(email, phone):
    """Поиск пользователя по его email, phone
    
    Args:
        email (str): электронная почта пользователя
        phone (str): Контактный номер телефона
        
    Returns:
        res (dict) | None: Словарь с данными пользователя, если найден, иначе None.
    """
    
    conn = None
    try:
        conn = get_conn()
        
        with conn.cursor(dictionary=True) as cur:
        
            sql_select = """
            SELECT last_name, id, password, phone, email from users
            WHERE (email = %s or phone = %s) and is_deleted = 0;
            """

            value = (email, phone)
            cur.execute(sql_select, value)
            
            res = cur.fetchone()
            
            return res

    except Error as e:
        print(f"Ошибка поиска {e}")
        return None
    
    finally:
        if conn:
            conn.close()


def get_user_by_id(user_id):
    """Получение пользователя по его id
    
    Args:
        user_id (str): id пользователя
        
    Returns:
        (dict)
    """
    conn = None
    try:
        conn = get_conn()
        with conn.cursor(dictionary=True) as cur:
            sql_select = """
            SELECT id, first_name, last_name, middle_name, password, phone, email , card_number, balance 
            FROM users
            WHERE id = %s and is_deleted = 0;
            """
            
            value = (user_id,)
            cur.execute(sql_select, value)
            return cur.fetchone()
        
    except Error as e:
        print(f"Ошибка поиска {e}")
        return None
    
    finally:
        if conn:
            conn.close()


def create_transactions(send_card, receiver_card, amount):
    """Процесс транзакции"""
    conn = None
    try:
        # валидация суммы
        # это важно либо же sql введет данные не верно
        try:
            # Эта строка пытается преобразовать (привести тип) того, что ввел пользователь, в число с плавающей точкой.
            # Если ввели "100" — превратит в 100.0.
            # Если ввели "100.50" — превратит в 100.5.
            # Если ввели "привет" — выбросит ошибку ValueError.
            # Именно поэтому ты оборачиваешь это в try...except
            amount = float(amount)
            # данные из HTML-формы всегда приходят в виде строк (str). 
            # Ты не можешь просто так вычесть строку из баланса в базе данных. 
            # Тебе в любом случае нужно превратить текст в число.
            if amount < 0:
                return "Сумма должна быть больше нуля"

        except ValueError:
            return f"Некоректная сумма"
        
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("SELECT id FROM users WHERE card_number = %s", (receiver_card,))
        
        if cur.fetchone() is None:
            return f"Получатель не найден"

        cur.execute("SELECT balance FROM users WHERE card_number = %s", (send_card,))
        sender = cur.fetchone()
        
        if sender is None:
            return f"Получатель не найден"
        
        if sender['balance'] < amount:
            return "Недостаточно средств"

        # отнимаем у отправителя сумму
        sql_transaction ="""
        UPDATE users
        SET balance = balance - %s
        WHERE users.card_number = %s
        """
        cur.execute(sql_transaction, (amount, send_card))
        # прибовляем получателю сумму
        sql_transaction ="""
        UPDATE users
        SET balance = balance + %s
        WHERE users.card_number = %s
        """
        cur.execute(sql_transaction, (amount, receiver_card))
        # прежде чем сделать commit мы создаем чек
        # если чек не создастся отменяем все
        sql_transaction = """
        INSERT INTO transactions (send_card, receiver_card, amount)
        VALUES (%s, %s, %s);
        """
        cur.execute(sql_transaction,(send_card, receiver_card, amount))
        cur.fetchone()
        conn.commit()
        return True
    
    except Error as e:
        print(f"ошибка создания транзакции - {e}")
        return False
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()