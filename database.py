import mysql.connector
from mysql.connector import Error
from config import MYSQL_CONFIG

def get_conn():
    """
    создание подключения
    Returns:
        obj: connection
    """
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        
        return connection
    
    except Error as e:
        print('Ошибка подключения к БД - {e}')
        return None


def get_all_users():
    """получаем всех пользователей"""
    conn = get_conn()
    
    if conn is None:
        return f"Ошибка к подключению БД", 500
    try:
        # dictionary=True ставим ЗДЕСЬ. Это настройка "пальца", а не "телефона"
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT id, first_name, last_name, card_number, balance FROM users')
        data = cur.fetchall()
        
        # Данные получили, курсор больше не нужен
        cur.close()
        
        # Закрываем соединение, чтобы не висело в Process List
        conn.close()
        
        return data
    
    except Error as e:
        cur.close()
        conn.close()
        return None


def create_user(values):
    """создать пользователя по его данным"""
    try:
        conn = get_conn()
        
        if conn is None:
            return f"Ошибка к подключению БД", 500
    
        sql_into = "SELECT id FROM users WHERE email = %s or phone = %s;"
        
        cur = conn.cursor()
        # val = values[4:5] # а почему ???
        val = values[4:6]
        res = cur.execute(sql_into, val)
        print(f' \n\n\n{res}\n\n\n')
        # if res: # а почеиу так?
        if res is None:
            return False
                
        sql_into = """
            INSERT INTO users
            (first_name, last_name, middle_name, password, phone, email, card_number) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql_into, values)
        id = cur.lastrowid
        cur.close()
        conn.close()
        return id
    
    except Error as e:
        cur.close()
        conn.close()
        print(f"ошибка вставки - {e}")
        return e


def get_user_by_info(email, phone):
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
            
        sql_select = """
        SELECT last_name, id, password, phone, email from users
        WHERE (email = %s or phone = %s) and is_deleted = 0;
        """
        
        value = (email, phone)
        cur.execute(sql_select, value)
        
        res = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return res
    
    except Error as e:
        cur.close()
        conn.close()
        print("Ошибка - {e}")
        return None


def get_user_by_id(user_id):
    try:
        conn = get_conn()
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
        return res
    
    except Error as e:
        cur.close()
        conn.close()
        print(f"ошибка - {e}")
        return None