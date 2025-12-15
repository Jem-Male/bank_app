import mysql.connector

con = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '7473',
    database = 'tasks'
)

cur = con.cursor()

cur.execute('SELECT * FROM users')
print(cur.fetchall())

