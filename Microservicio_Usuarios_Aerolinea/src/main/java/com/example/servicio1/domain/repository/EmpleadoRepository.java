package com.example.servicio1.domain.repository;

import com.example.servicio1.domain.dto.EmpleadoDTO;

import java.util.Optional;

public interface EmpleadoRepository {

    //Consultar todos los registros
    Iterable<EmpleadoDTO> findAll();

    //Consultar por ID
    Optional<EmpleadoDTO> findById(Long id);

    //Guardar
    EmpleadoDTO save(EmpleadoDTO empleadoDTO);

    //Actualizar
    EmpleadoDTO update(EmpleadoDTO empleadoDTO);

    //Eliminar
    void delete(Long id);

    //Validar si existe por ID
    boolean existsById(Long id);

    //Contar todos los registros
    long count();

    //Consultar por email
    Optional<EmpleadoDTO> findByEmail(String email);

    //Consultar por cedula
    Optional<EmpleadoDTO> findByCedula(String cedula);

    //Actualizar contraseña
    Optional<EmpleadoDTO> PutContrasenia(long id, String contrasenia);

    Optional<EmpleadoDTO> findByCargo(String cargo);
}
