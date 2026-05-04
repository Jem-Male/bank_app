import pytest
from DAO import (
    get_all_users,
    create_new_user, 
    get_user_for_evidence, 
    create_transaction_check, 
    create_transaction_user,
    process_transaction
)

from app import app, db 

# with app.app_context():
#     res, new_user = create_new_user(
#         first_name="First",
#         last_name="Last",
#         middle_name="Midl",
#         phone='+7707',
#         email="a@email.com",
#         card_number="1234",
#         password='1234'
#         )

# def test_add_a_new_user():
#     assert res == False
    

def get_a_user():
    res, user = get_user_for_evidence(
        email='a@e',
        phone="a@e"
    )
    return user
    # get_a_user()
    
# with app.app_context():
#     user = get_a_user()
#     print(user)

# # 2 and 6

with app.app_context():
    
    res, user_1_pass = get_user_for_evidence(id = 2)
    res, user_2_take = get_user_for_evidence(id = 6)


        
    result, *data = process_transaction(amout=1000, revecide_user=user_2_take, send_user=user_1_pass)
    
    print(result,'\n',data)