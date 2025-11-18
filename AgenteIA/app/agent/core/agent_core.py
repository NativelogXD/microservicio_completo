"""
AgentCore - Orquestador Principal del Sistema MCP

NÃºcleo central que coordina todos los componentes del agente:
1. Recibe mensajes del usuario
2. Orquesta el flujo de razonamiento
3. Gestiona la memoria conversacional
4. Ejecuta herramientas cuando es necesario
5. Genera respuestas coherentes y contextuales
"""

import logging
try:
    import structlog  # type: ignore
except ImportError:
    class _StructlogShim:
        def get_logger(self, name):
            return logging.getLogger(name)
    structlog = _StructlogShim()  # type: ignore
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import os
import uuid
import re
# Eliminado: carga de YAML/sinónimos para evitar heurísticas por strings

from ..core.reasoning_engine import ReasoningEngine, ReasoningResult, ActionType
from .memory_context import MemoryContext, ConversationMessage, MessageRole
from ..core.tool_manager import ToolManager, ExecutionResult, ExecutionStatus
from AgenteIA.app.core.tool_parallelizer import ToolParallelizer
from ..registry.semantic_registry import SemanticRegistry
from ..core.semantic_selector import SemanticSelector
from ..core.schema_extractor import SchemaExtractor
from AgenteIA.app.config.config import get_config, LLMConfig
from AgenteIA.app.client.mcp_http_client import MCPClient
from AgenteIA.app.models.mcp_models import MCPModelMapper


