package com.example.MicroService_Reserva.persistencia.service;

import com.example.MicroService_Reserva.domain.dto.ReservaDTO;
import com.example.MicroService_Reserva.persistencia.Entity.EstadoReserva;
import com.example.MicroService_Reserva.persistencia.Entity.Reserva;
import com.example.MicroService_Reserva.persistencia.Excepciones.ReservaInvalidaException;
import com.example.MicroService_Reserva.persistencia.Excepciones.ReservaNoEncontradaException;
import com.example.MicroService_Reserva.persistencia.Excepciones.ReservaYaActivaException;
import com.example.MicroService_Reserva.persistencia.crudRepository.ReservaCrudRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class ReservaService {

    private final com.example.MicroService_Reserva.persistencia.repository.ReservaRepository reservaRepository;

    @Autowired
    public ReservaService(com.example.MicroService_Reserva.persistencia.repository.ReservaRepository reservaRepository) {
        this.reservaRepository = reservaRepository;
    }

    public ReservaDTO save(ReservaDTO reservaDTO) {
        if (reservaDTO.getUsuario() == null || reservaDTO.getUsuario().isBlank()) {
            throw new ReservaInvalidaException("La reserva debe tener un usuario válido");
        }
        if (reservaDTO.getId_vuelo() == null || reservaDTO.getId_vuelo().isBlank()) {
            throw new ReservaInvalidaException("La reserva debe tener un vuelo válido");
        }
        if (reservaDTO.getEstado() == null || reservaDTO.getEstado().isBlank()) {
            reservaDTO.setEstado(EstadoReserva.PENDIENTE.name());
        }

        ReservaDTO reserva = reservaRepository.save(reservaDTO);
        return reserva;
    }

    public ReservaDTO findById(String id) {
        return reservaRepository.findById(id)
                .orElseThrow(() -> new ReservaNoEncontradaException("No se encontró la reserva con ID: " + id));
    }

    public List<ReservaDTO> findAll() {
        return reservaRepository.findAll();
    }

    public void deleteById(String id) {
        if (!reservaRepository.existsById(id)) {
            throw new ReservaNoEncontradaException("No se puede eliminar, la reserva con ID: " + id + " no existe");
        }
        reservaRepository.delete(id);
    }

    public ReservaDTO update(ReservaDTO reservaDTO) {
        if (reservaDTO.getId() == null || reservaDTO.getId().isBlank()) {
            throw new ReservaInvalidaException("El ID de la reserva es requerido para actualizar");
        }
        if (!reservaRepository.existsById(reservaDTO.getId())) {
            throw new ReservaNoEncontradaException("No se encontró la reserva con ID: " + reservaDTO.getId());
        }
        if (reservaDTO.getUsuario() == null || reservaDTO.getUsuario().isBlank()) {
            throw new ReservaInvalidaException("La reserva debe tener un usuario válido");
        }
        if (reservaDTO.getId_vuelo() == null || reservaDTO.getId_vuelo().isBlank()) {
            throw new ReservaInvalidaException("La reserva debe tener un vuelo válido");
        }
        if (reservaDTO.getEstado() == null || reservaDTO.getEstado().isBlank()) {
            throw new ReservaInvalidaException("La reserva debe tener un estado válido");
        }

        return reservaRepository.update(reservaDTO);
    }

    // -------- Búsquedas --------
    public List<ReservaDTO> buscarPorUsuario(String usuario) {
        return reservaRepository.findByUsuarioContaining(usuario);
    }

    public List<ReservaDTO> buscarPorEstado(String estado) {
        return reservaRepository.findByEstado(estado);
    }

    public List<ReservaDTO> buscarPorVuelo(String id_vuelo) {
        Optional<ReservaDTO> reserva = reservaRepository.findByVuelo(id_vuelo);
        return reserva.map(List::of).orElse(List.of());
    }

    // -------- Utilitarios --------
    public long count() {
        return reservaRepository.count();
    }

    public boolean existsById(String id) {
        return reservaRepository.existsById(id);
    }

    

    //aa//
}