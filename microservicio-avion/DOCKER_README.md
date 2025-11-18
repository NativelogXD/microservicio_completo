# 🐳 Dockerización del Microservicio de Aviones

Este documento explica cómo ejecutar el microservicio de aviones usando Docker y Docker Compose.

## 📋 Prerrequisitos

- Docker (versión 20.10 o superior)
- Docker Compose (versión 2.0 o superior)

## 🚀 Ejecución Rápida

### 1. Clonar y navegar al proyecto
```bash
cd microservicio-avion
```

### 2. Ejecutar con Docker Compose
```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d --build
```

### 3. Verificar que todo funciona
```bash
# Verificar el estado de los servicios
docker-compose ps

# Ver logs del microservicio
docker-compose logs aviones-api

# Ver logs de la base de datos
docker-compose logs postgres
```

## 🌐 Acceso a los Servicios

Una vez ejecutados los contenedores, podrás acceder a:

- **API del Microservicio**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **pgAdmin**: http://localhost:5050
  - Email: admin@aviones.com
  - Password: admin123

## 📊 Base de Datos

### Configuración
- **Host**: localhost (desde tu máquina) / postgres (desde contenedores)
- **Puerto**: 5432
- **Base de datos**: aviones_db
- **Usuario**: postgres
- **Password**: postgres123

### Conectar con pgAdmin
1. Ve a http://localhost:5050
2. Inicia sesión con las credenciales mencionadas
3. Agrega un nuevo servidor:
   - Host: postgres
   - Puerto: 5432
   - Usuario: postgres
   - Password: postgres123

## 🛠️ Comandos Útiles

### Gestión de Contenedores
```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (CUIDADO: elimina datos de BD)
docker-compose down -v

# Reconstruir solo el microservicio
docker-compose build aviones-api

# Ver logs en tiempo real
docker-compose logs -f aviones-api

# Ejecutar comandos dentro del contenedor
docker-compose exec aviones-api bash
```

### Gestión de Base de Datos
```bash
# Conectar a PostgreSQL directamente
docker-compose exec postgres psql -U postgres -d aviones_db

# Hacer backup de la base de datos
docker-compose exec postgres pg_dump -U postgres aviones_db > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U postgres -d aviones_db < backup.sql
```

## 🧪 Pruebas de la API

### Endpoints Principales
```bash
# Health check
curl http://localhost:8000/health

# Obtener información del microservicio
curl http://localhost:8000/

# Crear un avión
curl -X POST "http://localhost:8000/aviones/" \
     -H "Content-Type: application/json" \
     -d '{
       "modelo": "Boeing 737",
       "capacidad": 180,
       "aerolinea": "Avianca",
       "estado": "disponible",
       "fecha_fabricacion": "2020-01-15"
     }'

# Obtener todos los aviones
curl http://localhost:8000/aviones/

# Obtener avión por ID
curl http://localhost:8000/aviones/1
```

## 🔧 Desarrollo

### Modo Desarrollo
Para desarrollo activo, puedes montar el código fuente como volumen:

```bash
# El docker-compose.yml ya incluye el montaje del código
# Los cambios se reflejarán automáticamente
```

### Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto con:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=aviones_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
ENVIRONMENT=development
DEBUG=true
```

## 🐛 Solución de Problemas

### Puerto ya en uso
```bash
# Cambiar puertos en docker-compose.yml
# Busca "8000:8000" y cambia el primer puerto
```

### Base de datos no conecta
```bash
# Verificar que PostgreSQL esté funcionando
docker-compose logs postgres

# Reiniciar solo la base de datos
docker-compose restart postgres
```

### Contenedor no inicia
```bash
# Ver logs detallados
docker-compose logs aviones-api

# Reconstruir desde cero
docker-compose down -v
docker-compose up --build --force-recreate
```

## 📁 Estructura de Archivos Docker

```
microservicio-avion/
├── Dockerfile              # Configuración del contenedor
├── docker-compose.yml      # Orquestación de servicios
├── .dockerignore          # Archivos a ignorar en el build
├── init-db.sql            # Script de inicialización de BD
├── requirements.txt       # Dependencias Python
└── DOCKER_README.md       # Este archivo
```

## 🔒 Seguridad

- Las contraseñas en este ejemplo son para desarrollo
- En producción, usa variables de entorno seguras
- Considera usar Docker Secrets para credenciales sensibles
- El contenedor ejecuta con usuario no-root por seguridad

## 📈 Monitoreo

Los contenedores incluyen health checks:
- PostgreSQL: verifica conectividad
- API: verifica endpoint /health

Para ver el estado:
```bash
docker-compose ps
```

¡Tu microservicio de aviones ya está dockerizado y listo para usar! 🚀✈️


