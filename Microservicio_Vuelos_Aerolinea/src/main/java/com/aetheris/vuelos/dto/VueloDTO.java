package com.aetheris.vuelos.dto;

import lombok.*;
import java.time.LocalDate;
import java.time.LocalTime;
import jakarta.validation.constraints.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class VueloDTO {

    private String id; // ID único interno (se genera en backend)

    @NotBlank(message = "El código de vuelo no puede estar vacío")
    @Size(max = 10, message = "El código de vuelo no debe exceder 10 caracteres")
    private String codigoVuelo;     // Ej: "AV1234"

    @NotBlank(message = "El origen no puede estar vacío")
    private String origen;          // Ciudad/país origen

    @NotBlank(message = "El destino no puede estar vacío")
    private String destino;         // Ciudad/país destino

    @NotBlank(message = "Debe especificarse un avión")
    private String id_avion;         // Relación con microservicio Avión

    @NotBlank(message = "Debe especificarse un piloto")
    private String id_piloto;        // Relación con microservicio Empleados

    @NotNull(message = "La fecha del vuelo es obligatoria")
    @FutureOrPresent(message = "La fecha del vuelo no puede ser en el pasado")
    private LocalDate fecha;        // Fecha del vuelo

    @NotNull(message = "La hora del vuelo es obligatoria")
    private LocalTime hora;         // Hora de salida

    @Min(value = 30, message = "La duración mínima del vuelo es de 30 minutos")
    private int duracionMinutos;    // Duración estimada

    /*
    @Pattern(
            regexp = "PROGRAMADO|EN_VUELO|ATERRIZADO|CANCELADO",
            message = "El estado debe ser PROGRAMADO, EN_VUELO, ATERRIZADO o CANCELADO"
    )
    */
    private String estado;          // Estado del vuelo

    @Positive(message = "El precio base debe ser mayor que 0")
    private double precioBase;      // Precio base del vuelo
}
