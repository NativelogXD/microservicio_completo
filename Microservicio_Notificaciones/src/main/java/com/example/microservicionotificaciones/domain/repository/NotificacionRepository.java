package com.example.microservicionotificaciones.domain.repository;

import com.example.microservicionotificaciones.domain.dto.NotificacionDTO;

import java.util.Optional;

public interface NotificacionRepository {

    //Consultar todas las notificaciones
    Iterable<NotificacionDTO> findAll();

    //Consultar una notificacion por id
    Optional<NotificacionDTO> findById(Long id);

    //Guardar notificacion
    NotificacionDTO save(NotificacionDTO notificacionDTO);

    //Eliminar notificacion
    void deleteById(Long id);

    //validar si existe notificacion por ID
    boolean existsById(Long id);

    //Contar todas las notificaciones
    long count();

    //Consultar notificaciones por id de persona
    Iterable<NotificacionDTO> findAllByIdPersona(String id);
}
