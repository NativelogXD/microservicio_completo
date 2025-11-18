# Multi-stage Dockerfile for Spring Boot (Gradle)
# Build stage
FROM eclipse-temurin:21-jdk AS builder
WORKDIR /app

# Copy Gradle wrapper and project files
COPY gradlew .
COPY gradle ./gradle
COPY settings.gradle .
COPY build.gradle .
COPY src ./src

# Ensure gradlew is executable and build the fat jar
RUN chmod +x gradlew && ./gradlew clean bootJar --no-daemon

# Runtime stage
FROM eclipse-temurin:21-jre AS runtime
WORKDIR /app

# Copy the generated jar
COPY --from=builder /app/build/libs/*.jar /app/app.jar

EXPOSE 8080

# Optionally allow overriding port with SERVER_PORT env
ENV SERVER_PORT=8080

ENTRYPOINT ["java","-jar","/app/app.jar"]