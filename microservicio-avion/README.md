# Microservicio de Aviones 🚀

Un microservicio para la gestión de aviones desarrollado con FastAPI y arquitectura limpia.

## 🏗️ Arquitectura

El proyecto sigue los principios de **Clean Architecture** con las siguientes capas:

- **Domain**: Lógica de negocio, DTOs y contratos (interfaces)
- **Persistence**: Implementación de repositorios, entidades y mapeo de datos
- **Web**: Controladores REST y configuración de la API

## 📁 Estructura del Proyecto

```
app/
├── domain/
│   ├── dto/                 # Data Transfer Objects
│   ├── repository/          # Interfaces de repositorios
│   └── service/             # Interfaces de servicios
├── persistence/
│   ├── database/            # Configuración de base de datos
│   ├── entity/              # Entidades SQLAlchemy
│   ├── mapper/              # Mapeo entre DTOs y entidades
│   ├── repositoryImpl/      # Implementación de repositorios
│   └── serviceImpl/         # Implementación de servicios
├── web/
│   └── controller/          # Controladores REST
├── exception/               # Excepciones personalizadas
└── main.py                  # Punto de entrada de la aplicación
```

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd microservicio-avion
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar las variables según tu configuración
# POSTGRES_USER=tu_usuario
# POSTGRES_PASSWORD=tu_password
# POSTGRES_DB=aviones_db
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
```

### 5. Configurar base de datos PostgreSQL
```sql
CREATE DATABASE aviones_db;
```

### 6. Ejecutar la aplicación
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Una vez ejecutando la aplicación, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 Endpoints Disponibles

### Aviones
- `POST /aviones/` - Crear un nuevo avión
- `GET /aviones/` - Obtener todos los aviones (con paginación)
- `GET /aviones/{id}` - Obtener un avión por ID
- `PUT /aviones/{id}` - Actualizar un avión
- `DELETE /aviones/{id}` - Eliminar un avión
- `GET /aviones/estado/{estado}` - Obtener aviones por estado
- `GET /aviones/aerolinea/{aerolinea}` - Obtener aviones por aerolínea
- `GET /aviones/fecha-fabricacion/{fecha}` - Obtener aviones por fecha de fabricación

## 📊 Modelo de Datos

### AvionDTO
```json
{
  "id": 1,
  "modelo": "Boeing 737",
  "capacidad": 180,
  "aerolinea": "Avianca",
  "estado": "disponible",
  "fecha_fabricacion": "2020-01-15T00:00:00"
}
```

### Estados Disponibles
- `disponible`: Avión listo para vuelos
- `mantenimiento`: Avión en mantenimiento
- `fuera_de_servicio`: Avión no operativo

## 🧪 Testing

```bash
# Ejecutar tests (cuando estén implementados)
pytest

# Con coverage
pytest --cov=app
```

## 🛠️ Desarrollo

### Formateo de código
```bash
black app/
```

### Linting
```bash
flake8 app/
```

## 📝 Características Técnicas

- **Framework**: FastAPI
- **Base de Datos**: PostgreSQL con SQLAlchemy ORM
- **Validación**: Pydantic
- **Arquitectura**: Clean Architecture
- **Patrones**: Repository Pattern, Dependency Injection
- **Documentación**: Swagger/OpenAPI automática

## 🔒 Consideraciones de Seguridad

- Validación de entrada con Pydantic
- Manejo de excepciones personalizadas
- Configuración de CORS
- Variables de entorno para configuración sensible

## 📈 Monitoreo

- Endpoint de health check: `/health`
- Logging configurado
- Métricas de base de datos con pool de conexiones

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.