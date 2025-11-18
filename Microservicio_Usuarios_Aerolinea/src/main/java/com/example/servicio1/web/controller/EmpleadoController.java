package com.example.servicio1.web.controller;

import com.example.servicio1.domain.dto.EmpleadoDTO;
import com.example.servicio1.domain.dto.UpdatePasswordRequest;
import com.example.servicio1.domain.dto.UsuarioDTO;
import com.example.servicio1.domain.service.EmpleadoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/empleados")
@Tag(name = "Empleados", description = "API para la gestion de empleados")
public class EmpleadoController {

    @Autowired
    private EmpleadoService empleadoService;

    //Obtener todos los empleados
    @Operation(summary = "Obtener todos los empleados", description = "Retorna una lista de empleados")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Listado de empleados", content = @Content(mediaType = "application/json", schema = @Schema(implementation = UsuarioDTO.class))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/all")
    public ResponseEntity<Iterable<EmpleadoDTO>> getAllEmpleados(){
        Iterable<EmpleadoDTO> empleados = empleadoService.getAllEmpleados();
        return ResponseEntity.ok(empleados);
    }

    //Obtener un empleado por ID
    @Operation(summary = "Obtener un empleado por ID proporcionado", description = "Retorna un empleado segun el ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Empleado encontrado", content = @Content(mediaType = "application/json", schema = @Schema(implementation = EmpleadoDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content =  @Content)
    })
    @GetMapping("/{id}")
    public ResponseEntity<EmpleadoDTO> getEmpleadoById(@PathVariable @Parameter(description = "ID del empleado") Long id){
        EmpleadoDTO empleado = empleadoService.getEmpleadoById(id);
        return ResponseEntity.ok(empleado);
    }

    //Guardar un empleado
    @Operation(summary = "Crear un nuevo empleado", description = "Guardar un nuevo empleado en el sistema")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Empleado creado exitosamente", content = @Content(mediaType = "application/json", schema = @Schema(implementation = EmpleadoDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @PostMapping("/save")
    public ResponseEntity<EmpleadoDTO> saveEmpleado(@RequestBody @Parameter(description = "Datos de empleado") EmpleadoDTO empleado){
        EmpleadoDTO saveEmpleado = empleadoService.saveEmpleado(empleado);
        return ResponseEntity.status(HttpStatus.CREATED).body(saveEmpleado);
    }

    //Actualizar un empleado por ID
    @Operation(summary = "Actualizar un empleado por ID", description = "Actualiza un empleado existente por ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200",description = "Empleado actualizado exitosamente", content = @Content(mediaType = "application/json", schema = @Schema(implementation = EmpleadoDTO.class))),
            @ApiResponse(responseCode = "400", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "404", description = "Empleado no encontrado", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @PutMapping("/update/{id}")
    public ResponseEntity<EmpleadoDTO> updateEmpleado(@PathVariable @Parameter(description = "ID del empleado") Long id,
                                                                     @RequestBody @Parameter(description = "Datos del empleado actualizado") EmpleadoDTO empleado){
        empleado.setId(id);
        EmpleadoDTO updateEmpleado = empleadoService.updateEmpleado(empleado);
        return ResponseEntity.ok(updateEmpleado);
    }

    //Actualizar contraseña de empleado por ID
    @Operation(summary = "Actualizar la contraseña del empleado por ID", description = "Actualiza un empleado existente por id")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200",description = "Empleado actualizado exitosamente", content = @Content(mediaType = "application/json", schema = @Schema(implementation = EmpleadoDTO.class))),
            @ApiResponse(responseCode = "400", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "404", description = "Empleado no encontrado", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @PatchMapping("/updatePassword/{id}")
    public ResponseEntity<EmpleadoDTO> updatePassword(@PathVariable @Parameter(description = "ID del empleado") Long id,
                                                      @Valid @RequestBody @Parameter(description = "Contraseña actualizada")UpdatePasswordRequest passwordRequest){
        EmpleadoDTO updateEmpleado = empleadoService.PutContrasenia(id,passwordRequest.getPassword());
        return ResponseEntity.ok(updateEmpleado);
    }

    //Eliminar un empleado
    @Operation(summary = "Eliminar un empleado por ID", description = "Elimina un empleado segun el ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Empleado eliminado correctamente", content = @Content),
            @ApiResponse(responseCode = "404", description = "Empleado no encontrado", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @DeleteMapping("/delete/{id}")
    public ResponseEntity<EmpleadoDTO> deleteEmpleadoById(@PathVariable @Parameter(description = "ID del empleado") Long id){
        empleadoService.deleteEmpleado(id);
        return ResponseEntity.ok().build();
    }

    //Contar el numero total de empleados
    @Operation(summary = "Contar la cantidad de empleados", description = "Retorna el total de empleados registrados")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Cantidad de registros", content = @Content(mediaType = "application/json"))
    })
    @GetMapping("/count")
    public ResponseEntity<Long> getEmpleadoCount(){
        long count = empleadoService.countEmpleado();
        return ResponseEntity.ok(count);
    }

    //Obtener un empleado por email
    @Operation(summary = "Obtener un empleado por email proporcionado", description = "Retorna un empleado segun el email")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Empleado encontrado", content = @Content(mediaType = "application/json", schema = @Schema(implementation = EmpleadoDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/email/{email}")
    public ResponseEntity<EmpleadoDTO> getEmpleadoByEmail(@PathVariable @Parameter(description = "Email del empleado") String email) {
        EmpleadoDTO empleadoDTO = empleadoService.getEmpleadoByEmail(email);
        return ResponseEntity.ok(empleadoDTO);
    }

    //Obtener un empleado por cedula
    @Operation(summary = "Obtener un empleado por cedula proporcionada", description = "Retorna un empleado segun la cedula")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Empleado encontrado", content = @Content(mediaType = "application/json", schema = @Schema(implementation = EmpleadoDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/cedula/{cedula}")
    public ResponseEntity<EmpleadoDTO> getEmpleadoByECedula(@PathVariable @Parameter(description = "Cedula del empleado") String cedula) {
        EmpleadoDTO empleadoDTO = empleadoService.getEmpleadoByCedula(cedula);
        return ResponseEntity.ok(empleadoDTO);
    }

    //Obtener un empleado por su cargo
    @Operation(summary = "Obtener un empleado por cargo proporcionado", description = "Retorna un empleado segun su cargo")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Empleado encontrado", content = @Content(mediaType = "application/json", schema = @Schema(implementation = EmpleadoDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/cargo/{cargo}")
    public ResponseEntity<EmpleadoDTO> getEmpleadoByCargo(@PathVariable @Parameter(description = "Cargo del empleado") String cargo) {
        EmpleadoDTO empleadoDTO = empleadoService.getEmpleadoByCargo(cargo);
        return ResponseEntity.ok(empleadoDTO);
    }

}
