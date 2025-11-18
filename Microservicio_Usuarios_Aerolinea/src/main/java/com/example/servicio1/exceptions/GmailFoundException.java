package com.example.servicio1.exceptions;

public class GmailFoundException extends RuntimeException {
    public GmailFoundException() {
        super(String.format("este gmial ya existe"));
    }

}
