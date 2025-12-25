# Твои данные подключения
DB_USER = 'python'      # Твой пользователь (не root, молодец)
DB_PASS = '7473'        # Твой пароль
DB_HOST = 'localhost'
DB_NAME = 'bank'        # Имя базы данных (она должна быть уже создана в Workbench!)

# Собираем "адрес" для SQLAlchemy
# mysql+pymysql говорит: "Подключайся к MySQL, используя драйвер pymysql"
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = '8JBHUYVG*H(uijhu gyviU)'