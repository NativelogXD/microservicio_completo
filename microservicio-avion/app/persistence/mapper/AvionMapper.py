# app/domain/mappers.py
from typing import List
from app.domain.dto.avionDTO import AvionDTO, EstadoEnum
from app.persistence.entity.Avion import Avion
def dto_a_entidad(dto: AvionDTO) -> Avion:
    return Avion(
        id=dto.id,
        modelo=dto.modelo,
        capacidad=dto.capacidad,
        aerolinea=dto.aerolinea,
        estado=dto.estado,
        fecha_fabricacion=dto.fecha_fabricacion
    )

def entidad_a_dto(avion: Avion) -> AvionDTO:
    return AvionDTO(
        id=avion.id,
        modelo=avion.modelo,
        capacidad=avion.capacidad,
        aerolinea=avion.aerolinea,
        estado=avion.estado if avion.estado else EstadoEnum.disponible,
        fecha_fabricacion=avion.fecha_fabricacion
    )
