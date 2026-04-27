import pytest
from DAO import create_new_user, get_user_for_evidence
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
    
with app.app_context():
    def get_a_user():
        res, user = get_user_for_evidence(
            email='a@e',
            phone="a@e"
        )
        print(res, user.password)
    get_a_user()