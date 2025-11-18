package com.example.servicio1.domain.repository;


import com.example.servicio1.domain.dto.PersonaDTO;

import java.util.Optional;

public interface PersonaRepository {

    //Consultar todos los registros
    Iterable<PersonaDTO> findAll();

    //Consultar por ID
    Optional<PersonaDTO> findById(Long id);

    //Guardar
    PersonaDTO save(PersonaDTO personaDTO);

    //Actualizar
    PersonaDTO update(PersonaDTO personaDTO);

    //Eliminar
    void delete(Long id);

    //Validar si existe por ID
    boolean existsById(Long id);

    //Contar todos los registros
    long count();

    //Consultar por email
    Optional<PersonaDTO> findByEmail(String email);

    //Consultar por cedula
    Optional<PersonaDTO> findByCedula(String cedula);

    //Actualizar contraseña
    Optional<PersonaDTO> PutContrasenia(long id, String contrasenia);
}
