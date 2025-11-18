package com.example.servicio1.persistence.crud;

import com.example.servicio1.persistence.entity.Admin;
import org.springframework.data.repository.CrudRepository;

import java.util.Optional;

public interface AdminCrudRepository extends CrudRepository<Admin, Long> {

    Optional<Admin> findByEmail(String email);

    Optional<Admin> findByCedula(String cedula);
}
