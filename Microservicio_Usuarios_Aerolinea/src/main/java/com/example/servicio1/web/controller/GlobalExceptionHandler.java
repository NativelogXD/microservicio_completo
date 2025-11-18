package com.example.servicio1.web.controller;

import com.example.servicio1.exceptions.CedulaFoundException;
import com.example.servicio1.exceptions.GmailFoundException;
import com.example.servicio1.exceptions.UsuarioNotFoundException;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@ControllerAdvice
public class GlobalExceptionHandler {

    private ResponseEntity<Object> buildValidationResponse(List<String> details) {
        var body = new java.util.LinkedHashMap<String, Object>();
        body.put("status", HttpStatus.BAD_REQUEST.value());
        body.put("code", "VALIDATION_ERROR");
        body.put("message", "Error de validación en la solicitud");
        body.put("details", details);
        body.put("timestamp", Instant.now().toString());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(body);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Object> handleMethodArgumentNotValid(MethodArgumentNotValidException ex) {
        List<String> details = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(err -> formatFieldError(err))
                .collect(Collectors.toList());
        return buildValidationResponse(details);
    }

    private String formatFieldError(FieldError err) {
        String field = err.getField();
        String msg = err.getDefaultMessage();
        return field + ": " + msg;
    }

    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<Object> handleConstraintViolation(ConstraintViolationException ex) {
        List<String> details = ex.getConstraintViolations()
                .stream()
                .map(this::formatConstraintViolation)
                .collect(Collectors.toList());
        return buildValidationResponse(details);
    }

    private String formatConstraintViolation(ConstraintViolation<?> violation) {
        String path = violation.getPropertyPath() != null ? violation.getPropertyPath().toString() : "";
        String msg = violation.getMessage();
        return path + ": " + msg;
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<Object> handleJsonParseError(HttpMessageNotReadableException ex) {
        List<String> details = new ArrayList<>();
        details.add("JSON inválido o formato incorrecto: " + ex.getMostSpecificCause().getMessage());
        return buildValidationResponse(details);
    }

    // --- NUEVO: Mapeo explícito de errores de autenticación ---
    @ExceptionHandler(BadCredentialsException.class)
    public ResponseEntity<Object> handleBadCredentials(BadCredentialsException ex) {
        var body = new java.util.LinkedHashMap<String, Object>();
        body.put("status", HttpStatus.UNAUTHORIZED.value());
        body.put("code", "BAD_CREDENTIALS");
        body.put("message", "Credenciales inválidas");
        body.put("timestamp", Instant.now().toString());
        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(body);
    }

    @ExceptionHandler(UsernameNotFoundException.class)
    public ResponseEntity<Object> handleUserNotFound(UsernameNotFoundException ex) {
        var body = new java.util.LinkedHashMap<String, Object>();
        body.put("status", HttpStatus.NOT_FOUND.value());
        body.put("code", "USER_NOT_FOUND");
        body.put("message", "Usuario no encontrado");
        body.put("timestamp", Instant.now().toString());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(body);
    }

    @ExceptionHandler(UsuarioNotFoundException.class)
    public ResponseEntity<Object> handleUsuarioNotFound(UsuarioNotFoundException ex) {
        var body = new java.util.LinkedHashMap<String, Object>();
        body.put("status", HttpStatus.NOT_FOUND.value());
        body.put("code", "USER_NOT_FOUND");
        body.put("message", ex.getMessage());
        body.put("timestamp", Instant.now().toString());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(body);
    }

    @ExceptionHandler(GmailFoundException.class)
    public ResponseEntity<Object> handleGmailFound(GmailFoundException ex) {
        var body = new java.util.LinkedHashMap<String, Object>();
        body.put("status", HttpStatus.CONFLICT.value());
        body.put("code", "EMAIL_ALREADY_EXISTS");
        body.put("message", ex.getMessage());
        body.put("timestamp", Instant.now().toString());
        return ResponseEntity.status(HttpStatus.CONFLICT).body(body);
    }

    @ExceptionHandler(CedulaFoundException.class)
    public ResponseEntity<Object> handleCedulaFound(CedulaFoundException ex) {
        var body = new java.util.LinkedHashMap<String, Object>();
        body.put("status", HttpStatus.CONFLICT.value());
        body.put("code", "CEDULA_ALREADY_EXISTS");
        body.put("message", ex.getMessage());
        body.put("timestamp", Instant.now().toString());
        return ResponseEntity.status(HttpStatus.CONFLICT).body(body);
    }
}