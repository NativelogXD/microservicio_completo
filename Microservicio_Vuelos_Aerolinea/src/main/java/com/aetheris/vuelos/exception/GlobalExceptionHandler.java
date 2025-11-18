package com.aetheris.vuelos.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    private ResponseEntity<Map<String, Object>> buildResponse(
            Exception ex,
            HttpStatus status,
            String error,
            Map<String, Object> additionalData
    ) {
        Map<String, Object> response = new HashMap<>();
        response.put("timestamp", LocalDateTime.now());
        response.put("status", status.value());
        response.put("error", error);
        response.put("message", ex.getMessage());

        if (additionalData != null && !additionalData.isEmpty()) {
            response.put("errors", additionalData);
        }

        return new ResponseEntity<>(response, status);
    }

    // --- 404: NO SE ENCONTRÓ EL RECURSO ---
    @ExceptionHandler(VueloNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleVueloNotFound(VueloNotFoundException ex) {
        Map<String, Object> additionalData = new HashMap<>();
        additionalData.put("resourceName", ex.getResourceName());
        additionalData.put("fieldName", ex.getFieldName());

        if (ex.getFieldValueStr() != null) {
            additionalData.put("fieldValue", ex.getFieldValueStr());
        } else {
            additionalData.put("fieldValue", ex.getFieldValue());
        }

        return buildResponse(ex, HttpStatus.NOT_FOUND, "Vuelo no encontrado", additionalData);
    }

    // --- 409: YA EXISTE ALGO QUE NO DEBERÍA ---
    @ExceptionHandler(VueloFoundException.class)
    public ResponseEntity<Map<String, Object>> handleVueloExists(VueloFoundException ex) {
        return buildResponse(ex, HttpStatus.CONFLICT, "Duplicado: vuelo ya existe", null);
    }

    // --- 400: VALIDACIONES FALLIDAS ---
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationExceptions(MethodArgumentNotValidException ex) {
        Map<String, Object> validationErrors = new HashMap<>();
        for (FieldError error : ex.getBindingResult().getFieldErrors()) {
            validationErrors.put(error.getField(), error.getDefaultMessage());
        }
        return buildResponse(ex, HttpStatus.BAD_REQUEST, "Error de validación en los datos del vuelo", validationErrors);
    }

    // --- 400: ARGUMENTOS ILEGALES ---
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> handleIllegalArgument(IllegalArgumentException ex) {
        return buildResponse(ex, HttpStatus.BAD_REQUEST, "Solicitud incorrecta", null);
    }

    // --- 400: ESTADO NO VÁLIDO ---
    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<Map<String, Object>> handleIllegalState(IllegalStateException ex) {
        return buildResponse(ex, HttpStatus.BAD_REQUEST, "Estado inválido para la operación", null);
    }

    // --- 500: ERROR GENERAL INESPERADO ---
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGeneralException(Exception ex) {
        return buildResponse(ex, HttpStatus.INTERNAL_SERVER_ERROR, "Error interno del servidor en el módulo de vuelos", null);
    }
}
