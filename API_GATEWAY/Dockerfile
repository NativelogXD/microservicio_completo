# Etapa de build (compila tu proyecto con Gradle)
FROM gradle:9.1.0-jdk21 AS build

WORKDIR /app

# Copiar todo el proyecto
COPY . .

# Construir sin tests para agilizar
RUN gradle clean build -x test --no-daemon

# Etapa de runtime (solo lo necesario para correr)
FROM eclipse-temurin:21-jre
WORKDIR /app

# Copiar el jar construido desde la etapa anterior
COPY --from=build /app/build/libs/*.jar app.jar

# Exponer el puerto del API Gateway
EXPOSE 8080

# Ejecutar el jar
CMD ["java", "-jar", "app.jar"]
