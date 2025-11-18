# Multi-stage Dockerfile for Flask + Flasgger microservice

# Builder/runtime in one since Python typically installs at runtime
FROM python:3.13-slim

# Create non-root user for security
RUN useradd -m appuser
WORKDIR /app

# System deps (if needed for building some wheels)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables
ENV FLASK_APP=app.py \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Expose service port
EXPOSE 5000

# Switch to non-root
USER appuser

# Start the Flask app via python (app.py creates the app)
CMD ["python", "app.py"]