package com.example.servicio1.persistence.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "empleado")
@Inheritance(strategy = InheritanceType.JOINED)
public class Empleado extends Persona{

    @Column(name = "salario")
    private Double salario;

    @Column(name = "cargo")
    private String cargo;

    @PrePersist
    public void prePersist() {
        this.setRol(Rol.Empleado);
    }
}
