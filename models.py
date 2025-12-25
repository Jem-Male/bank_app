from flask_sqlalchemy import SQLAlchemy

# Это "подключалка", создаем её пока пустой, потом привяжем к Flask
db = SQLAlchemy()

# Класс = Таблица
# db.Model говорит: "Этот класс — не просто код, это таблица в базе"
class User(db.Model):
    
    # имя создаваемой таблицы
    # можно и без жэтого но в таком случае 
    # в качестве имени будет взята имя класса
    __tablename__ = 'users'
    
    # поля
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(50), nullable = False)
    last_name = db.Column(db.String(50), nullable = False)
    middle_name = db.Column(db.String(50), nullable = False)
    phone = db.Column(db.String(20), unique = True, nullable = True)
    email = db.Column(db.String(100), default = None, unique = True, nullable = True)
    password = db.Column(db.String(255), nullable = False)
    card_number = db.Column(db.String(16), unique = True, nullable = False)
    role = db.Column(db.String(20), default = 'client', nullable = False)
    status = db.Column(db.String(20), default = 'normal', nullable = False)
    
    # Использование Numeric вместо Float так как он не точный
    # precision=10 — общее количество цифр
    # scale=2 — количество знаков после запятой
    # balance = db.Column(db.Numeric(precision=10, scale=2), default='0.00', nullable=False)
    # да default='0.00' но при создании он станет обычным числом
    balance = db.Column(db.Numeric(10, 2), default=0, nullable = False)
    is_deleted = db.Column(db.Boolean(), default = False, nullable = False)
    
    # Метод __repr__ нужен просто для красивого вывода в print()
    # Как DataAnalyzer, только для отладки
    def __repr__(self):
        return f'<Created new user: id-{self.id}, name-{self.first_name} {self.last_name}, card-{self.card_number[-4:]}>'
    
