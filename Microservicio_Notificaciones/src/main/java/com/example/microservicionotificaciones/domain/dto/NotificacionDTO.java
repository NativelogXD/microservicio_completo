package com.example.microservicionotificaciones.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class NotificacionDTO {

    private Long id;

    @NotBlank(message = "El ID de la persona no puede ser nulo")
    private String id_persona;

    @NotBlank(message = "El email de destiono no puede estar vacio")
    private String emailDestino;

    @NotBlank(message = "El titulo no puede estar vacio")
    private String titulo;

    @NotBlank(message = "El mensaje no puede estar vacio")
    private String mensaje;
}
