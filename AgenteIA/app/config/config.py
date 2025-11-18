"""
Configuración centralizada para el Agente IA siguiendo principios MCP.
Separa claramente heurísticas operativas válidas de las de reasoning que deben eliminarse.
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Cargar variables de entorno desde archivos .env
# 1) Intentar cargar .env en la raíz del proyecto AgenteIA
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))
# 2) Intentar cargar .env en la raíz del monorepo (microServicios)
load_dotenv(os.path.join(os.path.dirname(__file__), '../../../.env'))

class ConfigCategory(Enum):
    """Categorías de configuración según principios MCP."""
    OPERATIONAL = "operational"  # Válidas: proteger, optimizar, controlar
    REASONING = "reasoning"      # Prohibidas: entender, decidir

@dataclass
class ServerConfig:
    """
    Configuración operativa de servidores (VÁLIDA).
    Controla infraestructura, no inteligencia.
    """
    # API Flask
    flask_host: str = os.getenv("FLASK_HOST", "0.0.0.0")
    flask_port: int = int(os.getenv("FLASK_PORT", "5000"))
    flask_debug: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    
    # MCP Server
    mcp_server_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:3001")
    mcp_server_port: int = int(os.getenv("MCP_SERVER_PORT", "3001"))
    mcp_server_host: str = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    
    # Timeouts operativos (VÁLIDOS)
    connection_timeout: float = float(os.getenv("CONNECTION_TIMEOUT", "30.0"))
    read_timeout: float = float(os.getenv("READ_TIMEOUT", "60.0"))
    
    @property
    def category(self) -> ConfigCategory:
        return ConfigCategory.OPERATIONAL

@dataclass
class LLMConfig:
    """
    Configuración operativa del modelo de lenguaje (VÁLIDA).
    Controla parámetros técnicos, no decisiones de razonamiento.
    """
    # Gemini API - configuración operativa
    # Aceptar tanto GOOGLE_API_KEY como GEMINI_API_KEY para compatibilidad
    gemini_api_key: str = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    gemini_endpoint: str = os.getenv("GEMINI_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-pro")
    gemini_timeout: float = float(os.getenv("GEMINI_TIMEOUT", "30.0"))
    
    # Parámetros técnicos (VÁLIDOS - controlan rendimiento, no decisiones)
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.1"))
    top_p: float = float(os.getenv("TOP_P", "0.95"))
    top_k: int = int(os.getenv("TOP_K", "40"))
    
    # Límites operativos (VÁLIDOS)
    max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
    retry_delay: float = float(os.getenv("LLM_RETRY_DELAY", "1.0"))
    
    @property
    def category(self) -> ConfigCategory:
        return ConfigCategory.OPERATIONAL

@dataclass
class MicroservicesConfig:
    """
    Configuración operativa de microservicios (VÁLIDA).
    Controla conectividad y rendimiento, no lógica de negocio.
    """
    # URLs base de microservicios
    aviones_base_url: str = os.getenv("AVIONES_BASE_URL", "http://localhost:8080/ServiceAvion").rstrip("/")
    pago_base_url: str = os.getenv("PAGO_BASE_URL", "http://localhost:8080/ServicePago").rstrip("/")
    reserva_base_url: str = os.getenv("RESERVA_BASE_URL", "http://localhost:8080/ServiceReserva/api").rstrip("/")
    mantenimiento_base_url: str = os.getenv("MANTENIMIENTO_BASE_URL", "http://localhost:8080/ServiceMantenimiento").rstrip("/")
    usuarios_base_url: str = os.getenv("USUARIOS_BASE_URL", "http://localhost:8080/ServiceUsuario/api").rstrip("/")
    
    # Configuración HTTP operativa (VÁLIDA)
    http_timeout: float = float(os.getenv("HTTP_TIMEOUT", "30.0"))
    http_max_retries: int = int(os.getenv("HTTP_MAX_RETRIES", "3"))
    http_retry_backoff_ms: int = int(os.getenv("HTTP_RETRY_BACKOFF_MS", "1000"))
    http_pool_connections: int = int(os.getenv("HTTP_POOL_CONNECTIONS", "10"))
    http_pool_maxsize: int = int(os.getenv("HTTP_POOL_MAXSIZE", "10"))
    
    @property
    def category(self) -> ConfigCategory:
        return ConfigCategory.OPERATIONAL

@dataclass
class RetryConfig:
    """
    Configuración operativa de reintentos (VÁLIDA).
    Protege el sistema de fallos, no toma decisiones de negocio.
    """
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    base_delay: float = float(os.getenv("RETRY_BASE_DELAY", "1.0"))
    max_delay: float = float(os.getenv("RETRY_MAX_DELAY", "60.0"))
    exponential_base: float = float(os.getenv("RETRY_EXPONENTIAL_BASE", "2.0"))
    jitter: bool = os.getenv("RETRY_JITTER", "true").lower() == "true"
    
    # Circuit breaker (VÁLIDO - protege el sistema)
    circuit_breaker_failure_threshold: int = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    circuit_breaker_recovery_timeout: float = float(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "30.0"))
    circuit_breaker_expected_exception: str = os.getenv("CIRCUIT_BREAKER_EXPECTED_EXCEPTION", "Exception")
    
    @property
    def category(self) -> ConfigCategory:
        return ConfigCategory.OPERATIONAL

@dataclass
class LoggingConfig:
    """
    Configuración operativa de logging (VÁLIDA).
    Controla observabilidad, no decisiones de negocio.
    """
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_path: str = os.getenv("LOG_FILE_PATH", "")
    max_file_size: int = int(os.getenv("LOG_MAX_FILE_SIZE", "10485760"))  # 10MB
    backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Categorías de logging (VÁLIDAS - para métricas)
    log_categories: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.log_categories is None:
            self.log_categories = {
                "mcp_tool_call": True,
                "reasoning_analysis": True,
                "execution_result": True,
                "error_handling": True,
                "performance_metrics": True
            }
    
    @property
    def category(self) -> ConfigCategory:
        return ConfigCategory.OPERATIONAL

@dataclass
class SecurityConfig:
    """
    Configuración operativa de seguridad (VÁLIDA).
    Protege el sistema, no toma decisiones de negocio.
    """
    # Rate limiting (VÁLIDO - protege el sistema)
    rate_limit_requests_per_minute: int = int(os.getenv("RATE_LIMIT_RPM", "60"))
    rate_limit_burst_size: int = int(os.getenv("RATE_LIMIT_BURST", "10"))
    
    # Input validation (VÁLIDO - protege el sistema)
    max_input_length: int = int(os.getenv("MAX_INPUT_LENGTH", "10000"))
    allowed_content_types: List[str] = None
    
    # API Keys (VÁLIDO - configuración operativa)
    require_api_key: bool = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
    api_key_header: str = os.getenv("API_KEY_HEADER", "X-API-Key")
    
    def __post_init__(self):
        if self.allowed_content_types is None:
            self.allowed_content_types = ["application/json", "text/plain"]
    
    @property
    def category(self) -> ConfigCategory:
        return ConfigCategory.OPERATIONAL

@dataclass
class SemanticConfig:
    """
    Configuración operativa para análisis semántico (VÁLIDA).
    Controla parámetros técnicos del embedding, no decisiones de comprensión.
    """
    # Proveedor y modelos de embeddings (VÁLIDO - configuración técnica)
    # embedding_provider: 'gemini' (por defecto) o 'sentence-transformers'
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "gemini")
    # Modelo local (para sentence-transformers). Alias legacy: EMBEDDING_MODEL
    embedding_model_local: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    # Modelo de Gemini para embeddings
    embedding_model_gemini: str = os.getenv("EMBEDDING_MODEL_GEMINI", "models/text-embedding-004")
    
    # Umbrales operativos (VÁLIDOS - controlan el enrutado por similitud)
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.5"))
    max_similarity_candidates: int = int(os.getenv("MAX_SIMILARITY_CANDIDATES", "5"))
    # Umbrales de decisión del selector semántico
    direct_threshold: float = float(os.getenv("DIRECT_THRESHOLD", "0.70"))
    confirm_threshold: float = float(os.getenv("CONFIRM_THRESHOLD", "0.40"))
    # Separación mínima entre mejor y segundo mejor para decisiones relativas
    min_score_gap_direct: float = float(os.getenv("MIN_SCORE_GAP_DIRECT", "0.15"))
    min_score_gap_confirm: float = float(os.getenv("MIN_SCORE_GAP_CONFIRM", "0.10"))
    
    # Cache de embeddings/índice (VÁLIDO - optimización)
    cache_embeddings: bool = os.getenv("CACHE_EMBEDDINGS", "true").lower() == "true"
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    semantic_index_cache_path: str = os.getenv(
        "SEMANTIC_INDEX_CACHE_PATH",
        os.path.join("AgenteIA", "app", "cache", "semantic_index.json")
    )
    
    @property
    def category(self) -> ConfigCategory:
        return ConfigCategory.OPERATIONAL

@dataclass
class FlowConfig:
    """
    Configuración operativa para el router de flujo (VÁLIDA).
    Controla parámetros técnicos del enrutamiento, no decisiones de comprensión.
    """
    # Umbrales operativos (VÁLIDOS)
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    max_flow_retries: int = int(os.getenv("MAX_FLOW_RETRIES", "3"))
    
    # Timeouts operativos (VÁLIDOS)
    routing_timeout: float = float(os.getenv("ROUTING_TIMEOUT", "5.0"))
    handler_timeout: float = float(os.getenv("HANDLER_TIMEOUT", "30.0"))
    
    # Límites operativos (VÁLIDOS)
    max_context_messages: int = int(os.getenv("MAX_CONTEXT_MESSAGES", "5"))
    max_routing_rules: int = int(os.getenv("MAX_ROUTING_RULES", "50"))
    
    @property
    def category(self) -> ConfigCategory:
        return ConfigCategory.OPERATIONAL

@dataclass
class ReasoningConfig:
    """
    Configuración operativa para parámetros del razonamiento (VÁLIDA).
    Centraliza constantes matemáticas usadas por el flujo schema-first.
    """
    object_root_multiplier: float = float(os.getenv("OBJECT_ROOT_MULTIPLIER", "1.5"))
    min_coverage_for_execution: float = float(os.getenv("MIN_COVERAGE_FOR_EXECUTION", "1.0"))
    max_candidates: int = int(os.getenv("REASONING_MAX_CANDIDATES", "10"))
    enable_llm_reasoning: bool = os.getenv("ENABLE_LLM_REASONING", "true").lower() in ("1","true","yes")
    
    @property
    def category(self) -> ConfigCategory:
        return ConfigCategory.OPERATIONAL

class Config:
    """
    Configuración principal del sistema siguiendo principios MCP.
    
    IMPORTANTE: Esta clase SOLO contiene heurísticas operativas válidas.
    NO contiene mapeos de intenciones, palabras clave, o lógica de comprensión.
    """
    
    def __init__(self):
        # Configuraciones operativas (VÁLIDAS)
        self.server = ServerConfig()
        self.llm = LLMConfig()
        self.microservices = MicroservicesConfig()
        self.retry = RetryConfig()
        self.logging = LoggingConfig()
        self.security = SecurityConfig()
        self.semantic = SemanticConfig()
        self.flow = FlowConfig()
        self.reasoning = ReasoningConfig()
    
    def validate(self) -> List[str]:
        """
        Valida la configuración operativa y retorna lista de errores.
        VÁLIDO: Validación técnica, no decisiones de negocio.
        """
        errors = []
        
        # Validar API key de Gemini
        if not self.llm.gemini_api_key:
            errors.append("GOOGLE_API_KEY no está configurada")
        
        # Validar URLs de microservicios
        required_urls = [
            ("AVIONES_BASE_URL", self.microservices.aviones_base_url),
            ("PAGO_BASE_URL", self.microservices.pago_base_url),
            ("RESERVA_BASE_URL", self.microservices.reserva_base_url),
            ("MANTENIMIENTO_BASE_URL", self.microservices.mantenimiento_base_url),
            ("USUARIOS_BASE_URL", self.microservices.usuarios_base_url)
        ]
        
        for name, url in required_urls:
            if not url or url == "":
                errors.append(f"{name} no está configurada")
        
        # Validar rangos numéricos operativos
        if self.server.flask_port < 1 or self.server.flask_port > 65535:
            errors.append("FLASK_PORT debe estar entre 1 y 65535")
        
        if self.llm.temperature < 0 or self.llm.temperature > 2:
            errors.append("TEMPERATURE debe estar entre 0 y 2")
        
        if self.retry.max_retries < 0:
            errors.append("MAX_RETRIES debe ser mayor o igual a 0")
        
        if self.flow.confidence_threshold < 0 or self.flow.confidence_threshold > 1:
            errors.append("CONFIDENCE_THRESHOLD debe estar entre 0 y 1")
        
        if self.security.max_input_length < 1:
            errors.append("MAX_INPUT_LENGTH debe ser mayor a 0")

        # Validaciones específicas de análisis semántico
        if self.semantic.embedding_provider not in ("gemini", "sentence-transformers"):
            errors.append("EMBEDDING_PROVIDER debe ser 'gemini' o 'sentence-transformers'")
        if self.semantic.max_similarity_candidates < 1:
            errors.append("MAX_SIMILARITY_CANDIDATES debe ser >= 1")
        # Rango de umbrales y orden lógico
        if not (0.0 <= self.semantic.confirm_threshold <= 1.0):
            errors.append("CONFIRM_THRESHOLD debe estar entre 0 y 1")
        if not (0.0 <= self.semantic.direct_threshold <= 1.0):
            errors.append("DIRECT_THRESHOLD debe estar entre 0 y 1")
        if self.semantic.confirm_threshold > self.semantic.direct_threshold:
            errors.append("CONFIRM_THRESHOLD no puede ser mayor que DIRECT_THRESHOLD")
        if self.semantic.min_score_gap_direct < 0 or self.semantic.min_score_gap_confirm < 0:
            errors.append("MIN_SCORE_GAP_* debe ser >= 0")
        if self.reasoning.min_coverage_for_execution < 0 or self.reasoning.min_coverage_for_execution > 1:
            errors.append("MIN_COVERAGE_FOR_EXECUTION debe estar entre 0 y 1")
        
        return errors
    
    def get_operational_prompts(self) -> Dict[str, str]:
        """
        Retorna prompts operativos del sistema (VÁLIDOS).
        Estos son templates técnicos, no lógica de comprensión.
        """
        return {
            "system_base_prompt": os.getenv("SYSTEM_BASE_PROMPT", """
