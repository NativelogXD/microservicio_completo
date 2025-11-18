package com.example.MicroService_Reserva.persistencia.controller;

import com.example.MicroService_Reserva.persistencia.Excepciones.ReservaInvalidaException;
import com.example.MicroService_Reserva.persistencia.Excepciones.ReservaNoEncontradaException;
import com.example.MicroService_Reserva.persistencia.Excepciones.ReservaYaActivaException;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

@ControllerAdvice
public class RestExceptionHandler {

    @ExceptionHandler(ReservaNoEncontradaException.class)
    public ResponseEntity<ApiError> handleReservaNoEncontrada(ReservaNoEncontradaException ex, HttpServletRequest request) {
        return build(HttpStatus.NOT_FOUND, "Reserva no encontrada", ex.getMessage(), request.getRequestURI());
    }

    @ExceptionHandler({ReservaInvalidaException.class, IllegalArgumentException.class})
    public ResponseEntity<ApiError> handleBadRequest(Exception ex, HttpServletRequest request) {
        return build(HttpStatus.BAD_REQUEST, "Solicitud inválida", ex.getMessage(), request.getRequestURI());
    }

    @ExceptionHandler(ReservaYaActivaException.class)
    public ResponseEntity<ApiError> handleConflict(ReservaYaActivaException ex, HttpServletRequest request) {
        return build(HttpStatus.CONFLICT, "Conflicto", ex.getMessage(), request.getRequestURI());
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiError> handleGeneric(Exception ex, HttpServletRequest request) {
        return build(HttpStatus.INTERNAL_SERVER_ERROR, "Error interno", "Ocurrió un error inesperado", request.getRequestURI());
    }

    private ResponseEntity<ApiError> build(HttpStatus status, String error, String message, String path) {
        ApiError body = new ApiError(status.value(), error, message, path);
        return ResponseEntity.status(status).body(body);
    }

    public static class ApiError {
        private final int status;
        private final String error;
        private final String message;
        private final String path;
        private final java.time.OffsetDateTime timestamp;

        public ApiError(int status, String error, String message, String path) {
            this.status = status;
            this.error = error;
            this.message = message;
            this.path = path;
            this.timestamp = java.time.OffsetDateTime.now();
        }

        public int getStatus() { return status; }
        public String getError() { return error; }
        public String getMessage() { return message; }
        public String getPath() { return path; }
        public java.time.OffsetDateTime getTimestamp() { return timestamp; }
    }
}