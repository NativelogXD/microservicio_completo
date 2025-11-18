package com.example.servicio1.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UsuarioDTO extends PersonaDTO {

    @NotBlank(message = "La direccion de la persona no puede estar vacia")
    private String direccion;

    private String id_reserva;
}
