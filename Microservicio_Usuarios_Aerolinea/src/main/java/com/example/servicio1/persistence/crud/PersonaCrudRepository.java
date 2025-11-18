package com.example.servicio1.persistence.crud;

import com.example.servicio1.persistence.entity.Persona;
import org.springframework.data.repository.CrudRepository;

import java.util.Optional;

public interface PersonaCrudRepository extends CrudRepository<Persona, Long> {

    Optional<Persona> findByEmail(String email);

    Optional<Persona> findByCedula(String cedula);
}
