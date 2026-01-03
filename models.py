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
    # created_ad = db.Column(db.DateTime, server_default = db.func.now())
    is_deleted = db.Column(db.Boolean(), default = False, nullable = False)
    
    # Метод __repr__ нужен просто для красивого вывода в print()
    # Как DataAnalyzer, только для отладки
    def __repr__(self):
        return f'<Created new user: id-{self.id}, name-{self.first_name} {self.last_name}, card-{self.card_number[-4:]}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "phone": self.phone,
            "email": self.email,
            "password": self.password,
            "card_number": self.card_number,
            "role": self.role,
            "status": self.status,
            "balance": self.balance,
            "is_deleted": self.is_deleted
        }
        
class Transaction(db.Model):
    
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    send_card = db.Column(db.String(16), db.ForeignKey('users.card_number'), nullable = False)
    receiver_card = db.Column(db.String(16), db.ForeignKey('users.card_number'), nullable = False)
    amount = db.Column(db.Numeric(10,2), nullable = False)
    status = db.Column(db.String(20), default = 'success')

    # created_at = db.Column(db.DateTime, default = datetime.utcnow()) - нет
    # это устаревший метод создания времени, причем не точный
    # лучше будет если БД само создаёт время
    # server_default (Дефолт на стороне Базы Данных)
    # db.func.now() - это инструкция для базы данных, а не готовое значение в Python
    created_ad = db.Column(db.DateTime, server_default = db.func.now())
    
    def __repr__(self):
        return f"new transaction create: id: {self.id}, status: {self.status}"
    
    def get_dict(self):
        return {
            "id": self.id,
            "sender": self.send_card,
            "receiver": self.receiver_card,
            "amount": float(self.amount),
            "create_at": self.created_ad.strftime('%Y-%m-%d %H:%M')
        }
