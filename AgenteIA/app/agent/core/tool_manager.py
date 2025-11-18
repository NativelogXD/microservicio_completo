"""
ToolManager - Ejecutor y Validador de Herramientas MCP

Sistema de gestión de herramientas que:
1. Valida parámetros antes de ejecución
2. Ejecuta herramientas MCP de forma segura
3. Maneja errores y reintentos automáticos
4. Proporciona logging detallado
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
from functools import lru_cache
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import traceback


class ExecutionStatus(Enum):
    """Estados de ejecución de herramientas."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"


@dataclass
class ExecutionResult:
    """
    Resultado de ejecución de una herramienta.
    
    Attributes:
        status: Estado de la ejecución
        result: Resultado de la herramienta (si exitosa)
        error: Mensaje de error (si falló)
        execution_time: Tiempo de ejecución en segundos
        tool_name: Nombre de la herramienta ejecutada
        arguments: Argumentos usados
        retry_count: Número de reintentos realizados
        metadata: Información adicional
    """
    status: ExecutionStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    tool_name: str = ""
    arguments: Dict[str, Any] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.arguments is None:
            self.arguments = {}
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        def _json_safe(value):
            try:
                # Pydantic v2
                if hasattr(value, "model_dump"):
                    return value.model_dump(mode="json")
                # Dataclasses
                from dataclasses import is_dataclass, asdict
                if is_dataclass(value):
                    return asdict(value)
                # Enums
                from enum import Enum as _Enum
                if isinstance(value, _Enum):
                    return value.value
                # List/Tuple
                if isinstance(value, (list, tuple)):
                    return [_json_safe(v) for v in value]
                # Dict
                if isinstance(value, dict):
                    return {k: _json_safe(v) for k, v in value.items()}
                # Tipos básicos o desconocidos
                return value
            except Exception:
                # Fallback a string en caso de tipo no serializable (e.g., SDKs externos)
                return str(value)

        return {
            "status": self.status.value,
            "result": _json_safe(self.result),
            "error": self.error,
            "execution_time": self.execution_time,
            "tool_name": self.tool_name,
            "arguments": _json_safe(self.arguments),
            "retry_count": self.retry_count,
            "metadata": _json_safe(self.metadata),
        }


