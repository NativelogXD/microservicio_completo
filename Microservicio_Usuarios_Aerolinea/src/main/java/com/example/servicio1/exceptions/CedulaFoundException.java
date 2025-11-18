package com.example.servicio1.exceptions;

public class CedulaFoundException extends RuntimeException {
    public CedulaFoundException() {
        super(String.format("esta cedula ya existe"));
    }
}
