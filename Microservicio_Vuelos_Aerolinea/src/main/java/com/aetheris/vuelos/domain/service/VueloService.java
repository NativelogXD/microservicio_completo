package com.aetheris.vuelos.domain.service;

import com.aetheris.vuelos.dto.VueloDTO;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;
import java.util.Optional;

public interface VueloService {

    // =========================================
    // CRUD Operations
    // =========================================

    Iterable<VueloDTO> getAllVuelos();

    Optional<VueloDTO> getVueloById(String id);

    VueloDTO saveVuelo(VueloDTO vueloDTO);

    VueloDTO updateVuelo(VueloDTO vueloDTO);

    void deleteVuelo(String id);

    long countVuelos();

    // =========================================
    // Búsquedas específicas
    // =========================================

    Optional<VueloDTO> getVueloByCode(String codigoVuelo);

    List<VueloDTO> getVuelosByRoute(String origen, String destino);

    List<VueloDTO> getVuelosByStatus(String estado);

    List<VueloDTO> getVuelosByDate(LocalDate fecha);

    List<VueloDTO> getVuelosByDateRange(LocalDate start, LocalDate end);

    List<VueloDTO> getVuelosByPlane(String id_avion);

    List<VueloDTO> getVuelosByPilot(String id_piloto);

    // =========================================
    // Búsquedas combinadas
    // =========================================

    List<VueloDTO> getVuelosByRouteAndDate(String origen, String destino, LocalDate fecha);

    List<VueloDTO> getVuelosByPriceRange(double minPrice, double maxPrice);

    List<VueloDTO> getUpcomingFlights(LocalDate today, LocalTime currentTime, int hoursMargin);

    // =========================================
    // Gestión de asientos y operaciones
    // =========================================

    boolean checkAvailability(String vueloId, int asientosSolicitados);

    boolean reserveSeats(String vueloId, int asientos);

    boolean updateFlightStatus(String vueloId, String nuevoEstado);

    boolean cancelFlight(String vueloId);

    boolean reassignPlane(String vueloId, String nuevo_id_avion);

    // =========================================
    // Estadísticas y consultas especiales
    // =========================================

    long countVuelosByStatus(String estado);

    Optional<VueloDTO> getCheapestFlight();

    List<VueloDTO> getLongestFlights(int cantidad);

    boolean existsVueloById(String id);
}