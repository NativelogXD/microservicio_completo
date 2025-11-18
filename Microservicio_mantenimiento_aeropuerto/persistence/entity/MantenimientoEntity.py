from sqlalchemy import Column, String, Date, Float
from database.session import Base
import uuid
from datetime import date
from enum import Enum as PyEnum

class EstadoEnum(str, PyEnum):
    Pendiente = "Pendiente"
    EnProceso = "EnProceso"
    Completado = "Completado"

class MantenimientoEntity(Base):
    __tablename__ = "mantenimientos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    id_avion = Column(String(50), nullable=False)
    tipo = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=False)
    fecha = Column(Date, nullable=False, default=date.today)
    responsable = Column(String(100), nullable=False)
    costo = Column(Float, nullable=False)
    estado = Column(String(20), nullable=False, default=EstadoEnum.Pendiente.value)