"""
ReasoningEngine - Motor Cognitivo del Agente MCP

Núcleo de razonamiento que utiliza Gemini LLM para:
1. Analizar intenciones del usuario
2. Decidir entre conversación, herramientas o aclaración
3. Generar respuestas estructuradas con justificación
4. Mantener coherencia cognitiva
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from ..system_prompt.base_prompt import SystemPrompts
from AgenteIA.app.agent.system_prompt.enhanced_prompt import build_system_prompt
from app.utils.json_normalizer import safe_parse_json, normalize_llm_output, repair_json_string
from ..gemini_function_calling import convert_mcp_tools_to_gemini


class ActionType(Enum):
    """
    Tipos de acciones que puede decidir el ReasoningEngine.
    """
    CONVERSATION = "conversation"
    TOOL_CALL = "tool_call"
    CLARIFY = "clarify"


@dataclass
class ReasoningResult:
    """
    Resultado estructurado del proceso de razonamiento.
    
    Attributes:
        action: Tipo de acción decidida (ActionType enum)
        tool_name: Nombre de la herramienta si action es tool_call
        arguments: Argumentos para la herramienta
        reasoning: Explicación del proceso de razonamiento
        confidence: Nivel de confianza en la decisión (0.0-1.0)
        processing_time: Tiempo de procesamiento en segundos
        raw_response: Respuesta cruda del LLM para debugging
        requires_clarification: Si se requiere aclaración
        clarification_question: Pregunta de aclaración si aplica
    """
    action: ActionType
    tool_name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    reasoning: str = ""
    confidence: float = 0.0
    processing_time: float = 0.0
    raw_response: str = ""
    requires_clarification: bool = False
    clarification_question: str = ""
    assistant_message: str = ""


class ReasoningEngine:
    """
    Motor de razonamiento cognitivo basado en Gemini LLM.
    
    Responsabilidades:
    - Analizar intenciones del usuario usando LLM
    - Generar contexto dinámico con herramientas disponibles
    - Tomar decisiones autónomas sobre acciones
    - Proporcionar explicaciones transparentes
    """
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.1,
        max_tokens: int = 1000
    ):
        """
        Inicializa el motor de razonamiento.
        
        Args:
            api_key: Clave API de Google Gemini
            model_name: Nombre del modelo Gemini a usar
            temperature: Temperatura para generación (0.0-1.0)
            max_tokens: Máximo número de tokens en respuesta
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Configurar Gemini
        genai.configure(api_key=api_key)
        
        # Configuración de seguridad permisiva para uso interno
        # Ajustada para cumplir con categorías válidas en la API (sin 'UNSPECIFIED')
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        # Inicializar modelo
        self.model = genai.GenerativeModel(
            model_name=model_name,
            safety_settings=self.safety_settings
        )
        
        try:
            import structlog  # type: ignore
            self.logger = structlog.get_logger(__name__)
        except Exception:
            self.logger = logging.getLogger(__name__)
        self.logger.info(f"ReasoningEngine inicializado con modelo {model_name}")

    async def analyze_intent(
        self,
        user_message: str,
        available_tools: List[Dict[str, Any]],
        conversation_context: Optional[List[Dict[str, str]]] = None
    ) -> ReasoningResult:
        return await self.analyze_intent_v2(user_message, available_tools, conversation_context)

    def _filter_tools_by_intent(self, intent: str, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Remove hardcoded intent-based filtering - return all tools sorted by preselection score
        # This allows the LLM to make the final decision without being biased by hardcoded categories
        return sorted(tools, key=lambda x: float(x.get("preselection_score", 0.0)), reverse=True)

    async def _call_gemini(self, prompt: str) -> str:
        """
        Realiza llamada al modelo Gemini con manejo de errores.
        
        Args:
            prompt: Prompt a enviar al modelo
            
        Returns:
            str: Respuesta del modelo
        """
        import asyncio
        import functools
        
        try:
            # Configurar parámetros de generación
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                candidate_count=1
            )
            
            # Ejecutar generate_content en un thread pool para mantener asincronía
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    self.model.generate_content,
                    prompt,
                    generation_config=generation_config,
                    safety_settings=self.safety_settings
                )
            )
            
            if not response.text:
                raise ValueError("Respuesta vacía del modelo Gemini")
            
            return response.text.strip()
            
        except Exception as e:
            self.logger.error(f"Error en llamada a Gemini: {str(e)}")
            raise

    def _parse_gemini_response(self, response: str) -> ReasoningResult:
        """
        Parsea la respuesta JSON del modelo Gemini con manejo robusto de errores.
        
        Args:
            response: Respuesta cruda del modelo
            
        Returns:
            ReasoningResult: Resultado parseado y validado
        """
        try:
            # Normalizar y parsear con utilitario general
            required_keys = ["action", "reasoning", "confidence"]
            parsed, err = safe_parse_json(response, schema_required_keys=required_keys, return_best_effort=True)
            cleaned_response = response.strip()
            self.logger.debug(f"Respuesta normalizada para parsing: {cleaned_response[:200]}...")
            if err and not parsed:
                self.logger.error(f"Error parseando JSON (safe_parse_json): {err}")
                return self._create_fallback_from_malformed_response(response, err)
            
            # Validar campos requeridos
            action_str = str(parsed.get("action", "")).lower()
            if action_str not in ["tool_call", "conversation", "clarify"]:
                raise ValueError(f"Acción inválida: {action_str}")
            
            # Convertir string a ActionType
            action_map = {
                "tool_call": ActionType.TOOL_CALL,
                "conversation": ActionType.CONVERSATION,
                "clarify": ActionType.CLARIFY
            }
            action = action_map[action_str]
            
            # Crear resultado
            result = ReasoningResult(
                action=action,
                tool_name=parsed.get("tool_name"),
                arguments=parsed.get("arguments", {}),
                reasoning=parsed.get("reasoning", "Sin explicación proporcionada"),
                confidence=float(parsed.get("confidence", 0.5)),
                requires_clarification=(action == ActionType.CLARIFY),
                clarification_question=parsed.get("clarification_question", "") if action == ActionType.CLARIFY else "",
                assistant_message=parsed.get("assistant_message", "")
            )
            
            # Validar coherencia
            if result.action == ActionType.TOOL_CALL and not result.tool_name:
                raise ValueError("tool_call requiere tool_name")
            
            return result
            
        except json.JSONDecodeError as e:
            # Con el normalizador, es menos probable llegar aquí, pero mantenemos compatibilidad
            self.logger.error(f"Error parseando JSON: {str(e)}")
            self.logger.debug(f"Respuesta problemática completa: {response}")
            self.logger.debug(f"Respuesta limpia problemática: {cleaned_response}")
            return self._create_fallback_from_malformed_response(response, str(e))
        
        except Exception as e:
            self.logger.error(f"Error validando respuesta: {str(e)}")
            return self._create_fallback_result("Error de parsing", str(e))

    def _repair_json_string(self, json_str: str) -> str:
        """Compatibilidad: delega en el utilitario general de reparación JSON."""
        try:
            return repair_json_string(json_str)
        except Exception as e:
            self.logger.warning(f"Error reparando JSON (util): {e}")
            return json_str

    def _create_fallback_from_malformed_response(self, response: str, error: str) -> ReasoningResult:
        """
        Crea un resultado de fallback analizando una respuesta malformada.
        
        Args:
            response: Respuesta original malformada
            error: Error de parsing
            
        Returns:
            ReasoningResult: Resultado de fallback
        """
        # Intentar extraer información útil de la respuesta malformada
        reasoning = f"Respuesta JSON malformada del modelo: {error}. "
        
        # Buscar patrones comunes en la respuesta
        if "tool_call" in response.lower():
            reasoning += "Parece ser una llamada a herramienta."
            return ReasoningResult(
                action=ActionType.CONVERSATION,
                reasoning=reasoning + " Reintentando con respuesta conversacional.",
                confidence=0.2,
                raw_response=response
            )
        elif "conversation" in response.lower():
            reasoning += "Parece ser una respuesta conversacional."
            return ReasoningResult(
                action=ActionType.CONVERSATION,
                reasoning=reasoning,
                confidence=0.3,
                raw_response=response
            )
        else:
            return ReasoningResult(
                action=ActionType.CONVERSATION,
                reasoning=reasoning + "Usando fallback conversacional.",
                confidence=0.1,
                raw_response=response
            )

    def _create_fallback_result(self, user_message: str, error: str) -> ReasoningResult:
        """
        Crea un resultado de fallback cuando hay errores.
        
        Args:
            user_message: Mensaje original del usuario
            error: Descripción del error
            
        Returns:
            ReasoningResult: Resultado de fallback seguro
        """
        return ReasoningResult(
            action=ActionType.CONVERSATION,
            reasoning=f"Error en análisis cognitivo: {error}. Respondiendo conversacionalmente.",
            confidence=0.1,
            raw_response=f"ERROR: {error}",
            requires_clarification=False,
            clarification_question=""
        )

    async def generate_clarification(
        self,
        user_message: str,
        missing_info: str
    ) -> str:
        """
        Genera una pregunta de aclaración para el usuario.
        
        Args:
            user_message: Mensaje original del usuario
            missing_info: Información que falta o es ambigua
            
        Returns:
            str: Pregunta de aclaración generada
        """
        try:
            prompt = SystemPrompts.get_clarification_prompt(user_message, missing_info)
            response = await self._call_gemini(prompt)
            return response
            
        except Exception as e:
            self.logger.error(f"Error generando aclaración: {str(e)}")
            return f"Necesito más información sobre: {missing_info}. ¿Podrías ser más específico?"

    async def handle_error_recovery(
        self,
        error_context: str,
        user_message: str
    ) -> str:
        """
        Genera respuesta de recuperación ante errores.
        
        Args:
            error_context: Contexto del error ocurrido
            user_message: Mensaje original del usuario
            
        Returns:
            str: Respuesta de recuperación
        """
        try:
            prompt = SystemPrompts.get_error_recovery_prompt(error_context, user_message)
            response = await self._call_gemini(prompt)
            return response
            
        except Exception as e:
            self.logger.error(f"Error en recuperación: {str(e)}")
            return "Ha ocurrido un error interno. Por favor, intenta reformular tu solicitud."

    async def _generate_conversational_response(
        self,
        conversation_history: List[Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera una respuesta conversacional usando Gemini.
        
        Args:
            conversation_history: Historial de conversación
            context: Contexto adicional
            
        Returns:
            str: Respuesta conversacional
        """
        try:
            # Construir prompt conversacional
            conversation_context = ""
            for msg in conversation_history[-3:]:  # Últimos 3 mensajes
                role = "Usuario" if msg.role.value == "user" else "Asistente"
                conversation_context += f"{role}: {msg.content}\n"
            
            prompt = f"""
Eres un asistente inteligente y conversacional. Responde de manera natural y útil.

Contexto de la conversación:
{conversation_context}

Reglas críticas:
- No afirmes haber ejecutado acciones ni creado/modificado recursos si no ejecutaste ninguna herramienta.
- Si la solicitud implica creación/acción, indica que necesitas usar herramientas y evita confirmar resultados.
- Mantén un tono amigable y profesional.

Genera una respuesta conversacional apropiada, natural y útil.
"""
            
            # Llamar a Gemini
            response = await self._call_gemini(prompt)
            
            if response:
                return response.strip()
            else:
                return "Entiendo. ¿En qué más puedo ayudarte?"
                
        except Exception as e:
            self.logger.error(f"Error generando respuesta conversacional: {str(e)}")
            return "Disculpa, tuve un problema generando la respuesta. ¿Podrías reformular tu pregunta?"

    def get_engine_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del motor de razonamiento.
        
        Returns:
            Dict con información de estado
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "status": "active",
            "api_configured": bool(self.api_key)
        }
    async def analyze_intent_v2(
        self,
        user_message: str,
        available_tools: List[Dict[str, Any]],
        conversation_context: Optional[List[Dict[str, str]]] = None
    ) -> ReasoningResult:
        start_time = datetime.now()
        try:
            tools = convert_mcp_tools_to_gemini(available_tools or [])
            
            # Construir contexto conversacional enriquecido
            ctx_lines: List[str] = []
            if conversation_context:
                for m in conversation_context[-5:]:
                    role = str(m.get("role", "")).upper()
                    content = str(m.get("content", ""))
                    ctx_lines.append(f"{role}: {content}")
            ctx = "\n\n".join(ctx_lines) if ctx_lines else ""
            
            # Análisis contextual de herramientas disponibles
            tools_analysis = []
            for tool in available_tools:
                tool_name = tool.get('name', 'unknown')
                tool_desc = tool.get('description', '')
                preselection_score = tool.get('preselection_score', None)
                
                analysis = f"- {tool_name}"
                if preselection_score is not None:
                    analysis += f" (relevancia semántica: {preselection_score:.2f})"
                analysis += f": {tool_desc}"
                tools_analysis.append(analysis)
            
            tools_context = "\n".join(tools_analysis) if tools_analysis else "No hay herramientas relevantes disponibles."
            
            # Prompt contextualizado y explícito
            system_context = (
                "CONTEXTO DEL SISTEMA:\n"
                "Eres un agente inteligente que selecciona herramientas basándose exclusivamente en análisis semántico contextual.\n"
                "DEBES analizar profundamente el mensaje del usuario y compararlo semánticamente con cada herramienta disponible.\n"
                "NO uses reglas predefinidas ni heurísticas. Tu decisión debe basarse puramente en la similitud contextual.\n"
                "Si el mensaje es de consulta (listar, ver, mostrar, obtener, buscar), NO selecciones herramientas de creación/acción.\n\n"
                "PROCESO DE ANÁLISIS REQUERIDO:\n"
                "1. Analiza cada palabra y concepto del mensaje del usuario\n"
                "2. Compara semánticamente con cada herramienta disponible\n"
                "3. Evalúa qué herramienta tiene mayor alineación semántica\n"
                "4. Considera el contexto conversacional previo\n"
                "5. Verifica que los parámetros requeridos puedan extraerse\n"
                "6. Explica tu razonamiento de forma detallada\n\n"
                "HERRAMIENTAS DISPONIBLES (ordenadas por relevancia semántica):\n"
                f"{tools_context}\n\n"
            )
            
            user_analysis = (
                f"MENSAJE DEL USUARIO A ANALIZAR: {user_message}\n\n"
                "INSTRUCCIONES PARA LA SELECCIÓN:\n"
                "- Analiza este mensaje profundamente\n"
                "- Compara con cada herramienta disponible usando comprensión semántica\n"
                "- Selecciona la que presente mayor correspondencia contextual\n"
                "- Si no hay coincidencia clara, responde conversacionalmente\n"
                "- Siempre explica tu razonamiento en tu respuesta"
            )
            
            system_prompt = build_system_prompt(group_id="default", jwt_token="", available_tools=available_tools or [])
            prompt = (
                (f"{system_prompt}\n\n" if system_prompt else "") +
                (f"{ctx}\n\n" if ctx else "") +
                system_context +
                user_analysis
            )
            
            import google.generativeai as genai
            model = genai.GenerativeModel(model_name=self.model_name, tools=tools, safety_settings=self.safety_settings)
            resp = await asyncio.get_event_loop().run_in_executor(None, lambda: model.generate_content(prompt))
            tool_name: Optional[str] = None
            arguments: Dict[str, Any] = {}
            assistant_text: str = ""
            try:
                cand = getattr(resp, "candidates", None)
                if cand and isinstance(cand, list) and cand:
                    content = getattr(cand[0], "content", None)
                    parts = getattr(content, "parts", []) if content else []
                    for p in parts:
                        fn = getattr(p, "function_call", None)
                        if fn and getattr(fn, "name", None):
                            tool_name = str(getattr(fn, "name"))
                            args = getattr(fn, "args", {})
                            if hasattr(args, "items"):
                                arguments = dict(args)
                            break
                        txt = getattr(p, "text", None)
                        if isinstance(txt, str) and txt.strip():
                            assistant_text = txt.strip()
            except Exception:
                pass
            if tool_name:
                # VALIDACIÓN CRÍTICA: Verificar que los parámetros requeridos puedan ser extraídos
                # Buscar el esquema de la herramienta seleccionada
                selected_tool_schema = None
                for tool_info in available_tools:
                    if tool_info.get('name') == tool_name:
                        selected_tool_schema = tool_info.get('parameters', {})
                        break
                
                # Si hay esquema, validar extractabilidad de parámetros
                if selected_tool_schema:
                    from ..schema_extractor import SchemaExtractor
                    schema_extractor = SchemaExtractor()
                    
                    # Probar extracción de parámetros
                    test_args = schema_extractor.extract_arguments(selected_tool_schema, user_message, tool_name)
                    
                    # Verificar si se pudieron extraer parámetros requeridos
                    required_fields = selected_tool_schema.get('required', []) or []
                    extracted_fields = list(test_args.keys()) if isinstance(test_args, dict) else []
                    
                    # CRÍTICO: Validar que los parámetros extraídos sean válidos y no contengan el texto completo
                    valid_parameters = True
                    if test_args and isinstance(test_args, dict):
                        for key, value in test_args.items():
                            if isinstance(value, str):
                                # Verificar que no sea el texto completo
                                if value.lower() == user_message.lower():
                                    valid_parameters = False
                                    break
                                # Verificar que no sea una parte muy grande del texto
                                if len(value.strip()) > len(user_message.strip()) * 0.8:
                                    valid_parameters = False
                                    break
                    
                    # Si no se extrajeron campos requeridos y hay campos requeridos, reconsiderar
                    if required_fields and (not extracted_fields or not valid_parameters):
                        self.logger.warning(f"[reasoning.validation] Tool '{tool_name}' selected but required parameters cannot be extracted")
                        
                        # Buscar herramientas alternativas que puedan tener parámetros extraíbles
                        alternative_tools = []
                        for tool_info in available_tools:
                            alt_name = tool_info.get('name')
                            if alt_name != tool_name:
                                alt_schema = tool_info.get('parameters', {})
                                if alt_schema:
                                    alt_args = schema_extractor.extract_arguments(alt_schema, user_message, alt_name)
                                    alt_required = alt_schema.get('required', []) or []
                                    
                                    # CRÍTICO: Validar que los parámetros extraídos sean válidos
                                    if alt_required and list(alt_args.keys()):
                                        # Verificar que los argumentos no contengan el texto completo como valores
                                        valid_alt_args = True
                                        for key, value in alt_args.items():
                                            if isinstance(value, str):
                                                if value.lower() == user_message.lower():
                                                    valid_alt_args = False
                                                    break
                                                if len(value.strip()) > len(user_message.strip()) * 0.8:
                                                    valid_alt_args = False
                                                    break
                                        
                                        if valid_alt_args:
                                            alternative_tools.append((alt_name, alt_args))
                        
                        # Si hay alternativas con parámetros extraíbles, usar la mejor
                        if alternative_tools:
                            # CRÍTICO: Validar que los parámetros extraídos sean válidos y no sean el texto completo
                            best_alt_name, best_alt_args = alternative_tools[0]
                            
                            # Verificar que los argumentos no contengan el texto completo como valores
                            valid_args = True
                            for key, value in best_alt_args.items():
                                if isinstance(value, str) and value.lower() == user_message.lower():
                                    valid_args = False
                                    break
                                if isinstance(value, str) and len(value.strip()) > len(user_message.strip()) * 0.8:
                                    valid_args = False
                                    break
                            
                            if valid_args:
                                self.logger.info(f"[reasoning.alternative] Using alternative tool '{best_alt_name}' with extractable parameters")
                                
                                result = ReasoningResult(
                                    action=ActionType.TOOL_CALL,
                                    tool_name=best_alt_name,
                                    arguments=best_alt_args,
                                    reasoning=f"Herramienta alternativa seleccionada tras validación de extractabilidad de parámetros",
                                    confidence=0.75,
                                )
                                result.processing_time = (datetime.now() - start_time).total_seconds()
                                return result
                            else:
                                self.logger.warning(f"[reasoning.alternative] Alternative tool '{best_alt_name}' has invalid parameters (contains full text)")
                        
                        # Si no hay alternativas viables, responder conversacionalmente
                        msg = "Entiendo que quieres crear algo, pero necesito más información específica para procesar tu solicitud."
                        result = ReasoningResult(
                            action=ActionType.CONVERSATION,
                            reasoning=f"Validación de extractabilidad fallida. Ninguna herramienta tiene parámetros extraíbles del mensaje.",
                            confidence=0.6,
                            assistant_message=msg,
                        )
                        result.processing_time = (datetime.now() - start_time).total_seconds()
                        return result
                
                # Construir razonamiento contextual detallado
                reasoning_parts = [
                    f"Análisis semántico contextual completado.",
                    f"La herramienta '{tool_name}' fue seleccionada basándose en:",
                    f"- Evaluación de relevancia semántica entre el mensaje y las herramientas disponibles",
                    f"- Análisis de viabilidad de extracción de parámetros requeridos",
                    f"- Consideración del contexto conversacional previo"
                ]
                
                if assistant_text and assistant_text.strip():
                    reasoning_parts.append(f"- Justificación adicional: {assistant_text.strip()}")
                
                detailed_reasoning = " ".join(reasoning_parts)
                
                result = ReasoningResult(
                    action=ActionType.TOOL_CALL,
                    tool_name=tool_name,
                    arguments=arguments,
                    reasoning=detailed_reasoning,
                    confidence=0.92,  # Alta confianza basada en análisis contextual
                )
                result.processing_time = (datetime.now() - start_time).total_seconds()
                return result
            
            # No se seleccionó herramienta - respuesta conversacional con razonamiento
            msg = assistant_text or "Después de analizar todas las herramientas disponibles, no encontré una coincidencia semántica suficientemente fuerte para ejecutar una acción específica."
            
            conversational_reasoning = (
                f"Análisis contextual completado. {msg} "
                f"Este resultado se basa en la evaluación semántica de las herramientas disponibles "
                f"y su alineación con la intención expresada en el mensaje."
            )
            
            result = ReasoningResult(
                action=ActionType.CONVERSATION,
                reasoning=conversational_reasoning,
                confidence=0.78,  # Confianza moderada basada en análisis
                assistant_message=msg,
            )
            result.processing_time = (datetime.now() - start_time).total_seconds()
            return result
        except Exception as e:
            return self._create_fallback_result(user_message, str(e))
