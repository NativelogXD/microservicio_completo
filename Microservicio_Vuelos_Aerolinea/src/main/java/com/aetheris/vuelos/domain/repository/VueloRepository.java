package com.aetheris.vuelos.domain.repository;

import com.aetheris.vuelos.dto.VueloDTO;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;
import java.util.Optional;

public interface VueloRepository {

    // =========================================
    // CRUD Operations
    // =========================================

    // Consultar todos los registros
    Iterable<VueloDTO> findAll();

    // Consultar por ID
    Optional<VueloDTO> findById(String id);

    // Consultar por código de vuelo
    Optional<VueloDTO> findByCode(String flightCode);

    // Guardar
    VueloDTO save(VueloDTO vueloDTO);

    // Actualizar
    VueloDTO update(VueloDTO vueloDTO);

    // Eliminar
    boolean deleteById(String id);

    // Validar si existe por ID
    boolean existsById(String id);

    // =========================================
    // Search / Querying
    // =========================================

    List<VueloDTO> findByRoute(String origin, String destination);
    List<VueloDTO> findByStatus(String status);
    List<VueloDTO> findByDate(LocalDate date);
    List<VueloDTO> findByDateRange(LocalDate start, LocalDate end);
    List<VueloDTO> findByPlane(String planeId);
    List<VueloDTO> findByPilot(String pilotId);
    List<VueloDTO> findByRouteAndDate(String origin, String destination, LocalDate date);
    List<VueloDTO> findByPriceRange(double min, double max);
    List<VueloDTO> findUpcomingFlights(LocalDate today, LocalTime currentTime, int hoursMargin);

    // =========================================
    // Seat Management
    // =========================================

    boolean hasAvailability(String flightId, int requestedSeats);
    boolean reserveSeats(String flightId, int seats);

    // =========================================
    // Flight State & Operations
    // =========================================

    boolean updateStatus(String flightId, String newStatus);
    boolean cancelFlight(String flightId);
    boolean reassignPlane(String flightId, String new_id_avion);

    // =========================================
    // Statistics
    // =========================================

    long countByStatus(String status);
    Optional<VueloDTO> findCheapestFlight();
    List<VueloDTO> findLongestFlights(int top);

    // Contar todos los registros
    long count();
}