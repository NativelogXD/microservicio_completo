"""
Utilidades generales para normalizar y parsear JSON proveniente de salidas LLM u otras fuentes poco estrictas.

Objetivos:
- Extraer bloques JSON válidos desde texto con ruido (markdown, texto mezclado, etc.)
- Reparar errores comunes (cadenas sin cerrar, llaves desbalanceadas, comas finales)
- Parsear de forma segura y opcionalmente validar contra un esquema simple
- Proveer una API reutilizable por cualquier microservicio (no acoplada al dominio reservas)
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union


def _strip_code_fences(text: str) -> str:
    """Elimina fences de markdown como ```json ... ``` o ``` ... ``` y recorta espacios."""
    t = text.strip()
    # Remover encabezado ```json o ```
    if t.startswith("```json"):
        t = t[7:]
    if t.startswith("```"):
        t = t[3:]
    # Remover cierre ``` al final
    if t.endswith("```"):
        t = t[:-3]
    return t.strip()


def _replace_smart_quotes(text: str) -> str:
    """Reemplaza comillas tipográficas por comillas ASCII para evitar errores JSON."""
    return (
        text
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )


def _remove_bom(text: str) -> str:
    """Elimina BOM si está presente."""
    return text.replace("\ufeff", "")


def extract_json_blocks(text: str) -> List[str]:
    """
    Extrae todos los candidatos de bloques JSON de una cadena. Busca objetos { ... } y arreglos [ ... ].
    Intenta equilibrar llaves/corchetes para cubrir respuestas cortadas.
    """
    t = _strip_code_fences(_remove_bom(_replace_smart_quotes(text)))

    candidates: List[str] = []

    # Patrón simple para bloques que aparentan JSON (objetos o arreglos)
    # Permite texto antes y después, pero intenta capturar el bloque central
    brace_stack: List[int] = []
    start_idx = None
    for i, ch in enumerate(t):
        if ch == '{' or ch == '[':
            if start_idx is None:
                start_idx = i
            brace_stack.append(1)
        elif ch == '}' or ch == ']':
            if brace_stack:
                brace_stack.pop()
                if not brace_stack and start_idx is not None:
                    block = t[start_idx:i+1]
                    candidates.append(block)
                    start_idx = None

    # Si no se detectaron bloques balanceados, intentar heurística por regex para el primer "{" ... "}"
    if not candidates:
        m = re.search(r"\{[\s\S]*\}", t)
        if m:
            candidates.append(m.group(0))
        else:
            # Intentar con arreglos
            m_arr = re.search(r"\[[\s\S]*\]", t)
            if m_arr:
                candidates.append(m_arr.group(0))

    return candidates


def repair_json_string(s: str) -> str:
    """
    Repara problemas comunes de JSON:
    - Cadenas sin cerrar
    - Llaves/corchetes desbalanceados
    - Comas colgantes antes de cierre
    - Comentarios tipo // o /* */
    """
    s = _strip_code_fences(_remove_bom(_replace_smart_quotes(s)))

    # Remover comentarios simples (no estándar JSON)
    s = re.sub(r"//.*", "", s)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)

    # Quitar comas colgantes antes de cierre de objeto/arreglo
    s = re.sub(r",\s*([}\]])", r"\1", s)

    # Reparar cadenas sin cerrar de forma básica: si número de comillas dobles es impar, añadir una al final
    if s.count('"') % 2 != 0:
        s += '"'

    # Balancear llaves y corchetes si faltan cierres
    open_braces = s.count('{')
    close_braces = s.count('}')
    if open_braces > close_braces:
        s += '}' * (open_braces - close_braces)

    open_brackets = s.count('[')
    close_brackets = s.count(']')
    if open_brackets > close_brackets:
        s += ']' * (open_brackets - close_brackets)

    return s.strip()


def extract_first_json(text: str) -> Optional[str]:
    """Devuelve el primer bloque JSON candidato encontrado en el texto, ya reparado heurísticamente."""
    blocks = extract_json_blocks(text)
    if not blocks:
        return None
    # Preferir el bloque que contiene campos comunes de contractos tipo acción
    preferred = None
    for b in blocks:
        if any(k in b for k in ["action", "tool_name", "arguments", "reasoning", "confidence"]):
            preferred = b
            break
    return repair_json_string(preferred or blocks[0])


def safe_parse_json(
    text: Union[str, bytes],
    schema_required_keys: Optional[List[str]] = None,
    return_best_effort: bool = False
) -> Tuple[Optional[Union[Dict[str, Any], List[Any]]], Optional[str]]:
    """
    Parsea de forma segura una respuesta potencialmente ruidosa y devuelve (objeto_json, error_str).

    - Extrae y repara el primer bloque JSON
    - Si falla, intenta cada candidato encontrado
    - Si schema_required_keys se provee, valida que existan como claves de nivel superior (para objetos)
    - Si return_best_effort es True, retorna el JSON parseado aunque falten claves
    """
    try:
        if isinstance(text, bytes):
            text = text.decode("utf-8", errors="ignore")

        # Intentar con el primer candidato preferido
        candidate = extract_first_json(text)
        candidates = extract_json_blocks(text) if candidate is None else [candidate]

        last_error = None
        for raw in candidates:
            repaired = repair_json_string(raw)
            try:
                parsed = json.loads(repaired)
                # Validación por claves requeridas si aplica
                if schema_required_keys and isinstance(parsed, dict):
                    missing = [k for k in schema_required_keys if k not in parsed]
                    if missing:
                        if return_best_effort:
                            return parsed, None
                        else:
                            last_error = f"Faltan claves requeridas: {missing}"
                            continue
                return parsed, None
            except Exception as e:
                last_error = str(e)
                continue

        return None, last_error or "No se pudo extraer ni parsear JSON de la respuesta"
    except Exception as outer:
        return None, f"Error en safe_parse_json: {outer}"


def normalize_llm_output(
    raw_text: str,
    schema_required_keys: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Capa de normalización general: intenta extraer JSON. Si no puede, devuelve un objeto conversacional estándar.
    Este contrato es reutilizable por cualquier microservicio.
    """
    parsed, err = safe_parse_json(raw_text, schema_required_keys=schema_required_keys, return_best_effort=True)
    if err or parsed is None:
        # Fallback conversacional uniforme
        return {
            "action": "conversation",
            "tool_name": None,
            "arguments": {},
            "reasoning": f"Salida no estructurada o JSON inválido. Detalle: {err}",
            "confidence": 0.1,
            "raw": raw_text
        }
    # Si parsed es lista, envolver en un objeto genérico
    if isinstance(parsed, list):
        return {
            "action": "conversation",
            "tool_name": None,
            "arguments": {},
            "reasoning": "La salida del modelo fue una lista; se retorna como contenido.",
            "confidence": 0.3,
            "content": parsed
        }
    # parsed es dict
    return parsed