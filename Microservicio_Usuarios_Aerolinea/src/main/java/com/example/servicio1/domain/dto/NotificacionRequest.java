package com.example.servicio1.domain.dto;

public record NotificacionRequest(
        String personId
        ,String emailDestino
        ,String titulo
        ,String mensaje) {
}
