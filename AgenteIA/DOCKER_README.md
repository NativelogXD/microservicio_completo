# 🐳 Docker Deployment para MCP Agent

Este directorio contiene la configuración Docker para desplegar el sistema MCP Agent completo con todos sus servicios de soporte.

## 🏗️ Arquitectura del Stack

### Servicios Incluidos

- **🤖 MCP Agent**: Aplicación principal con API Flask y MCP Server
- **🗄️ PostgreSQL**: Base de datos principal para persistencia
- **🔄 Redis**: Cache, sesiones y cola de tareas
- **🌐 Nginx**: Proxy reverso y balanceador de carga (opcional)
- **📊 Prometheus**: Recolección de métricas (opcional)
- **📈 Grafana**: Dashboards y visualización (opcional)

### Puertos Expuestos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| MCP Agent API | 5000 | API REST principal |
| MCP Server | 8000 | Servidor MCP WebSocket |
| PostgreSQL | 5432 | Base de datos |
| Redis | 6379 | Cache y sesiones |
| Nginx | 80/443 | Proxy reverso |
| Prometheus | 9090 | Métricas |
| Grafana | 3000 | Dashboards |

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  MCP Agent  │  │ PostgreSQL  │  │    Redis    │        │
│  │ API + Server│  │  Database   │  │   Cache     │        │
│  │ Port 5000/  │  │  Port 5432  │  │  Port 6379  │        │
│  │      8000   │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Nginx    │  │ Prometheus  │  │   Grafana   │        │
│  │ Reverse     │  │ Monitoring  │  │ Dashboard   │        │
│  │ Proxy       │  │ Port 9090   │  │ Port 3000   │        │
│  │ Port 80/443 │  │ (opcional)  │  │ (opcional)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Inicio Rápido

### 1. Preparación del Entorno

```powershell
# Navegar al directorio del proyecto
cd "C:\ruta\a\tu\proyecto\AgenteIA"

# Verificar que Docker esté ejecutándose
docker --version
docker-compose --version
```

### 2. Configuración de Variables

```powershell
# Editar el archivo .env existente
notepad .env
```

**Variables Esenciales a Configurar:**

```bash
# 🔑 OBLIGATORIO - API Key de Google Gemini
GEMINI_API_KEY=tu_gemini_api_key_aqui

# 🔒 Contraseñas seguras
POSTGRES_PASSWORD=mcp_secure_password_2024
REDIS_PASSWORD=redis_secure_password_2024
GRAFANA_PASSWORD=admin_secure_password_2024

# 🌐 URLs de tus microservicios
MICROSERVICE_AVIONES_URL=http://host.docker.internal:8001
MICROSERVICE_PAGO_URL=http://host.docker.internal:8002
MICROSERVICE_RESERVA_URL=http://host.docker.internal:8003
MICROSERVICE_MANTENIMIENTO_URL=http://host.docker.internal:8004
MICROSERVICE_USUARIOS_URL=http://host.docker.internal:8005
```

### 3. Despliegue con Script Automatizado

**Opción Recomendada - Usar el Script de Inicio:**

```powershell
# Inicio básico (solo agente, PostgreSQL, Redis)
.\start.ps1

# Con proxy Nginx
.\start.ps1 -Profile production

# Con monitoreo completo (Prometheus + Grafana)
.\start.ps1 -Profile monitoring

# Reconstruir imágenes y iniciar
.\start.ps1 -Build

# Ver logs en tiempo real
.\start.ps1 -Logs

# Detener todos los servicios
.\start.ps1 -Stop

# Ver ayuda completa
.\start.ps1 -Help
```

### 4. Despliegue Manual con Docker Compose

**Si prefieres usar Docker Compose directamente:**

```powershell
# Construir la imagen del agente
docker build -t mcp-agent:latest .

# Iniciar servicios básicos
docker-compose up -d mcp-agent postgres redis

# Iniciar con Nginx (producción)
docker-compose --profile production up -d

# Iniciar con monitoreo completo
docker-compose --profile monitoring up -d

# Ver logs
docker-compose logs -f mcp-agent

# Verificar estado
docker-compose ps
```

### 4. Deployment con Monitoreo (Opcional)

