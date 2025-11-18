from functools import lru_cache

@lru_cache(maxsize=50)
def cached_tool_schema(tool_name: str, schemas_snapshot: tuple) -> dict:
    return dict(schemas_snapshot[0]).get(tool_name) if schemas_snapshot else None