# models/mcp_models.py
"""
Modelos Pydantic completos para el servidor MCP.
Define tanto modelos de creación (CREATE) como de consulta/respuesta (GET).
Estos modelos se usan para validar requests y responses en las herramientas MCP.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum


# ==============================================
# ENUMS Y TIPOS COMUNES
# ==============================================

class EstadoReserva(str, Enum):
    ACTIVA = "ACTIVA"
    CANCELADA = "CANCELADA"
    COMPLETADA = "COMPLETADA"
    PENDIENTE = "PENDIENTE"


class EstadoAvion(str, Enum):
    DISPONIBLE = "disponible"
    MANTENIMIENTO = "mantenimiento"
    FUERA_SERVICIO = "fuera_de_servicio"


class EstadoPago(str, Enum):
    PENDIENTE = "PENDIENTE"
    COMPLETADO = "COMPLETADO"
    CANCELADO = "CANCELADO"
    FALLIDO = "FALLIDO"


class MetodoPago(str, Enum):
    TARJETA = "TARJETA"
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    PAYPAL = "PAYPAL"
    CRYPTO = "CRYPTO"


class EstadoMantenimiento(str, Enum):
    PENDIENTE = "Pendiente"
    EN_PROCESO = "En Proceso"
    COMPLETADO = "Completado"


class TipoMantenimiento(str, Enum):
    PREVENTIVO = "PREVENTIVO"
    CORRECTIVO = "CORRECTIVO"
    EMERGENCIA = "EMERGENCIA"
    INSPECCION = "INSPECCION"


class CanalNotificacion(str, Enum):
    SMS = "SMS"
    EMAIL = "EMAIL"


# ==============================================
# MODELOS DE CREACIÓN (CREATE) - ACTUALIZADOS
# ==============================================

class AvionCreate(BaseModel):
    """Modelo para crear un nuevo avión - Estructura real del AvionDTO."""
    modelo: str = Field(..., description="Modelo del avión")
    capacidad: int = Field(..., description="Capacidad de pasajeros", gt=0)
    aerolinea: str = Field(..., description="Aerolínea propietaria")
    estado: EstadoAvion = Field(EstadoAvion.DISPONIBLE, description="Estado del avión (disponible, mantenimiento, fuera_de_servicio)")
    fecha_fabricacion: Optional[date] = Field(None, description="Fecha de fabricación del avión")
    
    class Config:
        use_enum_values = True


class ReservaCreate(BaseModel):
    """Modelo para crear una nueva reserva - Estructura real del ReservaDTO."""
    usuario: str = Field(..., description="Nombre del usuario que hace la reserva")
    id_vuelo: str = Field(..., description="ID del vuelo")
    estado: EstadoReserva = Field(EstadoReserva.PENDIENTE, description="Estado de la reserva")
    Numasiento: str = Field(..., description="Número de asiento")
    
    class Config:
        use_enum_values = True


class PagoCreate(BaseModel):
    """Modelo para crear un nuevo pago - Estructura real del PagoDTO."""
    monto: float = Field(..., description="Monto del pago", gt=0)
    fecha: datetime = Field(default_factory=datetime.now, description="Fecha del pago")
    estado: EstadoPago = Field(EstadoPago.PENDIENTE, description="Estado del pago")
    moneda: str = Field("USD", description="Moneda del pago")
    metodo_pago: MetodoPago = Field(..., description="Método de pago")
    id_reserva: str = Field(..., description="ID de la reserva asociada")
    
    class Config:
        use_enum_values = True


class UsuarioCreate(BaseModel):
    """Modelo para crear un nuevo usuario - Estructura real del UsuarioDTO que hereda de PersonaDTO."""
    # Campos de PersonaDTO
    cedula: str = Field(..., description="Cédula del usuario")
    nombre: str = Field(..., description="Nombre del usuario")
    apellido: str = Field(..., description="Apellido del usuario")
    telefono: str = Field(..., description="Teléfono del usuario")
    email: str = Field(..., description="Email del usuario")
    rol: str = Field("Usuario", description="Rol del usuario")
    contrasenia: str = Field(..., description="Contraseña del usuario")
    # Campos específicos de UsuarioDTO
    direccion: str = Field(..., description="Dirección del usuario")
    id_reserva: str = Field(..., description="ID de reserva asociada")


class NotificacionCreate(BaseModel):
    id_persona: str = Field(..., alias="personId", description="ID de la persona destinataria")
    emailDestino: str = Field(..., description="Email de destino")
    titulo: str = Field(..., description="Título de la notificación")
    mensaje: str = Field(..., description="Mensaje de la notificación")
    model_config = ConfigDict(populate_by_name=True)

class NotificacionResponse(BaseModel):
    id: Optional[int] = Field(None, description="ID de la notificación")
    id_persona: str = Field(..., alias="personId", description="ID de la persona destinataria")
    emailDestino: str = Field(..., description="Email de destino")
    titulo: str = Field(..., description="Título de la notificación")
    mensaje: str = Field(..., description="Mensaje de la notificación")
    model_config = ConfigDict(populate_by_name=True)


class MantenimientoCreate(BaseModel):
    id_avion: str = Field(..., description="ID del avión")
    tipo: TipoMantenimiento = Field(..., description="Tipo de mantenimiento")
    descripcion: str = Field(..., description="Descripción del mantenimiento")
    fecha: str = Field(..., description="Fecha del mantenimiento (YYYY-MM-DD)")
    responsable: str = Field(..., description="Responsable")
    costo: float = Field(..., description="Costo", ge=0)
    estado: EstadoMantenimiento = Field(EstadoMantenimiento.PENDIENTE, description="Estado")


class EmpleadoCreate(BaseModel):
    """Modelo para crear un nuevo empleado."""
    nombre: str = Field(..., description="Nombre del empleado")
    email: str = Field(..., description="Email del empleado")
    cedula: str = Field(..., description="Cédula del empleado")
    telefono: Optional[str] = Field(None, description="Teléfono del empleado")
    salario: Optional[float] = Field(None, description="Salario del empleado", ge=0)
    cargo: Optional[str] = Field(None, description="Cargo del empleado")


class AdminCreate(BaseModel):
    """Modelo para crear un nuevo administrador."""
    nombre: str = Field(..., description="Nombre del administrador")
    email: str = Field(..., description="Email del administrador")
    cedula: str = Field(..., description="Cédula del administrador")
    telefono: Optional[str] = Field(None, description="Teléfono del administrador")
    nivel_acceso: Optional[str] = Field("ADMIN", description="Nivel de acceso del administrador")


# ==============================================
# MODELOS DE RESPUESTA (GET)
# ==============================================

class ReservaResponse(BaseModel):
    id: Optional[str] = Field(None, description="ID de la reserva")
    usuario: str = Field(..., description="Usuario de la reserva")
    id_vuelo: str = Field(..., description="ID del vuelo")
    estado: str = Field(..., description="Estado de la reserva")
    Numasiento: str = Field(..., description="Número de asiento")


class AvionResponse(BaseModel):
    """Modelo de respuesta para un avión."""
    id: Optional[int] = Field(None, description="ID único del avión")
    modelo: str = Field(..., description="Modelo del avión")
    capacidad: int = Field(..., description="Capacidad de pasajeros")
    aerolinea: str = Field(..., description="Aerolínea propietaria")
    estado: EstadoAvion = Field(..., description="Estado del avión")
    fecha_fabricacion: Optional[str] = Field(None, description="Fecha de fabricación")
    fecha_creacion: Optional[str] = Field(None, description="Fecha de creación")
    fecha_actualizacion: Optional[str] = Field(None, description="Fecha de actualización")
    
    class Config:
        use_enum_values = True


class PagoResponse(BaseModel):
    id: Optional[int] = Field(None, description="ID del pago")
    monto: float = Field(..., description="Monto del pago")
    fecha: Optional[str] = Field(None, description="Fecha del pago")
    estado: EstadoPago = Field(..., description="Estado del pago")
    moneda: str = Field(..., description="Moneda del pago")
    metodo_pago: Optional[MetodoPago] = Field(None, description="Método de pago")
    id_reserva: str = Field(..., description="ID de la reserva asociada")

class EstadoVuelo(str, Enum):
    PROGRAMADO = "PROGRAMADO"
    EN_VUELO = "EN_VUELO"
    ATERRIZADO = "ATERRIZADO"
    CANCELADO = "CANCELADO"
    DEMORADO = "DEMORADO"

class VueloCreate(BaseModel):
    codigoVuelo: str = Field(..., description="Código único del vuelo")
    origen: str = Field(..., description="Aeropuerto de origen")
    destino: str = Field(..., description="Aeropuerto de destino")
    id_avion: str = Field(..., alias="avionId", description="ID del avión")
    id_piloto: str = Field(..., alias="pilotoId", description="ID del piloto")
    fecha: str = Field(..., description="Fecha YYYY-MM-DD")
    hora: str = Field(..., description="Hora HH:MM o HH:MM:SS")
    duracionMinutos: int = Field(..., description="Duración en minutos", gt=0)
    estado: Optional[EstadoVuelo] = Field(EstadoVuelo.PROGRAMADO, description="Estado del vuelo")
    precioBase: float = Field(..., description="Precio base")
    model_config = ConfigDict(populate_by_name=True)

class VueloResponse(BaseModel):
    id: Optional[str] = Field(None, description="ID del vuelo")
    codigoVuelo: str = Field(..., description="Código único del vuelo")
    origen: str = Field(..., description="Aeropuerto de origen")
    destino: str = Field(..., description="Aeropuerto de destino")
    id_avion: str = Field(..., alias="avionId", description="ID del avión")
    id_piloto: str = Field(..., alias="pilotoId", description="ID del piloto")
    fecha: str = Field(..., description="Fecha YYYY-MM-DD")
    hora: str = Field(..., description="Hora HH:MM o HH:MM:SS")
    duracionMinutos: int = Field(..., description="Duración en minutos")
    estado: Optional[str] = Field(None, description="Estado del vuelo")
    precioBase: float = Field(..., description="Precio base")
    model_config = ConfigDict(populate_by_name=True)


class MantenimientoResponse(BaseModel):
    id: Optional[str] = Field(None, description="ID del mantenimiento")
    id_avion: str = Field(..., alias="avion_id", description="ID del avión")
    tipo: str = Field(..., description="Tipo de mantenimiento")
    descripcion: str = Field(..., description="Descripción del mantenimiento")
    fecha: str = Field(..., description="Fecha del mantenimiento (YYYY-MM-DD)")
    responsable: str = Field(..., description="Responsable")
    costo: float = Field(..., description="Costo")
    estado: str = Field(..., description="Estado")
    model_config = ConfigDict(populate_by_name=True)


class UsuarioResponse(BaseModel):
    """Modelo de respuesta para un usuario."""
    id: Optional[int] = Field(None, description="ID único del usuario")
    nombre: str = Field(..., description="Nombre del usuario")
    email: str = Field(..., description="Email del usuario")
    cedula: str = Field(..., description="Cédula del usuario")
    telefono: Optional[str] = Field(None, description="Teléfono del usuario")
    direccion: Optional[str] = Field(None, description="Dirección del usuario")
    id_reserva: Optional[str] = Field(None, alias="reserva_id", description="ID de reserva asociada")
    fecha_creacion: Optional[str] = Field(None, description="Fecha de creación")
    fecha_actualizacion: Optional[str] = Field(None, description="Fecha de actualización")
    model_config = ConfigDict(populate_by_name=True)


class EmpleadoResponse(BaseModel):
    """Modelo de respuesta para un empleado."""
    id: Optional[int] = Field(None, description="ID único del empleado")
    nombre: str = Field(..., description="Nombre del empleado")
    email: str = Field(..., description="Email del empleado")
    cedula: str = Field(..., description="Cédula del empleado")
    telefono: Optional[str] = Field(None, description="Teléfono del empleado")
    salario: Optional[float] = Field(None, description="Salario del empleado")
    cargo: Optional[str] = Field(None, description="Cargo del empleado")
    fecha_creacion: Optional[str] = Field(None, description="Fecha de creación")
    fecha_actualizacion: Optional[str] = Field(None, description="Fecha de actualización")


class AdminResponse(BaseModel):
    """Modelo de respuesta para un administrador."""
    id: Optional[int] = Field(None, description="ID único del administrador")
    nombre: str = Field(..., description="Nombre del administrador")
    email: str = Field(..., description="Email del administrador")
    cedula: str = Field(..., description="Cédula del administrador")
    telefono: Optional[str] = Field(None, description="Teléfono del administrador")
    nivel_acceso: Optional[str] = Field("ADMIN", description="Nivel de acceso")
    fecha_creacion: Optional[str] = Field(None, description="Fecha de creación")
    fecha_actualizacion: Optional[str] = Field(None, description="Fecha de actualización")


# ==============================================
# MODELOS DE CONSULTA (QUERY PARAMETERS)
# ==============================================

class ReservaQuery(BaseModel):
    """Modelo para consultas de reservas."""
    usuario: Optional[str] = Field(None, description="Filtrar por usuario")
    id_vuelo: Optional[str] = Field(None, description="Filtrar por ID de vuelo")
    estado: Optional[EstadoReserva] = Field(None, description="Filtrar por estado")
    fecha_desde: Optional[str] = Field(None, description="Fecha desde (YYYY-MM-DD)")
    fecha_hasta: Optional[str] = Field(None, description="Fecha hasta (YYYY-MM-DD)")
    limit: Optional[int] = Field(10, description="Límite de resultados", ge=1, le=100)
    offset: Optional[int] = Field(0, description="Offset para paginación", ge=0)
    
    class Config:
        use_enum_values = True


class AvionQuery(BaseModel):
    """Modelo para consultas de aviones."""
    aerolinea: Optional[str] = Field(None, description="Filtrar por aerolínea")
    estado: Optional[EstadoAvion] = Field(None, description="Filtrar por estado")
    modelo: Optional[str] = Field(None, description="Filtrar por modelo")
    capacidad_min: Optional[int] = Field(None, description="Capacidad mínima", ge=1)
    capacidad_max: Optional[int] = Field(None, description="Capacidad máxima", ge=1)
    fecha_fabricacion: Optional[str] = Field(None, description="Filtrar por fecha de fabricación")
    limit: Optional[int] = Field(10, description="Límite de resultados", ge=1, le=100)
    offset: Optional[int] = Field(0, description="Offset para paginación", ge=0)
    
    class Config:
        use_enum_values = True


class PagoQuery(BaseModel):
    """Modelo para consultas de pagos."""
    usuario: Optional[str] = Field(None, description="Filtrar por usuario")
    metodo: Optional[MetodoPago] = Field(None, description="Filtrar por método de pago")
    estado: Optional[EstadoPago] = Field(None, description="Filtrar por estado")
    moneda: Optional[str] = Field(None, description="Filtrar por moneda")
    monto_min: Optional[float] = Field(None, description="Monto mínimo", ge=0)
    monto_max: Optional[float] = Field(None, description="Monto máximo", ge=0)
    fecha_desde: Optional[str] = Field(None, description="Fecha desde (YYYY-MM-DD)")
    fecha_hasta: Optional[str] = Field(None, description="Fecha hasta (YYYY-MM-DD)")
    reserva_id: Optional[str] = Field(None, description="Filtrar por ID de reserva")
    limit: Optional[int] = Field(10, description="Límite de resultados", ge=1, le=100)
    offset: Optional[int] = Field(0, description="Offset para paginación", ge=0)
    
    class Config:
        use_enum_values = True


class MantenimientoQuery(BaseModel):
    """Modelo para consultas de mantenimientos."""
    avion_id: Optional[int] = Field(None, description="Filtrar por ID de avión", gt=0)
    tipo: Optional[TipoMantenimiento] = Field(None, description="Filtrar por tipo")
    estado: Optional[EstadoMantenimiento] = Field(None, description="Filtrar por estado")
    tecnico_asignado: Optional[str] = Field(None, description="Filtrar por técnico")
    fecha_inicio_desde: Optional[str] = Field(None, description="Fecha inicio desde (YYYY-MM-DD)")
    fecha_inicio_hasta: Optional[str] = Field(None, description="Fecha inicio hasta (YYYY-MM-DD)")
    costo_min: Optional[float] = Field(None, description="Costo mínimo", ge=0)
    costo_max: Optional[float] = Field(None, description="Costo máximo", ge=0)
    limit: Optional[int] = Field(10, description="Límite de resultados", ge=1, le=100)
    offset: Optional[int] = Field(0, description="Offset para paginación", ge=0)
    
    class Config:
        use_enum_values = True


# ==============================================
# MODELOS DE RESPUESTA COLECTIVA
# ==============================================

class ReservasListResponse(BaseModel):
    """Respuesta para lista de reservas."""
    reservas: List[ReservaResponse] = Field(default_factory=list)
    total: int = Field(0, description="Total de reservas")
    limit: int = Field(10, description="Límite aplicado")
    offset: int = Field(0, description="Offset aplicado")


class AvionesListResponse(BaseModel):
    """Respuesta para lista de aviones."""
    aviones: List[AvionResponse] = Field(default_factory=list)
    total: int = Field(0, description="Total de aviones")
    limit: int = Field(10, description="Límite aplicado")
    offset: int = Field(0, description="Offset aplicado")


class PagosListResponse(BaseModel):
    """Respuesta para lista de pagos."""
    pagos: List[PagoResponse] = Field(default_factory=list)
    total: int = Field(0, description="Total de pagos")
    limit: int = Field(10, description="Límite aplicado")
    offset: int = Field(0, description="Offset aplicado")


class MantenimientosListResponse(BaseModel):
    """Respuesta para lista de mantenimientos."""
    mantenimientos: List[MantenimientoResponse] = Field(default_factory=list)
    total: int = Field(0, description="Total de mantenimientos")
    limit: int = Field(10, description="Límite aplicado")
    offset: int = Field(0, description="Offset aplicado")


# ==============================================
# MODELOS DE ESTADÍSTICAS Y CONTADORES
# ==============================================

class ContadorResponse(BaseModel):
    """Respuesta para contadores simples."""
    count: int = Field(..., description="Número total")
    entity: str = Field(..., description="Tipo de entidad contada")
    timestamp: Optional[str] = Field(None, description="Timestamp de la consulta")


class EstadisticasResponse(BaseModel):
    """Respuesta para estadísticas generales."""
    total_reservas: int = Field(0, description="Total de reservas")
    total_aviones: int = Field(0, description="Total de aviones")
    total_pagos: int = Field(0, description="Total de pagos")
    total_mantenimientos: int = Field(0, description="Total de mantenimientos")
    total_usuarios: int = Field(0, description="Total de usuarios")
    timestamp: Optional[str] = Field(None, description="Timestamp de la consulta")


class PersonaResponse(BaseModel):
    id: Optional[int] = Field(None, description="ID de la persona")
    cedula: str = Field(..., description="Cédula")
    nombre: str = Field(..., description="Nombre")
    apellido: str = Field(..., description="Apellido")
    telefono: str = Field(..., description="Teléfono")
    email: str = Field(..., description="Email")
    rol: Optional[str] = Field(None, description="Rol")
    contrasenia: Optional[str] = Field(None, description="Contraseña (hash)")


# ==============================================
# MAPEO DE MODELOS PARA EL SERVIDOR MCP
# ==============================================

class MCPModelMapper:
    """
    Mapeador centralizado de modelos para el servidor MCP.
    Facilita la asignación de modelos a herramientas específicas.
    """
    
    # Modelos de creación
    CREATE_MODELS = {
        "reservas_crear": ReservaCreate,
        "create_avion": AvionCreate,
        "pagos_crear": PagoCreate,
        "mantenimientos_crear": MantenimientoCreate,
        "usuario_create": UsuarioCreate,  # Actualizado para coincidir con el nombre real de la herramienta
        "empleados_crear": EmpleadoCreate,
        "admins_crear": AdminCreate,
        "notificaciones_crear": NotificacionCreate,
        "vuelos_crear": VueloCreate,
        # Agregar más herramientas de creación según los nombres reales del servidor MCP
        "empleado_create": EmpleadoCreate,
        "admin_create": AdminCreate,
        "avion_create": AvionCreate,
        "pago_create": PagoCreate,
        "reserva_create": ReservaCreate,
        "mantenimiento_create": MantenimientoCreate,
        "notificacion_create": NotificacionCreate,
        "vuelo_create": VueloCreate,
    }
    
    # Modelos de respuesta individual
    RESPONSE_MODELS = {
        "reservas": ReservaResponse,
        "aviones": AvionResponse,
        "pagos": PagoResponse,
        "mantenimientos": MantenimientoResponse,
        "usuarios": UsuarioResponse,
        "empleados": EmpleadoResponse,
        "admins": AdminResponse,
        "notificaciones": NotificacionResponse,
        "vuelos": VueloResponse,
        "personas": PersonaResponse,
    }
    
    # Modelos de respuesta de lista
    LIST_RESPONSE_MODELS = {
        "reservas_list": ReservasListResponse,
        "aviones_list": AvionesListResponse,
        "pagos_list": PagosListResponse,
        "mantenimientos_list": MantenimientosListResponse,
    }
    
    # Modelos de consulta
    QUERY_MODELS = {
        "reservas_query": ReservaQuery,
        "aviones_query": AvionQuery,
        "pagos_query": PagoQuery,
        "mantenimientos_query": MantenimientoQuery,
    }
    
    @classmethod
    def get_create_model(cls, tool_name: str) -> Optional[BaseModel]:
        """Obtiene el modelo de creación para una herramienta."""
        return cls.CREATE_MODELS.get(tool_name)

    @classmethod
    def resolve_model_by_schema(cls, schema: Dict[str, Any]) -> Optional[BaseModel]:
        try:
            req = schema.get("required", []) or []
            props = schema.get("properties", {}) or {}
            keys: List[str] = []
            if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
                inner = props.get(req[0], {})
                keys = (inner.get("required", []) or [])
            else:
                keys = req
            if not keys:
                return None
            best_model = None
            best_score = -1.0
            for _, model in cls.CREATE_MODELS.items():
                try:
                    m_schema = model.model_json_schema() or {}
                    m_required = m_schema.get("required", []) or []
                    if not m_required:
                        continue
                    inter = len(set(keys) & set(m_required))
                    score = inter / max(1, len(set(keys)))
                    if score > best_score:
                        best_score = score
                        best_model = model
                except Exception:
                    continue
            return best_model
        except Exception:
            return None
    
    @classmethod
    def get_response_model(cls, entity_type: str) -> Optional[BaseModel]:
        """Obtiene el modelo de respuesta para un tipo de entidad."""
        return cls.RESPONSE_MODELS.get(entity_type)
    
    @classmethod
    def get_list_response_model(cls, entity_type: str) -> Optional[BaseModel]:
        """Obtiene el modelo de respuesta de lista para un tipo de entidad."""
        return cls.LIST_RESPONSE_MODELS.get(f"{entity_type}_list")
    
    @classmethod
    def get_query_model(cls, entity_type: str) -> Optional[BaseModel]:
        """Obtiene el modelo de consulta para un tipo de entidad."""
        return cls.QUERY_MODELS.get(f"{entity_type}_query")
    
    @classmethod
    def validate_create_data(cls, tool_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida datos de creación usando el modelo correspondiente.
        
        Args:
            tool_name: Nombre de la herramienta MCP
            data: Datos a validar
            
        Returns:
            Datos validados y normalizados
        """
        model_class = cls.get_create_model(tool_name)
        if not model_class:
            return data
        
        try:
            model_instance = model_class(**data)
            return model_instance.model_dump()
        except Exception as e:
            # Si falla la validación, retornar datos originales con error
            return {**data, "_validation_error": str(e)}
    
    @classmethod
    def validate_response_data(cls, entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida datos de respuesta usando el modelo correspondiente.
        
        Args:
            entity_type: Tipo de entidad (reservas, aviones, etc.)
            data: Datos a validar
            
        Returns:
            Datos validados y normalizados
        """
        model_class = cls.get_response_model(entity_type)
        if not model_class:
            return data
        
        try:
            model_instance = model_class(**data)
            return model_instance.model_dump()
        except Exception as e:
            # Si falla la validación, retornar datos originales con error
            return {**data, "_validation_error": str(e)}


# ==============================================
# EXPORTACIONES PARA COMPATIBILIDAD
# ==============================================

# Mantener compatibilidad con microservice_models.py
ReservaModel = ReservaCreate
AvionModel = AvionCreate
PagoModel = PagoCreate
MantenimientoModel = MantenimientoCreate

# Exportar el mapeador principal
ModelMapper = MCPModelMapper
