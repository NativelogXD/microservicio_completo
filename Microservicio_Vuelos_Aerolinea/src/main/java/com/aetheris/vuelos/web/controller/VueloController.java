package com.aetheris.vuelos.web.controller;

import com.aetheris.vuelos.dto.VueloDTO;
import com.aetheris.vuelos.domain.service.VueloService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/vuelos")
@Tag(name = "Gestión de Vuelos", description = "API para la gestión completa de vuelos")
public class VueloController {

    @Autowired
    private VueloService vueloService;

    // =========================================
    // OPERACIONES CRUD
    // =========================================

    @GetMapping
    @Operation(summary = "Obtener todos los vuelos", description = "Retorna una lista de todos los vuelos registrados en el sistema")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Vuelos obtenidos exitosamente"),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor")
    })
    public ResponseEntity<Iterable<VueloDTO>> obtenerTodosLosVuelos() {
        Iterable<VueloDTO> vuelos = vueloService.getAllVuelos();
        return ResponseEntity.ok(vuelos);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener vuelo por ID", description = "Retorna un vuelo específico basado en su ID único")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Vuelo encontrado exitosamente"),
            @ApiResponse(responseCode = "404", description = "Vuelo no encontrado"),
            @ApiResponse(responseCode = "400", description = "ID inválido")
    })
    public ResponseEntity<VueloDTO> obtenerVueloPorId(
            @PathVariable @Parameter(description = "ID único del vuelo", example = "123e4567-e89b-12d3-a456-426614174000") String id) {
        Optional<VueloDTO> vuelo = vueloService.getVueloById(id);
        return vuelo.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/codigo/{codigoVuelo}")
    @Operation(summary = "Obtener vuelo por código", description = "Retorna un vuelo específico basado en su código de vuelo")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Vuelo encontrado exitosamente"),
            @ApiResponse(responseCode = "404", description = "Vuelo no encontrado")
    })
    public ResponseEntity<VueloDTO> obtenerVueloPorCodigo(
            @PathVariable @Parameter(description = "Código del vuelo", example = "AV1234") String codigoVuelo) {
        Optional<VueloDTO> vuelo = vueloService.getVueloByCode(codigoVuelo);
        return vuelo.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    @Operation(summary = "Crear nuevo vuelo", description = "Crea un nuevo vuelo con los datos proporcionados")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "201", description = "Vuelo creado exitosamente"),
            @ApiResponse(responseCode = "400", description = "Datos del vuelo inválidos"),
            @ApiResponse(responseCode = "409", description = "El código de vuelo ya existe")
    })
    public ResponseEntity<VueloDTO> crearVuelo(
            @Valid @RequestBody @Parameter(description = "Datos del vuelo a crear") VueloDTO vueloDTO) {
        VueloDTO nuevoVuelo = vueloService.saveVuelo(vueloDTO);
        return new ResponseEntity<>(nuevoVuelo, HttpStatus.CREATED);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Actualizar vuelo existente", description = "Actualiza un vuelo existente con los nuevos datos proporcionados")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Vuelo actualizado exitosamente"),
            @ApiResponse(responseCode = "404", description = "Vuelo no encontrado"),
            @ApiResponse(responseCode = "400", description = "Datos inválidos")
    })
    public ResponseEntity<VueloDTO> actualizarVuelo(
            @PathVariable @Parameter(description = "ID único del vuelo") String id,
            @Valid @RequestBody @Parameter(description = "Datos actualizados del vuelo") VueloDTO vueloDTO) {

        // Asegurar que el ID del path coincida con el ID del body
        vueloDTO.setId(id);
        VueloDTO vueloActualizado = vueloService.updateVuelo(vueloDTO);
        return ResponseEntity.ok(vueloActualizado);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Eliminar vuelo", description = "Elimina un vuelo existente del sistema")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "204", description = "Vuelo eliminado exitosamente"),
            @ApiResponse(responseCode = "404", description = "Vuelo no encontrado")
    })
    public ResponseEntity<Void> eliminarVuelo(
            @PathVariable @Parameter(description = "ID único del vuelo a eliminar") String id) {
        vueloService.deleteVuelo(id);
        return ResponseEntity.noContent().build();
    }

    // =========================================
    // BÚSQUEDAS Y CONSULTAS
    // =========================================

    @GetMapping("/ruta/{origen}/{destino}")
    @Operation(summary = "Buscar vuelos por ruta", description = "Retorna vuelos que coincidan con el origen y destino especificados")
    public ResponseEntity<List<VueloDTO>> buscarVuelosPorRuta(
            @PathVariable @Parameter(description = "Ciudad/país de origen", example = "BOG") String origen,
            @PathVariable @Parameter(description = "Ciudad/país de destino", example = "MDE") String destino) {

        List<VueloDTO> vuelos = vueloService.getVuelosByRoute(origen, destino);
        return ResponseEntity.ok(vuelos);
    }

    @GetMapping("/estado/{estado}")
    @Operation(summary = "Buscar vuelos por estado", description = "Retorna vuelos que coincidan con el estado especificado")
    public ResponseEntity<List<VueloDTO>> buscarVuelosPorEstado(
            @PathVariable @Parameter(description = "Estado del vuelo", example = "PROGRAMADO") String estado) {

        List<VueloDTO> vuelos = vueloService.getVuelosByStatus(estado);
        return vuelos.isEmpty() ? ResponseEntity.noContent().build() : ResponseEntity.ok(vuelos);
    }

    @GetMapping("/fecha/{fecha}")
    @Operation(summary = "Buscar vuelos por fecha", description = "Retorna vuelos programados para una fecha específica")
    public ResponseEntity<List<VueloDTO>> buscarVuelosPorFecha(
            @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            @Parameter(description = "Fecha del vuelo (YYYY-MM-DD)", example = "2024-01-15") LocalDate fecha) {

        List<VueloDTO> vuelos = vueloService.getVuelosByDate(fecha);
        return vuelos.isEmpty() ? ResponseEntity.noContent().build() : ResponseEntity.ok(vuelos);
    }

    @GetMapping("/rango-fechas")
    @Operation(summary = "Buscar vuelos por rango de fechas", description = "Retorna vuelos programados dentro de un rango de fechas")
    public ResponseEntity<List<VueloDTO>> buscarVuelosPorRangoFechas(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            @Parameter(description = "Fecha de inicio (YYYY-MM-DD)") LocalDate inicio,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            @Parameter(description = "Fecha de fin (YYYY-MM-DD)") LocalDate fin) {

        List<VueloDTO> vuelos = vueloService.getVuelosByDateRange(inicio, fin);
        return vuelos.isEmpty() ? ResponseEntity.noContent().build() : ResponseEntity.ok(vuelos);
    }

    @GetMapping("/busqueda")
    @Operation(summary = "Búsqueda avanzada de vuelos", description = "Búsqueda flexible de vuelos con múltiples parámetros")
    public ResponseEntity<List<VueloDTO>> busquedaAvanzada(
            @RequestParam(required = false) @Parameter(description = "Ciudad/país de origen") String origen,
            @RequestParam(required = false) @Parameter(description = "Ciudad/país de destino") String destino,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            @Parameter(description = "Fecha específica del vuelo") LocalDate fecha,
            @RequestParam(required = false) @Parameter(description = "Estado del vuelo") String estado,
            @RequestParam(required = false, name = "id_avion") @Parameter(description = "ID del avión") String id_avion,
            @RequestParam(required = false, name = "id_piloto") @Parameter(description = "ID del piloto") String id_piloto) {

        // Implementar lógica de búsqueda combinada según los parámetros proporcionados
        if (origen != null && destino != null && fecha != null) {
            return ResponseEntity.ok(vueloService.getVuelosByRouteAndDate(origen, destino, fecha));
        } else if (origen != null && destino != null) {
            return ResponseEntity.ok(vueloService.getVuelosByRoute(origen, destino));
        } else if (fecha != null) {
            return ResponseEntity.ok(vueloService.getVuelosByDate(fecha));
        } else if (estado != null) {
            return ResponseEntity.ok(vueloService.getVuelosByStatus(estado));
        } else if (id_avion != null) {
            return ResponseEntity.ok(vueloService.getVuelosByPlane(id_avion));
        } else if (id_piloto != null) {
            return ResponseEntity.ok(vueloService.getVuelosByPilot(id_piloto));
        } else {
            return ResponseEntity.badRequest().build();
        }
    }

    // =========================================
    // OPERACIONES DE NEGOCIO
    // =========================================

    @PatchMapping("/{id}/estado")
    @Operation(summary = "Actualizar estado del vuelo", description = "Actualiza el estado de un vuelo existente")
    public ResponseEntity<Void> actualizarEstadoVuelo(
            @PathVariable String id,
            @RequestParam @Parameter(description = "Nuevo estado del vuelo") String nuevoEstado) {

        boolean actualizado = vueloService.updateFlightStatus(id, nuevoEstado);
        return actualizado ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
    }

    @PostMapping("/{id}/cancelar")
    @Operation(summary = "Cancelar vuelo", description = "Cancela un vuelo existente")
    public ResponseEntity<Void> cancelarVuelo(
            @PathVariable @Parameter(description = "ID del vuelo a cancelar") String id) {

        boolean cancelado = vueloService.cancelFlight(id);
        return cancelado ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
    }

    @PostMapping("/{id}/reasignar-avion")
    @Operation(summary = "Reasignar avión", description = "Reasigna un avión diferente a un vuelo")
    public ResponseEntity<Void> reasignarAvion(
            @PathVariable String id,
            @RequestParam(name = "nuevo_id_avion") @Parameter(description = "ID del nuevo avión") String nuevo_id_avion) {

        boolean reasignado = vueloService.reassignPlane(id, nuevo_id_avion);
        return reasignado ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
    }

    @GetMapping("/{id}/disponibilidad")
    @Operation(summary = "Verificar disponibilidad", description = "Verifica la disponibilidad de asientos en un vuelo")
    public ResponseEntity<Boolean> verificarDisponibilidad(
            @PathVariable String id,
            @RequestParam @Parameter(description = "Número de asientos solicitados") int asientos) {

        boolean disponible = vueloService.checkAvailability(id, asientos);
        return ResponseEntity.ok(disponible);
    }

    @PostMapping("/{id}/reservar-asientos")
    @Operation(summary = "Reservar asientos", description = "Reserva una cantidad específica de asientos en un vuelo")
    public ResponseEntity<Boolean> reservarAsientos(
            @PathVariable String id,
            @RequestParam @Parameter(description = "Número de asientos a reservar") int asientos) {

        boolean reservado = vueloService.reserveSeats(id, asientos);
        return reservado ? ResponseEntity.ok(true) : ResponseEntity.badRequest().body(false);
    }

    // =========================================
    // CONSULTAS ESPECIALES Y ESTADÍSTICAS
    // =========================================

    @GetMapping("/proximos")
    @Operation(summary = "Próximos vuelos", description = "Retorna los vuelos programados para las próximas horas")
    public ResponseEntity<List<VueloDTO>> obtenerProximosVuelos(
            @RequestParam(defaultValue = "6") @Parameter(description = "Margen de horas hacia adelante") int horas) {

        LocalDate hoy = LocalDate.now();
        LocalTime ahora = LocalTime.now();
        List<VueloDTO> vuelos = vueloService.getUpcomingFlights(hoy, ahora, horas);
        return ResponseEntity.ok(vuelos);
    }

    @GetMapping("/mas-barato")
    @Operation(summary = "Vuelo más económico", description = "Retorna el vuelo con el precio más bajo")
    public ResponseEntity<VueloDTO> obtenerVueloMasBarato() {
        Optional<VueloDTO> vuelo = vueloService.getCheapestFlight();
        return vuelo.map(ResponseEntity::ok)
                .orElse(ResponseEntity.noContent().build());
    }

    @GetMapping("/mas-largos")
    @Operation(summary = "Vuelos más largos", description = "Retorna los vuelos con mayor duración")
    public ResponseEntity<List<VueloDTO>> obtenerVuelosMasLargos(
            @RequestParam(defaultValue = "5") @Parameter(description = "Número de vuelos a retornar") int cantidad) {

        List<VueloDTO> vuelos = vueloService.getLongestFlights(cantidad);
        return ResponseEntity.ok(vuelos);
    }

    @GetMapping("/estadisticas/total")
    @Operation(summary = "Total de vuelos", description = "Retorna el número total de vuelos registrados")
    public ResponseEntity<Long> obtenerTotalVuelos() {
        long total = vueloService.countVuelos();
        return ResponseEntity.ok(total);
    }

    @GetMapping("/estadisticas/estado/{estado}")
    @Operation(summary = "Conteo por estado", description = "Retorna el número de vuelos por estado")
    public ResponseEntity<Long> obtenerConteoPorEstado(@PathVariable String estado) {
        long conteo = vueloService.countVuelosByStatus(estado);
        return ResponseEntity.ok(conteo);
    }
}
