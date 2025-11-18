package com.example.servicio1.persistence.crud;

import com.example.servicio1.persistence.entity.Empleado;
import org.springframework.data.repository.CrudRepository;

import java.util.Optional;

public interface EmpleadoCrudRepository extends CrudRepository<Empleado, Long> {

    Optional<Empleado> findByEmail(String email);

    Optional<Empleado> findByCedula(String cedula);

    Optional<Empleado> findByCargo(String cargo);
}
