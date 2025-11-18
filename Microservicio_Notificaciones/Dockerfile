# Multi-stage build for Spring Boot application
FROM gradle:8.5-jdk21 AS build

# Set working directory
WORKDIR /app

# Copy gradle files
COPY build.gradle settings.gradle ./
COPY gradle ./gradle

# Copy source code
COPY src ./src

# Build the application
RUN gradle build --no-daemon -x test

# Runtime stage
FROM eclipse-temurin:21-jre

# Set working directory
WORKDIR /app

# Copy the built jar from build stage
COPY --from=build /app/build/libs/*.jar app.jar

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/ServicioNotificaciones/actuator/health || exit 1

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]