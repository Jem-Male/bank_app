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
        with conn.cursor(dictionary=True) as cur:
            cur.execute('SELECT id, first_name, last_name, card_number, balance FROM users')
            
            return cur.fetchall()
        
    except Error as e:
        print("Ошибка - {e}")
        return None
    
    finally:
        if conn:
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
    conn = None
    try:
        conn = get_conn()
        with conn.cursor(dictionary=True) as cur:
            sql_select = """
            SELECT id, last_name, middle_name, password, phone, email , card_number, balance from users
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