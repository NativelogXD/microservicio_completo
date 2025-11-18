from typing import Any, Dict, List, Optional
from dataclasses import dataclass

def _convert_schema(mcp_schema: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(mcp_schema, dict):
        return {"type": "object"}
    t = mcp_schema.get("type") or ("object" if mcp_schema.get("properties") else "string")
    out: Dict[str, Any] = {"type": t}
    if "description" in mcp_schema:
        out["description"] = mcp_schema.get("description")
    if "enum" in mcp_schema and isinstance(mcp_schema["enum"], list):
        out["enum"] = list(mcp_schema["enum"])
    props = mcp_schema.get("properties") or {}
    if isinstance(props, dict):
        out_props: Dict[str, Any] = {}
        for k, v in props.items():
            out_props[k] = _convert_schema(v if isinstance(v, dict) else {"type": "string"})
        out["properties"] = out_props
    req = mcp_schema.get("required") or []
    if isinstance(req, list) and req:
        out["required"] = req
    return out

@dataclass
class FunctionDeclaration:
    name: str
    description: str
    parameters: Dict[str, Any]

def convert_mcp_schema_to_gemini(mcp_schema: Dict[str, Any]) -> Dict[str, Any]:
    return _convert_schema(mcp_schema or {"type": "object"})

def convert_mcp_tools_to_gemini(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    decls: List[FunctionDeclaration] = []
    for t in mcp_tools:
        name = t.get("name") or "unnamed_function"
        desc = t.get("description") or ""
        params = t.get("parameters") or {"type": "object"}
        schema = convert_mcp_schema_to_gemini(params)
        decls.append(FunctionDeclaration(name=name, description=desc, parameters=schema))
    return [{"function_declarations": [d.__dict__ for d in decls]}]