class ToolManager:
    """
    Gestor de herramientas MCP con validación y ejecución segura.
    
    Proporciona una interfaz unificada para ejecutar herramientas
    con manejo robusto de errores y validación de parámetros.
    """
    
    def __init__(
        self,
        max_retries: int = 2,
        timeout_seconds: int = 30,
        enable_validation: bool = True
    ):
        """
        Inicializa el gestor de herramientas.
        
        Args:
            max_retries: Máximo número de reintentos
            timeout_seconds: Timeout para ejecución de herramientas
            enable_validation: Habilitar validación de parámetros
        """
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.enable_validation = enable_validation
        
        # Registro de herramientas disponibles
        self.registered_tools: Dict[str, Callable] = {}
        self.tool_schemas: Dict[str, Dict[str, Any]] = {}
        
        # Estadísticas de ejecución
        self.execution_stats: Dict[str, Dict[str, Any]] = {}
        
        self.logger = structlog.get_logger(__name__)
        self.logger.info("ToolManager inicializado")

    def register_tool(
        self,
        name: str,
        handler: Callable,
        schema: Optional[Dict[str, Any]] = None,
        description: str = ""
    ) -> bool:
        """
        Registra una nueva herramienta.
        
        Args:
            name: Nombre único de la herramienta
            handler: Función que ejecuta la herramienta
            schema: Esquema de validación de parámetros
            description: Descripción de la herramienta
            
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            self.registered_tools[name] = handler
            
            if schema:
                self.tool_schemas[name] = schema
            
            # Inicializar estadísticas
            self.execution_stats[name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "avg_execution_time": 0.0,
                "last_executed": None,
                "description": description
            }
            
            self.logger.info(f"Herramienta '{name}' registrada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registrando herramienta '{name}': {str(e)}")
            return False

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Ejecuta una herramienta con validación y manejo de errores.
        
        Args:
            tool_name: Nombre de la herramienta a ejecutar
            arguments: Argumentos para la herramienta
            context: Contexto adicional para la ejecución
            
        Returns:
            ExecutionResult: Resultado de la ejecución
        """
        start_time = datetime.now()
        
        # Verificar que la herramienta existe
        if tool_name not in self.registered_tools:
            return ExecutionResult(
                status=ExecutionStatus.NOT_FOUND,
                error=f"Herramienta '{tool_name}' no encontrada",
                tool_name=tool_name,
                arguments=arguments
            )
        
        try:
            schema = self.get_tool_schema(tool_name) or {}
        except Exception:
            schema = {}

        try:
            arguments = self.normalize_arguments(schema, arguments)
        except Exception:
            pass

        # Validar argumentos si está habilitado
        if self.enable_validation:
            validation_error = self._validate_arguments(tool_name, arguments)
            if validation_error:
                return ExecutionResult(
                    status=ExecutionStatus.VALIDATION_ERROR,
                    error=validation_error,
                    tool_name=tool_name,
                    arguments=arguments
                )
        
        # Ejecutar con reintentos
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                self.logger.debug(
                    f"Ejecutando '{tool_name}' (intento {retry_count + 1})"
                )
                
                # Ejecutar herramienta con timeout
                result = await self._execute_with_timeout(
                    tool_name, arguments, context
                )
                
                # Calcular tiempo de ejecución
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Actualizar estadísticas
                self._update_execution_stats(tool_name, True, execution_time)
                
                cleaned_error = None
                cleaned_meta = None
                try:
                    if isinstance(result, dict):
                        if str(result.get("status")).lower() == "error" or result.get("error"):
                            body = result.get("body") or result.get("error")
                            try:
                                if isinstance(body, str):
                                    parsed = json.loads(body)
                                elif isinstance(body, dict):
                                    parsed = body
                                else:
                                    parsed = {"message": str(body)}
                                code = parsed.get("code") or parsed.get("status")
                                msg = parsed.get("message") or "Error en la herramienta"
                                details = parsed.get("details") or []
                                cleaned_error = f"{code}: {msg}"
                                cleaned_meta = {"details": details, "path": parsed.get("path")}
                            except Exception:
                                cleaned_error = str(body or result)
                        elif isinstance(result.get("result"), list) and result.get("result"):
                            first = result["result"][0]
                            if isinstance(first, dict) and first.get("type") == "text":
                                text = str(first.get("text", ""))
                                if "Error executing tool" in text:
                                    cleaned_error = text
                    elif isinstance(result, list) and result:
                        first = result[0]
                        if isinstance(first, dict) and first.get("type") == "text":
                            text = str(first.get("text", ""))
                            if "Error executing tool" in text:
                                cleaned_error = text
                except Exception:
                    pass

                if cleaned_error:
                    self._update_execution_stats(tool_name, False, execution_time)
                    return ExecutionResult(
                        status=ExecutionStatus.ERROR,
                        error=cleaned_error,
                        execution_time=execution_time,
                        tool_name=tool_name,
                        arguments=arguments,
                        retry_count=retry_count,
                        metadata=(cleaned_meta or {})
                    )

                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    result=result,
                    execution_time=execution_time,
                    tool_name=tool_name,
                    arguments=arguments,
                    retry_count=retry_count
                )
                
            except asyncio.TimeoutError:
                last_error = f"Timeout después de {self.timeout_seconds} segundos"
                self.logger.warning(f"Timeout ejecutando '{tool_name}'")
                
                if retry_count >= self.max_retries:
                    execution_time = (datetime.now() - start_time).total_seconds()
                    self._update_execution_stats(tool_name, False, execution_time)
                    
                    return ExecutionResult(
                        status=ExecutionStatus.TIMEOUT,
                        error=last_error,
                        execution_time=execution_time,
                        tool_name=tool_name,
                        arguments=arguments,
                        retry_count=retry_count
                    )
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(
                    f"Error ejecutando '{tool_name}' (intento {retry_count + 1}): {str(e)}"
                )
                
                if retry_count >= self.max_retries:
                    execution_time = (datetime.now() - start_time).total_seconds()
                    self._update_execution_stats(tool_name, False, execution_time)
                    
                    return ExecutionResult(
                        status=ExecutionStatus.ERROR,
                        error=last_error,
                        execution_time=execution_time,
                        tool_name=tool_name,
                        arguments=arguments,
                        retry_count=retry_count,
                        metadata={"traceback": traceback.format_exc()}
                    )
            
            retry_count += 1
            
            # Esperar antes del siguiente intento
            if retry_count <= self.max_retries:
                await asyncio.sleep(0.5 * retry_count)  # Backoff exponencial
        
        # No debería llegar aquí, pero por seguridad
        execution_time = (datetime.now() - start_time).total_seconds()
        return ExecutionResult(
            status=ExecutionStatus.ERROR,
            error=last_error or "Error desconocido",
            execution_time=execution_time,
            tool_name=tool_name,
            arguments=arguments,
            retry_count=retry_count
        )

    async def _execute_with_timeout(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Any:
        """
        Ejecuta herramienta con timeout.
        
        Args:
            tool_name: Nombre de la herramienta
            arguments: Argumentos para la herramienta
            context: Contexto adicional
            
        Returns:
            Any: Resultado de la herramienta
        """
        handler = self.registered_tools[tool_name]
        
        # Preparar argumentos para la función
        call_args = {"arguments": arguments}
        if context:
            call_args["context"] = context
        
        # Ejecutar con timeout
        if asyncio.iscoroutinefunction(handler):
            return await asyncio.wait_for(handler(**call_args), timeout=self.timeout_seconds)
        else:
            # Intentar ejecutar directamente y detectar si devuelve coroutine
            res = handler(**call_args)
            if asyncio.iscoroutine(res) or hasattr(res, "__await"):
                return await asyncio.wait_for(res, timeout=self.timeout_seconds)
            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(loop.run_in_executor(None, lambda: handler(**call_args)), timeout=self.timeout_seconds)

    def _validate_arguments(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Optional[str]:
        """
        Valida argumentos contra el esquema de la herramienta.
        
        Args:
            tool_name: Nombre de la herramienta
            arguments: Argumentos a validar
            
        Returns:
            str o None: Mensaje de error si hay problemas
        """
        if tool_name not in self.tool_schemas:
            return None  # No hay esquema, no validar
        
        schema = self.tool_schemas[tool_name]
        
        try:
            req = schema.get("required", []) or []
            props = schema.get("properties", {}) or {}
            if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
                root = req[0]
                inner = props.get(root, {})
                inner_req = inner.get("required", []) or []
                inner_props = inner.get("properties", {}) or {}
                root_val = arguments.get(root, {}) if isinstance(arguments, dict) else {}
                if not isinstance(root_val, dict):
                    missing = inner_req or []
                    return f"La herramienta '{tool_name}' requiere objeto raíz '{root}' de tipo dict. Faltan: " + ", ".join(missing)
                missing = [f for f in inner_req if f not in root_val]
                if missing:
                    # Incluir tipos esperados para mayor claridad
                    types = []
                    for m in missing:
                        tp = (inner_props.get(m, {}) or {}).get("type") or "string"
                        types.append(f"{m}:{tp}")
                    return f"La herramienta '{tool_name}' requiere los siguientes campos internos: " + ", ".join(types)
                for k, v in root_val.items():
                    if k in inner_props:
                        et = inner_props[k].get("type")
                        if et and not self._validate_type(v, et):
                            return f"Campo '{root}.{k}' debe ser de tipo {et} pero es {type(v).__name__}"
            else:
                missing = [r for r in req if r not in arguments]
                if missing:
                    return f"La herramienta '{tool_name}' requiere los siguientes campos: " + ", ".join(missing) + " (estructura: flat)"
                for k, v in arguments.items():
                    if k in props:
                        et = props[k].get("type")
                        if et and not self._validate_type(v, et):
                            return f"Campo '{k}' debe ser de tipo {et} pero es {type(v).__name__}"
            return None

        except Exception as e:
            return f"Error en validación: {str(e)}"

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """
        Valida el tipo de un valor.
        
        Args:
            value: Valor a validar
            expected_type: Tipo esperado
            
        Returns:
            bool: True si el tipo es correcto
        """
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True  # Tipo desconocido, asumir válido

    def normalize_arguments(self, schema: Dict[str, Any], arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            req = schema.get("required", []) or []
            props = schema.get("properties", {}) or {}
            if len(req) == 1:
                root = req[0]
                root_prop = props.get(root, {})
                if isinstance(root_prop, dict) and root_prop.get("type") == "object":
                    inner_props = (root_prop.get("properties") or {})
                    inner_required = (root_prop.get("required") or [])
                    args = dict(arguments)
                    def key_variants(k: str):
                        import re
                        v = [k, k.lower()]
                        v.append(re.sub(r"[^a-z0-9]", "", k.lower()))
                        camel_split = re.sub(r"([a-z])([A-Z])", r"\1 \2", k).lower()
                        v.append(camel_split)
                        v.append(re.sub(r"\s+", "", camel_split))
                        return list(dict.fromkeys(v))
                    if root not in args:
                        collected = {}
                        flat_lower = {str(kk).lower(): kk for kk in list(args.keys())}
                        for k in inner_required:
                            for kv in key_variants(k):
                                if kv in flat_lower:
                                    orig = flat_lower[kv]
                                    collected[k] = args.get(orig)
                                    break
                        for k in inner_props.keys():
                            if k in collected:
                                continue
                            for kv in key_variants(k):
                                if kv in flat_lower:
                                    orig = flat_lower[kv]
                                    collected[k] = args.get(orig)
                                    break
                        if collected:
                            for k in list(collected.keys()):
                                args.pop(k, None)
                            args[root] = collected
                    return args
            return arguments
        except Exception:
            return arguments

    def _update_execution_stats(
        self,
        tool_name: str,
        success: bool,
        execution_time: float
    ) -> None:
        """
        Actualiza estadísticas de ejecución.
        
        Args:
            tool_name: Nombre de la herramienta
            success: Si la ejecución fue exitosa
            execution_time: Tiempo de ejecución
        """
        if tool_name not in self.execution_stats:
            return
        
        stats = self.execution_stats[tool_name]
        
        stats["total_executions"] += 1
        stats["last_executed"] = datetime.now().isoformat()
        
        if success:
            stats["successful_executions"] += 1
        else:
            stats["failed_executions"] += 1
        
        # Actualizar tiempo promedio
        total_executions = stats["total_executions"]
        current_avg = stats["avg_execution_time"]
        stats["avg_execution_time"] = (
            (current_avg * (total_executions - 1) + execution_time) / total_executions
        )

    def get_available_tools(self) -> List[str]:
        """
        Obtiene lista de herramientas disponibles.
        
        Returns:
            List[str]: Nombres de herramientas registradas
        """
        return list(self.registered_tools.keys())

    @lru_cache(maxsize=50)
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el esquema de una herramienta.
        
        Args:
            tool_name: Nombre de la herramienta
            
        Returns:
            Dict o None: Esquema de la herramienta
        """
        return self.tool_schemas.get(tool_name)

    def get_execution_stats(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de ejecución.
        
        Args:
            tool_name: Herramienta específica (todas si None)
            
        Returns:
            Dict: Estadísticas de ejecución
        """
        if tool_name:
            return self.execution_stats.get(tool_name, {})
        
        return {
            "tools": self.execution_stats,
            "summary": {
                "total_tools": len(self.registered_tools),
                "total_executions": sum(
                    stats["total_executions"] 
                    for stats in self.execution_stats.values()
                ),
                "total_successes": sum(
                    stats["successful_executions"] 
                    for stats in self.execution_stats.values()
                ),
                "total_failures": sum(
                    stats["failed_executions"] 
                    for stats in self.execution_stats.values()
                )
            }
        }

    def unregister_tool(self, tool_name: str) -> bool:
        """
        Desregistra una herramienta.
        
        Args:
            tool_name: Nombre de la herramienta
            
        Returns:
            bool: True si se desregistró exitosamente
        """
        if tool_name in self.registered_tools:
            del self.registered_tools[tool_name]
            
            if tool_name in self.tool_schemas:
                del self.tool_schemas[tool_name]
            
            if tool_name in self.execution_stats:
                del self.execution_stats[tool_name]
            
            self.logger.info(f"Herramienta '{tool_name}' desregistrada")
            return True
        
        return False

    def clear_stats(self, tool_name: Optional[str] = None) -> None:
        """
        Limpia estadísticas de ejecución.
        
        Args:
            tool_name: Herramienta específica (todas si None)
        """
        if tool_name and tool_name in self.execution_stats:
            self.execution_stats[tool_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "avg_execution_time": 0.0,
                "last_executed": None,
                "description": self.execution_stats[tool_name].get("description", "")
            }
        elif not tool_name:
            for name in self.execution_stats:
                self.execution_stats[name] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "failed_executions": 0,
                    "avg_execution_time": 0.0,
                    "last_executed": None,
                    "description": self.execution_stats[name].get("description", "")
                }
        
        self.logger.info(f"Estadísticas limpiadas para {tool_name or 'todas las herramientas'}")
from functools import lru_cache
