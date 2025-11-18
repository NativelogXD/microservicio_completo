from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.domain.dto.avionDTO import AvionDTO, EstadoEnum
from app.persistence.database.database import SessionLocal
from app.persistence.mapper.AvionMapper import dto_a_entidad, entidad_a_dto
from app.persistence.serviceImpl.serviceAvion import ServiceAvion
from app.exception.avion_exceptions import AvionNotFoundError, AvionValidationError

# Crear el router con prefijo
router = APIRouter(prefix="/aviones", tags=["Aviones"])

def get_db():
    """Dependency para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_service(db: Session = Depends(get_db)):
    """Dependency para obtener el servicio de avión"""
    return ServiceAvion(db)


# ==================== RUTAS ESPECÍFICAS PRIMERO ====================

@router.get("/count")
def obtener_conteo_aviones(service: ServiceAvion = Depends(get_service)):
    """Obtener el conteo total de aviones en la base de datos"""
    try:
        aviones = service.getAllAviones(0, 10000)
        total = len(aviones)
        return {"total_aviones": total, "status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener conteo de aviones: {str(e)}"
        )


@router.get("/estado/{estado}", response_model=List[AvionDTO])
def obtener_aviones_por_estado(estado: str, service: ServiceAvion = Depends(get_service)):
    """Obtener aviones por estado"""
    if estado not in [e.value for e in EstadoEnum]:
        raise AvionValidationError(f"Estado inválido: {estado}")
    
    aviones = service.getAvionByEstado(estado)
    return [entidad_a_dto(avion) for avion in aviones]


@router.get("/aerolinea/{aerolinea}", response_model=List[AvionDTO])
def obtener_aviones_por_aerolinea(aerolinea: str, service: ServiceAvion = Depends(get_service)):
    """Obtener aviones por aerolínea"""
    aviones = service.getAvionByAerolinea(aerolinea)
    return [entidad_a_dto(avion) for avion in aviones]


@router.get("/fecha-fabricacion/{fecha_fabricacion}", response_model=List[AvionDTO])
def obtener_aviones_por_fecha_fabricacion(fecha_fabricacion: date, service: ServiceAvion = Depends(get_service)):
    """Obtener aviones por fecha de fabricación"""
    aviones = service.getAvionByFechaFabricacion(fecha_fabricacion)
    return [entidad_a_dto(avion) for avion in aviones]


# ==================== RUTAS GENERALES ====================

@router.post("/", response_model=AvionDTO, status_code=status.HTTP_201_CREATED)
def crear_avion(avion_dto: AvionDTO, service: ServiceAvion = Depends(get_service)):
    """Crear un nuevo avión"""
    try:
        avion_entidad = dto_a_entidad(avion_dto)
        avion_guardado = service.save(avion_entidad)
        return entidad_a_dto(avion_guardado)
    except Exception as e:
        raise AvionValidationError(f"Error al crear avión: {str(e)}")


@router.get("/", response_model=List[AvionDTO])
def obtener_todos_aviones(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    service: ServiceAvion = Depends(get_service)
):
    """Obtener todos los aviones con paginación"""
    aviones = service.getAllAviones(skip, limit)
    return [entidad_a_dto(avion) for avion in aviones]


# ==================== RUTAS CON PARÁMETROS AL FINAL ====================

@router.get("/{avion_id}", response_model=AvionDTO)
def obtener_avion(avion_id: int, service: ServiceAvion = Depends(get_service)):
    """Obtener un avión por su ID"""
    try:
        avion = service.getAvionById(avion_id)
        if not avion:
            raise AvionNotFoundError(f"Avión con ID {avion_id} no encontrado")
        return entidad_a_dto(avion)
    except AvionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Avión con ID {avion_id} no encontrado"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener avión: {str(e)}"
        )


@router.put("/{avion_id}", response_model=AvionDTO)
def actualizar_avion(avion_id: int, avion_dto: AvionDTO, service: ServiceAvion = Depends(get_service)):
    """Actualizar un avión existente"""
    try:
        avion_existente = service.getAvionById(avion_id)
        if not avion_existente:
            raise AvionNotFoundError(f"Avión con ID {avion_id} no encontrado")
        
        avion_dto.id = avion_id
        avion_entidad = dto_a_entidad(avion_dto)
        avion_actualizado = service.update(avion_entidad)
        return entidad_a_dto(avion_actualizado)
    except AvionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Avión con ID {avion_id} no encontrado"
        )
    except Exception as e:
        raise AvionValidationError(f"Error al actualizar avión: {str(e)}")


@router.delete("/{avion_id}")
def eliminar_avion(avion_id: int, service: ServiceAvion = Depends(get_service)):
    """Eliminar un avión"""
    try:
        avion_existente = service.getAvionById(avion_id)
        if not avion_existente:
            raise AvionNotFoundError(f"Avión con ID {avion_id} no encontrado")
        
        service.delete(avion_id)
        return {"message": f"Avión con ID {avion_id} eliminado exitosamente"}
    except AvionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Avión con ID {avion_id} no encontrado"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar avión: {str(e)}"
        )
