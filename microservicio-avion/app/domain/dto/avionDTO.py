from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum

class EstadoEnum(str, Enum):
    disponible = "disponible"
    mantenimiento = "mantenimiento"
    fuera_de_servicio = "fuera_de_servicio"

class AvionDTO(BaseModel):
    id: Optional[int] = None
    modelo: str = Field(min_length=2, max_length=100)
    capacidad: int = Field(gt=0, description="Capacidad debe ser mayor a 0")
    aerolinea: str = Field(min_length=2, max_length=100)
    estado: EstadoEnum = EstadoEnum.disponible
    fecha_fabricacion: Optional[date] = Field(default=None, description="Fecha en formato YYYY-MM-DD")
