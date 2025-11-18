package com.example.MicroService_Reserva.persistencia.controller;

import com.example.MicroService_Reserva.domain.dto.ReservaDTO;
import com.example.MicroService_Reserva.persistencia.Entity.EstadoReserva;
import com.example.MicroService_Reserva.persistencia.Entity.Reserva;
import com.example.MicroService_Reserva.persistencia.Excepciones.ReservaInvalidaException;
import com.example.MicroService_Reserva.persistencia.Excepciones.ReservaNoEncontradaException;
import com.example.MicroService_Reserva.persistencia.Excepciones.ReservaYaActivaException;
import com.example.MicroService_Reserva.persistencia.service.ReservaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/reservas")
@Tag(name = "Reservas", description = "API para la gestión de reservas")
public class ReservaController {

    private final ReservaService reservaService;

    @Autowired
    public ReservaController(ReservaService reservaService) {
        this.reservaService = reservaService;
    }

    // ----------- CRUD PRINCIPAL -----------

    @GetMapping
    @Operation(summary = "Obtener todos los registros de reservas", description = "Devuelve una lista completa de todas las reservas existentes en el sistema. Útil para obtener todos los datos o registros de reservas.")
    public ResponseEntity<List<ReservaDTO>> getAllReservas() {
        List<ReservaDTO> reservas = reservaService.findAll();
        return ResponseEntity.ok(reservas);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtener reserva por ID")
    public ResponseEntity<ReservaDTO> getReservaById(
            @PathVariable @Parameter(description = "ID de la reserva") String id) {
        try {
            ReservaDTO reserva = reservaService.findById(id);
            return ResponseEntity.ok(reserva);
        } catch (ReservaNoEncontradaException e) {
            return ResponseEntity.notFound().build();
        }
    }

    @PostMapping
    @Operation(summary = "Crear nueva reserva")
    public ResponseEntity<ReservaDTO> guardarReserva(
            @RequestBody @Parameter(description = "Datos de la reserva") ReservaDTO reservaDTO) {
        try {
            ReservaDTO nuevaReserva = reservaService.save(reservaDTO);
            return ResponseEntity.status(HttpStatus.CREATED).body(nuevaReserva);
        } catch (ReservaInvalidaException | ReservaYaActivaException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @PutMapping("/{id}")
    @Operation(summary = "Actualizar una reserva")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Reserva actualizada exitosamente"),
            @ApiResponse(responseCode = "404", description = "Reserva no encontrada"),
            @ApiResponse(responseCode = "400", description = "Datos de reserva inválidos")
    })
    public ResponseEntity<ReservaDTO> actualizarReserva(
            @PathVariable @Parameter(description = "ID de la reserva") String id,
            @RequestBody @Parameter(description = "Datos actualizados de la reserva") ReservaDTO reservaDTO) {
        try {
            // Asegurar que el ID del DTO coincida con el ID del path
            reservaDTO.setId(id);
            ReservaDTO reservaActualizada = reservaService.update(reservaDTO);
            return ResponseEntity.ok(reservaActualizada);
        } catch (ReservaNoEncontradaException e) {
            return ResponseEntity.notFound().build();
        } catch (ReservaInvalidaException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Eliminar una reserva")
    @ApiResponses({
            @ApiResponse(responseCode = "204", description = "Reserva eliminada exitosamente"),
            @ApiResponse(responseCode = "404", description = "Reserva no encontrada")
    })
    public ResponseEntity<Void> eliminarReserva(
            @PathVariable @Parameter(description = "ID de la reserva") String id) {
        reservaService.deleteById(id);
        return ResponseEntity.noContent().build();
    }

    // ----------- BÚSQUEDAS -----------

    @GetMapping("/buscar/usuario")
    @Operation(summary = "Buscar reservas por usuario")
    public ResponseEntity<List<ReservaDTO>> buscarPorUsuario(
            @RequestParam @Parameter(description = "Nombre del usuario") String usuario) {
        return ResponseEntity.ok(reservaService.buscarPorUsuario(usuario));
    }

    @GetMapping("/buscar/estado")
    @Operation(summary = "Buscar reservas por estado")
    public ResponseEntity<List<ReservaDTO>> buscarPorEstado(
            @RequestParam @Parameter(description = "Estado de la reserva") String estado) {
        return ResponseEntity.ok(reservaService.buscarPorEstado(estado));
    }

    @GetMapping("/buscar/vuelo")
    @Operation(summary = "Buscar reservas por vuelo")
    public ResponseEntity<List<ReservaDTO>> buscarPorVuelo(
            @RequestParam @Parameter(description = "ID del vuelo") String id_vuelo) {
        return ResponseEntity.ok(reservaService.buscarPorVuelo(id_vuelo));
    }

    // ----------- ESTADÍSTICAS -----------

    @GetMapping("/contar")
    @Operation(summary = "Contar total de reservas")
    public ResponseEntity<Long> contarReservas() {
        return ResponseEntity.ok(reservaService.count());
    }

    @GetMapping("/contar/estado")
    @Operation(summary = "Contar reservas por estado")
    public ResponseEntity<List<ReservaDTO>> contarPorEstado(
            @RequestParam @Parameter(description = "Estado de la reserva") String estado) {
        return ResponseEntity.ok(reservaService.buscarPorEstado(String.valueOf(EstadoReserva.valueOf(estado.toUpperCase()))));
    }
}
