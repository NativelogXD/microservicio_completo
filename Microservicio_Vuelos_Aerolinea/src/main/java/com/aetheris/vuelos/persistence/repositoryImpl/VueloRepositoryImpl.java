package com.aetheris.vuelos.persistence.repositoryImpl;

import com.aetheris.vuelos.domain.repository.VueloRepository;
import com.aetheris.vuelos.dto.VueloDTO;
import com.aetheris.vuelos.persistence.crud.VuelosCrudRepository;
import com.aetheris.vuelos.persistence.entity.Vuelo;
import com.aetheris.vuelos.persistence.mapper.VueloMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

@Repository
public class VueloRepositoryImpl implements VueloRepository {

    @Autowired
    private VuelosCrudRepository vuelosCrudRepository;

    @Autowired
    private VueloMapper vueloMapper;

    // =========================================
    // CRUD Operations - CORREGIDO
    // =========================================

    @Override
    public Iterable<VueloDTO> findAll() {
        Iterable<Vuelo> vuelos = vuelosCrudRepository.findAll();
        List<VueloDTO> dtos = StreamSupport.stream(vuelos.spliterator(), false)
                .map(vueloMapper::toDTO)
                .collect(Collectors.toList());
        return dtos;
    }

    @Override
    public Optional<VueloDTO> findById(String id) {
        return vuelosCrudRepository.findById(id)
                .map(vueloMapper::toDTO);
    }

    @Override
    public Optional<VueloDTO> findByCode(String flightCode) {
        return vuelosCrudRepository.findByCodigoVueloIgnoreCase(flightCode)
                .map(vueloMapper::toDTO);
    }

    @Override
    public VueloDTO save(VueloDTO vueloDTO) {
        Vuelo vuelo = vueloMapper.toEntity(vueloDTO);

        // Generar ID si no existe
        if (vuelo.getId() == null || vuelo.getId().isEmpty()) {
            vuelo.setId(UUID.randomUUID().toString());
        }

        Vuelo vueloGuardado = vuelosCrudRepository.save(vuelo);
        return vueloMapper.toDTO(vueloGuardado);
    }

    @Override
    public VueloDTO update(VueloDTO vueloDTO) {
        Optional<Vuelo> vueloExistente = vuelosCrudRepository.findById(vueloDTO.getId());
        if (vueloExistente.isEmpty()) {
            return null;
        }

        Vuelo vueloActual = vueloExistente.get();
        vueloMapper.updateEntityFromDTO(vueloDTO, vueloActual);

        Vuelo vueloActualizado = vuelosCrudRepository.save(vueloActual);
        return vueloMapper.toDTO(vueloActualizado);
    }

    @Override
    public boolean deleteById(String id) {
        if (!vuelosCrudRepository.existsById(id)) {
            return false;
        }
        vuelosCrudRepository.deleteById(id);
        return true;
    }

    @Override
    public boolean existsById(String id) {
        return vuelosCrudRepository.existsById(id);
    }

    @Override
    public long count() {
        return vuelosCrudRepository.count();
    }

    // =========================================
    // Search / Querying - CORREGIDO
    // =========================================

