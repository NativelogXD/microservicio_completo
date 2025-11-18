package com.example.microservicionotificaciones.persistence.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Date;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "notificaciones")
public class Notificacion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "person_id")
    private String id_persona;

    @Column(name = "email_destino")
    private String emailDestino;

    @Column(name = "titulo", nullable = false)
    private String titulo;

    @Column(name = "mensaje", nullable = false)
    private String mensaje;

    @Column(name = "fecha_creacion")
    private Date fechaCreacion;

    @Column(name = "fecha_lectura")
    private Date fechaLectura;

    @Column(name = "estado")
    private String estado;

    @PrePersist
    public void prePersist() {
        this.fechaCreacion = new Date();
        this.estado = "PENDIENTE";
    }
}
