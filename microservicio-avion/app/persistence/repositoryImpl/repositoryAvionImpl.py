# app/persistence/repositoryImpl/repositoryAvionImpl.py
from typing import Optional, List
from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.domain.dto.avionDTO import AvionDTO
from app.domain.repository.AvionRepository import AvionRepositorio
from app.persistence.entity.Avion import Avion
from app.persistence.mapper.AvionMapper import dto_a_entidad, entidad_a_dto


class AvionRepositoryImpl(AvionRepositorio):
    """
    Implementación concreta de AvionRepositorio usando SQLAlchemy.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    # Guardar recibe una ENTIDAD, no DTO
    def save(self, avion: Avion) -> Avion:
        self.db.add(avion)
        self.db.commit()
        self.db.refresh(avion)
        return avion

    def getAvion(self, avion_id: int) -> Optional[Avion]:
        return self.db.query(Avion).filter(Avion.id == avion_id).first()

    def getAvionByFechaFabricacion(self, fecha_fabricacion: date) -> List[Avion]:
        return self.db.query(Avion).filter(Avion.fecha_fabricacion == fecha_fabricacion).all()

    def getAvionByEstado(self, estado: str) -> List[Avion]:
        from app.domain.dto.avionDTO import EstadoEnum
        estado_enum = EstadoEnum(estado)
        return self.db.query(Avion).filter(Avion.estado == estado_enum).all()

    def getAvionByAerolinea(self, aerolinea: str) -> List[Avion]:
        return self.db.query(Avion).filter(Avion.aerolinea == aerolinea).all()

    def delete(self, avion_id: int) -> Optional[Avion]:
        avion = self.getAvion(avion_id)
        if avion:
            self.db.delete(avion)
            self.db.commit()
        return avion

    def edit(self, avion_id: int, avion_actualizado: Avion) -> Avion:
        avion = self.getAvion(avion_id)
        if not avion:
            raise HTTPException(status_code=404, detail=f"Avión {avion_id} no encontrado")

        for attr, value in avion_actualizado.__dict__.items():
            if attr != "_sa_instance_state":
                setattr(avion, attr, value)
        self.db.commit()
        self.db.refresh(avion)
        return avion
    
    def getAllAviones(self, skip: int, limit: int) -> List[Avion]:
        return self.db.query(Avion).offset(skip).limit(limit).all()
