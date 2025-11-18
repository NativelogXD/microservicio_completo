package com.example.servicio1.domain.repository;

import com.example.servicio1.domain.dto.AdminDTO;

import java.util.Optional;

public interface AdminRepository {

    //Consultar todos los registros
    Iterable<AdminDTO> findAll();

    //Consultar por ID
    Optional<AdminDTO> findById(Long id);

    //Guardar
    AdminDTO save(AdminDTO adminDTO);

    //Actualizar
    AdminDTO update(AdminDTO adminDTO);

    //Eliminar
    void delete(Long id);

    //Validar si existe por ID
    boolean existsById(Long id);

    //Contar todos los registros
    long count();

    //Consultar por email
    Optional<AdminDTO> findByEmail(String email);

    //Consultar por cedula
    Optional<AdminDTO> findByCedula(String cedula);

    //Actualizar contraseña
    Optional<AdminDTO> PutContrasenia(long id, String contrasenia);
}
