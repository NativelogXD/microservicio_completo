"""
# client_mcp.py
Fachada del AgentCore y cliente HTTP MCP unificado.

Este módulo proporciona:
- Importa y utiliza la única implementación de MCPClient desde app.client.mcp_http_client
- Función main(prompt) que usa AgentCore para procesar la consulta end-to-end
- Función get_tools_status() para el endpoint de debug del API

El objetivo es evitar duplicación de lógica/heurísticas y centralizar el flujo
en AgentCore + SemanticRegistry + ToolManager.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Any, Dict, List, Optional

from ..config import get_config
from ..agent.core.agent_core import AgentCore
from .mcp_http_client import MCPClient


logger = logging.getLogger(__name__)


# Nota: MCPClient se importa de app.client.mcp_http_client para evitar duplicación


# Instancia única del agente para reutilizar entre llamadas HTTP
_agent: Optional[AgentCore] = None
_tools_initialized: bool = False


async def _ensure_agent() -> AgentCore:
    global _agent, _tools_initialized
    import time
    start_time = time.time()
    logger.info(f"[DEBUG] _ensure_agent() iniciado - timestamp: {start_time}")
    
    if _agent is None:
        logger.info("[DEBUG] Creando nueva instancia de AgentCore...")
        cfg = get_config()
        logger.info(f"[DEBUG] Configuración cargada - API Key: {cfg.llm.gemini_api_key[:10]}...")
        
        create_start = time.time()
        _agent = AgentCore(
            gemini_api_key=cfg.llm.gemini_api_key,
            enable_reasoning=True,
            enable_tools=True
        )
        create_time = time.time() - create_start
        logger.info(f"[DEBUG] AgentCore creado en {create_time:.2f}s, inicializando herramientas...")
        
        try:
            tools_start = time.time()
            await _agent.initialize_tools()
            tools_time = time.time() - tools_start
            logger.info(f"[DEBUG] Herramientas inicializadas exitosamente en {tools_time:.2f}s")
            _tools_initialized = True
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[DEBUG] Error al inicializar herramientas (después de {elapsed:.2f}s): {str(e)}")
            raise
            
        total_time = time.time() - start_time
        logger.info(f"AgentCore inicializado y herramientas cargadas (total: {total_time:.2f}s)")
    elif not _tools_initialized:
        logger.info("[DEBUG] Re-inicializando herramientas...")
        reinit_start = time.time()
        await _agent.initialize_tools()
        reinit_time = time.time() - reinit_start
        logger.info(f"[DEBUG] Herramientas re-inicializadas en {reinit_time:.2f}s")
        _tools_initialized = True
    
    total_time = time.time() - start_time
    logger.info(f"[DEBUG] _ensure_agent() completado en {total_time:.2f}s")
    return _agent


async def prewarm_agent() -> Dict[str, Any]:
    """Inicializa el agente y precalienta el índice semántico para evitar latencias en la primera petición.

    Retorna un pequeño resumen del proceso de precalentamiento.
    """
    summary: Dict[str, Any] = {"status": "ok", "indexed_tools": 0}
    try:
        agent = await _ensure_agent()
        # Construir índice semántico si está disponible
        if agent.semantic_registry and agent.semantic_selector:
            try:
                count = agent.semantic_selector.build_index(agent.semantic_registry)
                summary["indexed_tools"] = count
                logger.info(f"Prewarm completado: índice semántico con {count} herramientas")
            except Exception as e:
                logger.warning(f"Error durante prewarm de índice semántico: {e}")
                summary["status"] = "partial"
                summary["detail"] = str(e)
        else:
            logger.info("Prewarm: registro o selector semántico no disponibles")
    except Exception as e:
        logger.error(f"Fallo en prewarm_agent: {e}")
        summary = {"status": "error", "detail": str(e)}
    return summary


async def main(prompt: str) -> Dict[str, Any]:
    """
    Procesa una consulta usando AgentCore y retorna una respuesta estructurada.
    """
    import time
    start_time = time.time()
    logger.info(f"[DEBUG] main() iniciado - timestamp: {start_time}, prompt: {prompt[:50]}...")
    
    try:
        logger.info("[DEBUG] Obteniendo agente...")
        agent_start = time.time()
        agent = await _ensure_agent()
        agent_time = time.time() - agent_start
        logger.info(f"[DEBUG] Agente obtenido en {agent_time:.2f}s, procesando mensaje...")
        
        process_start = time.time()
        response = await agent.process_message(prompt, context={})
        process_time = time.time() - process_start
        logger.info(f"[DEBUG] Mensaje procesado exitosamente en {process_time:.2f}s")

        # Construir respuesta para API
        result: Dict[str, Any] = {
            "status": "ok",
            "response": response.message,
            "tool_used": response.tool_used,
            "reasoning": response.reasoning,
            "confidence": response.confidence,
            "session_id": response.session_id,
        }

        # Adjuntar resultado de ejecución si existe
        if response.metadata and isinstance(response.metadata.get("execution_result"), dict):
            result["execution"] = response.metadata["execution_result"]

        total_time = time.time() - start_time
        logger.info(f"[DEBUG] main() completado exitosamente en {total_time:.2f}s")
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[DEBUG] Error en main() (después de {elapsed:.2f}s): {str(e)}")
        raise


async def get_tools_status() -> Dict[str, Any]:
    """Retorna estado actual de herramientas para debug (/debug/tools-status)."""
    try:
        agent = await _ensure_agent()
        tool_manager_tools = agent.tool_manager.get_available_tools() if agent.tool_manager else []
        semantic_tools = agent.semantic_registry.list_all_tools() if agent.semantic_registry else []

        discrepancies = {
            "in_tool_manager_not_in_semantic": [t for t in tool_manager_tools if t not in semantic_tools],
            "in_semantic_not_in_tool_manager": [t for t in semantic_tools if t not in tool_manager_tools],
        }

        return {
            "status": "ok",
            "tool_manager": {
                "count": len(tool_manager_tools),
                "tools": tool_manager_tools,
            },
            "semantic_registry": {
                "count": len(semantic_tools),
                "tools": semantic_tools,
            },
            "discrepancies": discrepancies,
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado de herramientas: {e}")
        return {"status": "error", "detail": str(e)}


if __name__ == "__main__":
    # Soporta prompt por argumentos o por stdin
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:]).strip()
    else:
        prompt = sys.stdin.read().strip()
    resultado = asyncio.run(main(prompt))
    print(json.dumps(resultado, ensure_ascii=False))