```bash
# Levantar con servicios de monitoreo
docker-compose --profile monitoring up -d

# Levantar con proxy de producción
docker-compose --profile production up -d

# Levantar todo (desarrollo completo)
docker-compose --profile monitoring --profile production up -d
```

## 🔧 Scripts de Deployment

### Script de Inicio Automático (Windows)

Crea `start-agente.bat`:

```batch
@echo off
echo Iniciando Agente IA MCP...

REM Verificar si Docker está corriendo
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker no está corriendo. Inicia Docker Desktop primero.
    pause
    exit /b 1
)

REM Verificar si existe el archivo .env
if not exist .env (
    echo ❌ Error: Archivo .env no encontrado
    echo Crea el archivo .env con las variables necesarias antes de continuar.
    pause
    exit /b 1
)

REM Construir y levantar servicios
echo Construyendo y levantando servicios...
docker-compose up -d

REM Mostrar estado
echo.
echo Estado de los servicios:
docker-compose ps

echo.
echo Agente IA disponible en: http://localhost:5000
echo Health check: http://localhost:5000/health
echo.
pause
```

### Script de Inicio Automático (Linux/Mac)

Crea `start-agente.sh`:

```bash
#!/bin/bash

echo "🚀 Iniciando Agente IA MCP..."

# Verificar si Docker está corriendo
if ! docker info >/dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo. Inicia Docker primero."
    exit 1
fi

# Verificar si existe el archivo .env
if [ ! -f .env ]; then
    echo "❌ Error: Archivo .env no encontrado"
    echo "⚠️  Crea el archivo .env con las variables necesarias antes de continuar."
    exit 1
fi

# Construir y levantar servicios
echo "🔨 Construyendo y levantando servicios..."
docker-compose up -d

# Mostrar estado
echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

echo ""
echo "✅ Agente IA disponible en: http://localhost:5000"
echo "🏥 Health check: http://localhost:5000/health"
echo ""
```

Hacer ejecutable:
```bash
chmod +x start-agente.sh
./start-agente.sh
```

## 🔍 Verificación y Testing

### Health Checks

```bash
# Verificar salud del Agente IA
curl http://localhost:5000/health

# Verificar versión
curl http://localhost:5000/version

# Test básico de query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "¿Cuál es el estado del sistema?"}'
```

### Verificación de Servicios

```bash
# Estado de todos los contenedores
docker-compose ps

# Logs específicos
docker-compose logs agente-ia
docker-compose logs postgres
docker-compose logs redis

# Logs en tiempo real
docker-compose logs -f agente-ia
```

### Testing de Base de Datos

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U agenteia -d agenteia_db

# Verificar Redis
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping
```

## 🛠️ Comandos de Mantenimiento

### Gestión de Contenedores

```bash
# Parar todos los servicios
docker-compose down

# Parar y eliminar volúmenes (⚠️ CUIDADO: Elimina datos)
docker-compose down -v

# Reconstruir imágenes
docker-compose build --no-cache

# Reiniciar un servicio específico
docker-compose restart agente-ia

# Escalar servicios (si es necesario)
docker-compose up -d --scale agente-ia=2
```

### Backup y Restauración

```bash
# Backup de PostgreSQL
docker-compose exec postgres pg_dump -U agenteia agenteia_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar PostgreSQL
docker-compose exec -T postgres psql -U agenteia agenteia_db < backup_file.sql

# Backup de volúmenes Docker
docker run --rm -v agenteia_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

### Limpieza del Sistema

```bash
# Limpiar imágenes no utilizadas
docker image prune -f

# Limpiar volúmenes no utilizados
docker volume prune -f

# Limpieza completa del sistema Docker
docker system prune -a --volumes
```

## 📊 Monitoreo y Observabilidad

### Acceso a Servicios de Monitoreo

- **Grafana Dashboard**: http://localhost:3000
  - Usuario: `admin`
  - Contraseña: `${GRAFANA_PASSWORD}`

- **Prometheus Metrics**: http://localhost:9090

- **Nginx Status**: http://localhost/nginx_status (si está configurado)

### Métricas Importantes

