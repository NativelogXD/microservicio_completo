# app/persistence/database.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()

# Usar SQLite por defecto para evitar dependencias de PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///aviones.db")

print(f"🔗 Usando base de datos: {DATABASE_URL}")

# Configurar el motor de base de datos
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# Crear la sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Crear todas las tablas en la base de datos"""
    try:
        print("📊 Creando tablas en la base de datos...")
        from app.persistence.entity.Avion import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        raise

def get_db():
    """Dependency para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
