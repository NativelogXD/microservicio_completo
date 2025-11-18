"""
Punto de entrada para ejecutar el servidor MCP como módulo.

Uso:
- python -m AgenteIA.app.server                 -> stdio
- python -m AgenteIA.app.server --http          -> SSE en puerto configurado
"""

from .server_mcp import run

if __name__ == "__main__":
    run()