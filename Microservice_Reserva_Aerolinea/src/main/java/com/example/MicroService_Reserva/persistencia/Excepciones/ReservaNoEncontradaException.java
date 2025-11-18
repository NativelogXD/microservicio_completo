package com.example.MicroService_Reserva.persistencia.Excepciones;

public class ReservaNoEncontradaException extends RuntimeException {
    public ReservaNoEncontradaException(String mensaje) {
        super(mensaje);
    }
}