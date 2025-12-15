f = False

if f:
    a = ', %s'
else:
    a=''

sql_into = f"""
INSERT INTO users(`first_name`, `last_name`, `middle_name`, `password`, `email`, `phone`, `card_number`) 
VALUES (%s, %s, %s, %s, %s, %s{a});
"""

print(sql_into)