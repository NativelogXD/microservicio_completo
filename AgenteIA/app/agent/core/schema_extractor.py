from typing import Any, Dict, Optional, List
import logging
from ..value_extractor import ValueExtractor
from AgenteIA.app.models.mcp_models import MCPModelMapper

class SchemaExtractor:
    def __init__(self, value_extractor: Optional[ValueExtractor] = None):
        self.value_extractor = value_extractor or ValueExtractor()

    def extract_arguments(self, schema: Dict[str, Any], text: str, tool_name: Optional[str] = None) -> Dict[str, Any]:
        logger = logging.getLogger(__name__)
        if not isinstance(schema, dict) or not text:
            return {}
        logger.info(f"[extraction.start] tool={tool_name} query_length={len(text)}")
        inlined = self._ensure_properties_inlined(schema, tool_name)
        props = inlined.get("properties", {}) or {}
        logger.info(f"[extraction.schema] tool={tool_name} has_properties={bool(props)} properties_count={len(props) if isinstance(props, dict) else 0}")
        meta = self._analyze_schema_structure(inlined)
        logger.info(f"[extraction.structure] tool={tool_name} type={meta.get('structure')} root_key={meta.get('root_key')} total_fields={meta.get('total_fields')}")
        
        # Verificar si hay campos requeridos
        required_fields = meta.get("required_fields", []) or []
        logger.info(f"[extraction.required] tool={tool_name} required_fields={required_fields}")
        
        if meta.get("structure") == "object_root":
            root = meta.get("root_key")
            inner = meta.get("inner_schema") or {}
            args = self._extract_object_root(root, inner, text)
            extracted_count = len((args.get(root, {}) or {})) if isinstance(args.get(root, {}), dict) else 0
            logger.info(f"[extraction.result] tool={tool_name} fields_extracted={extracted_count} structure={args}")
            
            # MODIFICACIÓN: Siempre retornar la estructura para que el sistema pueda identificar campos faltantes
            # incluso si no se extrajeron valores
            return args
        
        args = self._extract_flat_params(inlined, text)
        logger.info(f"[extraction.result] tool={tool_name} fields_extracted={len(args)} structure={args}")
        
        # MODIFICACIÓN: Siempre retornar los args extraídos para análisis de campos faltantes
        return args

    def _ensure_properties_inlined(self, schema: Dict[str, Any], tool_name: Optional[str]) -> Dict[str, Any]:
        req = schema.get("required", []) or []
        props = schema.get("properties", {}) or {}
        if req and not props:
            # PROCESO DINÁMICO: Intentar obtener modelo basado en el nombre de la herramienta sin hardcodear palabras clave
            if tool_name:
                model_cls = MCPModelMapper.get_create_model(tool_name)
                if model_cls:
                    js = model_cls.model_json_schema() or {}
                    schema["properties"] = js.get("properties", {}) or {}
                    if not schema.get("required"):
                        schema["required"] = js.get("required", []) or []
            props = schema.get("properties", {}) or {}
        # Manejar objeto raíz con $ref o sin 'properties' expandidas
        if len(req) == 1 and isinstance(props.get(req[0], {}), dict):
            root = req[0]
            inner = props.get(root, {}) or {}
            inner_required = inner.get("required", []) or []
            inner_props = inner.get("properties", {}) or {}
            root_type = inner.get("type")
            # PROCESO DINÁMICO: Intentar obtener modelo sin depender de palabras clave hardcodeadas
            if tool_name:
                model_cls = MCPModelMapper.get_create_model(tool_name)
                if model_cls:
                    js = model_cls.model_json_schema() or {}
                    if (root_type != "object") or (not inner_props) or (inner.get("$ref")) or (inner.get("anyOf")):
                        inner = {
                            "type": "object",
                            "properties": js.get("properties", {}) or {},
                            "required": js.get("required", []) or [],
                        }
                    else:
                        if not inner_required:
                            inner["required"] = js.get("required", []) or []
                        if not inner_props:
                            inner["properties"] = js.get("properties", {}) or {}
                schema.setdefault("properties", {})[root] = inner
                props = schema.get("properties", {}) or {}
        # Caso: esquema plano con propiedad que es objeto referenciado ($ref)
        if props:
            for k, pdef in list(props.items()):
                if isinstance(pdef, dict) and (pdef.get("$ref") or (not pdef.get("type") and pdef.get("properties") is None)):
                    model_cls = MCPModelMapper.get_create_model(tool_name) if tool_name else MCPModelMapper.resolve_model_by_schema(schema)
                    if model_cls:
                        js = model_cls.model_json_schema() or {}
                        props[k] = {
                            "type": "object",
                            "properties": js.get("properties", {}) or {},
                            "required": js.get("required", []) or [],
                        }
            schema["properties"] = props
            # PROCESO DINÁMICO: Intentar obtener modelo sin hardcodear palabras clave
            if tool_name and (not schema.get("required")):
                model_cls = MCPModelMapper.get_create_model(tool_name)
                if model_cls:
                    js = model_cls.model_json_schema() or {}
                    schema["required"] = js.get("required", []) or []
        return schema

    def _analyze_schema_structure(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        req = schema.get("required", []) or []
        props = schema.get("properties", {}) or {}
        if len(req) == 1 and isinstance(props.get(req[0], {}), dict) and props.get(req[0], {}).get("type") == "object":
            root = req[0]
            inner = props.get(root, {})
            inner_props = inner.get("properties", {}) or {}
            inner_required = inner.get("required", []) or []
            total = max(len(inner_required), len(inner_props)) if (inner_required or inner_props) else 0
            return {"structure": "object_root", "root_key": root, "inner_schema": inner, "total_fields": total, "required_fields": inner_required}
        total = max(len(req), len(props)) if (req or props) else 0
        return {"structure": "flat", "root_key": None, "inner_schema": None, "total_fields": total, "required_fields": req}

    def _extract_object_root(self, root_key: str, inner_schema: Dict[str, Any], text: str) -> Dict[str, Any]:
        logger = logging.getLogger(__name__)
        inner_props = inner_schema.get("properties", {}) or {}
        out: Dict[str, Any] = {}
        for k in sorted(inner_props.keys()):
            tp = (inner_props.get(k, {}) or {}).get("type")
            val = self.value_extractor.extract_value(text, k, {"type": tp or "string", **(inner_props.get(k, {}) or {})})
            logger.info(f"[extraction.field] tool={root_key} field={k} type={(tp or 'string')} value_found={val is not None}")
            if val is not None:
                out[k] = val
        if out:
            return {root_key: out}
        return {}

    def extract_arguments_with_context(self, schema: Dict[str, Any], text: str, conversation_history: Optional[List[Dict[str, Any]]] = None, tool_name: Optional[str] = None) -> Dict[str, Any]:
        inlined = self._ensure_properties_inlined(schema, tool_name)
        meta = self._analyze_schema_structure(inlined)
        if meta.get("structure") == "object_root":
            root = meta.get("root_key")
            inner = meta.get("inner_schema") or {}
            props = inner.get("properties", {}) or {}
            out: Dict[str, Any] = {}
            for k in sorted(props.keys()):
                val = self.value_extractor.extract_with_context(text, k, props.get(k, {}) or {}, conversation_history)
                if val is not None:
                    out[k] = val
            return {root: out} if out else {}
        props = inlined.get("properties", {}) or {}
        out: Dict[str, Any] = {}
        for k in sorted(props.keys()):
            val = self.value_extractor.extract_with_context(text, k, props.get(k, {}) or {}, conversation_history)
            if val is not None:
                out[k] = val
        return out

    def _extract_flat_params(self, schema: Dict[str, Any], text: str) -> Dict[str, Any]:
        logger = logging.getLogger(__name__)
        props = schema.get("properties", {}) or {}
        out: Dict[str, Any] = {}
        for k in sorted(props.keys()):
            pdef = (props.get(k, {}) or {})
            tp = pdef.get("type")
            if not tp and (isinstance(pdef.get("properties"), dict) or pdef.get("$ref")):
                tp = "object"
            val = self.value_extractor.extract_value(text, k, {"type": tp or "string", **pdef})
            logger.info(f"[extraction.field] tool=root field={k} type={(tp or 'string')} value_found={val is not None}")
            if val is not None:
                out[k] = val
        return out
