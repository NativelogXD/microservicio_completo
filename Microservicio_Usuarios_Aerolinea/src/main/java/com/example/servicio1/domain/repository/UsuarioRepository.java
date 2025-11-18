package com.example.servicio1.domain.repository;


import com.example.servicio1.domain.dto.UsuarioDTO;

import java.util.Optional;

public interface UsuarioRepository {

    //Consultar todos los registros
    Iterable<UsuarioDTO> findAll();

    //Consultar por ID
    Optional<UsuarioDTO> findById(Long id);

    //Guardar
    UsuarioDTO save(UsuarioDTO usuarioDTO);

    //Actualizar
    UsuarioDTO update(UsuarioDTO usuarioDTO);

    //Eliminar
    void delete(Long id);

    //Validar si existe por ID
    boolean existsById(Long id);

    //Contar todos los registros
    long count();

    //Consultar por email
    Optional<UsuarioDTO> findByEmail(String email);

    //Consultar por cedula
    Optional<UsuarioDTO> findByCedula(String cedula);

    //Actualizar contraseña
    Optional<UsuarioDTO> PutContrasenia(long id, String contrasenia);
}
