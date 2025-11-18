
"""
# server_mcp.py
Servidor MCP (Model Context Protocol) para gestión de aviones.

Expone herramientas MCP que consumen microservicios vía API Gateway HTTP.
Herramientas disponibles: consultar y crear aviones. Este servidor se comunica por stdio con el cliente MCP.
"""

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, List, Optional, Dict, Any
from datetime import datetime

import os
from dotenv import load_dotenv
import httpx
import asyncio
import hashlib
import time
import json

# Cargar variables de entorno
load_dotenv()

from pydantic import BaseModel, Field
from AgenteIA.app.models.mcp_models import (
    NotificacionCreate as MCPNotificacionCreate,
    NotificacionResponse as MCPNotificacionResponse,
    AvionResponse as MCPAvionResponse,
    AvionCreate as MCPAvionCreate,
    PagoResponse as MCPPagoResponse,
    PagoCreate as MCPPagoCreate,
    ReservaResponse as MCPReservaResponse,
    ReservaCreate as MCPReservaCreate,
    MantenimientoResponse as MCPMantenimientoResponse,
    MantenimientoCreate as MCPMantenimientoCreate,
    UsuarioResponse as MCPUsuarioResponse,
    UsuarioCreate as MCPUsuarioCreate,
    EmpleadoResponse as MCPEmpleadoResponse,
    AdminResponse as MCPAdminResponse,
    VueloResponse as MCPVueloResponse,
    VueloCreate as MCPVueloCreate,
    PersonaResponse as MCPPersonaResponse,
    ContadorResponse as MCPContadorResponse,
)
from mcp.server.fastmcp import FastMCP, Context

# --- 1. Modelos para Aviones (usando mcp_models) ---
Avion = MCPAvionResponse
AvionCreate = MCPAvionCreate

class AvionCount(BaseModel):
    total_aviones: int

# Modelos Pydantic para otros microservicios
from pydantic import ConfigDict

Pago = MCPPagoResponse
PagoCreate = MCPPagoCreate

class MontoQuery(BaseModel):
    monto: float

Reserva = MCPReservaResponse
ReservaCreate = MCPReservaCreate

Mantenimiento = MCPMantenimientoResponse
MantenimientoCreate = MCPMantenimientoCreate

# --- Modelos Pydantic para Microservicio de Usuarios ---
Persona = MCPPersonaResponse
Usuario = MCPUsuarioResponse
UsuarioCreate = MCPUsuarioCreate
Empleado = MCPEmpleadoResponse
Admin = MCPAdminResponse

# Eliminado: UpdatePasswordRequest (no se permiten operaciones de actualización)




Notificacion = MCPNotificacionResponse
NotificacionCreate = MCPNotificacionCreate






Vuelo = MCPVueloResponse
VueloCreate = MCPVueloCreate
class VueloUpdate(VueloCreate):
    id: Optional[str] = None
# --- 2. Contexto y Ciclo de Vida del Servidor HTTP ---
@dataclass
class AppContext:
    """Contexto de aplicación compartido por todas las herramientas (cliente HTTP)."""

    http_client: httpx.AsyncClient






