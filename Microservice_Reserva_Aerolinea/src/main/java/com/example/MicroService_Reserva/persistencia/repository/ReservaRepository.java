package com.example.MicroService_Reserva.persistencia.repository;




import com.example.MicroService_Reserva.domain.RepositoryInterface.repositoryInterface;
import com.example.MicroService_Reserva.domain.dto.ReservaDTO;
import com.example.MicroService_Reserva.persistencia.Entity.Reserva;
import com.example.MicroService_Reserva.persistencia.crudRepository.ReservaCrudRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Repository
public class ReservaRepository implements repositoryInterface {

    @Autowired
    private ReservaCrudRepository reservaCrudRepository;
    

    @Override
    public List<ReservaDTO> findAll() {
        List<Reserva> reservas = reservaCrudRepository.findAll();
        List<ReservaDTO> dtoList = new ArrayList<>();
        for (Reserva r : reservas) {
            dtoList.add(toDTO(r));
        }
        return dtoList;
    }

    @Override
    public Optional<ReservaDTO> findById(String id) {
        try {
            Long longId = Long.parseLong(id);
            return reservaCrudRepository.findById(longId).map(this::toDTO);
        } catch (NumberFormatException e) {
            return Optional.empty();
        }
    }

    @Override
    public ReservaDTO save(ReservaDTO reservaDTO) {
        Reserva entity = toEntity(reservaDTO);
        Reserva saved = reservaCrudRepository.save(entity);
        return toDTO(saved);
    }

    @Override
    public ReservaDTO update(ReservaDTO reservaDTO) {
        if (reservaDTO.getId() == null || reservaDTO.getId().isBlank()) {
            throw new IllegalArgumentException("El id de la reserva no puede ser nulo ni vacío para actualizar");
        }
        try {
            Long longId = Long.parseLong(reservaDTO.getId());
            if (!reservaCrudRepository.existsById(longId)) {
                throw new IllegalArgumentException("No existe una reserva con el id especificado");
            }
            Reserva entity = toEntity(reservaDTO);
            Reserva updated = reservaCrudRepository.save(entity);
            return toDTO(updated);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("El ID debe ser un número válido");
        }
    }

    @Override
    public void delete(String id) {
        try {
            Long longId = Long.parseLong(id);
            reservaCrudRepository.deleteById(longId);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("El ID debe ser un número válido");
        }
    }

    @Override
    public boolean existsById(String id) {
        try {
            Long longId = Long.parseLong(id);
            return reservaCrudRepository.existsById(longId);
        } catch (NumberFormatException e) {
            return false;
        }
    }

    @Override
    public long count() {
        return reservaCrudRepository.count();
    }

    @Override
    public Optional<ReservaDTO> findByUsuario(String usuario) {
        List<Reserva> reservas = reservaCrudRepository.findByUsuarioContaining(usuario);
        if (reservas == null || reservas.isEmpty()) {
            return Optional.empty();
        }
        return Optional.of(toDTO(reservas.get(0)));
    }

    @Override
    public Optional<ReservaDTO> findByVuelo(String vuelo) {
        List<Reserva> reservas = reservaCrudRepository.findByIdVuelo(vuelo);
        if (reservas == null || reservas.isEmpty()) {
            return Optional.empty();
        }
        return Optional.of(toDTO(reservas.get(0)));
    }

    @Override
    public List<ReservaDTO> findByEstado(String estado) {
        List<Reserva> reservas = reservaCrudRepository.findByEstado(estado);
        List<ReservaDTO> dtoList = new ArrayList<>();
        for (Reserva r : reservas) {
            dtoList.add(toDTO(r));
        }
        return dtoList;
    }

    @Override
    public List<ReservaDTO> findByUsuarioContaining(String usuario) {
        List<Reserva> reservas = reservaCrudRepository.findByUsuarioContaining(usuario);
        List<ReservaDTO> dtoList = new ArrayList<>();
        for (Reserva r : reservas) {
            dtoList.add(toDTO(r));
        }
        return dtoList;
    }




    // --- Métodos auxiliares de mapeo ---
    private ReservaDTO toDTO(Reserva r) {
        if (r == null) return null;
        ReservaDTO dto = new ReservaDTO();
        dto.setId(r.getId() != null ? r.getId().toString() : null);
        dto.setUsuario(r.getUsuario());
        dto.setId_vuelo(r.getId_vuelo());
        dto.setEstado(r.getEstado());
        dto.setNumasiento(r.getNumasiento());
        return dto;
    }

    private Reserva toEntity(ReservaDTO d) {
        if (d == null) return null;
        Reserva r = new Reserva();
        if (d.getId() != null && !d.getId().isBlank()) {
            try {
                r.setId(Long.parseLong(d.getId()));
            } catch (NumberFormatException e) {
                // For new entities, ID will be null and auto-generated
                r.setId(null);
            }
        }
        r.setUsuario(d.getUsuario());
        r.setId_vuelo(d.getId_vuelo());
        r.setEstado(d.getEstado());
        r.setNumasiento(d.getNumasiento());
        return r;
    }


}

