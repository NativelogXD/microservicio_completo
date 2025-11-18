from typing import List, Dict, Optional
import logging

try:
    import structlog  # type: ignore
except ImportError:
    class _StructlogShim:
        def get_logger(self, name):
            return logging.getLogger(name)
    structlog = _StructlogShim()  # type: ignore

logger = structlog.get_logger(__name__)


def find_best_match(search_term: str, candidates: List[Dict], key_field: str = "name") -> Optional[Dict]:
    s = (search_term or "").lower().strip()
    if not s:
        return None

    for c in candidates or []:
        if str(c.get(key_field, "")).lower() == s:
            logger.debug("exact_match_found", term=search_term, match=c.get(key_field))
            return c

    for c in candidates or []:
        val = str(c.get(key_field, "")).lower()
        if s in val or val in s:
            logger.debug("substring_match_found", term=search_term, match=c.get(key_field))
            return c

    words = set(s.split())
    best = None
    best_score = 0
    for c in candidates or []:
        val_words = set(str(c.get(key_field, "")).lower().split())
        score = len(words & val_words)
        if score > best_score:
            best_score = score
            best = c
    if best and best_score > 0:
        logger.debug("word_match_found", term=search_term, match=best.get(key_field), score=best_score)
        return best
    return None