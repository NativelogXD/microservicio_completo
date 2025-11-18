from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.web.controller.controllerAvion import router
from app.persistence.database.database import create_tables
from datetime import datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler para manejar el ciclo de vida de la aplicación
    - Startup: Crear tablas de base de datos
    - Shutdown: Limpiar recursos si es necesario
    """
    # Startup
    print("🚀 Iniciando Microservicio de Aviones...")
    create_tables()
    print("✅ Tablas de base de datos creadas")
    
    yield  # La aplicación está ejecutándose
    
    # Shutdown (opcional - para limpiar recursos)
    print("🛑 Cerrando Microservicio de Aviones...")


# Crear la aplicación FastAPI con lifespan handler
app = FastAPI(
    title="Microservicio de Aviones 🚀",
    description="API para gestión de aviones",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # Usar el nuevo lifespan handler
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar el router de aviones
app.include_router(router)

@app.get("/")
def root():
    """Endpoint raíz con información básica del microservicio"""
    return {
        "message": "Microservicio de Aviones 🚀",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    """Endpoint de salud para monitoreo"""
    return {"status": "healthy", "service": "aviones"}


# ==================== MANEJO ESTANDAR DE ERRORES ====================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Estandariza el error de validación en 400 con detalles de campos"""
    details = []
    try:
        for err in exc.errors():
            loc = '.'.join([str(x) for x in err.get('loc', [])])
            msg = err.get('msg')
            details.append(f"{loc}: {msg}")
    except Exception:
        details = [str(exc)]

    return JSONResponse(
        status_code=400,
        content={
            "status": 400,
            "code": "VALIDATION_ERROR",
            "message": "Error de validación en la solicitud",
            "details": details,
            "path": str(request.url.path),
            "timestamp": datetime.utcnow().isoformat() + 'Z',
        },
    )