```bash
# Métricas del contenedor
docker stats agente-ia-mcp

# Uso de recursos
docker-compose exec agente-ia top

# Logs estructurados
docker-compose logs agente-ia | grep ERROR
docker-compose logs agente-ia | grep WARNING
```

## 🔒 Configuración de Seguridad

### Variables de Entorno Sensibles

```bash
# Generar contraseñas seguras
openssl rand -base64 32  # Para POSTGRES_PASSWORD
openssl rand -base64 32  # Para REDIS_PASSWORD
openssl rand -base64 32  # Para GRAFANA_PASSWORD
```

### Configuración SSL/TLS (Producción)

1. Crear directorio para certificados:
```bash
mkdir -p nginx/ssl
```

2. Generar certificados (desarrollo):
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/agente.key \
  -out nginx/ssl/agente.crt
```

3. Configurar Nginx (crear `nginx/nginx.conf`)

### Firewall y Red

```bash
# Verificar puertos expuestos
docker-compose port agente-ia 5000

# Configurar red personalizada
docker network ls
docker network inspect agenteia_agente-network
```

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# Verificar logs de PostgreSQL
docker-compose logs postgres

# Reiniciar PostgreSQL
docker-compose restart postgres
```

#### 2. Error de API Key de Gemini
```bash
# Verificar variables de entorno
docker-compose exec agente-ia env | grep GEMINI

# Verificar configuración
docker-compose exec agente-ia cat /app/.env
```

#### 3. Problemas de Memoria/Performance
```bash
# Verificar uso de recursos
docker stats

# Ajustar límites en docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
```

#### 4. Problemas de Red
```bash
# Verificar conectividad entre servicios
docker-compose exec agente-ia ping postgres
docker-compose exec agente-ia ping redis

# Verificar DNS interno
docker-compose exec agente-ia nslookup postgres
```

### Logs de Debug

```bash
# Habilitar modo debug
echo "FLASK_DEBUG=true" >> .env
echo "LOG_LEVEL=DEBUG" >> .env
docker-compose restart agente-ia

# Ver logs detallados
docker-compose logs -f agente-ia
```

## 📈 Optimización de Performance

### Configuración de Producción

```yaml
# En docker-compose.yml, agregar:
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.25'
```

### Cache y Redis

```bash
# Verificar estadísticas de Redis
docker-compose exec redis redis-cli -a $REDIS_PASSWORD info stats

# Limpiar cache si es necesario
docker-compose exec redis redis-cli -a $REDIS_PASSWORD flushall
```

### Base de Datos

```bash
# Optimizar PostgreSQL
docker-compose exec postgres psql -U agenteia -d agenteia_db -c "VACUUM ANALYZE;"

# Verificar índices
docker-compose exec postgres psql -U agenteia -d agenteia_db -c "\di"
```

## 🔄 Actualizaciones y Deployment

### Actualización de la Aplicación

```bash
# 1. Hacer backup
./backup.sh

# 2. Parar servicios
docker-compose down

# 3. Actualizar código
git pull origin main

# 4. Reconstruir imagen
docker-compose build agente-ia

# 5. Levantar servicios
docker-compose up -d

# 6. Verificar deployment
curl http://localhost:5000/health
```

### Deployment en Producción

```bash
# Usar perfil de producción
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Con SSL y monitoreo completo
docker-compose --profile production --profile monitoring up -d
```

## 📞 Soporte y Contacto

Para problemas o preguntas:

1. **Verificar logs**: `docker-compose logs -f agente-ia`
2. **Revisar health checks**: `curl http://localhost:5000/health`
3. **Consultar documentación**: Este README y comentarios en el código
4. **Issues del proyecto**: [Crear issue en el repositorio]

---

## 📝 Notas Adicionales

- **Desarrollo**: Usa `docker-compose up` sin `-d` para ver logs en tiempo real
- **Producción**: Siempre usa `-d` y configura monitoreo apropiado
- **Seguridad**: Cambia todas las contraseñas por defecto antes de producción
- **Backup**: Configura backups automáticos para datos críticos
- **Monitoreo**: Usa Grafana y Prometheus para observabilidad completa

¡El Agente IA MCP está listo para funcionar en contenedores! 🚀