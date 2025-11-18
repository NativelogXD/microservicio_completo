package com.example.servicio1.domain.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class AdminDTO extends PersonaDTO {

    @NotBlank(message = "El nivel de acceso no puede estar vacio")
    private String nivelAcceso;

    @Min(value = 1, message = "El monto debe ser mayor a 0")
    private Double sueldo;

    @NotBlank(message = "los permisos no pueden estar vacios")
    private String permiso;
}
