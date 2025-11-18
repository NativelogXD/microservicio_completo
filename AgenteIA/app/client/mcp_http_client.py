"""
Cliente MCP asíncrono que habla con el servidor FastMCP vía SSE.

Motivación: el servidor actual se inicia con mcp.run(transport="sse"),
por lo que no expone rutas REST /tools ni /run_tool. Este cliente usa
la librería oficial mcp para abrir una sesión SSE y:
- listar herramientas disponibles
- invocar una herramienta por nombre con argumentos

Se mantiene aislado de AgentCore para evitar dependencias circulares.
"""

import os
import logging
import asyncio
from typing import Any, Dict, List, Optional

from mcp.client.sse import sse_client
from mcp import ClientSession

from ..config import get_config

logger = logging.getLogger(__name__)


class MCPClient:
    """
    Cliente para interactuar con el servidor MCP vía SSE.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        config = get_config()
        # base_url sin sufijo; el endpoint SSE suele ser base + '/sse'
        self.base_url = (base_url or config.server.mcp_server_url.rstrip("/"))
        # Reducir timeout para evitar bloqueos prolongados
        self.timeout = timeout or float(os.getenv("MCP_CLIENT_TIMEOUT", "30"))
        self.sse_url = f"{self.base_url}/sse"
        logger.info(f"MCPClient configurado (SSE). Base URL: {self.base_url}, sse: {self.sse_url}, timeout: {self.timeout}s")

    async def test_connection(self) -> bool:
        """Intenta abrir una sesión SSE e inicializar el protocolo MCP."""
        try:
            async with sse_client(self.sse_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return True
        except Exception as e:
            logger.error(f"Error probando conexión MCP (SSE): {e}")
            return False

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Lista herramientas disponibles del servidor MCP.

        Devuelve una lista de dicts con al menos la clave 'name'. Si el servidor
        ofrece más metadatos (descripción, parámetros), se incluyen cuando están disponibles.
        """
        import time
        start_time = time.time()
        logger.info(f"[DEBUG] get_available_tools() iniciado - timestamp: {start_time}, URL: {self.sse_url}, timeout: {self.timeout}s")
        
        # Implementar reintentos con backoff exponencial
        max_retries = 3
        base_delay = 2  # segundos
        
        for attempt in range(max_retries):
            try:
                attempt_start = time.time()
                logger.info(f"[DEBUG] Intento {attempt + 1}/{max_retries} de conexión SSE...")
                
                # Aplicar timeout total a la operación completa
                async def _get_tools_with_timeout():
                    sse_start = time.time()
                    async with sse_client(self.sse_url) as (read, write):
                        sse_time = time.time() - sse_start
                        logger.info(f"[DEBUG] Conexión SSE establecida en {sse_time:.2f}s, creando sesión...")
                        
                        session_start = time.time()
                        async with ClientSession(read, write) as session:
                            session_create_time = time.time() - session_start
                            logger.info(f"[DEBUG] Sesión creada en {session_create_time:.2f}s, inicializando...")
                            
                            init_start = time.time()
                            await session.initialize()
                            init_time = time.time() - init_start
                            logger.info(f"[DEBUG] Sesión MCP inicializada en {init_time:.2f}s")
                            
                            tools: List[Dict[str, Any]] = []
                            # Intentar API estándar
                            list_start = time.time()
                            logger.info("[DEBUG] Listando herramientas...")
                            listed = await session.list_tools()  # type: ignore[attr-defined]
                            list_time = time.time() - list_start
                            logger.info(f"[DEBUG] Herramientas listadas en {list_time:.2f}s: {listed}")
                            
                            # En el SDK oficial, list_tools devuelve un objeto con atributo `.tools`
                            items = getattr(listed, "tools", None)
                            if items is None:
                                # Compatibilidad: si no existe `.tools`, asumir que es ya una lista
                                items = listed
                            # Normalizar a lista
                            if not isinstance(items, list):
                                items = list(items) if hasattr(items, "__iter__") else []
                            
                            logger.info(f"[DEBUG] Procesando {len(items) if items else 0} herramientas")
                            for t in items:
                                # Compatibilidad: algunos clientes exponen atributos .name/.description/.inputSchema
                                if isinstance(t, dict):
                                    name = t.get("name")
                                    description = t.get("description", "")
                                    params = t.get("inputSchema") or t.get("parameters")
                                else:
                                    name = getattr(t, "name", None)
                                    description = getattr(t, "description", "")
                                    params = getattr(t, "inputSchema", None)
                                # Intentar normalizar a dict cuando no lo es
                                if params is not None and not isinstance(params, dict):
                                    try:
                                        if hasattr(params, "to_dict"):
                                            params = params.to_dict()
                                        elif hasattr(params, "model_dump"):
                                            params = params.model_dump()  # type: ignore
                                        elif hasattr(params, "jsonSchema"):
                                            js = getattr(params, "jsonSchema")
                                            params = js if isinstance(js, dict) else None
                                        elif hasattr(params, "schema"):
                                            sc = getattr(params, "schema")
                                            params = sc if isinstance(sc, dict) else None
                                        else:
                                            params = None
                                    except Exception:
                                        params = None
                                if name:
                                    tools.append({
                                        "name": name,
                                        "description": description or "",
                                        "parameters": params if isinstance(params, dict) else None
                                    })
                            # Fallback adicional: algunos clientes guardan herramientas en `session.tools`
                            if not tools:
                                possible = getattr(session, "tools", None)
                                if isinstance(possible, list):
                                    for t in possible:
                                        name = getattr(t, "name", None) or (t.get("name") if isinstance(t, dict) else None)
                                        description = getattr(t, "description", "") if isinstance(t, dict) else getattr(t, "description", "")
                                        params = getattr(t, "inputSchema", None) if not isinstance(t, dict) else t.get("inputSchema")
                                        if name:
                                            tools.append({
                                                "name": name,
                                                "description": description or "",
                                                "parameters": params if isinstance(params, dict) else None
                                            })
                            
                            total_time = time.time() - start_time
                            attempt_time = time.time() - attempt_start
                            logger.info(f"[DEBUG] get_available_tools() completado en {attempt_time:.2f}s (total: {total_time:.2f}s) - {len(tools)} herramientas encontradas")
                            return tools
                
                # Aplicar timeout con asyncio.wait_for
                try:
                    tools_result = await asyncio.wait_for(_get_tools_with_timeout(), timeout=self.timeout)
                    return tools_result
                except asyncio.TimeoutError:
                    total_time = time.time() - start_time
                    logger.error(f"[TIMEOUT] Operación excedió el timeout de {self.timeout}s después de {total_time:.2f}s")
                    raise TimeoutError(f"La operación excedió el timeout de {self.timeout} segundos")
                        
            except Exception as e:
                attempt_time = time.time() - attempt_start
                total_time = time.time() - start_time
                logger.error(f"Error en intento {attempt + 1} listando herramientas MCP (SSE) - tiempo: {attempt_time:.2f}s (total: {total_time:.2f}s): {e}")
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Backoff exponencial
                    logger.info(f"[DEBUG] Reintentando en {delay} segundos (total elapsed: {total_time:.2f}s)...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"[DEBUG] Todos los intentos fallaron. Error final después de {total_time:.2f}s: {str(e)}", exc_info=True)
                    return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invoca una herramienta por nombre usando el protocolo MCP vía SSE."""
        try:
            async with sse_client(self.sse_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    res = await session.call_tool(tool_name, arguments=arguments)
                    # Normalizar respuesta en dict
                    if hasattr(res, "structuredContent") and res.structuredContent:
                        return {"status": "ok", "result": res.structuredContent}
                    # Fallback: convertir 'content' (lista de partes MCP) a JSON seguro
                    content = getattr(res, "content", None)
                    def _to_json_safe(item):
                        try:
                            # Casos comunes del SDK MCP
                            t = getattr(item, "type", None)
                            if t == "text":
                                return {"type": "text", "text": getattr(item, "text", "")}
                            if t == "json":
                                return {"type": "json", "json": getattr(item, "json", None)}
                            # Si ya es dict
                            if isinstance(item, dict):
                                return item
                            # Fallback genérico
                            return str(item)
                        except Exception:
                            return str(item)

                    if isinstance(content, list):
                        safe_parts = [_to_json_safe(p) for p in content]
                        # Si hay exactamente un elemento JSON, devolverlo plano
                        json_items = [p.get("json") for p in safe_parts if isinstance(p, dict) and p.get("type") == "json"]
                        if len(json_items) == 1:
                            return {"status": "ok", "result": json_items[0]}
                        return {"status": "ok", "result": safe_parts}
                    # Si content no es lista, devolverlo como string seguro
                    return {"status": "ok", "result": str(content) if content is not None else None}
        except Exception as e:
            logger.error(f"Error llamando herramienta MCP '{tool_name}' (SSE): {e}")
            return {"status": "error", "error": str(e)}
