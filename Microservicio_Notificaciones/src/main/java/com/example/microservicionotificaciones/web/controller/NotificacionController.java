package com.example.microservicionotificaciones.web.controller;

import com.example.microservicionotificaciones.domain.dto.NotificacionDTO;
import com.example.microservicionotificaciones.domain.service.NotificacionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;

@RestController
@RequestMapping("/api/notificaciones")
@Tag(name = "Notificaciones", description = "API para la gestion de notificaciones")
public class NotificacionController {

    @Autowired
    private NotificacionService notificacionService;

    //Obtener todas las notificaciones
    @Operation(summary = "Obtener todas las notificaciones", description = "Retorna una lista de notificaciones")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Listado de notificaciones", content = @Content(mediaType = "application/json", schema = @Schema(implementation = NotificacionDTO.class))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/all")
    public ResponseEntity<Iterable<NotificacionDTO>> getNotificaciones() {
        Iterable<NotificacionDTO> notificaciones = notificacionService.findAll();
        return ResponseEntity.ok(notificaciones);
    }

    //Obtener una notificacion por ID
    @Operation(summary = "Obtener una notificacion por el id proporcionado", description = "Retorna una notificacion segun el ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Notificacion encontrada", content =  @Content(schema = @Schema(implementation = NotificacionDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/{id}")
    public ResponseEntity<NotificacionDTO> getNotificacionPorId(@PathVariable @Parameter(description = "ID de la notificacion") Long id) {
        NotificacionDTO notificacion = notificacionService.findById(id);
        return ResponseEntity.ok(notificacion);
    }

    //Guardar una notificacion
    @Operation(summary = "Crear nueva notificacion", description = "Guardar una nueva notificacion en el sistema")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Notificacion creada exitosamente", content = @Content(schema = @Schema(implementation = NotificacionDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @PostMapping("/save")
    public  ResponseEntity<NotificacionDTO> saveNotificacion(@RequestBody @Parameter(description = "Datos de la notificacion") NotificacionDTO notificacion) throws IOException, InterruptedException {
        NotificacionDTO saveNotificacion = notificacionService.save(notificacion);
        return ResponseEntity.status(HttpStatus.CREATED).body(saveNotificacion);
    }

    //Eliminar una notificacion
    @Operation(summary = "Eliminar una notificacion por ID", description = " Elimina una notificacion segun el ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Notificacion eliminada exitosamente", content = @Content),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    public  ResponseEntity<Void> deleteNotificacion(@PathVariable @Parameter(description = "Id de la notificacion") Long id) {
        notificacionService.deleteById(id);
        return ResponseEntity.ok().build();
    }

    //Contar notificaciones
    @Operation(summary = "Contar la cantidad de notificaciones", description = "Retorna el total de notificaciones en el sistema")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Cantidad de registrs", content = @Content(mediaType = "application/json"))
    })
    @GetMapping("/count")
    public ResponseEntity<Long> getCount() {
        long count = notificacionService.countNotificaciones();
        return ResponseEntity.ok(count);
    }

    //Obtener notificaciones por ID de la persona
    @Operation(summary = "Obtener todas las notificaciones segun el id de la persona", description = "Retorna una lista de notificaciones segun el ID proporcionado")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Listado de notificaciones", content = @Content(mediaType = "application/json", schema = @Schema(implementation = NotificacionDTO.class))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/all/{id}")
    public ResponseEntity<Iterable<NotificacionDTO>> getNotificacionesById(@PathVariable @Parameter(description = "ID de la persona") Long id) {
        Iterable<NotificacionDTO> notificaciones = notificacionService.findAllByPersonaId(id);
        return ResponseEntity.ok(notificaciones);
    }
}
