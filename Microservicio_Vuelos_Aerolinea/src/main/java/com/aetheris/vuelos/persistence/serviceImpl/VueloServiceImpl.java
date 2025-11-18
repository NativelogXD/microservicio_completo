package com.aetheris.vuelos.persistence.serviceImpl;

import com.aetheris.vuelos.domain.repository.VueloRepository;
import com.aetheris.vuelos.domain.service.VueloService;
import com.aetheris.vuelos.dto.VueloDTO;
import com.aetheris.vuelos.exception.VueloFoundException;
import com.aetheris.vuelos.exception.VueloNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;
import java.util.Optional;

@Service
public class VueloServiceImpl implements VueloService {

    @Autowired
    private VueloRepository vueloRepository;

    // =========================================
    // CRUD Operations
    // =========================================

    @Override
    public Iterable<VueloDTO> getAllVuelos() {
        return vueloRepository.findAll();
    }

    @Override
    public Optional<VueloDTO> getVueloById(String id) {
        return vueloRepository.findById(id);
    }

    @Override
    public VueloDTO saveVuelo(VueloDTO vueloDTO) {
        // Validar que el código de vuelo no exista
        if (vueloDTO.getCodigoVuelo() != null &&
                vueloRepository.findByCode(vueloDTO.getCodigoVuelo()).isPresent()) {
            throw new VueloFoundException();
        }

        return vueloRepository.save(vueloDTO);
    }

    @Override
    public VueloDTO updateVuelo(VueloDTO vueloDTO) {
        // Verificar que el vuelo existe
        if (vueloDTO.getId() == null || !vueloRepository.existsById(vueloDTO.getId())) {
            throw new VueloNotFoundException("Vuelo", "Vuelo id", vueloDTO.getId());
        }

        return vueloRepository.update(vueloDTO);
    }

    @Override
    public void deleteVuelo(String id) {
        if (!vueloRepository.existsById(id)) {
            throw new VueloNotFoundException("Vuelo", "Vuelo id", id);
        }
        vueloRepository.deleteById(id);
    }

    @Override
    public long countVuelos() {
        return vueloRepository.count();
    }

    @Override
    public boolean existsVueloById(String id) {
        return vueloRepository.existsById(id);
    }

    // =========================================
    // Búsquedas específicas
    // =========================================

    @Override
    public Optional<VueloDTO> getVueloByCode(String codigoVuelo) {
        return vueloRepository.findByCode(codigoVuelo);
    }

    @Override
    public List<VueloDTO> getVuelosByRoute(String origen, String destino) {
        return vueloRepository.findByRoute(origen, destino);
    }

    @Override
    public List<VueloDTO> getVuelosByStatus(String estado) {
        return vueloRepository.findByStatus(estado);
    }

    @Override
    public List<VueloDTO> getVuelosByDate(LocalDate fecha) {
        return vueloRepository.findByDate(fecha);
    }

    @Override
    public List<VueloDTO> getVuelosByDateRange(LocalDate start, LocalDate end) {
        return vueloRepository.findByDateRange(start, end);
    }

    @Override
    public List<VueloDTO> getVuelosByPlane(String id_avion) {
        return vueloRepository.findByPlane(id_avion);
    }

    @Override
    public List<VueloDTO> getVuelosByPilot(String id_piloto) {
        return vueloRepository.findByPilot(id_piloto);
    }

    // =========================================
    // Búsquedas combinadas
    // =========================================

    @Override
    public List<VueloDTO> getVuelosByRouteAndDate(String origen, String destino, LocalDate fecha) {
        return vueloRepository.findByRouteAndDate(origen, destino, fecha);
    }

    @Override
    public List<VueloDTO> getVuelosByPriceRange(double minPrice, double maxPrice) {
        return vueloRepository.findByPriceRange(minPrice, maxPrice);
    }

    @Override
    public List<VueloDTO> getUpcomingFlights(LocalDate today, LocalTime currentTime, int hoursMargin) {
        return vueloRepository.findUpcomingFlights(today, currentTime, hoursMargin);
    }

    // =========================================
    // Gestión de asientos y operaciones
    // =========================================

    @Override
    public boolean checkAvailability(String vueloId, int asientosSolicitados) {
        if (!vueloRepository.existsById(vueloId)) {
            throw new VueloNotFoundException("Vuelo", "Vuelo id", vueloId);
        }
        return vueloRepository.hasAvailability(vueloId, asientosSolicitados);
    }

    @Override
    public boolean reserveSeats(String vueloId, int asientos) {
        if (!vueloRepository.existsById(vueloId)) {
            throw new VueloNotFoundException("Vuelo", "Vuelo id", vueloId);
        }
        return vueloRepository.reserveSeats(vueloId, asientos);
    }

    @Override
    public boolean updateFlightStatus(String vueloId, String nuevoEstado) {
        if (!vueloRepository.existsById(vueloId)) {
            throw new VueloNotFoundException("Vuelo", "Vuelo id",  vueloId);
        }

        // Validar que el estado sea uno de los permitidos
        if (!isValidStatus(nuevoEstado)) {
            throw new IllegalArgumentException("Estado no válido: " + nuevoEstado);
        }

        return vueloRepository.updateStatus(vueloId, nuevoEstado);
    }

    @Override
    public boolean cancelFlight(String vueloId) {
        if (!vueloRepository.existsById(vueloId)) {
            throw new VueloNotFoundException("Vuelo", "Vuelo id",  vueloId);
        }
        return vueloRepository.cancelFlight(vueloId);
    }

    @Override
    public boolean reassignPlane(String vueloId, String nuevo_id_avion) {
        if (!vueloRepository.existsById(vueloId)) {
            throw new VueloNotFoundException("Vuelo", "Vuelo id",  vueloId);
        }
        return vueloRepository.reassignPlane(vueloId, nuevo_id_avion);
    }

    // =========================================
    // Estadísticas y consultas especiales
    // =========================================

    @Override
    public long countVuelosByStatus(String estado) {
        return vueloRepository.countByStatus(estado);
    }

    @Override
    public Optional<VueloDTO> getCheapestFlight() {
        return vueloRepository.findCheapestFlight();
    }

    @Override
    public List<VueloDTO> getLongestFlights(int cantidad) {
        return vueloRepository.findLongestFlights(cantidad);
    }

    // =========================================
    // Métodos auxiliares privados
    // =========================================

    /**
     * Valida que el estado del vuelo sea uno de los permitidos
     */
    private boolean isValidStatus(String estado) {
        return estado != null &&
                (estado.equals("PROGRAMADO") ||
                        estado.equals("EN_VUELO") ||
                        estado.equals("ATERRIZADO") ||
                        estado.equals("CANCELADO"));
    }
}