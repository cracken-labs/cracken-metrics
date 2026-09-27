from sqlmodel import create_engine, SQLModel, Session
from app.config import settings

# Берем промышленную строку подключения из нашего конфига
DATABASE_URL = settings.DATABASE_URL

# Создаем движок Postgres
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    """Автоматически создает таблицы в схеме Postgres при первом запуске бэкенда"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Генератор транзакционных сессий базы данных для FastAPI"""
    with Session(engine) as session:
        yield session
