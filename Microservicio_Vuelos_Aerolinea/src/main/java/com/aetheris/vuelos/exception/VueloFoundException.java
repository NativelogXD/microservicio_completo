package com.aetheris.vuelos.exception;

public class VueloFoundException extends RuntimeException {
    public VueloFoundException() {
        super("Este código de vuelo ya existe");
    }

    public VueloFoundException(String message) {
        super(message);
    }

    public VueloFoundException(String message, Throwable cause) {
        super(message, cause);
    }
}
