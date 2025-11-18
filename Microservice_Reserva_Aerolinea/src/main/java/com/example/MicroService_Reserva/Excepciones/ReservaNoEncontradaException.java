package com.example.MicroService_Reserva.Excepciones;

public class ReservaNoEncontradaException extends RuntimeException {
    public ReservaNoEncontradaException(String mensaje) {
        super(mensaje);
    }
}