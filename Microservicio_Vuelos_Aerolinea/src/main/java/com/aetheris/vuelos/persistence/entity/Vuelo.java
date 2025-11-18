package com.aetheris.vuelos.persistence.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Entity
@Table(name = "vuelo")
public class Vuelo {

    @Id
    @Column(name = "id", nullable = false, unique = true, updatable = false, length = 36)
    @Builder.Default
    private String id = UUID.randomUUID().toString(); // ID único interno

    @Column(name = "codigo_vuelo", nullable = false, length = 10)
    private String codigoVuelo;       // Ej: "AV1234"

    @Column(name = "origen", nullable = false, length = 100)
    private String origen;            // Ciudad/país origen

    @Column(name = "destino", nullable = false, length = 100)
    private String destino;           // Ciudad/país destino

    @Column(name = "avion_id", nullable = false, length = 36)
    private String id_avion;           // Relación con microservicio Avión

    @Column(name = "piloto_id", nullable = false, length = 36)
    private String id_piloto;          // Relación con microservicio Empleados

    @Column(name = "fecha", nullable = false)
    private LocalDate fecha;          // Fecha del vuelo

    @Column(name = "hora", nullable = false)
    private LocalTime hora;           // Hora de salida

    @Column(name = "duracion_minutos", nullable = false)
    private int duracionMinutos;      // Duración estimada

    @Column(name = "estado", nullable = false, length = 20)
    @Builder.Default
    private String estado = "PROGRAMADO"; // PROGRAMADO, EN_VUELO, ATERRIZADO, CANCELADO

    @Column(name = "precio_base", nullable = false)
    private double precioBase;        // Precio base del vuelo
}
