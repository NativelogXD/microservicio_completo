package com.example.servicio1.persistence.mapper;

import com.example.servicio1.domain.dto.EmpleadoDTO;
import com.example.servicio1.persistence.entity.Empleado;
import org.mapstruct.InheritInverseConfiguration;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring", uses = PersonaMapper.class)
public interface EmpleadoMapper {

    //Mapeo de Empleado a EmpleadoDTO
    @Mapping(source = "salario", target = "salario")
    @Mapping(source = "cargo", target = "cargo")
    EmpleadoDTO toDTO(Empleado empleado);

    //Mapeo inverso
    @InheritInverseConfiguration
    Empleado toEntity(EmpleadoDTO empleadoDTO);
}
