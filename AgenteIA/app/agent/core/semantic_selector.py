"""
SemanticSelector - Capa de selección semántica con embeddings Gemini

Responsable de:
- Construir y mantener un índice de embeddings de herramientas MCP
- Rankear herramientas por similitud coseno frente a la consulta
- Decidir la ruta de acción: 'direct', 'confirm' o 'conversation' según umbrales
- Proveer metadatos de trazabilidad para auditoría

Implementación usando google.generativeai para generar embeddings
(modelo por defecto: models/text-embedding-004).
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import google.generativeai as genai
# Compatibilidad con el nuevo cliente google-genai 1.x si está disponible
try:
    from google import genai as genai_v1  # type: ignore
except Exception:  # pragma: no cover
    genai_v1 = None

from ..registry.semantic_registry import SemanticRegistry, ToolDefinition
from AgenteIA.app.config.config import get_config


@dataclass
class RankedTool:
    name: str
    score: float
    tool: ToolDefinition


class SemanticSelector:
    """
    Selector semántico basado en embeddings Gemini.

    Decisión:
    - direct: score >= direct_threshold
    - confirm: confirm_threshold <= score < direct_threshold
    - conversation: score < confirm_threshold
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        embedding_model: Optional[str] = None,
        direct_threshold: Optional[float] = None,
        confirm_threshold: Optional[float] = None,
        max_candidates: Optional[int] = None,
        cache_path: Optional[str] = None,
    ):
        cfg = get_config()
        self.logger = logging.getLogger(__name__)

        # Config por defecto desde SemanticConfig
        self.api_key = api_key or cfg.llm.gemini_api_key
        # Preferir configuración centralizada sobre variables de entorno
        default_embed_model = cfg.semantic.embedding_model_gemini
        self.embedding_model = embedding_model or default_embed_model
        self.direct_threshold = (
            direct_threshold if direct_threshold is not None else cfg.semantic.direct_threshold
        )
        self.confirm_threshold = (
            confirm_threshold if confirm_threshold is not None else cfg.semantic.confirm_threshold
        )
        self.max_candidates = (
            max_candidates if max_candidates is not None else cfg.semantic.max_similarity_candidates
        )
        self.cache_path = cache_path or cfg.semantic.semantic_index_cache_path

        # Estado interno
        self._tool_embeddings: Dict[str, List[float]] = {}
        self._tool_texts: Dict[str, str] = {}
        self._initialized = False

        # Configurar cliente
        self._embeddings_enabled = False
        try:
            genai.configure(api_key=self.api_key)
            self._initialized = True
            if self.api_key and self.embedding_model:
                self._embeddings_enabled = True
        except Exception as e:
            self.logger.error(f"No se pudo inicializar cliente de embeddings Gemini: {e}")
            self._initialized = False
            self._embeddings_enabled = False

        # Cliente alternativo (google-genai 1.x), si está disponible
        self._genai_client = None
        if genai_v1 is not None and self.api_key:
            try:
                self._genai_client = genai_v1.Client(api_key=self.api_key)
            except Exception as e:
                # No es crítico; sólo mejora compatibilidad
                self.logger.warning(f"No se pudo inicializar google-genai Client v1: {e}")

        # Intentar cargar cache
        self._load_cache()

    def _load_cache(self) -> None:
        try:
            if self.cache_path and os.path.exists(self.cache_path):
                self.logger.info(f"[semantic.index.build] Intentando cargar cache desde: {self.cache_path}")
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.logger.debug(f"[semantic.index.build] Contenido del cache leído: {len(content)} caracteres")
                    # Intentar parsear el JSON primero para verificar validez
                    try:
                        data = json.loads(content)
                        self._tool_embeddings = data.get("embeddings", {})
                        self._tool_texts = data.get("texts", {})
                        self.logger.info(f"[semantic.index.build] Cache de índice cargada exitosamente: {len(self._tool_embeddings)} herramientas")
                    except json.JSONDecodeError as json_error:
                        self.logger.error(f"[semantic.index.build] Error de JSON en cache: {json_error}")
                        self.logger.error(f"[semantic.index.build] Posición del error: línea {json_error.lineno}, columna {json_error.colno}")
                        # Si el JSON está corrupto, intentar recuperar parcialmente
                        try:
                            # Intentar reparar el JSON
                            repaired_content = content.replace('\n', ' ').replace('\r', ' ')
                            data = json.loads(repaired_content)
                            self._tool_embeddings = data.get("embeddings", {})
                            self._tool_texts = data.get("texts", {})
                            self.logger.warning(f"[semantic.index.build] Cache recuperada parcialmente: {len(self._tool_embeddings)} herramientas")
                        except Exception as repair_error:
                            self.logger.error(f"[semantic.index.build] No se pudo reparar el cache: {repair_error}")
                            # Inicializar con valores vacíos
                            self._tool_embeddings = {}
                            self._tool_texts = {}
                            self.logger.warning("[semantic.index.build] Cache ignorada, usando índice vacío")
        except Exception as e:
            self.logger.error(f"[semantic.index.build] Error crítico al cargar cache: {e}")
            self._tool_embeddings = {}
            self._tool_texts = {}
            # No fallar el inicio del sistema por cache corrupto
            self.logger.warning("[semantic.index.build] Continuando sin cache debido a error crítico")

    def _save_cache(self) -> None:
        try:
            if not self.cache_path:
                return
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump({"embeddings": self._tool_embeddings, "texts": self._tool_texts}, f)
            self.logger.debug("[semantic.index.build] Cache de índice guardada")
        except Exception as e:
            self.logger.warning(f"No se pudo guardar cache de índice semántico: {e}")

    def _populate_texts_from_registry(self, registry: SemanticRegistry) -> None:
        try:
            if not registry or not getattr(registry, "tools", None):
                return
            for name, tool in registry.tools.items():
                text = getattr(tool, "text_content", None) or f"{tool.description} {getattr(tool, 'example', '')} {getattr(tool, 'category', '')}"
                self._tool_texts[name] = text
        except Exception:
            pass

    def _embed_text(self, text: str, is_query: bool = False) -> Optional[List[float]]:
        """Genera embedding para texto usando Gemini (con compatibilidad para ambas librerías)."""
        if not self._initialized:
            # Aun así intentamos con cliente v1 si existe
            if self._genai_client is None:
                return None
        # task_type recomendado: RETRIEVAL_QUERY para consulta, RETRIEVAL_DOCUMENT para documentos
        task_type = "RETRIEVAL_QUERY" if is_query else "RETRIEVAL_DOCUMENT"

        # 1) Intento con google-generativeai (0.8.x)
        try:
            res = genai.embed_content(model=self.embedding_model, content=text, task_type=task_type)
            # Posibles formas de respuesta:
            # - {"embedding": {"values": [...]}}
            # - objeto con atributo .embedding.values
            # - {"values": [...]} (algunos casos)
            if isinstance(res, dict):
                if "embedding" in res and isinstance(res["embedding"], dict):
                    values = res["embedding"].get("values") or res["embedding"].get("value")
                    if isinstance(values, list):
                        return values
                # Algunas variantes devuelven directamente una lista en la clave values
                if "values" in res and isinstance(res["values"], list):
                    return res["values"]
                # O un listado de embeddings
                if "embeddings" in res and isinstance(res["embeddings"], list) and res["embeddings"]:
                    first = res["embeddings"][0]
                    if isinstance(first, dict) and isinstance(first.get("values"), list):
                        return first.get("values")
            # Atributo .embedding.values
            if hasattr(res, "embedding"):
                emb_obj = getattr(res, "embedding")
                if hasattr(emb_obj, "values"):
                    try:
                        return list(getattr(emb_obj, "values"))
                    except Exception:
                        pass
            # Diccionario indexado
            try:
                return res["embedding"]["values"]  # type: ignore[index]
            except Exception:
                pass
        except Exception as e:
            # No abortamos aún; probamos con cliente v1
            self.logger.debug(f"Fallback a google-genai v1 tras error embed_content v0.8.x: {e}")

        # 2) Intento con google-genai (1.x), si tenemos cliente
        if self._genai_client is not None:
            try:
                # API google-genai 1.x expone embed_content bajo client.models y usa 'contents' en lugar de 'content'
                # Además, el parámetro de configuración va en 'config'
                try:
                    from google.genai.types import EmbedContentConfig  # type: ignore
                    cfg_obj = EmbedContentConfig(task_type=task_type)
                except Exception:
                    cfg_obj = None
                resp = self._genai_client.models.embed_content(
                    model=self.embedding_model,
                    contents=[text],
                    config=cfg_obj,
                )
                # Posibles formas:
                # - resp.embedding.values
                # - resp.embeddings[0].values
                if hasattr(resp, "embedding") and hasattr(resp.embedding, "values"):
                    try:
                        return list(resp.embedding.values)  # type: ignore[attr-defined]
                    except Exception:
                        pass
                if hasattr(resp, "embeddings") and isinstance(resp.embeddings, list) and resp.embeddings:
                    first = resp.embeddings[0]
                    if hasattr(first, "values"):
                        try:
                            return list(first.values)
                        except Exception:
                            pass
                # Si fuera dict
                if isinstance(resp, dict):
                    if "embedding" in resp and isinstance(resp["embedding"], dict):
                        values = resp["embedding"].get("values")
                        if isinstance(values, list):
                            return values
                    if "embeddings" in resp and isinstance(resp["embeddings"], list) and resp["embeddings"]:
                        first = resp["embeddings"][0]
                        if isinstance(first, dict) and isinstance(first.get("values"), list):
                            return first.get("values")
            except Exception as e:
                self.logger.error(f"Error generando embedding (cliente v1): {e}")
                return None

        # Si llegamos aquí, no pudimos parsear la respuesta
        try:
            # Registrar tipo para diagnóstico
            rtype = None
            try:
                rtype = type(res).__name__  # type: ignore[name-defined]
            except Exception:
                pass
            self.logger.warning(f"Formato inesperado de respuesta de embed_content (tipo={rtype})")
        except Exception:
            # evitar cualquier error en logging
            pass
        return None

    def build_index(self, registry: SemanticRegistry) -> int:
        """
        Construye/actualiza el índice de embeddings para las herramientas del registro.
        Retorna el número de herramientas indexadas.
        """
        if not registry or not registry.tools:
            return 0
        updated = 0
        for name, tool in registry.tools.items():
            text = getattr(tool, "text_content", None) or f"{tool.description} {getattr(tool, 'example', '')} {getattr(tool, 'category', '')}"
            # Si el texto cambió o no hay embedding, re-generar
            if (name not in self._tool_embeddings) or (self._tool_texts.get(name) != text):
                emb = self._embed_text(text, is_query=False)
                if emb:
                    self._tool_embeddings[name] = emb
                    self._tool_texts[name] = text
                    updated += 1
        if updated:
            self._save_cache()
        self.logger.info(f"[semantic.index.build] Índice actualizado. Nuevas/actualizadas: {updated}, total: {len(self._tool_embeddings)}")
        return len(self._tool_embeddings)

    def rank_tools(self, query: str, registry: SemanticRegistry, top_k: Optional[int] = None) -> List[RankedTool]:
        """Rankea herramientas por similitud coseno con la consulta."""
        if not query or not registry or not registry.tools:
            return []
        if not self._initialized:
            return self.rank_tools_with_fallback(query, registry, top_k=top_k)
        # Asegurar índice
        self.build_index(registry)
        q_emb = self._embed_text(query, is_query=True)
        if not q_emb:
            return self.rank_tools_with_fallback(query, registry, top_k=top_k)
        q = np.array(q_emb, dtype=np.float32)
        # Verificación de dimensiones y reconstrucción si el cache está desalineado
        try:
            q_dim = int(q.shape[0])
            mismatch = False
            for name, emb in list(self._tool_embeddings.items()):
                try:
                    if len(emb) != q_dim:
                        mismatch = True
                        break
                except Exception:
                    mismatch = True
                    break
            if mismatch:
                self.logger.warning("[semantic.index.build] Dimensiones de embeddings en cache no coinciden con el modelo actual; reconstruyendo índice")
                self._tool_embeddings = {}
                self._tool_texts = {}
                self._populate_texts_from_registry(registry)
                self.build_index(registry)
                if not self._tool_embeddings and self._tool_texts:
                    self._save_cache()
        except Exception:
            pass
        # Normalizar L2
        q_norm = q / (np.linalg.norm(q) + 1e-12)
        # Similaridad por producto punto con embeddings normalizados
        ranked: List[RankedTool] = []
        for name, emb in self._tool_embeddings.items():
            v = np.array(emb, dtype=np.float32)
            if v.shape[0] != q.shape[0]:
                # Saltar embeddings con dimensión incorrecta si persisten
                continue
            v_norm = v / (np.linalg.norm(v) + 1e-12)
            score = float(np.dot(q_norm, v_norm))
            tool = registry.get_tool_definition(name)
            if tool:
                ranked.append(RankedTool(name=name, score=score, tool=tool))
        ranked.sort(key=lambda x: x.score, reverse=True)
        limit = top_k or self.max_candidates
        top = ranked[:limit]
        self.logger.info(f"[semantic.search] Top {len(top)} para '{query[:80]}...': " + 
                         ", ".join([f"{rt.name}:{rt.score:.3f}" for rt in top]))
        return top

    def decide(self, ranked: List[RankedTool]) -> Tuple[str, Optional[RankedTool]]:
        """
        Decide la ruta considerando umbrales mínimos y separación relativa.
        Retorna (decision, best_tool).
        """
        if not ranked:
            self.logger.info("[semantic.threshold.decisions] Sin candidatos: conversation")
            return "conversation", None
        best = ranked[0]
        second_score = ranked[1].score if len(ranked) > 1 else 0.0
        gap = float(best.score - second_score)
        try:
            self.logger.info(f"[semantic.separation] best={best.score:.3f} second={second_score:.3f} gap={gap:.3f}")
        except Exception:
            pass
        # Guardas mínimas
        if best.score < self.confirm_threshold:
            decision = "conversation"
        else:
            if best.score >= self.direct_threshold and gap >= get_config().semantic.min_score_gap_direct:
                decision = "direct"
            elif best.score >= self.confirm_threshold and gap >= get_config().semantic.min_score_gap_confirm:
                decision = "confirm"
            else:
                decision = "conversation"
        self.logger.info(f"[semantic.threshold.decisions] decision={decision} best={best.name} score={best.score:.3f} thresholds(direct={self.direct_threshold}, confirm={self.confirm_threshold})")
        return decision, best

    def rank_tools_with_fallback(self, query: str, registry: SemanticRegistry, top_k: Optional[int] = None) -> List[RankedTool]:
        r = self.rank_tools(query, registry, top_k=top_k)
        if r:
            return r
        # Fallback a TF-IDF del registro semántico
        try:
            fallback = registry.find_top_tools(query=query, max_results=top_k or self.max_candidates)
            ranked: List[RankedTool] = []
            for td in fallback:
                name = getattr(td, "name", None)
                if not name:
                    continue
                params = getattr(td, "parameters", {}) or {}
                score = 0.3 + self._schema_match_score(params, query)
                ranked.append(RankedTool(name=name, score=score, tool=td))
            return ranked
        except Exception:
            return []

    def _schema_match_score(self, schema: Dict[str, Any], query: str) -> float:
        import re
        if not isinstance(schema, dict):
            return 0.0
        req = schema.get("required", []) or []
        props = schema.get("properties", {}) or {}
        keys: List[str] = []
        if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
            inner = props.get(req[0], {})
            keys = (inner.get("required", []) or [])
        else:
            keys = req
        if not keys:
            return 0.0
        q = query or ""
        hits = 0
        for k in keys:
            pat = rf"(?i)\b{re.escape(k)}\b"
            if re.search(pat, q):
                hits += 1
        frac = hits / max(1, len(keys))
        return min(0.4, frac * 0.4)

    def prepare_llm_tools_context(self, ranked: List[RankedTool]) -> List[Dict[str, Any]]:
        """Convierte RankedTool a dicts consistentes para el contexto del LLM con información semántica enriquecida."""
        result: List[Dict[str, Any]] = []
        for rt in ranked:
            tool = rt.tool
            td: Dict[str, Any]
            if hasattr(tool, "to_dict"):
                td = tool.to_dict()  # Debe incluir name, description, parameters
                if not isinstance(td, dict):
                    td = {
                        "name": getattr(tool, "name", rt.name),
                        "description": getattr(tool, "description", ""),
                        "parameters": getattr(tool, "parameters", {}) or {},
                    }
            else:
                td = {
                    "name": getattr(tool, "name", rt.name),
                    "description": getattr(tool, "description", ""),
                    "parameters": getattr(tool, "parameters", {}) or {},
                }
            
            # Enriquecer el contexto semánticamente sin hardcodear heurísticas
            name = td.get("name", "")
            description = td.get("description", "")
            
            # Analizar la estructura de parámetros para dar contexto al LLM
            params = td.get("parameters", {}) or {}
            properties = params.get("properties", {}) or {}
            required_params = params.get("required", []) or []
            
            # Crear un contexto semántico basado en el nombre, descripción y parámetros
            semantic_context = f"Tool: {name}. Description: {description}"
            
            if properties:
                param_info = []
                for param_name, param_info_dict in properties.items():
                    param_type = param_info_dict.get("type", "unknown")
                    param_desc = param_info_dict.get("description", "")
                    is_required = param_name in required_params
                    param_info.append(f"Parameter '{param_name}' ({param_type}, {'required' if is_required else 'optional'}): {param_desc}")
                
                if param_info:
                    semantic_context += " Parameters: " + "; ".join(param_info)
            
            # Agregar contexto semántico sin hardcodear intenciones específicas
            td["semantic_context"] = semantic_context
            td["preselection_score"] = rt.score
            result.append(td)
        return result

    def rank_tools_with_context(self, query: str, conversation_history: List[Dict], registry, top_k: Optional[int] = None) -> List[RankedTool]:
        if not conversation_history:
            return self.rank_tools(query, registry, top_k)
        recent = [m.get('content','') for m in conversation_history[-3:] if m.get('role') == 'user'][-2:]
        if recent:
            ctx = " ".join(recent)
            enhanced = f"{query} | contexto_previo: {ctx}"
            self.logger.info(f"[semantic.context] enhanced='{enhanced[:80]}'")
            return self.rank_tools(enhanced, registry, top_k)
        return self.rank_tools(query, registry, top_k)
