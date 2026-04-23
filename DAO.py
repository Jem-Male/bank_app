from models import Transaction, User, db
from sqlalchemy import select, or_

def get_all_users():
    users_list = User.query.all() 
    return users_list


def get_user_for_evidence(
    *, id = None, email = None, phone = None, card_number = None
    ):
    
    return db.session.scalar(select(User).where(or_(
        User.id == id,
        User.email == email,
        User.phone == phone,
        User.card_number == card_number
    ),User.is_deleted != True))

# 100 94