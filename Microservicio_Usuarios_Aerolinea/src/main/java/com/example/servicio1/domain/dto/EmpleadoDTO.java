package com.example.servicio1.domain.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class EmpleadoDTO extends PersonaDTO {

    @Min(value = 1,message = "El monto debe ser mayor a 0")
    private Double salario;

    @NotBlank(message = "El cargo no puede estar vacio")
    private String cargo;
}
