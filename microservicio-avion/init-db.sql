-- Script de inicialización de la base de datos para el microservicio de aviones
-- Este script se ejecuta automáticamente cuando se crea el contenedor de PostgreSQL

-- Crear la base de datos si no existe (ya se crea automáticamente por las variables de entorno)
-- CREATE DATABASE IF NOT EXISTS aviones_db;

-- Conectar a la base de datos
\c aviones_db;

-- Crear extensiones útiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Comentario sobre las tablas
-- Las tablas se crean automáticamente por SQLAlchemy a través del código de la aplicación
-- Este script está aquí para futuras personalizaciones de la base de datos

-- Ejemplo de datos iniciales (opcional)
-- INSERT INTO aviones (modelo, capacidad, aerolinea, estado, fecha_fabricacion) VALUES
-- ('Boeing 737', 180, 'Avianca', 'disponible', '2020-01-15'),
-- ('Airbus A320', 150, 'LATAM', 'disponible', '2019-06-20'),
-- ('Boeing 787', 290, 'Avianca', 'mantenimiento', '2021-03-10');


