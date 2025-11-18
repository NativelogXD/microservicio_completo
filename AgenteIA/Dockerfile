# 🐳 Dockerfile para MCP Agent - Sistema Completo
FROM python:3.12-slim

# Metadatos del contenedor
LABEL maintainer="MCP Agent Team"
LABEL version="1.0.0"
LABEL description="Sistema de Agente Conversacional Inteligente basado en MCP"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r mcpagent && useradd -r -g mcpagent mcpagent

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY pyproject.toml ./
# Asegurar archivo README para metadatos de build
COPY README.md ./
# Requisitos de dependencias de runtime
COPY requirements.txt ./

# Instalar dependencias del proyecto usando pip
RUN pip install -r requirements.txt && pip install -e .

# Copiar código fuente de la aplicación
COPY . ./

# Crear directorios necesarios
RUN mkdir -p /app/logs /app/data

# Cambiar permisos al usuario no-root
RUN chown -R mcpagent:mcpagent /app
USER mcpagent

# Exponer puertos
EXPOSE 5000 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando por defecto - API Server con Gunicorn/Uvicorn
# Añadimos timeout extendido para evitar worker timeouts durante inicialización
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.api.api:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--keep-alive", "5", "--graceful-timeout", "30"]
