package com.example.MicroService_Reserva.persistencia.Excepciones;

public class ReservaYaActivaException extends RuntimeException {
    public ReservaYaActivaException(String mensaje) {
        super(mensaje);
    }
}