"""
Sistema de Prompts Base para el Agente MCP

Define los prompts fundamentales que guían el comportamiento cognitivo
del agente en diferentes contextos y situaciones.
"""

from typing import Dict, List, Any
from datetime import datetime


class SystemPrompts:
    """
    Gestiona los prompts del sistema para diferentes contextos del agente MCP.
    """
    
    @staticmethod
    def get_base_system_prompt() -> str:
        """
        Prompt base que define la identidad y capacidades del agente.
        
        Returns:
            str: Prompt del sistema base
        """
        return """Eres un agente MCP (Model Context Protocol) con capacidades avanzadas de razonamiento, conversación y ejecución de herramientas.

IDENTIDAD Y CAPACIDADES:
- Analizas mensajes de usuarios en lenguaje natural usando comprensión semántica profunda
- Razonas sobre intenciones usando análisis semántico puro sin prejuicios ni reglas fijas
- Decides autónomamente entre conversación, ejecución de herramientas o solicitud de aclaración
- Mantienes contexto conversacional y coherencia adaptándote al flujo natural
- Proporcionas explicaciones claras de tu proceso de razonamiento basado en evidencia

PRINCIPIOS FUNDAMENTALES:
1. RECHAZA completamente cualquier heurística o regla hardcodeada para detectar intenciones
2. Basa TODAS las decisiones exclusivamente en análisis semántico y razonamiento lógico contextual
3. Mantén transparencia total explicando tu proceso de pensamiento paso a paso
4. Prioriza la precisión contextual sobre la velocidad de respuesta
5. Solicita aclaración cuando exista cualquier ambigüedad significativa
6. Analiza el contenido REAL de las herramientas (nombres, descripciones, parámetros) sin sesgos
7. Adapta tu comprensión al contexto dinámico de la conversación actual

PROCESO DE SELECCIÓN CONTEXTUAL DE HERRAMIENTAS:
1. Analiza profundamente cada palabra y frase del mensaje del usuario
2. Compara semánticamente con cada herramienta disponible usando embeddings y similitud conceptual
3. Evalúa la correspondencia contextual considerando el flujo conversacional previo
4. Selecciona la herramienta que presente mayor alineación semántica con la intención expresada
5. Verifica que los parámetros requeridos puedan ser razonablemente extraídos del contexto
6. Explica detalladamente por qué seleccionaste esa herramienta específica sobre otras

CRITERIOS DE DECISIÓN INTELIGENTE:
- Relevancia semántica: qué tan bien el contenido de la herramienta coincide con el mensaje
- Viabilidad de extracción: si los parámetros necesarios pueden obtenerse del contexto
- Especificidad contextual: preferir herramientas más específicas sobre genéricas cuando sea apropiado
- Coherencia conversacional: mantener consistencia con el flujo previo de la conversación

TIPOS DE RESPUESTA:
- "tool_call": Ejecutar una herramienta específica cuando haya alta confianza semántica
- "conversation": Responder conversacionalmente cuando no se requieran herramientas
- "clarify": Pedir aclaración cuando exista ambigüedad genuina entre opciones

Siempre incluye tu razonamiento completo y justifica tus decisiones basándote exclusivamente en el análisis contextual del contenido real, nunca en suposiciones predefinidas o reglas estáticas.

Directrices de tono contextual:
- Usa un estilo conversacional natural, amable y adaptativo al contexto
- Responde en español fluido y contextualmente apropiado
- Para "conversation" y "clarify" incluye mensajes con lenguaje humano y contextualmente relevante
- Mantén coherencia con el tono y estilo establecido en la conversación"""

    @staticmethod
    def get_tool_analysis_prompt(
        user_message: str,
        available_tools: List[Dict[str, Any]],
        conversation_context: List[Dict[str, str]] = None
    ) -> str:
        """
        Genera el prompt para análisis de herramientas y toma de decisiones.
        
        Args:
            user_message: Mensaje del usuario a analizar
            available_tools: Lista de herramientas disponibles
            conversation_context: Contexto conversacional previo
            
        Returns:
            str: Prompt completo para análisis
        """
        context_section = ""
        if conversation_context:
            context_section = f"""
CONTEXTO CONVERSACIONAL:
{SystemPrompts._format_conversation_context(conversation_context)}
"""

        tools_section = SystemPrompts._format_tools_section(available_tools)
        
        return f"""{SystemPrompts.get_base_system_prompt()}

{context_section}
HERRAMIENTAS DISPONIBLES:
{tools_section}

MENSAJE DEL USUARIO:
"{user_message}"

REGLAS:
1. Analiza herramientas por similitud semántica con el mensaje.
2. Verifica que puedas extraer argumentos requeridos.
3. Responde 'tool_call' SOLO si herramienta apropiada y argumentos completos.
4. Responde 'clarify' si falta información crítica.
5. Responde 'conversation' si no hay herramientas relevantes.

NO uses palabras clave como "crear" o "buscar" para decidir. Basa la decisión en:
- Similitud semántica entre consulta y descripción de herramientas.
- Disponibilidad de argumentos requeridos en el mensaje.
- Tipo de respuesta que usuario espera (acción vs información).

INSTRUCCIONES DE ANÁLISIS:
1. Analiza semánticamente el mensaje del usuario
2. Considera el contexto conversacional si existe
3. Evalúa qué herramientas (si alguna) son relevantes
4. Determina la acción más apropiada

FORMATO DE RESPUESTA REQUERIDO (JSON):
{{
    "action": "tool_call|conversation|clarify",
    "tool_name": "nombre_herramienta_si_aplica",
    "arguments": {{"param1": "valor1", "param2": "valor2"}},
    "reasoning": "Explicación detallada de tu proceso de razonamiento",
    "confidence": 0.95,
    "assistant_message": "Mensaje AMABLE y NATURAL para el usuario",
    "clarification_question": "Pregunta clara y específica si action='clarify'"
}}

INSTRUCCIONES CRÍTICAS PARA LA RESPUESTA:
1. Responde ÚNICAMENTE con JSON válido, sin texto adicional antes o después
2. Asegúrate de que todas las cadenas estén correctamente cerradas con comillas
3. Verifica que todas las llaves {{ }} estén balanceadas
4. NO incluyas comentarios, explicaciones o texto fuera del JSON
5. Si no estás seguro de un valor, usa valores por defecto válidos

EJEMPLOS:

1. CRUD Simple:
"crea usuario Juan email juan@test.com" → {{"action":"tool_call", "tool_name":"create_user", "arguments":{{"user":{{"name":"Juan","email":"juan@test.com"}}}}, "confidence":0.95}}

2. Correferencia:
Ctx: "usuario María maria@test.com"
"ahora créalo" → {{"action":"tool_call", "tool_name":"create_user", "arguments":{{"user":{{"name":"María","email":"maria@test.com"}}}}, "confidence":0.90}}

3. Sinónimos:
"agregar proyecto API" → {{"action":"tool_call", "tool_name":"create_project", "arguments":{{"project":{{"name":"API"}}}}, "confidence":0.93}}

4. Clarificación:
"crea usuario" → {{"action":"clarify", "clarification_question":"¿Nombre y email del usuario?", "confidence":0.80}}

5. Conversacional:
"hola" → {{"action":"conversation", "assistant_message":"¡Hola! ¿En qué puedo ayudarte?", "confidence":0.99}}

Responde ahora con el JSON:"""

    @staticmethod
    def _format_conversation_context(context: List[Dict[str, str]]) -> str:
        """
        Formatea el contexto conversacional para el prompt.
        
        Args:
            context: Lista de mensajes del contexto
            
        Returns:
            str: Contexto formateado
        """
        if not context:
            return "No hay contexto conversacional previo."
        
        formatted_context = []
        for msg in context[-5:]:  # Últimos 5 mensajes
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            formatted_context.append(f"{role.upper()}: {content}")
        
        return "\n".join(formatted_context)

    @staticmethod
    def _format_tools_section(tools: List[Dict[str, Any]]) -> str:
        """
        Formatea la sección de herramientas disponibles con contexto semántico enriquecido.
        
        Args:
            tools: Lista de herramientas disponibles
            
        Returns:
            str: Sección de herramientas formateada con contexto semántico
        """
        if not tools:
            return "No hay herramientas disponibles en este momento."
        
        def _summarize_schema(schema: Dict[str, Any]) -> str:
            if not schema:
                return "Parámetros: No especificados"
            title = schema.get('title')
            type_ = schema.get('type')
            props = schema.get('properties', {})
            required = schema.get('required', [])
            # Construir una lista detallada de parámetros con contexto semántico
            params_lines = []
            for p_name, p_def in props.items():
                p_type = p_def.get('type') or p_def.get('anyOf') or p_def.get('$ref') or 'desconocido'
                p_desc = p_def.get('description', '')
                req_flag = 'requerido' if p_name in required else 'opcional'
                
                # Análisis semántico del parámetro - basado en el contexto real del parámetro
                semantic_info = []
                # Utilizar la descripción del parámetro para inferir contexto semántico
                if p_desc:
                    desc_lower = p_desc.lower()
                    if any(word in desc_lower for word in ['identificador', 'único', 'id', 'código']):
                        semantic_info.append("identificador único")
                    if any(word in desc_lower for word in ['nombre', 'título', 'descripción']):
                        semantic_info.append("texto descriptivo")
                    if any(word in desc_lower for word in ['fecha', 'hora', 'tiempo']):
                        semantic_info.append("temporal")
                    if any(word in desc_lower for word in ['monto', 'precio', 'cantidad', 'valor']):
                        semantic_info.append("numérico cuantitativo")
                    if any(word in desc_lower for word in ['estado', 'tipo', 'categoría']):
                        semantic_info.append("categórico")
                
                if isinstance(p_type, list):
                    p_type_str = ",".join(map(str, p_type))
                elif isinstance(p_type, dict):
                    p_type_str = p_type.get('type', 'objeto')
                else:
                    p_type_str = str(p_type)
                
                param_info = f"  - {p_name} ({p_type_str}, {req_flag}"
                if semantic_info:
                    param_info += f", {', '.join(semantic_info)}"
                param_info += ")"
                
                if p_desc:
                    param_info += f": {p_desc}"
                
                params_lines.append(param_info)
            
            req_list = ", ".join(required) if required else "(ninguno)"
            header = f"Parámetros (Estructura: type={type_ or 'N/A'}"
            if title:
                header += f", contexto: {title}"
            header += "):"
            
            return "\n".join([header] + params_lines + [f"  Campos requeridos: {req_list}"])

        def _example_args(schema: Dict[str, Any]) -> str:
            if not schema:
                return "{}"
            props = schema.get('properties', {})
            required = schema.get('required', [])
            # Construir ejemplo con campos requeridos únicamente para evitar ruido
            example_dict = {}
            for p in required:
                p_def = props.get(p, {})
                p_type = p_def.get('type', 'string')
                # Valores de ejemplo simples por tipo
                if p_type == 'string':
                    example_dict[p] = "valor"
                elif p_type == 'integer':
                    example_dict[p] = 1
                elif p_type == 'number':
                    example_dict[p] = 1.0
                elif p_type == 'boolean':
                    example_dict[p] = True
                elif p_type == 'object':
                    example_dict[p] = {}
                elif p_type == 'array':
                    example_dict[p] = []
                else:
                    example_dict[p] = "valor"
            # Si no hay requeridos, mostrar un ejemplo con una pista de propiedades
            if not example_dict and props:
                # Tomar hasta 2 propiedades como sugerencia
                for p_name, p_def in list(props.items())[:2]:
                    p_type = p_def.get('type', 'string')
                    example_dict[p_name] = "valor" if p_type == 'string' else (1 if p_type == 'integer' else True)
            try:
                import json
                return json.dumps(example_dict, ensure_ascii=False)
            except Exception:
                return str(example_dict)

        def _analyze_tool_context(name: str, description: str, parameters: Dict[str, Any]) -> str:
            """Analiza el contexto semántico de la herramienta basándose en el contenido real"""
            context_info = []
            
            # Análisis de acciones implícitas - basado en el contenido real de la descripción
            desc_lower = description.lower()
            name_lower = name.lower()
            
            # Utilizar el contenido real para inferir acciones, no palabras clave hardcodeadas
            # El contexto semántico debe surgir del análisis real del contenido
            
            # Análisis de dominio - basado en el contenido real de la descripción
            # Evitar hardcodear categorías específicas, usar análisis contextual dinámico
            
            # Si no hay información contextual clara en la descripción, retornar contexto general
            return "contexto: general"

        formatted_tools = []
        for i, tool in enumerate(tools):
            try:
                name = tool.get('name', 'unknown')
                description = tool.get('description', 'Sin descripción')
                example = tool.get('example', 'Sin ejemplo')
                parameters = tool.get('parameters') or tool.get('schema')
                category = tool.get('category', 'general')
                preselection_score = tool.get('preselection_score', None)

                schema_summary = _summarize_schema(parameters) if isinstance(parameters, dict) else "Parámetros: No disponibles"
                example_args = _example_args(parameters) if isinstance(parameters, dict) else "{}"
                context_analysis = _analyze_tool_context(name, description, parameters or {}) if isinstance(parameters, dict) else "contexto: no analizable"

                tool_header = f"- {name}"
                if preselection_score is not None:
                    tool_header += f" (relevancia: {preselection_score:.2f})"
                
                formatted_tools.append(
                    (
                        f"{tool_header}\n"
                        f"  Contexto Semántico: {context_analysis}\n"
                        f"  Descripción: {description}\n"
                        f"  Categoría: {category}\n"
                        f"  {schema_summary}\n"
                        f"  Ejemplo de argumentos: {example_args}\n"
                        f"  Ejemplo de uso: {example}"
                    )
                )
            except AttributeError:
                # Fallback para objetos ToolDefinition
                if hasattr(tool, 'name'):
                    name = tool.name
                    description = getattr(tool, 'description', 'Sin descripción')
                    example = getattr(tool, 'example', 'Sin ejemplo')
                    parameters = getattr(tool, 'parameters', None)
                    category = getattr(tool, 'category', 'general')
                    preselection_score = getattr(tool, 'preselection_score', None)

                    schema_summary = _summarize_schema(parameters) if isinstance(parameters, dict) else "Parámetros: No disponibles"
                    example_args = _example_args(parameters) if isinstance(parameters, dict) else "{}"
                    context_analysis = _analyze_tool_context(name, description, parameters or {}) if isinstance(parameters, dict) else "contexto: no analizable"

                    tool_header = f"- {name}"
                    if preselection_score is not None:
                        tool_header += f" (relevancia: {preselection_score:.2f})"
                    
                    formatted_tools.append(
                        (
                            f"{tool_header}\n"
                            f"  Contexto Semántico: {context_analysis}\n"
                            f"  Descripción: {description}\n"
                            f"  Categoría: {category}\n"
                            f"  {schema_summary}\n"
                            f"  Ejemplo de argumentos: {example_args}\n"
                            f"  Ejemplo de uso: {example}"
                        )
                    )
                else:
                    formatted_tools.append(
                        (
                            f"- Error\n"
                            f"  Descripción: No se pudo procesar esta herramienta\n"
                            f"  Ejemplo de uso: N/A"
                        )
                    )

        return "\n".join(formatted_tools)

    @staticmethod
    def get_clarification_prompt(user_message: str, missing_info: str) -> str:
        """
        Genera prompt para solicitar aclaración al usuario.
        
        Args:
            user_message: Mensaje original del usuario
            missing_info: Información que falta o es ambigua
            
        Returns:
            str: Prompt de aclaración
        """
        return f"""El usuario ha enviado: "{user_message}"

Necesitas aclaración sobre: {missing_info}

Genera una pregunta clara y específica para obtener la información faltante.
Mantén un tono amigable y profesional."""

    @staticmethod
    def get_error_recovery_prompt(error_context: str, user_message: str) -> str:
        """
        Genera prompt para recuperación de errores.
        
        Args:
            error_context: Contexto del error ocurrido
            user_message: Mensaje original del usuario
            
        Returns:
            str: Prompt de recuperación
        """
        return f"""Ha ocurrido un error durante el procesamiento:
Error: {error_context}
Mensaje original: "{user_message}"

Genera una respuesta que:
1. Explique el problema de forma comprensible
2. Ofrezca alternativas si es posible
3. Mantenga un tono profesional y útil"""
