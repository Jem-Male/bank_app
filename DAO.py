# Data Access Object

from models import Transaction, User, db
from sqlalchemy import select, or_

def get_all_users():
    users_list = db.session.scalars(select(User).where(User.is_deleted != True)).all()
    return users_list


def get_user_for_evidence(
    *, id = None, email = None, phone = None, card_number = None
    ) -> bool|object:
    
    try:
        user = db.session.scalar(select(User).where(or_(
            User.id == id,
            User.email == email,
            User.phone == phone,
            User.card_number == card_number
        ),User.is_deleted != True))
        
        return True, user
    
    except Exception as e:
        return False, e

def create_new_user(*, first_name, last_name, middle_name, phone, email, password, card_number) -> bool|object:
    
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


def create_transaction_check(*, send_user, revecide_user, amount) -> bool|object:
    try:
        
        new_transaction = Transaction(
            send_card = send_user.card_number,
            receiver_card = revecide_user.card_number,
            amount = amount
        )
        
        db.session.add(new_transaction)
        return True, new_transaction

    except Exception as e:
        db.session.rollback()
        return False, e


def create_transaction_user(*, send_user, revecide_user, amount):
    try:
        
        send_user.balance -= amount
        revecide_user.balance += amount
        
        return True, None
    
    except Exception as e:
        
        return False, e

def process_transaction(*, amout, revecide_user, send_user):
    """Start transaction

    Args:
        amout (_type_): _description_
        revecide_user (_type_): _description_
        send_user (_type_): _description_

    Returns:
    
    """
    
    try:
        result_transaction_user, error_info_or_None = create_transaction_user(
            amount=amout, 
            revecide_user=revecide_user, 
            send_user=send_user
        )
        
        result_transaction_check, transaction_check = create_transaction_check(
            amount=amout,
            revecide_user=revecide_user,
            send_user=send_user
        )
        
        db.session.commit()
       
        print("New Transaction:")
        return True, transaction_check

    except Exception as e:
        
        db.session.rollback()
        return False, e


# def create_
