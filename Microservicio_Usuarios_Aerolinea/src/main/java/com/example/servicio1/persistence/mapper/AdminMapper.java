package com.example.servicio1.persistence.mapper;

import com.example.servicio1.domain.dto.AdminDTO;
import com.example.servicio1.persistence.entity.Admin;
import org.mapstruct.InheritInverseConfiguration;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring", uses = PersonaMapper.class)
public interface AdminMapper {

    //Mapeo de Admin a AdminDTO
    @Mapping(source = "nivelAcceso", target = "nivelAcceso")
    @Mapping(source = "sueldo", target = "sueldo")
    @Mapping(source = "permiso", target = "permiso")
    AdminDTO toDTO(Admin admin);

    //Mapeo inverso
    @InheritInverseConfiguration
    Admin toEntity(AdminDTO adminDTO);
}
