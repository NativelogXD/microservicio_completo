"""
Extractor de valores basado en tipos sin hardcodeos.

Este módulo proporciona una forma limpia y extensible de extraer valores
de texto natural basándose en el tipo de dato esperado, sin depender de
palabras clave o patrones hardcodeados.
"""

import re
import json
from typing import Any, Dict, List, Optional, Union
from AgenteIA.app.utils.fuzzy_matcher import find_best_match


class ValueCandidate:
    """Representa un candidato a valor extraído con su contexto."""
    
    def __init__(self, value: Any, start_pos: int, end_pos: int, confidence: float = 1.0):
        self.value = value
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "confidence": self.confidence
        }


class ValueExtractor:
    """
    Extractor de valores que funciona por tipo y contexto, no por nombres hardcodeados.
    
    Principios:
    1. Extraer TODOS los valores de un tipo del texto
    2. Desambiguar usando contexto (posición, cercanía con el campo)
    3. No usar palabras clave hardcodeadas
    4. Ser extensible para nuevos tipos
    """
    
    def __init__(self):
        # Mapeo de tipos JSON a métodos extractores
        self.type_extractors = {
            "integer": self._extract_integers,
            "number": self._extract_numbers,
            "string": self._extract_strings,
            "boolean": self._extract_booleans,
            "email": self._extract_emails,
            "date": self._extract_dates,
            "datetime": self._extract_datetimes,
        }
        
        # Valores booleanos naturales (sin hardcodeo de idioma)
        self.boolean_mappings = {
            "true": True, "verdadero": True, "si": True, "sí": True, 
            "yes": True, "1": True, "activo": True, "activa": True,
            "false": False, "falso": False, "no": False, 
            "0": False, "inactivo": False, "inactiva": False
        }
    
    def extract_value(self, text: str, field_name: str, field_schema: Dict[str, Any]) -> Optional[Any]:
        """
        Extrae un valor del texto basándose en el esquema del campo.
        
        Args:
            text: Texto del usuario
            field_name: Nombre del campo (para contexto)
            field_schema: Esquema JSON del campo con tipo y constraints
            
        Returns:
            Valor extraído y convertido al tipo correcto, o None
        """
        if not text or not field_schema:
            return None
        
        # CRÍTICO: Validación para evitar que el texto completo sea usado como valor
        # Si el texto es muy corto y no contiene información específica, retornar None
        if len(text.strip()) < 5:
            return None
        
        # Obtener tipo del esquema
        field_type = field_schema.get("type", "string")
        
        if field_type == "object":
            nested = self._extract_nested_object(field_schema, text)
            return nested if nested else None
        extractor = self.type_extractors.get(field_type, self._extract_strings)
        
        direct = self._extract_near_field(text, field_name, field_schema)
        if direct is not None:
            direct = self._clean_extracted_value(direct, field_schema)
            # Validación estricta de tipo y constraints del esquema
            if not self._validate_type_strict(direct, field_type):
                direct = None
            elif not self._satisfies_constraints(direct, field_schema):
                direct = None
            # CRÍTICO: Validación adicional - no usar el texto completo como valor
            elif isinstance(direct, str) and direct.lower() == text.strip().lower():
                return None
            if direct is not None:
                return direct
        
        candidates = extractor(text)
        
        if not candidates:
            return None
        
        val = self._disambiguate_candidates(candidates, field_name, text, field_schema)
        if val is None and len(candidates) == 1:
            val = candidates[0].value
        if val is not None:
            val = self._clean_extracted_value(val, field_schema)
            # CRÍTICO: Validación final - no usar el texto completo como valor
            if isinstance(val, str) and val.lower() == text.strip().lower():
                return None
        if val is not None and not self._validate_type_strict(val, field_type):
            return None
        return val

    def _clean_extracted_value(self, value: Any, field_schema: Dict[str, Any]) -> Any:
        """
        Limpia el valor extraído SIN usar patrones hardcodeados.
        Deja que el contexto semántico maneje la interpretación.
        """
        try:
            tp = field_schema.get("type", "string")
            if tp in ("string", None):
                s = str(value)
                s = s.strip()
                
                # Limpieza básica de espacios y puntuación al inicio/final, incluyendo cierres de bloque
                s = s.strip(" ,.;:)}]")
                return s
            if tp in ("integer", "number"):
                import re
                m = re.search(r"[-+]?[0-9]*\.?[0-9]+", str(value))
                if m:
                    v = m.group(0)
                    return int(v) if tp == "integer" else float(v)
                return value
            if tp == "boolean":
                s = str(value).strip().lower()
                if s in ("true", "sí", "si", "1"):
                    return True
                if s in ("false", "no", "0"):
                    return False
                return value
            if tp == "array":
                return value if isinstance(value, list) else [value]
            return value
        except Exception:
            return value
    
    def _extract_near_field(self, text: str, field_name: str, field_schema: Dict[str, Any]) -> Optional[Any]:
        """
        Extrae valores basándose en la proximidad al nombre del campo SIN patrones hardcodeados.
        Deja que el contexto semántico y la posición manejen la extracción.
        """
        if not text or not field_name:
            return None
        variations = self._generate_field_variations(field_name)
        def _normalize(s: str) -> str:
            try:
                import unicodedata
                s = unicodedata.normalize('NFD', s)
                s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
            except Exception:
                pass
            return s
        t = _normalize(text)
        tp = field_schema.get("type", "string")
        
        for var in variations:
            try:
                vnorm = _normalize(var)
                if tp == "integer":
                    m = re.search(rf"\b{re.escape(vnorm)}\b\s*[:=]?\s*(-?\d+)", t, re.IGNORECASE)
                    if m:
                        return int(m.group(1))
                elif tp == "number":
                    m = re.search(rf"\b{re.escape(vnorm)}\b\s*[:=]?\s*(-?\d+(?:[.,]\d+)?)", t, re.IGNORECASE)
                    if m:
                        s = m.group(1).replace(',', '.')
                        return float(s)
                elif tp == "boolean":
                    alt = "|".join([re.escape(k) for k in self.boolean_mappings.keys()])
                    m = re.search(rf"\b{re.escape(vnorm)}\b\s*[:=]?\s*\b({alt})\b", t, re.IGNORECASE)
                    if m:
                        k = m.group(1).lower()
                        return self.boolean_mappings.get(k)
                elif tp == "string":
                    m = re.search(rf"\b{re.escape(vnorm)}\b\s*[:=]?\s*([^\n,;]+)", t, re.IGNORECASE)
                    if m:
                        s = m.group(1).strip()
                        if s:
                            return s
                elif tp == "object":
                    return None
                else:
                    m = re.search(rf"\b{re.escape(vnorm)}\b\s*[:=]?\s*([^\n,;]+)", t, re.IGNORECASE)
                    if m:
                        s = m.group(1).strip()
                        if s:
                            return s
                if field_schema.get("format") == "email":
                    m = re.search(rf"\b{re.escape(vnorm)}\b\s*[:=]?\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", t, re.IGNORECASE)
                    if m:
                        return m.group(1)
            except Exception:
                continue
        return None

    def extract_with_context(
        self,
        text: str,
        field_name: str,
        field_schema: Dict[str, Any],
        conversation_history: Optional[List[Dict]] = None
    ) -> Optional[Any]:
        val = self.extract_value(text, field_name, field_schema)
        if val is not None:
            return val
        if conversation_history:
            for m in reversed(conversation_history[-3:]):
                if m.get('role') != 'user':
                    continue
                ctx_val = self.extract_value(str(m.get('content','')), field_name, field_schema)
                if ctx_val is not None:
                    return ctx_val
        return None
    
    def _extract_integers(self, text: str) -> List[ValueCandidate]:
        """Extrae todos los números enteros del texto."""
        candidates = []
        
        # Patrón para números enteros (positivos y negativos)
        pattern = r'-?\d+'
        
        for match in re.finditer(pattern, text):
            number_str = match.group()
            try:
                number = int(number_str)
                # Aceptar enteros grandes (cédulas, teléfonos, IDs); limitar razonablemente
                if -999999999999999 <= number <= 999999999999999:
                    candidates.append(ValueCandidate(
                        value=number,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=1.0
                    ))
            except ValueError:
                continue
        
        return candidates
    
    def _extract_numbers(self, text: str) -> List[ValueCandidate]:
        """Extrae todos los números decimales del texto."""
        candidates = []
        
        # Patrones para números decimales
        patterns = [
            r'-?\d+\.\d+',  # Decimal con punto
            r'-?\d+,\d+',   # Decimal con coma (europeo)
        ]
        
        # Primero buscar decimales
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                number_str = match.group().replace(',', '.')  # Normalizar coma a punto
                try:
                    number = float(number_str)
                    candidates.append(ValueCandidate(
                        value=number,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=1.0
                    ))
                except ValueError:
                    continue
        
        # Si no hay decimales, buscar enteros como números
        if not candidates:
            integers = self._extract_integers(text)
            for candidate in integers:
                candidates.append(ValueCandidate(
                    value=float(candidate.value),
                    start_pos=candidate.start_pos,
                    end_pos=candidate.end_pos,
                    confidence=0.9  # Menor confianza por ser entero
                ))
        
        return candidates
    
    def _extract_strings(self, text: str) -> List[ValueCandidate]:
        """Extrae cadenas de texto entre comillas o palabras significativas."""
        candidates = []
        
        # CRÍTICO: No extraer nada si el texto es muy corto o no contiene información específica
        if len(text.strip()) <= 5:
            return candidates
        
        # Patrones para strings entre comillas
        quote_patterns = [
            r'"([^"]*)"',  # Dobles comillas
            r"'([^']*)'",   # Simples comillas
            r'`([^`]*)`',   # Backticks
        ]
        
        # Extraer strings entre comillas (alta confianza)
        for pattern in quote_patterns:
            for match in re.finditer(pattern, text):
                string_value = match.group(1).strip()
                if string_value and len(string_value) >= 2:  # Mínimo 2 caracteres
                    candidates.append(ValueCandidate(
                        value=string_value,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=1.0
                    ))
        
        # Si no hay strings entre comillas, buscar palabras significativas
        if not candidates:
            # Patrón 1: palabras capitalizadas (nombres propios)
            name_pattern = r'\b[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+(?:\s+[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)*\b'
            for match in re.finditer(name_pattern, text):
                name = match.group()
                # Evitar que el texto completo sea considerado un nombre válido
                if name.lower() != text.lower() and len(name) < len(text):
                    candidates.append(ValueCandidate(
                        value=name,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.7
                    ))
            
            # Patrón 2: secuencias de palabras que podrían ser nombres
            # Buscar grupos de 2-4 palabras (incluyendo letras acentuadas)
            word_sequence_pattern = r'\b[a-záéíóúüñ]+(?:\s+[a-záéíóúüñ]+){1,3}\b'
            for match in re.finditer(word_sequence_pattern, text, re.IGNORECASE):
                sequence = match.group()
                # CRÍTICO: Validaciones estrictas para evitar usar el texto completo
                if (len(sequence) >= 6 and 
                    sequence.lower() not in ['con el', 'de la', 'del usuario', 'con un', 'un usuario', 'una persona'] and
                    sequence.lower() != text.lower() and  # No debe ser el texto completo
                    len(sequence) < len(text) * 0.5):  # MÁS ESTRICTO: Debe ser significativamente más corta que el texto completo (menos del 50%)
                    candidates.append(ValueCandidate(
                        value=sequence,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.5
                    ))
            
            # Patrón 3: buscar específicamente después de "con" o "de" para capturar nombres completos
            # Este patrón busca: "con X Y" o "de X Y Z" (incluyendo letras acentuadas)
            after_preposition_pattern = r'(?:con|de)\s+([a-záéíóúüñ]+(?:\s+[a-záéíóúüñ]+){1,3})(?:\s+(?:y|con|de|para)|[,\n]|$)'
            for match in re.finditer(after_preposition_pattern, text, re.IGNORECASE):
                sequence = match.group(1)
                # CRÍTICO: Validaciones estrictas para evitar usar el texto completo
                if (len(sequence) >= 4 and 
                    sequence.lower() != text.lower() and  # No debe ser el texto completo
                    len(sequence) < len(text) * 0.4):  # MÁS ESTRICTO: Debe ser significativamente más corta que el texto completo (menos del 40%)
                    candidates.append(ValueCandidate(
                        value=sequence,
                        start_pos=match.start(1),
                        end_pos=match.end(1),
                        confidence=0.6
                    ))
        
        return candidates
    
    def _extract_booleans(self, text: str) -> List[ValueCandidate]:
        """Extrae valores booleanos del texto."""
        candidates = []
        text_lower = text.lower()
        
        # Buscar cada mapeo booleano
        for word, value in self.boolean_mappings.items():
            # Buscar palabra completa, no parte de otra palabra
            pattern = r'\b' + re.escape(word) + r'\b'
            for match in re.finditer(pattern, text_lower):
                candidates.append(ValueCandidate(
                    value=value,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9
                ))
        
        return candidates
    
    def _extract_emails(self, text: str) -> List[ValueCandidate]:
        """Extrae direcciones de email del texto."""
        candidates = []
        
        # Patrón básico de email
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        for match in re.finditer(pattern, text):
            email = match.group()
            candidates.append(ValueCandidate(
                value=email,
                start_pos=match.start(),
                end_pos=match.end(),
                confidence=1.0
            ))
        
        return candidates
    
    def _extract_dates(self, text: str) -> List[ValueCandidate]:
        """Extrae fechas del texto."""
        candidates = []
        
        # Patrones comunes de fecha
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY o MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY o MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            for match in re.finditer(pattern, text):
                date_str = match.group()
                candidates.append(ValueCandidate(
                    value=date_str,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9
                ))
        
        return candidates
    
    def _extract_datetimes(self, text: str) -> List[ValueCandidate]:
        """Extrae fechas y horas del texto."""
        candidates = []
        
        # Patrones de datetime
        datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',  # ISO format
            r'\d{2}/\d{2}/\d{4}[T ]\d{2}:\d{2}:\d{2}',  # Con fecha
        ]
        
        for pattern in datetime_patterns:
            for match in re.finditer(pattern, text):
                datetime_str = match.group()
                candidates.append(ValueCandidate(
                    value=datetime_str,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9
                ))
        
        return candidates

    def _extract_nested_object(self, object_schema: Dict[str, Any], text: str) -> Optional[Dict[str, Any]]:
        props = object_schema.get("properties", {}) or {}
        out: Dict[str, Any] = {}
        for k, p in props.items():
            tp = p.get("type", "string")
            val = self.extract_value(text, k, p)
            if val is not None:
                out[k] = val
        return out if out else None

    def _validate_type_strict(self, value: Any, expected_type: str) -> bool:
        mapping = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "number": lambda v: (isinstance(v, int) or isinstance(v, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
        }
        fn = mapping.get(expected_type)
        return fn(value) if fn else True
    
    def _disambiguate_candidates(
        self, 
        candidates: List[ValueCandidate], 
        field_name: str, 
        text: str,
        field_schema: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Desambigua entre múltiples candidatos basándose en contexto.
        
        Estrategias (sin hardcodeos):
        1. Filtrar candidatos que contienen el nombre del campo
        2. Cercanía al nombre del campo en el texto
        3. Mayor confianza
        4. Orden de aparición (primer candidato)
        """
        if not candidates:
            return None
        
        # Si hay restricciones en el esquema, usarlas para filtrar
        filtered_candidates = self._filter_by_constraints(candidates, field_schema)
        if filtered_candidates:
            candidates = filtered_candidates
        
        # Estrategia 1: Filtrar candidatos que contienen el nombre del campo (probablemente incorrectos)
        clean_candidates = []
        for candidate in candidates:
            # Si el candidato contiene el nombre del campo, probablemente es un falso positivo
            if field_name.lower() not in str(candidate.value).lower():
                clean_candidates.append(candidate)
        
        # Si después de filtrar quedan candidatos, usarlos
        if clean_candidates:
            candidates = clean_candidates
        
        # Estrategia 2: Buscar candidatos cerca del nombre del campo
        field_positions = self._find_field_positions(field_name, text)
        
        if field_positions:
            # Calcular distancia de cada candidato al campo
            best_candidate = None
            min_distance = float('inf')
            
            for candidate in candidates:
                for field_pos in field_positions:
                    # Distancia absoluta entre posiciones
                    distance = abs(candidate.start_pos - field_pos)
                    if distance < min_distance:
                        min_distance = distance
                        best_candidate = candidate
            
            if best_candidate and min_distance < 200:
                return best_candidate.value
        else:
            return None
        
        # Estrategia 3: Mayor confianza
        best_confidence = max(c.confidence for c in candidates)
        best_candidates = [c for c in candidates if c.confidence == best_confidence]
        
        if len(best_candidates) == 1:
            return best_candidates[0].value
        
        # Estrategia 4: Primer candidato (orden de aparición)
        return min(candidates, key=lambda c: c.start_pos).value
    
    def _find_field_positions(self, field_name: str, text: str) -> List[int]:
        """Encuentra todas las posiciones donde aparece el nombre del campo."""
        positions = []
        
        # Variaciones del nombre del campo (sin hardcodeos)
        variations = self._generate_field_variations(field_name)
        def _normalize(s: str) -> str:
            try:
                import unicodedata
                s = unicodedata.normalize('NFD', s)
                s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
            except Exception:
                pass
            return s.lower()
        text_lower = _normalize(text)
        
        for variation in variations:
            pattern = r'\b' + re.escape(_normalize(variation)) + r'\b'
            for match in re.finditer(pattern, text_lower):
                positions.append(match.start())
        
        return positions
    
    def _generate_field_variations(self, field_name: str) -> List[str]:
        """Genera variaciones del nombre del campo para búsqueda flexible."""
        variations = [field_name]
        
        # Separar camelCase y snake_case
        import re
        
        # CamelCase: generar solo variantes compuestas para evitar colisiones con partes genéricas
        camel_parts = re.findall(r'[A-Z][a-z]*|[a-z]+', field_name)
        if len(camel_parts) > 1:
            # No agregar partes individuales como "user"/"name" para evitar capturas erróneas
            # Sí agregar variantes compuestas
            variations.append(' '.join(camel_parts))
            variations.append(''.join(camel_parts).lower())
        
        # Snake_case: generar solo variantes compuestas para evitar colisiones con partes genéricas
        snake_parts = field_name.split('_')
        if len(snake_parts) > 1:
            # No agregar partes individuales como "user"/"name" para evitar capturas erróneas
            # Sí agregar variantes compuestas
            variations.append(' '.join(snake_parts))
            variations.append(''.join(snake_parts).lower())
        
        # Eliminar duplicados
        return list(set(variations))
    
    def _filter_by_constraints(
        self, 
        candidates: List[ValueCandidate], 
        field_schema: Dict[str, Any]
    ) -> List[ValueCandidate]:
        """
        Filtra candidatos basándose en restricciones del esquema.
        
        Ejemplos de constraints:
        - enum: valores permitidos
        - minimum/maximum: rangos numéricos
        - minLength/maxLength: longitud de strings
        - pattern: regex para validación
        """
        filtered = []
        
        for candidate in candidates:
            value = candidate.value
            keep = True
            
            # Validar enum
            if "enum" in field_schema:
                allowed_values = field_schema["enum"]
                if value not in allowed_values:
                    keep = False
            
            # Validar rangos numéricos
            if isinstance(value, (int, float)):
                if "minimum" in field_schema and value < field_schema["minimum"]:
                    keep = False
                if "maximum" in field_schema and value > field_schema["maximum"]:
                    keep = False
            
            # Validar longitud de strings
            if isinstance(value, str):
                if "minLength" in field_schema and len(value) < field_schema["minLength"]:
                    keep = False
                if "maxLength" in field_schema and len(value) > field_schema["maxLength"]:
                    keep = False
                
                # Validar pattern regex
                if "pattern" in field_schema:
                    pattern = field_schema["pattern"]
                    if not re.match(pattern, value):
                        keep = False
            
            if keep:
                filtered.append(candidate)
        
        return filtered

    def _satisfies_constraints(self, value: Any, field_schema: Dict[str, Any]) -> bool:
        """
        Verifica si un valor cumple las restricciones declaradas en el esquema.
        Soporta: enum, rangos numéricos (minimum/maximum), longitud (minLength/maxLength), y pattern.
        """
        try:
            # Enum
            if "enum" in field_schema:
                if value not in field_schema["enum"]:
                    return False

            # Rangos numéricos
            if isinstance(value, (int, float)):
                if "minimum" in field_schema and value < field_schema["minimum"]:
                    return False
                if "maximum" in field_schema and value > field_schema["maximum"]:
                    return False

            # Longitud de strings
            if isinstance(value, str):
                if "minLength" in field_schema and len(value) < field_schema["minLength"]:
                    return False
                if "maxLength" in field_schema and len(value) > field_schema["maxLength"]:
                    return False
                if "pattern" in field_schema:
                    pattern = field_schema["pattern"]
                    if not re.match(pattern, value):
                        return False
            return True
        except Exception:
            return True
    
    def add_custom_extractor(self, type_name: str, extractor_func) -> None:
        """
        Agrega un extractor personalizado para un tipo específico.
        
        Args:
            type_name: Nombre del tipo (ej: "phone", "url")
            extractor_func: Función que recibe texto y retorna List[ValueCandidate]
        """
        self.type_extractors[type_name] = extractor_func

    def extract_with_fuzzy_matching(
        self,
        text: str,
        field_name: str,
        field_schema: Dict[str, Any],
        available_options: Optional[List[Dict]] = None
    ) -> Optional[Any]:
        val = self.extract_value(text, field_name, field_schema)
        if val and available_options:
            best = find_best_match(str(val), available_options, key_field="name")
            if best:
                return best.get("name")
        return val
