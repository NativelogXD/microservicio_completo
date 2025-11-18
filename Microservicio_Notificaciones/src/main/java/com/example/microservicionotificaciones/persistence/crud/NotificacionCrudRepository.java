package com.example.microservicionotificaciones.persistence.crud;

import com.example.microservicionotificaciones.persistence.entity.Notificacion;
import org.springframework.data.repository.CrudRepository;

import java.util.Optional;

public interface NotificacionCrudRepository extends CrudRepository<Notificacion, Long> {

    Iterable<Notificacion> findByIdPersona(String idPersona);
}
