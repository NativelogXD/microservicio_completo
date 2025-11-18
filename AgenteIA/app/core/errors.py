from typing import Optional
try:
    from fastapi import status
    from fastapi.responses import JSONResponse
except Exception:
    status = type('status', (), {
        'HTTP_400_BAD_REQUEST': 400,
        'HTTP_401_UNAUTHORIZED': 401,
        'HTTP_404_NOT_FOUND': 404,
        'HTTP_500_INTERNAL_SERVER_ERROR': 500,
        'HTTP_504_GATEWAY_TIMEOUT': 504,
    })

    class JSONResponse:  # Fallback mínimo
        def __init__(self, status_code: int, content: dict):
            self.status_code = status_code
            self.content = content


ERROR_DEFINITIONS = {
    "AGT-400-01": {"status": status.HTTP_400_BAD_REQUEST, "message": "The query field is required."},
    "AGT-400-02": {"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid request format or parameters"},
    "AGT-401-01": {"status": status.HTTP_401_UNAUTHORIZED, "message": "Authorization header is required"},
    "AGT-404-01": {"status": status.HTTP_404_NOT_FOUND, "message": "Tool not found in registry"},
    "AGT-500-01": {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "Internal server error. Please try again later."},
    "AGT-500-02": {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "MCP server connection failed"},
    "AGT-504-01": {"status": status.HTTP_504_GATEWAY_TIMEOUT, "message": "Request timeout exceeded"},
}


def error_response(code: str, override_message: Optional[str] = None) -> JSONResponse:
    definition = ERROR_DEFINITIONS.get(code, ERROR_DEFINITIONS["AGT-500-01"])  # type: ignore
    message = override_message or definition["message"]
    return JSONResponse(status_code=definition["status"], content={"error": message, "code": code})