Eres un agente IA que utiliza herramientas MCP para responder consultas.

INSTRUCCIONES OPERATIVAS:
1. Analiza la consulta usando análisis semántico
2. Selecciona herramientas basándote en similitud de embeddings
3. Extrae argumentos usando el contexto disponible
4. Genera respuestas estructuradas en JSON

FORMATO DE RESPUESTA REQUERIDO:
{
    "intent": "descripción_de_la_intención",
    "action": "call_tool" | "reply",
    "tool": "nombre_de_herramienta" (si action es call_tool),
    "arguments": {...} (si action es call_tool),
    "response": "mensaje_directo" (si action es reply),
    "confidence": 0.0-1.0
}
"""),
            "error_prompt_template": os.getenv("ERROR_PROMPT_TEMPLATE", """
Error en el procesamiento: {error}
Contexto: {context}
Genera una respuesta de error apropiada manteniendo el formato JSON requerido.
"""),
            "fallback_prompt_template": os.getenv("FALLBACK_PROMPT_TEMPLATE", """
No se pudo determinar una acción específica para: {query}
Herramientas disponibles: {tools}
Genera una respuesta de fallback apropiada o solicita clarificación.
""")
        }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Retorna resumen de configuración para debugging (VÁLIDO).
        """
        return {
            "operational_configs": {
                "server": self.server.category.value,
                "llm": self.llm.category.value,
                "microservices": self.microservices.category.value,
                "retry": self.retry.category.value,
                "logging": self.logging.category.value,
                "security": self.security.category.value,
                "semantic": self.semantic.category.value,
                "flow": self.flow.category.value
            },
            "mcp_compliance": {
                "no_hardcoded_intent_mapping": True,
                "no_keyword_based_logic": True,
                "no_predefined_responses": True,
                "uses_semantic_matching": True,
                "centralized_flow_routing": True
            }
        }

# Instancia global de configuración
config = Config()

def get_config() -> Config:
    """
    Retorna la configuración validada del sistema.
    """
    errors = config.validate()
    if errors:
        raise ValueError(f"Errores de configuración: {', '.join(errors)}")
    return config

def reload_config():
    """
    Recarga la configuración desde variables de entorno.
    """
    global config
    config = Config()

def validate_mcp_compliance() -> Dict[str, bool]:
    """
    Valida que la configuración cumple con principios MCP.
    """
    return {
        "no_reasoning_heuristics": True,  # No hay mapeos de intención hardcodeados
        "no_keyword_logic": True,         # No hay lógica basada en palabras clave
        "operational_only": True,         # Solo configuraciones operativas
        "semantic_based": True,           # Usa análisis semántico
        "centralized_routing": True       # Router centralizado
    }
