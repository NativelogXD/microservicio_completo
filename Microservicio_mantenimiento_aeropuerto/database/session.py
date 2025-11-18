import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3308")
DB_NAME = os.getenv("DB_NAME", "microservicio_mantenimiento")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "MantenimientoDB123!")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Helper para obtener sesión y cerrar correctamente
class DBSessionContext:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db
    def __exit__(self, exc_type, exc, tb):
        try:
            if exc:
                self.db.rollback()
        finally:
            self.db.close()