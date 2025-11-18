package com.example.microservicionotificaciones.persistence.crud;

import com.example.microservicionotificaciones.persistence.entity.Notificacion;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface NotificacionCrudRepository extends CrudRepository<Notificacion, Long> {

    @Query("SELECT n FROM Notificacion n WHERE n.id_persona = :idPersona")
    Iterable<Notificacion> findByIdPersona(@Param("idPersona") String idPersona);
}
