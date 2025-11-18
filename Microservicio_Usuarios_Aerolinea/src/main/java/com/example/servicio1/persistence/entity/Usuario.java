package com.example.servicio1.persistence.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "usuario")
@Inheritance(strategy = InheritanceType.JOINED)
public class Usuario extends Persona{

    @Column(name = "direccion")
    private String direccion;

    @Column(name = "reservaId")
    private String id_reserva;

    @PrePersist
    public void prePersist() {
        this.setRol(Rol.Usuario);
    }
}
