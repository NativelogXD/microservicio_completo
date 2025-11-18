"""
SemanticRegistry - Catálogo Dinámico de Herramientas MCP

Sistema de registro semántico que:
1. Mantiene catálogo dinámico de herramientas disponibles
2. Usa similitud textual básica para relevancia semántica
3. Selecciona las top 3 herramientas más relevantes
4. Evita heurísticas y mapeos hardcodeados
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import re
import numpy as np

# Opcional: embeddings ligeros con sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    _HAS_EMBEDDINGS = True
except Exception:
    SentenceTransformer = None  # type: ignore
    _HAS_EMBEDDINGS = False


@dataclass
class ToolDefinition:
    """
    Definición completa de una herramienta MCP.
    
    Attributes:
        name: Nombre único de la herramienta
        description: Descripción detallada de funcionalidad
        example: Ejemplo de uso típico
        parameters: Esquema de parámetros requeridos
        category: Categoría funcional (opcional)
        text_content: Contenido textual para similitud
        usage_count: Contador de uso para métricas
        last_used: Timestamp del último uso
    """
    name: str
    description: str
    example: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    category: Optional[str] = None
    text_content: Optional[str] = None
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la definición a diccionario para el LLM."""
        return {
            "name": self.name,
            "description": self.description,
            "example": self.example,
            "parameters": self.parameters,
            "category": self.category
        }


