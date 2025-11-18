package com.example.MicroService_Reserva.persistencia.Excepciones;

public class ReservaInvalidaException extends RuntimeException {
    public ReservaInvalidaException(String mensaje) {
        super(mensaje);
    }
}