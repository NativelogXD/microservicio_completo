# Multi-stage build for Spring Boot application (Vuelos)
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

# Expose port for Vuelos service
EXPOSE 8888

# Run the application
ENTRYPOINT ["java", "-jar", "app.jar"]