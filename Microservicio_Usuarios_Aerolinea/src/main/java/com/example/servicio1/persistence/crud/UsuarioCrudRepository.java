package com.example.servicio1.persistence.crud;

import com.example.servicio1.persistence.entity.Usuario;
import org.springframework.data.repository.CrudRepository;

import java.util.Optional;

public interface UsuarioCrudRepository extends CrudRepository<Usuario, Long> {

    Optional<Usuario> findByCedula(String cedula);

    Optional<Usuario> findByEmail(String email);
}
