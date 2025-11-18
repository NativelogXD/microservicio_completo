# Reglas Globales del Sistema MCP Agent

## Principios Fundamentales

### 1. **No Heurísticas**
- ❌ **PROHIBIDO**: Usar condiciones fijas, patrones hardcodeados o reglas if/else para detectar intenciones
- ❌ **PROHIBIDO**: Mapeos literales entre palabras clave y herramientas
- ✅ **REQUERIDO**: Todo razonamiento debe pasar por el LLM (Gemini)
- ✅ **REQUERIDO**: Usar análisis semántico y embeddings para similitud

### 2. **Razonamiento Explícito**
- Cada decisión debe ser explicable y trazable
- El ReasoningEngine debe documentar su proceso lógico
- Las respuestas deben incluir el campo `reasoning` con justificación
- Mantener transparencia en todas las operaciones

### 3. **Arquitectura Modular**
- Cada componente tiene una responsabilidad única y bien definida
- No mezclar lógica de razonamiento con ejecución de herramientas
- Interfaces claras entre módulos
- Facilitar testing y mantenimiento

### 4. **Gestión de Contexto**
- Mantener memoria conversacional relevante
- Evitar pérdida de contexto entre interacciones
- Priorizar información reciente pero conservar contexto histórico importante
- Limitar memoria para evitar sobrecarga del LLM

### 5. **Manejo de Errores**
- Fallar de forma elegante y recuperable
- Proporcionar mensajes de error útiles al usuario
- Implementar reintentos automáticos cuando sea apropiado
- Logging detallado para debugging

## Flujo de Decisión

### Tipos de Acción Válidos:
1. **"tool_call"**: Ejecutar una herramienta específica
2. **"conversation"**: Responder de forma conversacional
3. **"clarify"**: Pedir aclaración al usuario

### Criterios de Decisión:
- **Tool Call**: Cuando el usuario solicita una acción específica que puede ser ejecutada
- **Conversation**: Para preguntas generales, saludos, o información que no requiere herramientas
- **Clarify**: Cuando la intención es ambigua o faltan parámetros necesarios

## Calidad del Código

### Estándares:
- Python 3.11+ con type hints completos
- Documentación en docstrings para todas las clases y métodos
- Convenciones PEP8 estrictas
- Manejo de excepciones apropiado
- Testing unitario para componentes críticos

### Estructura de Respuesta JSON:
```json
{
    "action": "tool_call|conversation|clarify",
    "tool_name": "nombre_herramienta",
    "arguments": {"param1": "valor1"},
    "reasoning": "Explicación del proceso lógico",
    "confidence": 0.95
}
```

## Restricciones de Implementación

### ❌ **NO PERMITIDO**:
- Usar `if "palabra" in query.lower()` para detectar intenciones
- Hardcodear mapeos de herramientas
- Lógica de decisión basada en patrones fijos
- Inferencias sin justificación del LLM

### ✅ **REQUERIDO**:
- Análisis semántico con embeddings
- Razonamiento LLM para todas las decisiones
- Validación de parámetros antes de ejecución
- Contexto dinámico basado en herramientas disponibles

## Métricas de Calidad

- **Precisión**: >90% en detección de intenciones correctas
- **Explicabilidad**: Todas las decisiones deben ser trazables
- **Robustez**: Manejo elegante de casos edge y errores
- **Eficiencia**: Respuesta <3 segundos para consultas típicas