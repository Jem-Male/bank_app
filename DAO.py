# Data Access Object

from models import Transaction, User, db
from sqlalchemy import select, or_

def get_all_users():
    users_list = db.session.scalars(select(User).where(User.is_deleted != True)).all()
    return users_list


def get_user_for_evidence(
    *, id = None, email = None, phone = None, card_number = None
    ):
    
    try:
        user = db.session.scalar(select(User).where(or_(
            User.id == id,
            User.email == email,
            User.phone == phone,
            User.card_number == card_number
        ),User.is_deleted != True))
        
        if user is None:
            return False, object()
        
        return True, user
    
    except Exception as e:
        return e, object()

def create_new_user(*, first_name, last_name, middle_name, phone, email, password, card_number):
    
    new_user = User(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            phone=phone,
            email=email,
            password=password,
            card_number=card_number,
            balance=0 # Начальный баланс
        )
    
    try:
        db.session.add(new_user) # "Добавь в список задач"
        db.session.commit()      # "Выполни SQL запрос INSERT"
        return True, new_user
    
    except Exception as e:
        db.session.rollback() # Если ошибка - отменяем
        return False, f"Ошибка регистрации пользователя: {e}"
        


# def create_