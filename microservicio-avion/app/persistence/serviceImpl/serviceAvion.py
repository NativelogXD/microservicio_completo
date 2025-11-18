# app/service/service_avion.py
from typing import List, Optional
from datetime import date

from app.persistence.entity.Avion import Avion
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.persistence.repositoryImpl.repositoryAvionImpl import AvionRepositoryImpl


class ServiceAvion:
    """
    Capa de servicio para Avion. Llama a AvionRepositoryImpl para la persistencia.
    """

    def __init__(self, db_session: Session):
        self.repo = AvionRepositoryImpl(db_session)

    def save(self, avion: Avion) -> Avion:
        # Aquí podrías agregar validaciones antes de guardar
        return self.repo.save(avion)

    def getAvion(self, avion_id: int) -> Optional[Avion]:
        return self.repo.getAvion(avion_id)

    def getAvionByFechaFabricacion(self, fecha_fabricacion: date) -> List[Avion]:
        return self.repo.getAvionByFechaFabricacion(fecha_fabricacion)

    def getAvionByEstado(self, estado: str) -> List[Avion]:
        return self.repo.getAvionByEstado(estado)

    def getAvionByAerolinea(self, aerolinea: str) -> List[Avion]:
        return self.repo.getAvionByAerolinea(aerolinea)

    def delete(self, avion_id: int) -> Optional[Avion]:
        return self.repo.delete(avion_id)

    def edit(self, avion_id: int, avion_actualizado: Avion) -> Avion:
        return self.repo.edit(avion_id, avion_actualizado)
    
    def getAllAviones(self, skip: int, limit: int) -> List[Avion]:
        return self.repo.getAllAviones(skip, limit)
