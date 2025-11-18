package com.example.servicio1.persistence.mapper;

import com.example.servicio1.domain.dto.UsuarioDTO;
import com.example.servicio1.persistence.entity.Usuario;
import org.mapstruct.InheritInverseConfiguration;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring", uses = PersonaMapper.class)
public interface UsuarioMapper {

    //Mapeo de Usuario a UsuarioDTO
    @Mapping(source = "direccion", target = "direccion")
    @Mapping(source = "id_reserva", target = "id_reserva")
    UsuarioDTO toDTO(Usuario usuario);

    //Mapeo inverso
    @InheritInverseConfiguration
    Usuario toEntity(UsuarioDTO usuarioDTO);
}
