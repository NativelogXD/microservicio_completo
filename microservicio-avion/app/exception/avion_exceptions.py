# app/exception/avion_exceptions.py
from fastapi import HTTPException
from typing import Any, Dict, Optional


class AvionException(HTTPException):
    """Excepción base para errores relacionados con aviones"""
    
    def __init__(self, status_code: int, detail: str, headers: Optional[Dict[str, Any]] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class AvionNotFoundError(AvionException):
    """Excepción cuando no se encuentra un avión"""
    
    def __init__(self, avion_id: int):
        super().__init__(
            status_code=404,
            detail=f"Avión con ID {avion_id} no encontrado"
        )


class AvionValidationError(AvionException):
    """Excepción para errores de validación de avión"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=400,
            detail=f"Error de validación: {detail}"
        )


class AvionDuplicateError(AvionException):
    """Excepción cuando se intenta crear un avión duplicado"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=409,
            detail=f"Conflicto: {detail}"
        )


class AvionBusinessLogicError(AvionException):
    """Excepción para errores de lógica de negocio"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=422,
            detail=f"Error de lógica de negocio: {detail}"
        )

