package com.aetheris.vuelos.persistence.mapper;

import org.mapstruct.*;

import com.aetheris.vuelos.dto.VueloDTO;
import com.aetheris.vuelos.persistence.entity.Vuelo;
import org.mapstruct.factory.Mappers;

@Mapper(
        componentModel = "spring",
        nullValuePropertyMappingStrategy = NullValuePropertyMappingStrategy.IGNORE,
        nullValueCheckStrategy = NullValueCheckStrategy.ALWAYS
)
public interface VueloMapper {

    // =========================================
    // Mapeo básico Entity → DTO
    // =========================================

    @Mapping(target = "codigoVuelo", source = "codigoVuelo")
    @Mapping(target = "origen", source = "origen")
    @Mapping(target = "destino", source = "destino")
    @Mapping(target = "id_avion", source = "id_avion")
    @Mapping(target = "id_piloto", source = "id_piloto")
    @Mapping(target = "fecha", source = "fecha")
    @Mapping(target = "hora", source = "hora")
    @Mapping(target = "duracionMinutos", source = "duracionMinutos")
    @Mapping(target = "estado", source = "estado")
    @Mapping(target = "precioBase", source = "precioBase")
    VueloDTO toDTO(Vuelo vuelo);

    // =========================================
    // Mapeo básico DTO → Entity
    // =========================================

    @InheritInverseConfiguration
    @Mapping(target = "id", source = "id")
    Vuelo toEntity(VueloDTO vueloDTO);

    @Mapping(target = "id", ignore = true) // No actualizar el ID
    void updateEntityFromDTO(VueloDTO vueloDTO, @MappingTarget Vuelo vuelo);
}