package com.example.servicio1.persistence.mapper;

import com.example.servicio1.domain.dto.PersonaDTO;
import com.example.servicio1.persistence.entity.Persona;
import org.mapstruct.InheritInverseConfiguration;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;

@Mapper(componentModel = "spring")
public interface PersonaMapper {

    //Mapeo Persona a PersonaDTO
    @Mapping(source = "id", target = "id")
    @Mapping(source = "cedula", target = "cedula")
    @Mapping(source = "nombre", target = "nombre")
    @Mapping(source = "apellido", target = "apellido")
    @Mapping(source = "telefono", target = "telefono")
    @Mapping(source = "email", target = "email")
    @Mapping(source = "contrasenia", target = "contrasenia")
    @Mapping(source = "rol", target = "rol", qualifiedByName = "mapRolToString")
    PersonaDTO toDTO(Persona persona);

    //Mapeo inverso
    @InheritInverseConfiguration
    @Mapping(source = "rol", target = "rol", qualifiedByName = "mapStringToRol")
    Persona toEntity(PersonaDTO personaDTO);

    @Named("mapRolToString")
    static String mapRolToString(Persona.Rol rol) {return rol != null ? rol.name() : null;}

    @Named("mapStringToRol")
    static Persona.Rol mapStringToRol(String rol) {
        return rol != null ? Persona.Rol.valueOf(rol) : null;
    }
}
