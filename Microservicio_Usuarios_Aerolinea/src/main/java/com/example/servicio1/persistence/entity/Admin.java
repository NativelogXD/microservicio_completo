package com.example.servicio1.persistence.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "admin")
@PrimaryKeyJoinColumn(name = "persona_id")
public class Admin extends Persona{

    @Column(name = "nivel_acceso", nullable = false)
    private String nivelAcceso;

    @Column(name = "sueldo", nullable = false)
    private double sueldo;

    @Column(name = "permisos", nullable = false)
    private String permiso; // Ejemplo : "Gestionar vuelos, Gestionar aviones, Gestionar reservas, etc"

    @PrePersist
    public void prePersist() {
        this.setRol(Rol.Admin);
    }
}
