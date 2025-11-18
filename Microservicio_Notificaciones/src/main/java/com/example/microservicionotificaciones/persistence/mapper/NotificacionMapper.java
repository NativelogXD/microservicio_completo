package com.example.microservicionotificaciones.persistence.mapper;

import com.example.microservicionotificaciones.domain.dto.NotificacionDTO;
import com.example.microservicionotificaciones.persistence.entity.Notificacion;
import org.mapstruct.InheritInverseConfiguration;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface NotificacionMapper {

    //Mapeo de Notificacion a NotificacionDTO
    NotificacionDTO toDTO(Notificacion notificacion);

    //Mapeo inverso
    @InheritInverseConfiguration
    Notificacion toEntity(NotificacionDTO notificacionDTO);
}
