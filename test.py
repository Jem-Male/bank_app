# from werkzeug.security import generate_password_hash, check_password_hash # <--- 1. Импорт
# import mysql.connector
# from mysql.connector import Error
# from config import MYSQL_CONFIG

# print(check_password_hash('scrypt:32768:8:1$DXTw01V2rK2uPGgV$1fd528ca296ff7e93ff4dbdafd2ccd2a3102a5f96e17af7722ef26593a953f3f107e3f18fb653eec7e4717e93c23820c09a01e7a6557e6186599f8ff725bdb49','123456789'))


# def get_db():
#     try:
#         connection = mysql.connector.connect(**MYSQL_CONFIG)
#         return connection
    
#     except Error as e:
#         print("Ошибка соединения: {e}")
#         return None
    
# try:
#     conn = get_db()
#     cur = conn.cursor(dictionary=True)
#     sql_select = """
#     select id, password, phone, email , is_deleted from users
#     WHERE email = %s or phone = %s;
#     """
#     value = (None, '+123456789')
#     print(value)
#     cur.execute(sql_select, value)
            
#     res = cur.fetchall()
#     cur.close()
#     conn.close()
#     password = '123456789'
#     print(password)
#     user_hash = res[0]['password'] 
#     if check_password_hash(user_hash, password):
#         print(f"все верно")
        
#     print(f"ничего не верно")
# except Error as e:
#     print(f"ошибка - {e}")



from flask import session
def sess():
    """базовая работа с сессиями"""
    
    # сесии представляют из себя словарь данных
    session = {
    'user_id': 5,
    'theme': 'dark',
    'cart': [1, 2, 3]
    }
    
    # создания сессии
    sess = 'каие либо данные'
    session['название_сессии'] = sess

    # получения данных с сесии
    sess_result = session.get('низвание_сессии')
    
    # чтобы удвлить сесию:
    session.pop('Ключ: название сессии', None) # None для мягкого удаления ибо если pop не найдет 'Ключ: название сессии' то он выдаст ошибку
    
    # чтобы удалить все данные сесии
    session.clear()
    
    
def get_new_user():
     """lastrowid"""
     # !!лучше использовать - result = cur.lastrowid!!
     # каждый пользователь → отдельная трубка
     # lastrowid лежит внутри трубки
     # чужие данные туда не попадают
     # ✔ cur.lastrowid потокобезопасен
     # ✔ параллельные регистрации не конфликтуют
     # ✔ чужой id не прилетит
                        
     # # здесь просто ищем подзователя чтобы вернуть ему его id
     # sql_select = """
     # SELECT id from users
     # WHERE (email = %s or phone = %s) and is_deleted = 0;
     # """

     # value = (email, phone)
     # cur.execute(sql_select, value)

     # res = cur.fetchone()
            
     # получить id вставленного пользователя
     new_user_id = cur.lastrowid

     # сохраняем изменения
     conn.commit()           

     cur.close()
     conn.close()

     session['user_id'] = new_user_id
     
# в будущем надо будет добавить декоратор для БД

from database import create_user


v = ('в', 'в', 'в', 'scrypt:32768:8:1$Zlmj0v1O17XisnGm$f186db3b5863ff67a7ed0bc5d115cb2efed8add34664871fe7ee876fddb1194ec119b72b35277887405b952a042eeeff2a5c7296e8fda779023bd7de3835159f', ',33654', 'Электронная почта 6', '769316277979')
create_user(v)