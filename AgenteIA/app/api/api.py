"""
# api.py
API HTTP mínima para invocar al cliente MCP mediante POST /query.

Recibe {"consulta": "..."} y devuelve el resultado directo dentro de la clave 'data'.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncio
import logging
import time
import uuid
from AgenteIA.app.utils.logging_config import configure_logging
from AgenteIA.app.core.errors import error_response
try:
    import structlog  # type: ignore
except ImportError:
    class _StructlogShim:
        def get_logger(self, name):
            return logging.getLogger(name)
        class contextvars:
            @staticmethod
            def bind_contextvars(**kwargs):
                pass
            @staticmethod
            def clear_contextvars():
                pass
    structlog = _StructlogShim()  # type: ignore

# Configurar logging a nivel DEBUG para ver los mensajes detallados de timing
configure_logging()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = structlog.get_logger(__name__)
logger.info("Logging configurado a nivel DEBUG")

# Import diferido para evitar errores en startup que afecten /health
client_main = None

app = FastAPI()

# Precalentamiento del agente en segundo plano para evitar latencias en la primera petición
# @app.on_event("startup")  # DESACTIVADO temporalmente para debugging
async def _startup_prewarm():
    try:
        # Import diferido para no bloquear el arranque si hay problemas de dependencias
        from ..client.client_mcp import prewarm_agent as _prewarm_agent
    except Exception as e:
        logging.getLogger(__name__).warning(f"Prewarm no disponible por error de import: {e}")
        return

    async def _run_prewarm():
        try:
            summary = await _prewarm_agent()
            logging.getLogger(__name__).info(f"Prewarm ejecutado: {summary}")
        except Exception as e:
            logging.getLogger(__name__).warning(f"Fallo al ejecutar prewarm: {e}")

    # Ejecutar sin bloquear el arranque del servidor
    logging.getLogger(__name__).info("[DEBUG] Creando tarea de prewarm en background...")
    asyncio.create_task(_run_prewarm())
    logging.getLogger(__name__).info("[DEBUG] Tarea de prewarm creada exitosamente")

@app.get("/health")
def health_check():
    """Endpoint de salud para verificar que el servicio esté funcionando."""
    return {"status": "ok", "service": "AgenteIA"}

@app.post("/query")
async def leer_consulta(request: Request):
    """Endpoint principal: envía la consulta al cliente MCP y retorna su resultado sin modificaciones."""
    global client_main
    if client_main is None:
        from ..client.client_mcp import main as _client_main
        client_main = _client_main

    try:
        datos = await request.json()
    except Exception:
        datos = None

    if not isinstance(datos, dict) or "consulta" not in datos:
        return error_response("AGT-400-01")

    consulta = datos.get("consulta")
    try:
        resultado = await client_main(consulta)
    except Exception as e:
        return error_response("AGT-500-02", override_message=str(e))

    return {"data": resultado}

@app.get("/debug/tools-status")
async def debug_tools_status():
    """Endpoint de depuración: estado de herramientas registradas en AgentCore y SemanticRegistry."""
    global client_main
    # Import diferido para evitar errores en startup
    try:
        from ..client.client_mcp import get_tools_status as _get_tools_status
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "ImportError", "detail": str(e)})

    try:
        status = await _get_tools_status()
        return {"data": status}
    except Exception as e:
        return JSONResponse(status_code=502, content={"error": "Fallo al obtener estado de herramientas", "detail": str(e)})

@app.get("/debug/tool-schema/{name}")
async def debug_tool_schema(name: str):
    try:
        from ..client.client_mcp import _ensure_agent as _ensure
        agent = await _ensure()
        schema = agent.tool_manager.get_tool_schema(name) if agent and agent.tool_manager else None
        return {"name": name, "schema": schema}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "ToolSchemaError", "detail": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()
    try:
        structlog.contextvars.bind_contextvars(request_id=request_id, method=request.method, path=request.url.path)
    except Exception:
        pass
    logger.info("request_started", client_host=(request.client.host if request.client else None))
    try:
        response = await call_next(request)
        duration = time.time() - start
        logger.info("request_completed", status_code=response.status_code, duration_ms=round(duration * 1000, 2))
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        duration = time.time() - start
        logger.error("request_failed", error=str(e), duration_ms=round(duration * 1000, 2))
        raise
    finally:
        try:
            structlog.contextvars.clear_contextvars()
        except Exception:
            pass