class SemanticRegistry:
    """
    Registro semántico de herramientas MCP.
    
    Utiliza TF-IDF y similitud coseno para encontrar
    herramientas semánticamente relevantes sin dependencias pesadas.
    """
    
    def __init__(
        self,
        max_tools_in_context: int = 3,
        similarity_threshold: float = 0.15,  # Umbral mínimo
        use_embeddings: bool = True,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Inicializa el registro semántico.
        
        Args:
            max_tools_in_context: Máximo de herramientas en contexto LLM
            similarity_threshold: Umbral mínimo de similitud
        """
        self.max_tools_in_context = max_tools_in_context
        self.similarity_threshold = similarity_threshold
        
        # Inicializar vectorizador TF-IDF
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2),
            lowercase=True
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("SemanticRegistry inicializado (TF-IDF como fallback)")
        
        # Inicializar embeddings opcionales
        self.use_embeddings = bool(use_embeddings) and _HAS_EMBEDDINGS
        self.embedder = None
        if self.use_embeddings:
            try:
                # Nota: nombre del modelo puede variar según distribución
                self.embedder = SentenceTransformer(embedding_model_name)
                self.logger.info(f"Embeddings habilitados con modelo: {embedding_model_name}")
            except Exception as e:
                self.logger.warning(f"No se pudo cargar el modelo de embeddings: {e}. Usando TF-IDF.")
                self.use_embeddings = False
        
        # Registro de herramientas
        self.tools: Dict[str, ToolDefinition] = {}
        self._tool_texts: List[str] = []
        self._tool_names: List[str] = []
        self._tfidf_matrix = None
        self._embedding_matrix: Optional[np.ndarray] = None

    def register_tool(
        self,
        name: str,
        description: str,
        example: str,
        parameters: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None
    ) -> bool:
        """
        Registra una nueva herramienta en el catálogo.
        
        Args:
            name: Nombre único de la herramienta
            description: Descripción detallada
            example: Ejemplo de uso
            parameters: Esquema de parámetros
            category: Categoría funcional
            
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            # Crear contenido textual enriquecido para similitud semántica mejorada
            tool_text = f"{name} {description} {example}"
            if category:
                tool_text += f" {category}"
            
            # Agregar información de parámetros para mejorar la coincidencia semántica
            try:
                params = parameters or {}
                req = params.get("required", []) or []
                props = params.get("properties", {}) or {}
                
                # Agregar nombres de parámetros importantes al texto para mejor contexto
                param_texts = []
                for param_name in req:
                    if param_name in props:
                        param_info = props[param_name]
                        param_desc = param_info.get("description", "")
                        param_type = param_info.get("type", "")
                        param_texts.append(f"{param_name} {param_desc} {param_type}")
                
                if param_texts:
                    tool_text += f" parametros requeridos: {' '.join(param_texts)}"
                
                # Agregar información sobre la estructura para mejor contexto semántico
                if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
                    root_key = req[0]
                    inner_props = props.get(root_key, {}).get("properties", {}) or {}
                    inner_required = props.get(root_key, {}).get("required", []) or []
                    if inner_required:
                        tool_text += f" campos internos: {' '.join(inner_required)}"
                
                # PROCESO DINÁMICO: Generar contexto semántico basado en el contenido real de la herramienta
                # Sin hardcodeos - utilizar solo la información disponible en la herramienta misma
                
                # Agregar información de contexto basada en los parámetros y estructura real
                if req:
                    # Agregar los nombres de parámetros para contexto semántico natural
                    param_context = " ".join(req)
                    tool_text += f" contexto_parametros: {param_context}"
                
                # Si hay estructura de objeto interno, agregar esa información
                if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
                    root_key = req[0]
                    inner_props = props.get(root_key, {}).get("properties", {}) or {}
                    inner_required = props.get(root_key, {}).get("required", []) or []
                    if inner_required:
                        inner_context = " ".join(inner_required)
                        tool_text += f" estructura_interna: {inner_context}"
                        
            except Exception as param_e:
                # Si hay error al procesar parámetros, continuar con el texto básico
                self.logger.debug(f"Error al procesar parámetros para texto enriquecido: {param_e}")
                # Fallback: agregar solo los nombres de parámetros requeridos
                if req:
                    tool_text += f" parametros: {' '.join(req)}"
                    keys = (inner.get("required", []) or [])
                else:
                    keys = req
                if keys:
                    tool_text += " " + " ".join(keys)
            except Exception:
                pass
            
            # Crear definición de herramienta
            tool_def = ToolDefinition(
                name=name,
                description=description,
                example=example,
                parameters=parameters or {},
                category=category,
                text_content=tool_text
            )
            
            # Registrar herramienta
            self.tools[name] = tool_def
            self._tool_texts.append(tool_text)
            self._tool_names.append(name)
            
            # Regenerar matrices de similitud
            self._rebuild_tfidf_matrix()
            self._rebuild_embedding_matrix()
            
            self.logger.info(f"Herramienta '{name}' registrada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registrando herramienta '{name}': {str(e)}")
            return False

    def _rebuild_tfidf_matrix(self):
        """Reconstruye la matriz TF-IDF con todas las herramientas."""
        if self._tool_texts:
            try:
                self._tfidf_matrix = self.vectorizer.fit_transform(self._tool_texts)
            except Exception as e:
                self.logger.error(f"Error construyendo matriz TF-IDF: {str(e)}")
                self._tfidf_matrix = None

    def _rebuild_embedding_matrix(self):
        """Reconstruye la matriz de embeddings si está habilitada."""
        if not self.use_embeddings or self.embedder is None:
            self._embedding_matrix = None
            return
        try:
            # Genera embeddings para todos los textos de herramientas
            embeddings = self.embedder.encode(self._tool_texts, normalize_embeddings=True)
            # Asegurar tipo ndarray y normalización L2
            if isinstance(embeddings, list):
                embeddings = np.array(embeddings)
            self._embedding_matrix = embeddings
        except Exception as e:
            self.logger.error(f"Error construyendo matriz de embeddings: {e}")
            self._embedding_matrix = None

    def find_relevant_tools(
        self,
        query: str,
        max_results: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[ToolDefinition]:
        """
        Encuentra herramientas semánticamente relevantes para una consulta.
        
        Args:
            query: Consulta del usuario
            max_results: Máximo número de resultados (usa default si None)
            similarity_threshold: Umbral de similitud (usa default si None)
            
        Returns:
            List[ToolDefinition]: Herramientas ordenadas por relevancia que superan el umbral
        """
        if not self.tools:
            self.logger.warning("No hay herramientas registradas")
            return []
        
        # Usar valores por defecto si no se proporcionan
        max_results = max_results or self.max_tools_in_context
        similarity_threshold = similarity_threshold or self.similarity_threshold
        
        try:
            # Calcular similitudes usando embeddings o TF-IDF
            if self.use_embeddings and self._embedding_matrix is not None:
                q_emb = self.embedder.encode([query], normalize_embeddings=True)
                q_vec = q_emb[0]
                similarities = np.dot(self._embedding_matrix, q_vec)
            else:
                if self._tfidf_matrix is None:
                    return []
                query_vector = self.vectorizer.transform([query])
                similarities = cosine_similarity(query_vector, self._tfidf_matrix).flatten()
            
            # Filtrar por umbral y ordenar por similitud
            tool_similarities = [
                (self.tools[self._tool_names[i]], float(similarities[i]))
                for i in range(len(self._tool_names))
                if similarities[i] >= similarity_threshold
            ]
            
            # Ordenar por similitud descendente
            tool_similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Retornar solo las herramientas (sin scores) limitadas por max_results
            return [tool_def for tool_def, _ in tool_similarities[:max_results]]
            
        except Exception as e:
            self.logger.error(f"Error encontrando herramientas relevantes: {e}")
            return []

    def find_top_tools(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> List[ToolDefinition]:
        """
        Obtiene las herramientas top por similitud, ignorando el umbral.
        """
        if not self.tools:
            return []
        max_results = max_results or self.max_tools_in_context
        try:
            if self.use_embeddings and self._embedding_matrix is not None:
                q_emb = self.embedder.encode([query], normalize_embeddings=True)
                q_vec = q_emb[0]
                similarities = np.dot(self._embedding_matrix, q_vec)
            else:
                if self._tfidf_matrix is None:
                    return []
                query_vector = self.vectorizer.transform([query])
                similarities = cosine_similarity(query_vector, self._tfidf_matrix).flatten()
            tool_similarities = []
            for i, similarity in enumerate(similarities):
                tool_name = self._tool_names[i]
                tool_def = self.tools[tool_name]
                tool_similarities.append((similarity, tool_def))
            tool_similarities.sort(key=lambda x: x[0], reverse=True)
            return [tool_def for _, tool_def in tool_similarities[:max_results]]
        except Exception:
            return []
        
        max_results = max_results or self.max_tools_in_context
        
        try:
            if self.use_embeddings and self._embedding_matrix is not None:
                # Embeddings: similitud coseno directa sobre vectores normalizados
                q_emb = self.embedder.encode([query], normalize_embeddings=True)
                q_vec = q_emb[0]
                # Similaridad coseno: producto punto porque ambos están normalizados
                similarities = np.dot(self._embedding_matrix, q_vec)
            else:
                if self._tfidf_matrix is None:
                    # Fallback imposible: sin TF-IDF
                    self.logger.warning("Matriz TF-IDF no disponible")
                    return []
                # Vectorizar la consulta con TF-IDF
                query_vector = self.vectorizer.transform([query])
                similarities = cosine_similarity(query_vector, self._tfidf_matrix).flatten()
            
            # Crear lista de (similitud, herramienta)
            tool_similarities = []
            for i, similarity in enumerate(similarities):
                if similarity >= self.similarity_threshold:
                    tool_name = self._tool_names[i]
                    tool_def = self.tools[tool_name]
                    tool_similarities.append((similarity, tool_def))
            
            # Ordenar por similitud descendente
            tool_similarities.sort(key=lambda x: x[0], reverse=True)
            
            # Extraer herramientas y limitar resultados
            result = [tool_def for _, tool_def in tool_similarities[:max_results]]
            
            self.logger.debug(
                f"Encontradas {len(result)} herramientas relevantes para: '{query[:50]}...'"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error buscando herramientas relevantes: {str(e)}")
            return []

    def get_tools_for_llm_context(self, query: str) -> List[Dict[str, Any]]:
        """
        Obtiene herramientas formateadas para contexto del LLM.
        
        Args:
            query: Consulta del usuario
            
        Returns:
            List[Dict]: Herramientas en formato para LLM
        """
        relevant_tools = self.find_relevant_tools(query)
        return [tool.to_dict() for tool in relevant_tools]

    def update_tool_usage(self, tool_name: str) -> None:
        """
        Actualiza estadísticas de uso de una herramienta.
        
        Args:
            tool_name: Nombre de la herramienta usada
        """
        if tool_name in self.tools:
            self.tools[tool_name].usage_count += 1
            self.tools[tool_name].last_used = datetime.now()
            self.logger.debug(f"Actualizado uso de herramienta '{tool_name}'")

    def get_tool_definition(self, tool_name: str) -> Optional[ToolDefinition]:
        """
        Obtiene la definición completa de una herramienta.
        
        Args:
            tool_name: Nombre de la herramienta
            
        Returns:
            ToolDefinition o None si no existe
        """
        return self.tools.get(tool_name)

    def list_all_tools(self) -> List[str]:
        """
        Lista nombres de todas las herramientas registradas.
        
        Returns:
            List[str]: Nombres de herramientas
        """
        return list(self.tools.keys())

    def remove_tool(self, tool_name: str) -> bool:
        """
        Remueve una herramienta del registro.
        
        Args:
            tool_name: Nombre de la herramienta a remover
            
        Returns:
            bool: True si se removió exitosamente
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            # Reconstruir estructuras auxiliares
            if tool_name in self._tool_names:
                index = self._tool_names.index(tool_name)
                del self._tool_names[index]
                del self._tool_texts[index]
                self._rebuild_tfidf_matrix()
            self.logger.info(f"Herramienta '{tool_name}' removida del registro")
            return True
        return False

    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del registro.
        
        Returns:
            Dict con estadísticas del registro
        """
        if not self.tools:
            return {
                "total_tools": 0,
                "categories": [],
                "most_used": None,
                "vectorizer": "TF-IDF",
                "similarity_threshold": self.similarity_threshold,
                "max_context_tools": self.max_tools_in_context
            }
        
        # Calcular estadísticas
        categories = list(set(
            tool.category for tool in self.tools.values() 
            if tool.category
        ))
        
        most_used_tool = max(
            self.tools.values(),
            key=lambda t: t.usage_count,
            default=None
        )
        
        return {
            "total_tools": len(self.tools),
            "categories": categories,
            "most_used": most_used_tool.name if most_used_tool else None,
            "vectorizer": "TF-IDF",
            "similarity_threshold": self.similarity_threshold,
            "max_context_tools": self.max_tools_in_context
        }

    def export_registry(self) -> Dict[str, Any]:
        """
        Exporta el registro completo para persistencia.
        
        Returns:
            Dict con datos del registro
        """
        export_data = {
            "tools": {},
            "config": {
                "vectorizer": "TF-IDF",
                "max_tools_in_context": self.max_tools_in_context,
                "similarity_threshold": self.similarity_threshold
            },
            "exported_at": datetime.now().isoformat()
        }
        
        for name, tool in self.tools.items():
            export_data["tools"][name] = {
                "name": tool.name,
                "description": tool.description,
                "example": tool.example,
                "parameters": tool.parameters,
                "category": tool.category,
                "usage_count": tool.usage_count,
                "last_used": tool.last_used.isoformat() if tool.last_used else None
            }
        
        return export_data

    def load_registry(self, registry_data: Dict[str, Any]) -> bool:
        """
        Carga registro desde datos exportados.
        
        Args:
            registry_data: Datos del registro exportado
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            tools_data = registry_data.get("tools", {})
            
            for tool_name, tool_data in tools_data.items():
                self.register_tool(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    example=tool_data["example"],
                    parameters=tool_data.get("parameters", {}),
                    category=tool_data.get("category")
                )
                
                # Restaurar estadísticas de uso
                if tool_name in self.tools:
                    self.tools[tool_name].usage_count = tool_data.get("usage_count", 0)
                    if tool_data.get("last_used"):
                        self.tools[tool_name].last_used = datetime.fromisoformat(
                            tool_data["last_used"]
                        )
            
            self.logger.info(f"Registro cargado con {len(tools_data)} herramientas")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cargando registro: {str(e)}")
            return False