class AgentStatus(Enum):
    """Estados del agente."""
    IDLE = "idle"
    PROCESSING = "processing"
    EXECUTING_TOOL = "executing_tool"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class AgentResponse:
    """
    Respuesta completa del agente.
    
    Attributes:
        message: Mensaje de respuesta para el usuario
        action_taken: Tipo de acciÃ³n realizada
        tool_used: Herramienta utilizada (si aplica)
        reasoning: Proceso de razonamiento
        confidence: Nivel de confianza (0.0-1.0)
        execution_time: Tiempo total de procesamiento
        session_id: ID de la sesiÃ³n
        metadata: InformaciÃ³n adicional
    """
    message: str
    action_taken: str
    tool_used: Optional[str] = None
    reasoning: str = ""
    confidence: float = 0.0
    execution_time: float = 0.0
    session_id: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la respuesta a diccionario."""
        return asdict(self)


class AgentCore:
    """
    NÃºcleo central del agente MCP.
    
    Orquesta todos los componentes para proporcionar una interfaz
    unificada de procesamiento de mensajes con capacidades de
    razonamiento, memoria y ejecuciÃ³n de herramientas.
    """
    
    def __init__(
        self,
        gemini_api_key: str,
        session_id: Optional[str] = None,
        max_memory_messages: int = 20,
        enable_reasoning: bool = True,
        enable_tools: bool = True
    ):
        """
        Inicializa el nÃºcleo del agente.
        
        Args:
            gemini_api_key: Clave API de Gemini
            session_id: ID de sesiÃ³n (se genera si no se proporciona)
            max_memory_messages: MÃ¡ximo de mensajes en memoria
            enable_reasoning: Habilitar motor de razonamiento
            enable_tools: Habilitar ejecuciÃ³n de herramientas
        """
        # Inicializar logger primero
        self.logger = structlog.get_logger(__name__)
        
        self.session_id = session_id or str(uuid.uuid4())
        self.enable_reasoning = enable_reasoning
        self.enable_tools = enable_tools
        
        # Eliminado: carga de sinónimos desde fichero. El sistema debe operar con similitud semántica pura.

        # Estado del agente
        self.status = AgentStatus.IDLE
        self.last_activity = datetime.now()
        
        # Inicializar componentes
        llm_config = LLMConfig()
        
        # Inicializar ReasoningEngine
        if enable_reasoning:
            self.logger.info("Inicializando ReasoningEngine...")
            from .reasoning_engine import ReasoningEngine
            self.reasoning_engine = ReasoningEngine(
                model_name=llm_config.gemini_model,
                api_key=gemini_api_key
            )
            self.logger.info("ReasoningEngine inicializado correctamente")
        else:
            self.reasoning_engine = None
        
        self.memory_context = MemoryContext(max_messages=max_memory_messages)
        
        # Inicializar componentes de herramientas con logging detallado
        if enable_tools:
            self.logger.info("Inicializando ToolManager...")
            self.tool_manager = ToolManager()
            self.logger.info("ToolManager inicializado correctamente")
            
            self.logger.info("Inicializando SemanticRegistry...")
            self.semantic_registry = SemanticRegistry()
            self.logger.info("SemanticRegistry inicializado correctamente")
            
            self.logger.info("Inicializando SemanticSelector...")
            self.semantic_selector = SemanticSelector()
            self.logger.info("SemanticSelector inicializado correctamente")
        else:
            self.tool_manager = None
            self.semantic_registry = None
            self.semantic_selector = None
        
        # Inicializar cliente MCP y cargar herramientas
        self.logger.info(f"Inicializando MCPClient - enable_tools: {enable_tools}")
        try:
            self.mcp_client = MCPClient() if enable_tools else None
            self.logger.info(f"MCPClient inicializado correctamente: {self.mcp_client is not None}")
        except Exception as e:
            self.logger.error(f"Error inicializando MCPClient: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.mcp_client = None
            
        self.available_tools = {}
        self.schema_extractor = SchemaExtractor()
        
        # EstadÃ­sticas de sesiÃ³n
        self.session_stats = {
            "messages_processed": 0,
            "tools_executed": 0,
            "reasoning_calls": 0,
            "errors": 0,
            "total_response_time": 0.0,
            "avg_response_time": 0.0,
            "session_start": datetime.now()
        }
        
        self.logger.info("agent_core_initialized", session_id=self.session_id)

        self.info_gathering_tools = set()
        self.dependency_map = {}
        self.tool_parallelizer = ToolParallelizer()
        self._tools_loaded = False
    
    # Método _load_synonyms eliminado para evitar reglas deterministas por coincidencia textual.

    async def initialize_tools(self) -> None:
        """
        Inicializa las herramientas MCP de forma asÃ­ncrona.
        Debe ser llamado despuÃ©s de crear la instancia del agente.
        """
        import time
        start_time = time.time()
        self.logger.info(f"[DEBUG] initialize_tools() iniciado - timestamp: {start_time}")
        
        if self.enable_tools and self.mcp_client:
            self.logger.info("[DEBUG] Condiciones habilitadas para cargar herramientas MCP")
            self.logger.info("Ejecutando _load_tools_from_mcp()...")
            try:
                tools_start = time.time()
                await self._load_tools_from_mcp()
                tools_time = time.time() - tools_start
                self.logger.info(f"[DEBUG] _load_tools_from_mcp() completado en {tools_time:.2f}s")
            except Exception as e:
                self.logger.error(f"[DEBUG] Error en _load_tools_from_mcp(): {str(e)}")
                raise
        else:
            self.logger.warning(f"No se cargaron herramientas MCP - enable_tools: {self.enable_tools}, mcp_client: {self.mcp_client}")
        
        total_time = time.time() - start_time
        self.logger.info(f"Herramientas disponibles despuÃ©s de inicializaciÃ³n: {len(self.available_tools)} (total: {total_time:.2f}s)")
        self.logger.info(f"[DEBUG] initialize_tools() completado - total time: {total_time:.2f}s")
        try:
            await self._rebuild_planner()
        except Exception:
            pass

    async def process_message(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Procesa un mensaje del usuario de forma completa.
        
        Args:
            user_message: Mensaje del usuario
            context: Contexto adicional
            
        Returns:
            AgentResponse: Respuesta completa del agente
        """
        start_time = datetime.now()
        self.status = AgentStatus.PROCESSING
        
        try:
            self.logger.info(f"[DEBUG] process_message iniciado: {user_message[:100]}...")
            
            # Agregar mensaje del usuario a la memoria
            self.memory_context.add_message(
                role=MessageRole.USER,
                content=user_message
            )
            
            loop_counter = 0
            tool_exec_count = 0
            response = None
            while loop_counter < 10:
                self.logger.info(f"[DEBUG] Iniciando fase de razonamiento...")
                reasoning_result = await self._perform_reasoning(user_message, context)
                self.logger.info(f"agentic_loop_iteration", iteration=loop_counter + 1)
                self.logger.info(f"[DEBUG] Razonamiento completado: {reasoning_result.action}")
                if reasoning_result.action == ActionType.TOOL_CALL:
                    try:
                        deps = self.dependency_map.get(reasoning_result.tool_name) or []
                        self.logger.info("tools_requested", tool_count=1 + len(deps), tools=[reasoning_result.tool_name] + deps)
                    except Exception:
                        pass
                    await self._execute_dependencies(reasoning_result.tool_name, context)
                    response = await self._execute_tool_action(reasoning_result, context)
                    tool_exec_count += 1
                    try:
                        tool_payload = self._format_tool_result_for_memory(response)
                        self.memory_context.add_message(role=MessageRole.USER, content=tool_payload)
                    except Exception:
                        pass
                    loop_counter += 1
                    continue
                response = await self._execute_action(reasoning_result, context)
                break
            
            # Safety check: ensure response is not None
            if response is None:
                self.logger.error("_execute_action returned None, creating fallback response")
                response = AgentResponse(
                    message="Lo siento, ocurriÃ³ un error interno al procesar tu solicitud.",
                    action_taken="error",
                    reasoning="Error interno: respuesta nula del ejecutor de acciones",
                    confidence=0.0,
                    execution_time=0.0,
                    session_id=self.session_id
                )
            
            # Agregar respuesta del agente a la memoria
            self.memory_context.add_message(
                role=MessageRole.ASSISTANT,
                content=response.message,
                metadata={
                    "action": response.action_taken,
                    "tool_used": response.tool_used,
                    "confidence": response.confidence
                }
            )
            
            # Actualizar estadÃ­sticas
            execution_time = (datetime.now() - start_time).total_seconds()
            response.execution_time = execution_time
            response.session_id = self.session_id
            
            self._update_session_stats(execution_time, success=True)
            
            self.status = AgentStatus.IDLE
            self.last_activity = datetime.now()
            try:
                resp_len = len(response.message or "")
            except Exception:
                resp_len = 0
            self.logger.info(
                "query_processed",
                iterations=loop_counter + 1,
                total_tools=tool_exec_count,
                duration_ms=int(execution_time * 1000),
                response_length=resp_len,
            )
            self.logger.info("message_processed", duration_s=execution_time)
            return response

        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error("process_message_error", error=str(e))
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_session_stats(execution_time, success=False)
            
            return AgentResponse(
                message=f"Lo siento, ocurriÃ³ un error procesando tu mensaje: {str(e)}",
                action_taken="error",
                reasoning="Error interno del sistema",
                confidence=0.0,
                execution_time=execution_time,
                session_id=self.session_id,
                metadata={"error": str(e)}
            )

    def _format_tool_result_for_memory(self, response: 'AgentResponse') -> str:
        try:
            payload = {
                "tool": response.tool_used,
                "status": (response.metadata or {}).get("execution_result", {}).get("status"),
                "result": (response.metadata or {}).get("execution_result", {}).get("result"),
                "error": (response.metadata or {}).get("execution_result", {}).get("error")
            }
            return json.dumps({"tool_result": payload}, ensure_ascii=False)
        except Exception:
            return "tool_result"

    async def _perform_reasoning(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]]
    ) -> ReasoningResult:
        self.logger.info(f"_perform_reasoning - enable_reasoning: {self.enable_reasoning}")
        self.logger.info(f"_perform_reasoning - reasoning_engine: {self.reasoning_engine is not None}")
        if not self.enable_reasoning or not self.reasoning_engine:
            return ReasoningResult(
                action=ActionType.CONVERSATION,
                tool_name="",
                arguments={},
                reasoning="Modo sin razonamiento - respuesta conversacional",
                confidence=0.5,
                requires_clarification=False,
                clarification_question=""
            )
        try:
            self.session_stats["reasoning_calls"] += 1
            if not (self.enable_tools and self.tool_manager):
                return ReasoningResult(action=ActionType.CONVERSATION, reasoning="Herramientas no habilitadas", confidence=0.4)
            cfg = get_config()
            if cfg and getattr(cfg, 'reasoning', None) and getattr(cfg.reasoning, 'enable_llm_reasoning', False):
                conversation_context = self.memory_context.get_context_for_llm(include_system=False, max_messages_override=5)
                try:
                    self.logger.info(f"[reasoning.context] Using {len(conversation_context)} messages with importance filtering")
                except Exception:
                    pass
                available_tools: List[Dict[str, Any]] = []
                try:
                    if self.semantic_selector and self.semantic_registry:
                        ranked = self.semantic_selector.rank_tools(user_message, self.semantic_registry, top_k=10)
                        for rt in ranked:
                            tn = rt.get("name", "")
                            if not tn:
                                continue
                            schema = self.tool_manager.get_tool_schema(tn) or {}
                            desc = rt.get("description", "")
                            available_tools.append({"name": tn, "description": desc, "parameters": schema, "preselection_score": rt.get("score", 0.0)})
                    else:
                        tm_names = list(self.tool_manager.tool_schemas.keys()) if hasattr(self.tool_manager, 'tool_schemas') else []
                        for tn in tm_names:
                            schema = self.tool_manager.get_tool_schema(tn) or {}
                            desc = ""
                            if self.semantic_registry:
                                td = self.semantic_registry.get_tool_definition(tn)
                                desc = getattr(td, 'description', '') if td else ''
                            available_tools.append({"name": tn, "description": desc, "parameters": schema})
                    self.logger.info(f"[reasoning.tools] available={len(available_tools)}")
                except Exception:
                    available_tools = []
                try:
                    self.logger.info("[reasoning.mode] Using Function Calling v2")
                    rr = await self.reasoning_engine.analyze_intent_v2(user_message, available_tools, conversation_context)
                except AttributeError:
                    self.logger.info("[reasoning.fallback] Using original analyze_intent")
                    rr = await self.reasoning_engine.analyze_intent(user_message, available_tools, conversation_context)
                except Exception as e:
                    self.logger.error(f"[reasoning.error] Function calling failed: {e}")
                    rr = await self.reasoning_engine.analyze_intent(user_message, available_tools, conversation_context)
                if rr and rr.action != ActionType.CONVERSATION:
                    return rr
            # Fallback semántico limpio: si el LLM no decide, usar el top de selección semántica
            try:
                ranked = self.semantic_selector.rank_tools(user_message, self.semantic_registry, top_k=1) if (self.semantic_selector and self.semantic_registry) else []
                if ranked:
                    top = ranked[0]
                    top_name = getattr(top, "name", top.get("name") if isinstance(top, dict) else "")
                    top_score = getattr(top, "score", top.get("score") if isinstance(top, dict) else 0.0)
                    dt = getattr(get_config().semantic, "direct_threshold", 0.7)
                    if top_name and top_score >= dt and self.tool_manager:
                        schema = self.tool_manager.get_tool_schema(top_name) or {}
                        extracted = {}
                        try:
                            extracted = self.schema_extractor.extract_arguments(schema, user_message, tool_name=top_name) or {}
                        except Exception:
                            extracted = {}
                        # Calcular campos requeridos y cobertura
                        props = schema.get("properties", {}) or {}
                        req = schema.get("required", []) or []
                        required_fields = []
                        provided_fields = []
                        if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
                            root = req[0]
                            inner = props.get(root, {}) or {}
                            inner_required = inner.get("required", []) or []
                            required_fields = inner_required
                            inner_vals = extracted.get(root, {}) if isinstance(extracted, dict) else {}
                            # Considerar tanto claves dentro del objeto raíz como claves planas ya extraídas
                            provided_fields = []
                            for k in inner_required:
                                if k in (inner_vals or {}) or k in (extracted or {}):
                                    provided_fields.append(k)
                        else:
                            required_fields = req
                            provided_fields = [k for k in req if k in (extracted or {})]
                        cov_ratio = (len(provided_fields) / max(len(required_fields), 1)) if required_fields else 1.0
                        min_cov = getattr(get_config().reasoning, "min_coverage_for_execution", 1.0)
                        if extracted and cov_ratio >= min_cov:
                            return ReasoningResult(
                                action=ActionType.TOOL_CALL,
                                tool_name=top_name,
                                arguments=extracted,
                                reasoning=f"Fallback semántico (score={top_score:.3f})",
                                confidence=min(0.8, 0.6 + (top_score - dt)),
                                requires_clarification=False,
                                clarification_question=""
                            )
                        else:
                            # Pedir aclaración con campos faltantes
                            missing = []
                            if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
                                root = req[0]
                                inner = props.get(root, {}) or {}
                                inner_required = inner.get("required", []) or []
                                inner_vals = extracted.get(root, {}) if isinstance(extracted, dict) else {}
                                missing = [f for f in inner_required if f not in (inner_vals or {})]
                            else:
                                missing = [f for f in req if f not in (extracted or {})]
                            msg = self._build_clarification_message(top_name, missing)
                            return ReasoningResult(
                                action=ActionType.CLARIFY,
                                tool_name=top_name,
                                arguments=extracted,
                                reasoning=f"Fallback de aclaración (score={top_score:.3f})",
                                confidence=0.5,
                                requires_clarification=True,
                                clarification_question=msg
                            )
            except Exception:
                pass
            return ReasoningResult(
                action=ActionType.CONVERSATION,
                reasoning="Sin decisión del LLM; respuesta conversacional",
                confidence=0.6
            )
        except Exception as e:
            self.logger.error(f"Error en razonamiento: {str(e)}")
            return ReasoningResult(
                action=ActionType.CONVERSATION,
                tool_name="",
                arguments={},
                reasoning=f"Error en razonamiento, fallback a conversación: {str(e)}",
                confidence=0.1,
                requires_clarification=False,
                clarification_question=""
            )

    async def _execute_action(
        self,
        reasoning_result: ReasoningResult,
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """
        Ejecuta la acciÃ³n determinada por el razonamiento.
        
        Args:
            reasoning_result: Resultado del razonamiento
            context: Contexto adicional
            
        Returns:
            AgentResponse: Respuesta del agente
        """
        self.logger.info(f"_execute_action - ActionType: {reasoning_result.action}")
        self.logger.info(f"_execute_action - raw_response: {reasoning_result.raw_response}")
        self.logger.info(f"_execute_action - confidence: {reasoning_result.confidence}")
        
        if reasoning_result.action == ActionType.CLARIFY:
            self.logger.info("Ejecutando acciÃ³n CLARIFY")
            msg = reasoning_result.clarification_question or ""
            try:
                tool_name_for_schema = None
                if self.tool_manager and reasoning_result.tool_name and reasoning_result.tool_name in self.tool_manager.tool_schemas:
                    tool_name_for_schema = reasoning_result.tool_name
                elif self.tool_manager and self.semantic_selector and self.semantic_registry:
                    recent = self.memory_context.get_recent_messages(1)
                    q = recent[0].content if recent else ""
                    ranked = self.semantic_selector.rank_tools(q, self.semantic_registry, top_k=3)
                    if ranked:
                        chosen = None
                        for rt in ranked:
                            name = rt.name
                            schema_candidate = self.tool_manager.tool_schemas.get(name)
                            if not schema_candidate:
                                continue
                            req_cand = schema_candidate.get("required", [])
                            props_cand = schema_candidate.get("properties", {})
                            has_object_required = False
                            for rr in req_cand:
                                pc = props_cand.get(rr, {})
                                if pc.get("type") == "object" and (pc.get("required") or []):
                                    has_object_required = True
                                    break
                            if has_object_required:
                                chosen = name
                                break
                        if not chosen:
                            for rt in ranked:
                                name = rt.name
                                schema_candidate = self.tool_manager.tool_schemas.get(name)
                                if schema_candidate and (schema_candidate.get("required") or []):
                                    chosen = name
                                    break
                        tool_name_for_schema = chosen or ranked[0].name
                if tool_name_for_schema and tool_name_for_schema in self.tool_manager.tool_schemas:
                    schema = self.tool_manager.tool_schemas[tool_name_for_schema]
                    req = schema.get("required", [])
                    props = schema.get("properties", {})
                    fields_set = set()
                    if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
                        inner_req = (props.get(req[0], {}) or {}).get("required", []) or []
                        for k in inner_req:
                            fields_set.add(k)
                    else:
                        for r in req:
                            fields_set.add(r)
                    model_cls = MCPModelMapper.get_create_model(tool_name_for_schema) or MCPModelMapper.resolve_model_by_schema(schema)
                    if model_cls:
                        try:
                            schema_json = model_cls.model_json_schema()
                            inner = schema_json.get("required", []) or []
                            for k in inner:
                                fields_set.add(k)
                        except Exception:
                            pass
                    fields = sorted(fields_set)
                    if fields:
                        detalle = ", ".join(fields)
                        human = f"Para continuar, necesito: {detalle}."
                        msg = f"{msg} {human}".strip()
            except Exception:
                pass
            return AgentResponse(
                message=msg.strip(),
                action_taken="clarification",
                reasoning=reasoning_result.reasoning,
                confidence=reasoning_result.confidence
            )
        
        elif reasoning_result.action == ActionType.TOOL_CALL:
            self.logger.info("Ejecutando acciÃ³n TOOL_CALL")
            try:
                arg_struct = reasoning_result.arguments or {}
                self.logger.info(f"[decision.execute] tool={reasoning_result.tool_name} arguments_structure_size={len(arg_struct) if isinstance(arg_struct, dict) else 0}")
            except Exception:
                pass
            # Auto-normalización de argumentos: si el esquema requiere un objeto raíz
            try:
                if self.tool_manager and reasoning_result.tool_name:
                    schema = self.tool_manager.get_tool_schema(reasoning_result.tool_name) or {}
                    req = schema.get("required", []) or []
                    props = schema.get("properties", {}) or {}
                    if len(req) == 1:
                        root = req[0]
                        root_prop = props.get(root, {})
                        if isinstance(root_prop, dict) and root_prop.get("type") == "object":
                            inner_props = (root_prop.get("properties") or {})
                            inner_required = (root_prop.get("required") or [])
                            args = reasoning_result.arguments or {}
                            # Si no trae el objeto raíz pero sí claves internas, envolver
                            if root not in args:
                                collected = {}
                                for k in inner_required:
                                    if k in args:
                                        collected[k] = args.get(k)
                                # También incluir cualquier clave que pertenezca al objeto interno
                                for k in inner_props.keys():
                                    if k in args and k not in collected:
                                        collected[k] = args.get(k)
                                if collected:
                                    # Mover claves planas dentro del objeto raíz
                                    for k in list(collected.keys()):
                                        args.pop(k, None)
                                    args[root] = collected
                                    reasoning_result.arguments = args
            except Exception:
                pass
            # Sin heurísticas de reencaminamiento: ejecutar la herramienta seleccionada por el LLM
            await self._execute_dependencies(reasoning_result.tool_name, context)
            return await self._execute_tool_action(reasoning_result, context)
        
        else:  # CONVERSATION
            self.logger.info("Ejecutando acciÃ³n CONVERSATION")
            return await self._generate_conversational_response(reasoning_result, context)

    def _get_missing_fields(self, structure: Dict[str, Any], schema: Dict[str, Any], extracted_args: Dict[str, Any]) -> List[str]:
        try:
            if structure.get("structure") == "object_root":
                root_key = structure.get("root_key")
                props = (schema or {}).get("properties", {}) or {}
                inner_schema = (props.get(root_key, {}) or {})
                inner_required = inner_schema.get("required", []) or []
                if not inner_required:
                    try:
                        from ..models.mcp_models import MCPModelMapper
                        model_cls = MCPModelMapper.resolve_model_by_schema(schema)
                        if model_cls:
                            js = model_cls.model_json_schema() or {}
                            inner_required = js.get("required", []) or []
                    except Exception:
                        pass
                inner_dict = extracted_args.get(root_key, {}) if isinstance(extracted_args, dict) else {}
                return [f for f in inner_required if f not in inner_dict]
            required = (schema or {}).get("required", []) or []
            return [f for f in required if f not in (extracted_args or {})]
        except Exception:
            return []

    def _build_clarification_message(self, tool_name: str, missing_fields: List[str]) -> str:
        if not missing_fields:
            return "Faltan parámetros requeridos para completar la operación."
        if len(missing_fields) > 5:
            fields_str = ", ".join(missing_fields[:5]) + f" y {len(missing_fields)-5} más"
        else:
            fields_str = ", ".join(missing_fields)
        return f"Para {tool_name}, necesito: {fields_str}. Por favor proporciona esta información."

    def _extract_value_by_type(self, text: str, key: str, expected_type: Optional[str]) -> Optional[Any]:
        """Extrae valor por tipo esperado del texto natural - versión completamente sin hardcodeos."""
        if not text or not key:
            return None
        
        # Importar el nuevo extractor
        from .value_extractor import ValueExtractor
        
        # Crear extractor con el nuevo enfoque
        extractor = ValueExtractor()
        
        # Crear un esquema mínimo solo con el tipo
        field_schema = {"type": expected_type or "string"}
        
        # Extraer valor usando el nuevo sistema sin hardcodeos
        return extractor.extract_value(text, key, field_schema)


    async def _execute_tool_action(
        self,
        reasoning_result: ReasoningResult,
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """
        Ejecuta una herramienta.
        
        Args:
            reasoning_result: Resultado del razonamiento
            context: Contexto adicional
            
        Returns:
            AgentResponse: Respuesta con resultado de la herramienta
        """
        if not self.enable_tools or not self.tool_manager:
            return AgentResponse(
                message="Las herramientas estÃ¡n deshabilitadas en este agente.",
                action_taken="tool_disabled",
                reasoning="Herramientas no disponibles",
                confidence=0.0
            )
        
        self.status = AgentStatus.EXECUTING_TOOL
        
        try:
            try:
                self.logger.info(f"[execution.start] tool={reasoning_result.tool_name} arguments_count={len(reasoning_result.arguments or {})}")
            except Exception:
                pass
            execution_result = await self.tool_manager.execute_tool(
                tool_name=reasoning_result.tool_name,
                arguments=reasoning_result.arguments,
                context=context
            )
            
            self.session_stats["tools_executed"] += 1
            
            if execution_result.status == ExecutionStatus.SUCCESS:
                res = execution_result.result
                if isinstance(res, dict) and res.get("status") == "error":
                    message = self._format_tool_error_response(
                        reasoning_result,
                        ExecutionResult(
                            status=ExecutionStatus.ERROR,
                            error=res,
                            tool_name=reasoning_result.tool_name,
                            arguments=reasoning_result.arguments,
                        ),
                    )
                    confidence = max(reasoning_result.confidence - 0.2, 0.0)
                else:
                    message = self._format_tool_success_response(
                        reasoning_result, execution_result
                    )
                    confidence = min(reasoning_result.confidence + 0.1, 1.0)
                    try:
                        self.logger.info(f"[execution.success] tool={reasoning_result.tool_name} time={execution_result.execution_time}")
                    except Exception:
                        pass
            else:
                message = self._format_tool_error_response(
                    reasoning_result, execution_result
                )
                confidence = max(reasoning_result.confidence - 0.2, 0.0)
                try:
                    self.logger.info(f"[execution.error] tool={reasoning_result.tool_name} error={execution_result.error} time={execution_result.execution_time}")
                except Exception:
                    pass
            
            return AgentResponse(
                message=message,
                action_taken="tool_execution",
                tool_used=reasoning_result.tool_name,
                reasoning=reasoning_result.reasoning,
                confidence=confidence,
                metadata={
                    "execution_result": execution_result.to_dict(),
                    "tool_arguments": reasoning_result.arguments
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error ejecutando herramienta: {str(e)}")
            
            return AgentResponse(
                message=f"Error ejecutando la herramienta {reasoning_result.tool_name}: {str(e)}",
                action_taken="tool_error",
                tool_used=reasoning_result.tool_name,
                reasoning=reasoning_result.reasoning,
                confidence=0.1,
                metadata={"error": str(e)}
            )

    async def _generate_conversational_response(
        self,
        reasoning_result: ReasoningResult,
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """
        Genera una respuesta conversacional.
        
        Args:
            reasoning_result: Resultado del razonamiento
            context: Contexto adicional
            
        Returns:
            AgentResponse: Respuesta conversacional
        """
        # Si tenemos motor de razonamiento, usar Gemini para generar respuesta
        if self.reasoning_engine:
            try:
                conversation_history = self.memory_context.get_recent_messages(count=3)
                
                # Obtener el mensaje del usuario desde reasoning_result
                user_message = reasoning_result.raw_response if reasoning_result.raw_response else "mensaje conversacional"
                
                response_message = await self.reasoning_engine._generate_conversational_response(
                    conversation_history, context
                )
                
                return AgentResponse(
                    message=response_message,
                    action_taken="conversation",
                    reasoning=reasoning_result.reasoning,
                    confidence=reasoning_result.confidence
                )
                
            except Exception as e:
                self.logger.error(f"Error generando respuesta conversacional: {str(e)}")
        
        # Fallback a respuesta genÃ©rica
        return AgentResponse(
            message="Entiendo tu mensaje. Â¿En quÃ© mÃ¡s puedo ayudarte?",
            action_taken="conversation",
            reasoning="Respuesta conversacional genÃ©rica",
            confidence=0.3
        )

    def _format_tool_success_response(
        self,
        reasoning_result: ReasoningResult,
        execution_result: ExecutionResult
    ) -> str:
        """
        Formatea respuesta de herramienta exitosa.
        
        Args:
            reasoning_result: Resultado del razonamiento
            execution_result: Resultado de la ejecuciÃ³n
            
        Returns:
            str: Mensaje formateado
        """
        tool_name = reasoning_result.tool_name
        result = execution_result.result
        
        # Formatear segÃºn el tipo de resultado
        if isinstance(result, dict):
            if "message" in result:
                return f"Listo. {result['message']}"
            return f"Listo. Ejecuté {tool_name} correctamente."
        if isinstance(result, str):
            return f"Listo. {result}"
        return f"Listo. Ejecuté {tool_name} correctamente."

    def _format_tool_error_response(
        self,
        reasoning_result: ReasoningResult,
        execution_result: ExecutionResult
    ) -> str:
        """
        Formatea respuesta de error de herramienta.
        
        Args:
            reasoning_result: Resultado del razonamiento
            execution_result: Resultado de la ejecuciÃ³n
            
        Returns:
            str: Mensaje de error formateado
        """
        tool_name = reasoning_result.tool_name
        error = execution_result.error
        parsed = None
        try:
            s = error if isinstance(error, str) else str(error)
            if s:
                import json, re
                m = re.search(r"\{.*\}", s)
                if m:
                    candidate = m.group(0)
                    parsed = json.loads(candidate)
        except Exception:
            parsed = None
        
        if execution_result.status == ExecutionStatus.NOT_FOUND:
            return f"No encontré la herramienta '{tool_name}'."
        if execution_result.status == ExecutionStatus.VALIDATION_ERROR:
            return f"Datos incompletos o inválidos para {tool_name}: {error}"
        if execution_result.status == ExecutionStatus.TIMEOUT:
            return f"La herramienta {tool_name} tardó demasiado en responder."
        if parsed and isinstance(parsed, dict):
            code = parsed.get("code") or parsed.get("status")
            msg = parsed.get("message")
            det = parsed.get("details")
            path = parsed.get("path")
            parts = []
            if code:
                parts.append(f"HTTP {code}")
            if path:
                parts.append(f"{path}")
            base = f"Error en {tool_name}"
            if parts:
                base += f" ({' - '.join(parts)})"
            if msg:
                base += f": {msg}"
            if isinstance(det, list) and det:
                base += "\n" + "\n".join(str(d) for d in det)
            return base
        return f"Error en {tool_name}: {error}"

    def _update_session_stats(self, execution_time: float, success: bool) -> None:
        """
        Actualiza estadÃ­sticas de la sesiÃ³n.
        
        Args:
            execution_time: Tiempo de ejecuciÃ³n
            success: Si fue exitoso
        """
        self.session_stats["messages_processed"] += 1
        
        if not success:
            self.session_stats["errors"] += 1
        
        # Actualizar tiempo promedio de respuesta
        total_messages = self.session_stats["messages_processed"]
        current_avg = self.session_stats["avg_response_time"]
        self.session_stats["avg_response_time"] = (
            (current_avg * (total_messages - 1) + execution_time) / total_messages
        )

    async def _execute_dependencies(self, tool_name: str, context: Optional[Dict[str, Any]]) -> None:
        deps = self.dependency_map.get(tool_name) or []
        if not deps:
            return
        tasks = []
        for dep in deps:
            if self.tool_manager and dep in self.tool_manager.registered_tools:
                tasks.append(self.tool_manager.execute_tool(dep, {}, context))
        if tasks:
            try:
                self.logger.info("executing_tool_group_parallel", group_size=len(tasks))
                await asyncio.gather(*tasks)
                self.logger.info("executing_dependent_tools_parallel", tool_count=len(tasks))
            except Exception:
                pass

    async def _rebuild_planner(self) -> None:
        self.info_gathering_tools = set()
        self.dependency_map = {}
        names: list[str] = []
        if isinstance(self.available_tools, dict):
            names = list(self.available_tools.keys())
        elif self.tool_manager and hasattr(self.tool_manager, 'registered_tools'):
            names = list(self.tool_manager.registered_tools.keys())
        for n in names:
            sch = self.tool_manager.get_tool_schema(n) or {}
            req = sch.get("required", []) or []
            props = sch.get("properties", {}) or {}
            if not req:
                self.info_gathering_tools.add(n)
                continue
            if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
                inner = props.get(req[0], {}) or {}
                inner_req = inner.get("required", []) or []
                if not inner_req:
                    self.info_gathering_tools.add(n)
        for n in names:
            sch = self.tool_manager.get_tool_schema(n) or {}
            props = sch.get("properties", {}) or {}
            req = sch.get("required", []) or []
            keys: list[str] = []
            if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
                inner = props.get(req[0], {}) or {}
                keys = (inner.get("required", []) or [])
            else:
                keys = req
            if not keys:
                continue
            query = " ".join(keys)
            candidates: list[str] = []
            if self.semantic_registry:
                top = self.semantic_registry.find_top_tools(query=query, max_results=5)
                for td in top:
                    name = getattr(td, "name", "")
                    if name and name in self.info_gathering_tools:
                        candidates.append(name)
            self.dependency_map[n] = sorted(list(set(candidates)))

    # MÃ©todos de gestiÃ³n de herramientas
    
    def register_tool(
        self,
        name: str,
        handler,
        description: str,
        schema: Optional[Dict[str, Any]] = None,
        examples: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> bool:
        """
        Registra una nueva herramienta.
        
        Args:
            name: Nombre de la herramienta
            handler: FunciÃ³n manejadora
            description: DescripciÃ³n de la herramienta
            schema: Esquema de validaciÃ³n
            examples: Ejemplos de uso
            
        Returns:
            bool: True si se registrÃ³ exitosamente
        """
        if not self.enable_tools:
            return False
        effective_schema = schema or {}
        try:
            if isinstance(effective_schema, dict) and effective_schema:
                req = effective_schema.get("required", []) or []
                props = effective_schema.get("properties", {}) or {}
                if not req and isinstance(props, dict):
                    object_keys = [k for k, v in props.items() if isinstance(v, dict) and v.get("type") == "object"]
                    if len(object_keys) == 1:
                        effective_schema["required"] = [object_keys[0]]
                        req = effective_schema["required"]
                if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
                    root = req[0]
                    inner = props.get(root, {}) or {}
                    inner_required = inner.get("required", []) or []
                    inner_props = inner.get("properties", {}) or {}
                    from ..models.mcp_models import MCPModelMapper
                    model_cls = MCPModelMapper.get_create_model(name)
                    if model_cls:
                        js = model_cls.model_json_schema() or {}
                        mr = js.get("required", []) or []
                        mp = js.get("properties", {}) or {}
                        if mr and not inner_required:
                            inner["required"] = mr
                        if mp and not inner_props:
                            inner["properties"] = mp
                        effective_schema["properties"][root] = inner
        except Exception:
            pass
        # Registrar en el gestor de herramientas
        tool_registered = self.tool_manager.register_tool(
            name=name,
            handler=handler,
            schema=effective_schema,
            description=description
        )
        
        # Registrar en el registro semÃ¡ntico
        if tool_registered and self.semantic_registry:
            # Usar el primer ejemplo si hay varios
            example = examples[0] if examples else f"Usar {name}"
            self.semantic_registry.register_tool(
                name=name,
                description=description,
                example=example,
                parameters=effective_schema,
                category=category or "general"
            )
        
        return tool_registered

    def get_session_info(self) -> Dict[str, Any]:
        """
        Obtiene informaciÃ³n de la sesiÃ³n actual.
        
        Returns:
            Dict: InformaciÃ³n de la sesiÃ³n
        """
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "last_activity": self.last_activity.isoformat(),
            "components": {
                "reasoning_enabled": self.enable_reasoning,
                "tools_enabled": self.enable_tools,
                "reasoning_engine": self.reasoning_engine is not None,
                "tool_manager": self.tool_manager is not None,
                "semantic_registry": self.semantic_registry is not None,
                "mcp_client": self.mcp_client is not None
            },
            "stats": self.session_stats,
            "memory": {
                "total_messages": len(self.memory_context.messages),
                "recent_messages": len(self.memory_context.get_recent_messages(5))
            },
            "available_tools": self.available_tools
        }

    def clear_memory(self) -> None:
        """Limpia la memoria conversacional."""
        self.memory_context.clear()
        self.logger.info("Memoria conversacional limpiada")

    def get_available_tools(self) -> List[str]:
        """
        Obtiene lista de herramientas disponibles.
        
        Returns:
            List[str]: Nombres de herramientas
        """
        return list(self.available_tools.keys())

    async def _load_tools_from_mcp(self) -> None:
        """
        Carga herramientas desde el servidor MCP de forma asÃ­ncrona.
        """
        import time
        start_time = time.time()
        self.logger.info(f"[DEBUG] _load_tools_from_mcp() iniciado - timestamp: {start_time}")
        try:
            self.logger.info("Cargando herramientas desde servidor MCP...")
            self.logger.info("[DEBUG] Llamando a mcp_client.get_available_tools()...")
            mcp_start = time.time()
            tools = await self.mcp_client.get_available_tools()
            mcp_time = time.time() - mcp_start
            self.logger.info(f"[DEBUG] Herramientas obtenidas en {mcp_time:.2f}s: {len(tools) if tools else 0}")
            
            if tools:
                self.logger.info(f"Obtenidas {len(tools)} herramientas del servidor MCP")
                
                for i, tool in enumerate(tools):
                    tool_start = time.time()
                    tool_name = tool.get("name")
                    if tool_name:
                        # Crear handler genÃ©rico para la herramienta MCP
                        handler_start = time.time()
                        handler = self.create_mcp_handler(tool_name, tool)
                        handler_time = time.time() - handler_start
                        
                        # Registrar usando el mÃ©todo del AgentCore que registra en ambos lugares
                        description = tool.get("description", "")
                        examples = [f"Usar {tool_name} para {description}"] if description else None
                        
                        register_start = time.time()
                        success = self.register_tool(
                            name=tool_name,
                            handler=handler,
                            description=description,
                            schema=tool.get("parameters"),
                            examples=examples,
                            category=tool.get("category")
                        )
                        register_time = time.time() - register_start
                        
                        if success:
                            # Agregar a available_tools
                            self.available_tools[tool_name] = tool
                            self.logger.debug(f"Herramienta MCP registrada: {tool_name} (handler: {handler_time:.2f}s, registro: {register_time:.2f}s)")
                        else:
                            self.logger.warning(f"Error registrando herramienta MCP: {tool_name} (handler: {handler_time:.2f}s, registro: {register_time:.2f}s)")
                    else:
                        self.logger.warning(f"Herramienta sin nombre encontrada: {tool}")
                    
                    tool_time = time.time() - tool_start
                    # Log de progreso cada 5 herramientas o si una herramienta tarda más de 1 segundo
                    if (i + 1) % 5 == 0 or tool_time > 1.0:
                        elapsed = time.time() - start_time
                        self.logger.info(f"[PROGRESO] Procesadas {i + 1}/{len(tools)} herramientas (tiempo total: {elapsed:.2f}s, última: {tool_time:.2f}s)")
            else:
                self.logger.warning("No se obtuvieron herramientas del servidor MCP")
            
            # IMPORTANTE: Reconstruir el índice semántico después de cargar nuevas herramientas
            if self.semantic_selector and self.semantic_registry:
                try:
                    self.logger.info("Reconstruyendo índice semántico con nuevas herramientas...")
                    indexed_count = self.semantic_selector.build_index(self.semantic_registry)
                    self.logger.info(f"Índice semántico reconstruido con {indexed_count} herramientas")
                except Exception as e:
                    self.logger.warning(f"Error reconstruyendo índice semántico: {e}")
                
        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"Error al cargar herramientas desde MCP (después de {elapsed:.2f}s): {str(e)}")
            self.logger.exception("Detalles del error:")
            raise
        
        total_time = time.time() - start_time
        self.logger.info(f"[DEBUG] _load_tools_from_mcp() completado en {total_time:.2f}s")
        try:
            await self._rebuild_planner()
        except Exception:
            pass
    
    def create_mcp_handler(self, tool_name: str, tool_info: Dict[str, Any]):
        """
        Crea un handler genÃ©rico para una herramienta MCP.
        
        Args:
            tool_name: Nombre de la herramienta
            tool_info: InformaciÃ³n de la herramienta
            
        Returns:
            Handler asÃ­ncrono para la herramienta
        """
        async def mcp_handler(arguments: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
            """Handler genÃ©rico para ejecutar herramientas MCP.

            Nota: ToolManager invoca handlers con la firma (arguments, context),
            por lo que debemos evitar envolver los argumentos dentro de otra clave
            'arguments' para no generar anidamiento doble.
            """
            try:
                args = dict(arguments or {})
                ctxd = context or {}
                for k in ("jwt_token", "group_id", "usuario_id"):
                    if k not in args and isinstance(ctxd, dict) and k in ctxd:
                        args[k] = ctxd[k]
                self.logger.info(f"Ejecutando herramienta MCP: {tool_name} con argumentos: {args}")
                result = await self.mcp_client.call_tool(tool_name, args)
                self.logger.info(f"Resultado de {tool_name}: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Error ejecutando herramienta MCP {tool_name}: {e}")
                raise
        
        return mcp_handler
    async def _ensure_tools_loaded(self) -> None:
        if self._tools_loaded:
            return
        if self.enable_tools and self.mcp_client:
            try:
                await self._load_tools_from_mcp()
                self._tools_loaded = True
            except Exception:
                pass
