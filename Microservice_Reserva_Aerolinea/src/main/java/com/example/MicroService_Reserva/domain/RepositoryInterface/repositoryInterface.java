package com.example.MicroService_Reserva.domain.RepositoryInterface;

import com.example.MicroService_Reserva.domain.dto.ReservaDTO;

import java.util.Optional;
import java.util.List;

public interface repositoryInterface {


    List<ReservaDTO> findAll();

    // Consultar por ID
    Optional<ReservaDTO> findById(String id);

    // Guardar
    ReservaDTO save(ReservaDTO reservaDTO);

    // Actualizar
    ReservaDTO update(ReservaDTO reservaDTO);

    // Eliminar
    void delete(String id);

    // Validar si existe por ID
    boolean existsById(String id);

    // Contar todos los registros
    long count();

    // Consultar por usuario
    Optional<ReservaDTO> findByUsuario(String usuario);

    // Consultar por vuelo
    Optional<ReservaDTO> findByVuelo(String id_vuelo);

    // Consultar por estado
    List<ReservaDTO> findByEstado(String estado);

    // Consultar por usuario (lista)
    List<ReservaDTO> findByUsuarioContaining(String usuario);
    
}