    @Override
    public List<VueloDTO> findByRoute(String origin, String destination) {
        return vuelosCrudRepository.findByOrigenIgnoreCaseAndDestinoIgnoreCase(origin, destination)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    @Override
    public List<VueloDTO> findByStatus(String status) {
        return vuelosCrudRepository.findByEstadoIgnoreCase(status)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    @Override
    public List<VueloDTO> findByDate(LocalDate date) {
        return vuelosCrudRepository.findByFecha(date)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    @Override
    public List<VueloDTO> findByDateRange(LocalDate start, LocalDate end) {
        return vuelosCrudRepository.findByFechaBetween(start, end)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    @Override
    public List<VueloDTO> findByPlane(String id_avion) {
        return vuelosCrudRepository.findByIdAvion(id_avion)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    @Override
    public List<VueloDTO> findByPilot(String id_piloto) {
        return vuelosCrudRepository.findByIdPiloto(id_piloto)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    @Override
    public List<VueloDTO> findByRouteAndDate(String origin, String destination, LocalDate date) {
        return vuelosCrudRepository.findByOrigenAndDestinoAndFecha(origin, destination, date)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    @Override
    public List<VueloDTO> findByPriceRange(double min, double max) {
        return vuelosCrudRepository.findByPrecioBaseBetween(min, max)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    @Override
    public List<VueloDTO> findUpcomingFlights(LocalDate today, LocalTime currentTime, int hoursMargin) {
        LocalTime endTime = currentTime.plusHours(hoursMargin);
        return vuelosCrudRepository.findByFechaAndHoraBetween(today, currentTime, endTime)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    // =========================================
    // Seat Management - SIMULADO (como pediste)
    // =========================================

    @Override
    public boolean hasAvailability(String flightId, int requestedSeats) {
        // Simulación temporal - siempre retorna true
        return vuelosCrudRepository.existsById(flightId);
    }

    @Override
    public boolean reserveSeats(String flightId, int seats) {
        // Simulación temporal - siempre retorna true si el vuelo existe
        return vuelosCrudRepository.existsById(flightId);
    }

    // =========================================
    // Flight State & Operations - CORREGIDO
    // =========================================

    @Override
    public boolean updateStatus(String flightId, String newStatus) {
        Optional<Vuelo> vueloOpt = vuelosCrudRepository.findById(flightId);
        if (vueloOpt.isEmpty()) {
            return false;
        }

        Vuelo vuelo = vueloOpt.get();
        vuelo.setEstado(newStatus);
        vuelosCrudRepository.save(vuelo);
        return true;
    }

    @Override
    public boolean cancelFlight(String flightId) {
        Optional<Vuelo> vueloOpt = vuelosCrudRepository.findById(flightId);
        if (vueloOpt.isEmpty()) {
            return false;
        }

        Vuelo vuelo = vueloOpt.get();
        vuelo.setEstado("CANCELADO");
        // NOTA: Eliminada la línea que modificaba asientosDisponibles
        vuelosCrudRepository.save(vuelo);
        return true;
    }

    @Override
    public boolean reassignPlane(String flightId, String new_id_avion) {
        Optional<Vuelo> vueloOpt = vuelosCrudRepository.findById(flightId);
        if (vueloOpt.isEmpty()) {
            return false;
        }

        Vuelo vuelo = vueloOpt.get();
        vuelo.setId_avion(new_id_avion);
        vuelosCrudRepository.save(vuelo);
        return true;
    }

    // =========================================
    // Statistics - CORREGIDO
    // =========================================

    @Override
    public long countByStatus(String status) {
        return vuelosCrudRepository.countByEstado(status);
    }

    @Override
    public Optional<VueloDTO> findCheapestFlight() {
        return vuelosCrudRepository.findFirstByOrderByPrecioBaseAsc()
                .map(vueloMapper::toDTO);
    }

    @Override
    public List<VueloDTO> findLongestFlights(int top) {
        return vuelosCrudRepository.findTop5ByOrderByDuracionMinutosDesc()
                .stream().limit(top).map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    // =========================================
    // Métodos adicionales útiles - CORREGIDO
    // =========================================

    public List<VueloDTO> findByOrigin(String origin) {
        return vuelosCrudRepository.findByOrigenIgnoreCase(origin)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    public List<VueloDTO> findByDestination(String destination) {
        return vuelosCrudRepository.findByDestinoIgnoreCase(destination)
                .stream().map(vueloMapper::toDTO).collect(Collectors.toList());
    }

    public boolean existsByCode(String codigoVuelo) {
        return vuelosCrudRepository.existsByCodigoVueloIgnoreCase(codigoVuelo);
    }

    public long countByRoute(String origin, String destination) {
        return vuelosCrudRepository.countByOrigenAndDestino(origin, destination);
    }
}