@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Crea y cierra el cliente HTTP durante el ciclo de vida del server."""
    # Habilitamos follow_redirects para manejar respuestas 307 del API Gateway
    http_client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)
    try:
        yield AppContext(http_client=http_client)
    finally:
        await http_client.aclose()
        print("🔌 Cliente HTTP cerrado.")





# --- 3. Creación del Servidor MCP ---
# Le pasamos el nuevo gestor de ciclo de vida y configuración de puerto
port = int(os.getenv("PORT", "3001"))
mcp = FastMCP("AvionesServer", lifespan=app_lifespan, host="0.0.0.0", port=port)

# Nota: Algunas versiones del paquete mcp no exponen el atributo `router` en FastMCP.
# Para maximizar compatibilidad, evitamos definir rutas HTTP personalizadas aquí.
# El servidor SSE se inicia con `mcp.run(transport="sse")` en el bloque main.

# --- 4. Herramientas MCP para Aviones (HTTP vía API Gateway) ---

# Base URL del API Gateway para el microservicio de aviones
# rstrip('/') para evitar dobles barras al construir rutas
AVIONES_BASE_URL = (os.getenv("AVIONES_BASE_URL", "http://localhost:8080/ServiceAvion") or "").rstrip("/")
USER_SERVICE_API_KEY = (os.getenv("USER_SERVICE_API_KEY", "n9PqV2rX6jZ4mC7vB1kL3gH5fD8sA0qW2eR4tY6uI8oPz9xV1cZ3bN5mK7jL9gH4fD6sA1qW3eR5tY7uI9oPz0xV2cZ4bN6mK8jLgH5fD7sA2qW4eR6tY8uI0oPz9xV1cZ3bN5mK7jL9gH4fD6sA1qW3eR5tY7uI9oPz0xV2cZ4bN6mK8jLgH5fD7sA2qW4eR6tY8uI0oP") or "").strip()

@mcp.tool()
async def get_total_avion_count(ctx: Context) -> MCPContadorResponse:
    """Devuelve contador total de aviones usando modelo de mcp_models."""
    url = f"{AVIONES_BASE_URL}/aviones"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error al contar aviones: {data}")
    if isinstance(data, list):
        total = len(data)
    else:
        items = data.get("items") if isinstance(data, dict) else None
        total = len(items) if isinstance(items, list) else 0
    return MCPContadorResponse(count=total, entity="aviones")

@mcp.tool()
async def listar_aviones(ctx: Context) -> List[Avion]:
    """Lista todos los aviones vía API Gateway.

    Sinónimos: listar aviones, mostrar todos los aviones, ver aviones, aviones.
    """
    url = f"{AVIONES_BASE_URL}/aviones"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Avion.model_validate(item) for item in (data or [])]

@mcp.tool()
async def get_avion_by_id(avion_id: int, ctx: Context) -> Optional[Avion]:
    """Obtiene un avión por su ID usando API Gateway."""
    url = f"{AVIONES_BASE_URL}/aviones/{avion_id}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return None
    try:
        return Avion.model_validate(data)
    except Exception:
        return None

@mcp.tool()
async def get_aviones_by_estado(estado: str, ctx: Context) -> List[Avion]:
    """Lista aviones por estado (disponible, mantenimiento, fuera_de_servicio) vía API Gateway."""
    url = f"{AVIONES_BASE_URL}/estado/{estado}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Avion.model_validate(item) for item in (data or [])]

@mcp.tool()
async def get_aviones_by_aerolinea(aerolinea: str, ctx: Context) -> List[Avion]:
    """Lista aviones por aerolínea vía API Gateway."""
    url = f"{AVIONES_BASE_URL}/aerolinea/{aerolinea}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Avion.model_validate(item) for item in (data or [])]

@mcp.tool()
async def get_aviones_by_fecha_fabricacion(fecha_fabricacion: str, ctx: Context) -> List[Avion]:
    """Lista aviones por fecha de fabricación exacta (formato YYYY-MM-DD) vía API Gateway."""
    try:
        fecha_str = datetime.fromisoformat(fecha_fabricacion).strftime("%Y-%m-%d")
    except Exception:
        fecha_str = fecha_fabricacion
    url = f"{AVIONES_BASE_URL}/fecha-fabricacion/{fecha_str}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Avion.model_validate(item) for item in (data or [])]

@mcp.tool()
async def create_avion(avion: AvionCreate, ctx: Context) -> Avion:
    """Crea un avión y devuelve el registro creado (vía API Gateway)."""
    url = f"{AVIONES_BASE_URL}/aviones"
    payload = avion.model_dump(mode="json")
    data = await _http_post(ctx, url, json=payload)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return Avion.model_validate(data)





# --- 5. Herramientas MCP HTTP para otros microservicios ---
# Configuración de URLs base para microservicios (sobrescribibles por variables de entorno)
PAGO_BASE_URL = (os.getenv("PAGO_BASE_URL", "http://localhost:8080/ServicePago") or "").rstrip("/")
RESERVA_BASE_URL = (os.getenv("RESERVA_BASE_URL", "http://localhost:8080/ServiceReserva/api") or "").rstrip("/")
MANTENIMIENTO_BASE_URL = (os.getenv("MANTENIMIENTO_BASE_URL", "http://localhost:8080/ServiceMantenimiento") or "").rstrip("/")
USUARIOS_BASE_URL = (os.getenv("USUARIOS_BASE_URL", "http://localhost:8081/Servicio1/api") or "").rstrip("/")
NOTIFICACIONES_BASE_URL = (os.getenv("NOTIFICACIONES_BASE_URL", "http://localhost:8080/ServiceNotificaciones/api") or "").rstrip("/")
VUELOS_BASE_URL = (os.getenv("VUELOS_BASE_URL", "http://localhost:8888/GestionVuelos/api") or "").rstrip("/")



_IDEMPOTENCY_TTL_SECONDS = int(os.getenv("IDEMPOTENCY_TTL_SECONDS", "15"))
_recent_post_cache: Dict[str, Any] = {}

def _make_idempotency_key(url: str, payload: Optional[Dict[str, Any]]) -> str:
    try:
        body = payload or {}
        key_data = json.dumps(body, sort_keys=True, separators=(",", ":"))
        raw = f"{url}|{key_data}"
        return hashlib.sha256(raw.encode()).hexdigest()
    except Exception:
        return hashlib.sha256(f"{url}|{str(payload)}".encode()).hexdigest()

# Helper HTTP compartido (MODIFICADO)
async def _http_request(ctx: Context, method: str, url: str, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None):
    client: httpx.AsyncClient = ctx.request_context.lifespan_context.http_client
    max_retries = int(os.getenv("HTTP_MAX_RETRIES", "2"))
    backoff_ms = int(os.getenv("HTTP_RETRY_BACKOFF_MS", "200"))
    
    headers = {}
    if url.startswith(USUARIOS_BASE_URL) and USER_SERVICE_API_KEY:
        headers["X-API-Key"] = USER_SERVICE_API_KEY
    attempt = 0
    idempotency_key = None
    if method.upper() == "POST" and json is not None:
        idempotency_key = _make_idempotency_key(url, json)
        cached = _recent_post_cache.get(idempotency_key)
        if cached:
            ts = cached.get("ts", 0)
            if time.time() - ts < _IDEMPOTENCY_TTL_SECONDS:
                return cached.get("data")
        headers["X-Idempotency-Key"] = idempotency_key
    while True:
        try:
            # 4. Pasa los headers (vacíos o con la clave) a la petición
            resp = await client.request(method, url, params=params, json=json, headers=headers)
            
            resp.raise_for_status()
            try:
                data = resp.json()
            except Exception:
                data = {"status": "ok", "result": resp.text}
            if idempotency_key:
                try:
                    _recent_post_cache[idempotency_key] = {"ts": time.time(), "data": data}
                except Exception:
                    pass
            return data
        except httpx.HTTPStatusError as e:
            # ... (tu manejo de errores no cambia)
            body_text = ""
            try:
                body_text = e.response.text
            except Exception:
                body_text = ""
            # (Añadido log para debugging)
            if e.response.status_code in (401, 403):
                print(f"ERROR 401/403: Llamada a {url} falló. ¿API Key incorrecta o SecurityConfig de Java no está listo?")
            
            return {"status": "error", "code": e.response.status_code, "message": str(e), "url": str(e.request.url), "body": body_text}
        except httpx.RequestError as e:
            # ... (tu manejo de reintentos no cambia)
            if attempt < max_retries:
                attempt += 1
                await asyncio.sleep(backoff_ms / 1000.0)
                continue
            return {"status": "error", "message": f"HTTP request failed: {e}", "url": getattr(e, 'request', None) and str(e.request.url)}



async def _http_get(ctx: Context, url: str, params: Optional[Dict[str, Any]] = None):
    return await _http_request(ctx, "GET", url, params=params)

async def _http_post(ctx: Context, url: str, json: Optional[Dict[str, Any]] = None):
    return await _http_request(ctx, "POST", url, json=json)






# Operaciones PUT/DELETE eliminadas: solo create y get

   
# --- Pagos ---
@mcp.tool()
async def listar_pagos(ctx: Context) -> List[Pago]:
    """
    Listar pagos.
    Sinónimos: listar pagos, mostrar pagos, ver pagos, obtener pagos.
    """
    url = f"{PAGO_BASE_URL}/get-all"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Pago.model_validate(item) for item in (data or [])]





@mcp.tool()
async def pagos_get_by_id(id: int, ctx: Context) -> Optional[Pago]:
    """Obtiene un pago por su ID (valida respuesta)."""
    url = f"{PAGO_BASE_URL}/get/{id}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return None
    try:
        return Pago.model_validate(data)
    except Exception:
        return None





@mcp.tool()
async def pagos_buscar_por_estado(estado: str, ctx: Context) -> List[Pago]:
    """Busca pagos por estado: PENDIENTE, COMPLETADO o CANCELADO."""
    url = f"{PAGO_BASE_URL}/buscar/estado/{estado}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Pago.model_validate(item) for item in (data or [])]

@mcp.tool()
async def pagos_buscar_por_reserva(reserva_id: str, ctx: Context) -> Optional[Pago]:
    """Busca pago asociado a una reserva (ID de reserva como string)."""
    url = f"{PAGO_BASE_URL}/buscar/reserva/{reserva_id}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return None
    try:
        return Pago.model_validate(data)
    except Exception:
        return None

@mcp.tool()
async def pagos_buscar_por_moneda(moneda: str, ctx: Context) -> List[Pago]:
    """Busca pagos por moneda."""
    url = f"{PAGO_BASE_URL}/buscar/moneda/{moneda}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Pago.model_validate(item) for item in (data or [])]

@mcp.tool()
async def pagos_buscar_por_monto(query: MontoQuery, ctx: Context) -> List[Pago]:
    """Busca pagos por monto."""
    url = f"{PAGO_BASE_URL}/buscar/monto/{query.monto}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Pago.model_validate(item) for item in (data or [])]

@mcp.tool()
async def pagos_buscar_por_fecha(fecha: str, ctx: Context) -> List[Pago]:
    """Busca pagos por fecha (YYYY-MM-DD)."""
    url = f"{PAGO_BASE_URL}/buscar/fecha/{fecha}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Pago.model_validate(item) for item in (data or [])]

@mcp.tool()
async def pagos_buscar_por_metodo(metodo: str, ctx: Context) -> List[Pago]:
    """Busca pagos por método de pago."""
    url = f"{PAGO_BASE_URL}/buscar/metodo/{metodo}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Pago.model_validate(item) for item in (data or [])]

@mcp.tool()
async def pagos_crear(pago: PagoCreate, ctx: Context) -> Pago:
    """Crea un pago (payload validado) y retorna el registro creado."""
    url = f"{PAGO_BASE_URL}/crear"
    payload = pago.model_dump(mode="json")
    try:
        if not payload.get("fecha"):
            payload["fecha"] = datetime.now().isoformat()
    except Exception:
        pass
    data = await _http_post(ctx, url, json=payload)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return Pago.model_validate(data)

# Operaciones de actualización y borrado de pagos eliminadas (solo create/get)

# --- Reservas ---
@mcp.tool()
async def listar_reservas(ctx: Context) -> List[Reserva]:
    """
    Listar reservas registradas.
    Sinónimos: listar reservas, mostrar reservas, ver reservas, obtener reservas.
    """
    url = f"{RESERVA_BASE_URL}/reservas"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Reserva.model_validate(item) for item in (data or [])]

@mcp.tool()
async def reservas_get_by_id(id: int, ctx: Context) -> Optional[Reserva]:
    """Obtiene reserva por ID (valida respuesta)."""
    url = f"{RESERVA_BASE_URL}/reservas/{id}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return None
    try:
        return Reserva.model_validate(data)
    except Exception:
        return None

@mcp.tool()
async def reservas_buscar_por_usuario(usuario: str, ctx: Context) -> List[Reserva]:
    """Busca reservas por usuario (query param usuario)."""
    url = f"{RESERVA_BASE_URL}/reservas/buscar/usuario"
    data = await _http_get(ctx, url, params={"usuario": usuario})
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Reserva.model_validate(item) for item in (data or [])]

@mcp.tool()
async def reservas_buscar_por_estado(estado: str, ctx: Context) -> List[Reserva]:
    """Busca reservas por estado (query param estado)."""
    url = f"{RESERVA_BASE_URL}/reservas/buscar/estado"
    data = await _http_get(ctx, url, params={"estado": estado})
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Reserva.model_validate(item) for item in (data or [])]

@mcp.tool()
async def reservas_buscar_por_vuelo(id_vuelo: str, ctx: Context) -> List[Reserva]:
    """Busca reservas por id_vuelo (query param id_vuelo)."""
    url = f"{RESERVA_BASE_URL}/reservas/buscar/vuelo"
    data = await _http_get(ctx, url, params={"id_vuelo": id_vuelo})
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Reserva.model_validate(item) for item in (data or [])]

@mcp.tool()
async def reservas_contar(ctx: Context) -> int:
    """Cuenta el total de reservas."""
    url = f"{RESERVA_BASE_URL}/reservas/contar"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    try:
        return int(data) if not isinstance(data, dict) else int(data.get("result", data.get("count", data.get("total", 0))))
    except Exception:
        raise RuntimeError(f"Respuesta inesperada: {data}")

@mcp.tool()
async def reservas_contar_por_estado(estado: str, ctx: Context) -> int:
    """Cuenta reservas por estado (query param estado)."""
    url = f"{RESERVA_BASE_URL}/reservas/contar/estado"
    data = await _http_get(ctx, url, params={"estado": estado})
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    try:
        return int(data) if not isinstance(data, dict) else int(data.get("result", data.get("count", data.get("total", 0))))
    except Exception:
        raise RuntimeError(f"Respuesta inesperada: {data}")

@mcp.tool()
async def reservas_crear(reserva: ReservaCreate, ctx: Context) -> Reserva:
    """Crea una reserva (payload validado) y retorna el registro creado."""
    url = f"{RESERVA_BASE_URL}/reservas"
    payload = reserva.model_dump(mode="json")
    print(f"[reservas_crear] POST {url} payload={payload}")
    data = await _http_post(ctx, url, json=payload)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return Reserva.model_validate(data)

# --- Mantenimiento ---
@mcp.tool()
async def listar_mantenimientos(ctx: Context) -> List[Mantenimiento]:
    """Listar mantenimientos."""
    url = f"{MANTENIMIENTO_BASE_URL}/mantenimientos"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Mantenimiento.model_validate(item) for item in (data or [])]

@mcp.tool()
async def mantenimientos_por_avion(id_avion: str, ctx: Context) -> List[Mantenimiento]:
    """Busca mantenimientos por ID de avión."""
    url = f"{MANTENIMIENTO_BASE_URL}/mantenimientos/avion/{id_avion}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Mantenimiento.model_validate(item) for item in (data or [])]

@mcp.tool()
async def mantenimientos_por_estado(estado: str, ctx: Context) -> List[Mantenimiento]:
    """Busca mantenimientos por estado."""
    url = f"{MANTENIMIENTO_BASE_URL}/mantenimientos/estado/{estado}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Mantenimiento.model_validate(item) for item in (data or [])]

@mcp.tool()
async def mantenimientos_get_by_id(id: str, ctx: Context) -> Optional[Mantenimiento]:
    """Obtiene un mantenimiento por ID."""
    url = f"{MANTENIMIENTO_BASE_URL}/mantenimientos/{id}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return None
    try:
        return Mantenimiento.model_validate(data)
    except Exception:
        return None

@mcp.tool()
async def mantenimientos_crear(mantenimiento: MantenimientoCreate, ctx: Context) -> Mantenimiento:
    """
    Crea un mantenimiento (payload validado) y retorna el registro creado.
    Usa este comando cuando el usuario diga cosas como:
    - "Crear mantenimiento para el avión AV-456"
    - "Registrar mantenimiento preventivo con fecha 2025-10-10"
    - "Agregar revisión de sistemas hidráulicos"
    
    """
    url = f"{MANTENIMIENTO_BASE_URL}/mantenimientos"
    payload = mantenimiento.model_dump(mode="json")
    # Normalizar fecha a 'YYYY-MM-DD' para cumplir validación del microservicio
    try:
        if isinstance(mantenimiento.fecha, datetime):
            payload["fecha"] = mantenimiento.fecha.strftime("%Y-%m-%d")
        else:
            fecha_val = payload.get("fecha")
            if isinstance(fecha_val, str):
                try:
                    dt = datetime.fromisoformat(fecha_val)
                    payload["fecha"] = dt.strftime("%Y-%m-%d")
                except Exception:
                    # Mantener formato original si no es ISO parseable
                    pass
    except Exception:
        # No bloquear por normalización; continuar con payload original
        pass
    data = await _http_post(ctx, url, json=payload)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return Mantenimiento.model_validate(data)

# Operaciones de actualización de mantenimientos eliminadas (solo create/get)

# --- Usuarios ---
@mcp.tool()
async def listar_usuarios(ctx: Context) -> List[Usuario]:
    """
    Listar usuarios del sistema.
    Sinónimos: listar usuarios, mostrar usuarios, ver usuarios, obtener usuarios.
    """
    url = f"{USUARIOS_BASE_URL}/usuarios/all"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Usuario.model_validate(item) for item in (data or [])]

@mcp.tool()
async def usuario_create(usuario: UsuarioCreate, ctx: Context) -> Usuario:
    """
    Crea un usuario (POST /usuarios/save) y devuelve el registro creado.

    Sinónimos: crear usuario, registrar usuario, nuevo usuario, usuarios save, alta de usuario.
    """
    url = f"{USUARIOS_BASE_URL}/usuarios/save"
    payload = usuario.model_dump(mode="json")
    data = await _http_post(ctx, url, json=payload)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    # Validamos contra el modelo Usuario
    return Usuario.model_validate(data)

@mcp.tool()
async def usuario_get_by_id(id: int, ctx: Context) -> Optional[Usuario]:
    """Obtiene usuario por ID."""
    url = f"{USUARIOS_BASE_URL}/usuarios/{id}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return None
    try:
        return Usuario.model_validate(data)
    except Exception:
        return None

@mcp.tool()
async def usuarios_count(ctx: Context) -> MCPContadorResponse:
    """Cuenta usuarios usando ContadorResponse."""
    url = f"{USUARIOS_BASE_URL}/usuarios/count"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    if isinstance(data, dict) and "count" in data:
        total = int(data["count"])
    else:
        total = int(data or 0)
    return MCPContadorResponse(count=total, entity="usuarios")

@mcp.tool()
async def usuarios_por_email(email: str, ctx: Context) -> Optional[Usuario]:
    """Busca usuario por email."""
    url = f"{USUARIOS_BASE_URL}/usuarios/email/{email}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return Usuario.model_validate(data) if data else None

@mcp.tool()
async def usuarios_por_cedula(cedula: str, ctx: Context) -> Optional[Usuario]:
    """Busca usuario por cédula."""
    url = f"{USUARIOS_BASE_URL}/usuarios/cedula/{cedula}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return Usuario.model_validate(data) if data else None

@mcp.tool()
async def listar_administradores(ctx: Context) -> List[Admin]:
    """
    Listar administradores.
    Sinónimos: listar administradores, mostrar administradores, ver administradores, obtener administradores.
    """
    url = f"{USUARIOS_BASE_URL}/admins/all"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Admin.model_validate(item) for item in (data or [])]

@mcp.tool()
async def listar_empleados(ctx: Context) -> List[Empleado]:
    """
    Listar empleados.
    Sinónimos: listar empleados, mostrar empleados, ver empleados, obtener empleados.
    """
    url = f"{USUARIOS_BASE_URL}/empleados/all"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Empleado.model_validate(item) for item in (data or [])]

@mcp.tool()
async def empleados_por_cargo(cargo: str, ctx: Context) -> List[Empleado]:
    """Busca empleados por cargo."""
    url = f"{USUARIOS_BASE_URL}/empleados/cargo/{cargo}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Empleado.model_validate(item) for item in (data or [])]

@mcp.tool()
async def listar_personas(ctx: Context) -> List[Persona]:
    """
    Listar personas.
    Sinónimos: listar personas, mostrar personas, ver personas, obtener personas.
    """
    url = f"{USUARIOS_BASE_URL}/personas/all"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Persona.model_validate(item) for item in (data or [])]




# --- Vuelos ---
@mcp.tool()
async def listar_vuelos(ctx: Context) -> List[Vuelo]:
    """Listar vuelos."""
    url = f"{VUELOS_BASE_URL}/vuelos"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Vuelo.model_validate(item) for item in (data or [])]

@mcp.tool()
async def vuelo_get_by_id(id: str, ctx: Context) -> Optional[Vuelo]:
    """Obtiene un vuelo por su ID (string UUID)."""
    url = f"{VUELOS_BASE_URL}/vuelos/{id}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return None
    try:
        return Vuelo.model_validate(data)
    except Exception:
        return None

@mcp.tool()
async def vuelo_get_by_codigo(codigoVuelo: str, ctx: Context) -> Optional[Vuelo]:
    """Obtiene un vuelo por su código (ej: AV1234)."""
    url = f"{VUELOS_BASE_URL}/vuelos/codigo/{codigoVuelo}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return None
    try:
        return Vuelo.model_validate(data)
    except Exception:
        return None

@mcp.tool()
async def vuelos_create(vuelo: VueloCreate, ctx: Context) -> Vuelo:
    """Crea un vuelo y devuelve el registro creado (201)."""
    url = f"{VUELOS_BASE_URL}/vuelos"
    payload = vuelo.model_dump(mode="json", by_alias=True)
    # Normalización de hora a HH:MM:SS si viene en HH:MM
    try:
        h = payload.get("hora")
        if isinstance(h, str) and len(h) == 5:
            payload["hora"] = f"{h}:00"
    except Exception:
        pass
    data = await _http_post(ctx, url, json=payload)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return Vuelo.model_validate(data)



@mcp.tool()
async def vuelos_buscar_por_ruta(origen: str, destino: str, ctx: Context) -> List[Vuelo]:
    """Busca vuelos por ruta (origen/destino)."""
    url = f"{VUELOS_BASE_URL}/vuelos/ruta/{origen}/{destino}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Vuelo.model_validate(item) for item in (data or [])]

@mcp.tool()
async def vuelos_buscar_por_estado(estado: str, ctx: Context) -> List[Vuelo]:
    """Busca vuelos por estado (PROGRAMADO, EN_VUELO, ATERRIZADO, CANCELADO)."""
    url = f"{VUELOS_BASE_URL}/vuelos/estado/{estado}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Vuelo.model_validate(item) for item in (data or [])]

@mcp.tool()
async def vuelos_buscar_por_fecha(fecha: str, ctx: Context) -> List[Vuelo]:
    """Busca vuelos por fecha (YYYY-MM-DD)."""
    url = f"{VUELOS_BASE_URL}/vuelos/fecha/{fecha}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Vuelo.model_validate(item) for item in (data or [])]

@mcp.tool()
async def vuelos_busqueda_avanzada(
    origen: str = "",
    destino: str = "",
    fecha: str = "",
    estado: str = "",
    id_avion: str = "",
    id_piloto: str = "",
    ctx: Context = None
) -> List[Vuelo]:
    """Búsqueda avanzada con combinación de parámetros."""
    url = f"{VUELOS_BASE_URL}/vuelos/busqueda"
    params: Dict[str, Any] = {}
    if origen: params["origen"] = origen
    if destino: params["destino"] = destino
    if fecha: params["fecha"] = fecha
    if estado: params["estado"] = estado
    if id_avion: params["id_avion"] = id_avion
    if id_piloto: params["id_piloto"] = id_piloto
    data = await _http_get(ctx, url, params=params)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Vuelo.model_validate(item) for item in (data or [])]

# @mcp.tool()  # disabled: solo consultas (GET) y creación (POST) para vuelos
async def vuelos_actualizar_estado(id: str, nuevo_estado: str, ctx: Context) -> bool:
    """Actualiza el estado del vuelo via PATCH."""
    url = f"{VUELOS_BASE_URL}/vuelos/{id}/estado"
    data = await _http_request(ctx, "PATCH", url, params={"nuevoEstado": nuevo_estado})
    if isinstance(data, dict) and data.get("status") == "error":
        return False
    return True

# @mcp.tool()  # disabled: solo consultas (GET) y creación (POST) para vuelos
async def vuelos_cancelar(id: str, ctx: Context) -> bool:
    """Cancela un vuelo (POST /{id}/cancelar)."""
    url = f"{VUELOS_BASE_URL}/vuelos/{id}/cancelar"
    data = await _http_post(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return False
    return True

# @mcp.tool()  # disabled: solo consultas (GET) y creación (POST) para vuelos
async def vuelos_reasignar_avion(id: str, nuevo_id_avion: str, ctx: Context) -> bool:
    """Reasigna un avión a un vuelo (POST /{id}/reasignar-avion?nuevo_id_avion=...)."""
    url = f"{VUELOS_BASE_URL}/vuelos/{id}/reasignar-avion"
    data = await _http_request(ctx, "POST", url, params={"nuevo_id_avion": nuevo_id_avion})
    if isinstance(data, dict) and data.get("status") == "error":
        return False
    return True

@mcp.tool()
async def vuelos_verificar_disponibilidad(id: str, asientos: int, ctx: Context) -> bool:
    """Verifica disponibilidad de asientos (GET /{id}/disponibilidad?asientos=...)."""
    url = f"{VUELOS_BASE_URL}/vuelos/{id}/disponibilidad"
    data = await _http_get(ctx, url, params={"asientos": asientos})
    if isinstance(data, dict) and data.get("status") == "error":
        return False
    # El endpoint devuelve un booleano
    return bool(data) if isinstance(data, (bool, int, float, str)) else True

# @mcp.tool()  # disabled: solo consultas (GET) y creación (POST) para vuelos
async def vuelos_reservar_asientos(id: str, asientos: int, ctx: Context) -> bool:
    """Reserva asientos en el vuelo (POST /{id}/reservar-asientos?asientos=...)."""
    url = f"{VUELOS_BASE_URL}/vuelos/{id}/reservar-asientos"
    data = await _http_request(ctx, "POST", url, params={"asientos": asientos})
    if isinstance(data, dict) and data.get("status") == "error":
        # Si la API devolvió 400 por no reservar, interpretamos como False
        return False
    # El endpoint devuelve un booleano
    return bool(data) if isinstance(data, (bool, int, float, str)) else True

@mcp.tool()
async def vuelos_proximos(horas: int , ctx: Context) -> List[Vuelo]:
    """Obtiene próximos vuelos en las siguientes 'horas'."""
    url = f"{VUELOS_BASE_URL}/vuelos/proximos"
    data = await _http_get(ctx, url, params={"horas": horas})
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Vuelo.model_validate(item) for item in (data or [])]

@mcp.tool()
async def vuelos_mas_barato(ctx: Context) -> Optional[Vuelo]:
    """Obtiene el vuelo más económico (o None si no hay contenido)."""
    url = f"{VUELOS_BASE_URL}/vuelos/mas-barato"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return None
    try:
        return Vuelo.model_validate(data)
    except Exception:
        return None

@mcp.tool()
async def vuelos_mas_largos(cantidad: int , ctx: Context) -> List[Vuelo]:
    """Obtiene los vuelos con mayor duración (top N)."""
    url = f"{VUELOS_BASE_URL}/vuelos/mas-largos"
    data = await _http_get(ctx, url, params={"cantidad": cantidad})
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Vuelo.model_validate(item) for item in (data or [])]

@mcp.tool()
async def vuelos_estadisticas_total(ctx: Context) -> int:
    """Devuelve el total de vuelos registrados."""
    url = f"{VUELOS_BASE_URL}/vuelos/estadisticas/total"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    try:
        # El endpoint retorna un número simple
        return int(data) if not isinstance(data, dict) else int(data.get("result", data.get("total", 0)))
    except Exception:
        raise RuntimeError(f"Respuesta inesperada: {data}")

@mcp.tool()
async def vuelos_conteo_por_estado(estado: str, ctx: Context) -> int:
    """Devuelve el conteo de vuelos por estado."""
    url = f"{VUELOS_BASE_URL}/vuelos/estadisticas/estado/{estado}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    try:
        return int(data) if not isinstance(data, dict) else int(data.get("result", data.get("count", 0)))
    except Exception:
        raise RuntimeError(f"Respuesta inesperada: {data}")
# --- Notificaciones ---
@mcp.tool()
async def listar_notificaciones(ctx: Context) -> List[MCPNotificacionResponse]:
    """
    Listar notificaciones.
    Sinónimos: listar notificaciones, mostrar notificaciones, ver notificaciones, obtener notificaciones.
    """
    url = f"{NOTIFICACIONES_BASE_URL}/notificaciones/all"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [MCPNotificacionResponse.model_validate(item) for item in (data or [])]

@mcp.tool()
async def notificaciones_get_by_id(id: int, ctx: Context) -> Optional[Notificacion]:
    """Obtiene una notificación por ID."""
    url = f"{NOTIFICACIONES_BASE_URL}/notificaciones/{id}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        return None
    try:
        return Notificacion.model_validate(data)
    except Exception:
        return None

@mcp.tool()
async def notificaciones_buscar_por_estado(estado: str, ctx: Context) -> List[Notificacion]:
    """Busca notificaciones por estado (PENDIENTE, ENVIADA, FALLIDA)."""
    url = f"{NOTIFICACIONES_BASE_URL}/notificaciones/estado/{estado}"
    data = await _http_get(ctx, url)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return [Notificacion.model_validate(item) for item in (data or [])]

@mcp.tool()
async def notificaciones_crear(notificacion: MCPNotificacionCreate, ctx: Context) -> MCPNotificacionResponse:
    """Crea una notificación y devuelve el registro creado."""
    url = f"{NOTIFICACIONES_BASE_URL}/notificaciones/save"
    payload = notificacion.model_dump(mode="json", by_alias=True)
    data = await _http_post(ctx, url, json=payload)
    if isinstance(data, dict) and data.get("status") == "error":
        raise RuntimeError(f"Error HTTP: {data}")
    return MCPNotificacionResponse.model_validate(data)


def run():
    """Arranca el servidor MCP.

    Por defecto usa stdio. Si se pasa el flag '--http' en sys.argv,
    inicia transporte SSE en el puerto configurado.
    """
    import sys
    if "--http" in sys.argv:
        print(f"🚀 Iniciando servidor MCP en modo SSE en puerto {port}")
        mcp.run(transport="sse")
    else:
        print("🚀 Iniciando servidor MCP en modo stdio")
        mcp.run()


# --- 6. Ejecución del Servidor ---
if __name__ == "__main__":
    run()
@mcp.tool()
async def organizar_datos_ui(datos_ui: str) -> Dict[str, Any]:
    import json
    try:
        ui_data = json.loads(datos_ui)
    except json.JSONDecodeError as e:
        return {"error": f"Error parseando JSON: {str(e)}", "received": datos_ui}
    if not isinstance(ui_data, dict):
        return {"error": "datos_ui debe ser un objeto JSON", "received": datos_ui}
    if "actions" not in ui_data:
        ui_data["actions"] = []
    if "visualizations" not in ui_data:
        ui_data["visualizations"] = []
    if not isinstance(ui_data["actions"], list):
        ui_data["actions"] = []
    if not isinstance(ui_data["visualizations"], list):
        ui_data["visualizations"] = []
    return {"success": True, "ui_data": ui_data, "metadata": {"actions_count": len(ui_data["actions"]), "visualizations_count": len(ui_data["visualizations"]), "total_items": len(ui_data["actions"]) + len(ui_data["visualizations"])}}
