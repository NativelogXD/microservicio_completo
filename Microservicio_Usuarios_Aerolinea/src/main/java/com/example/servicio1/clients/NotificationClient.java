package com.example.servicio1.clients;

import com.example.servicio1.domain.dto.NotificacionRequest;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

@Service
public class NotificationClient {

    private final WebClient webClient;

    public NotificationClient() {
        this.webClient = WebClient.builder()
                .baseUrl("http://api-gateway:8080/ServiceNotificaciones/api/notificaciones")
                .build();
    }

    public void enviarNotificacion(String personId, String email, String nombre) {
        NotificacionRequest notificacion = new NotificacionRequest(
                personId,
                email,
                "Registro exitoso",
                "Hola " + nombre + ", tu cuenta ha sido creada con éxito."
        );

        System.out.println("➡️ Enviando notificación: " + notificacion);

        try {
            webClient.post()
                    .uri("/save")
                    .bodyValue(notificacion)
                    .retrieve()
                    .bodyToMono(Void.class)
                    .onErrorResume(e -> Mono.empty())
                    .block();
        } catch (Exception e) {
            System.out.println("Error al enviar notificación: " + e.getMessage());
        }
    }
}
