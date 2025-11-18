package com.example.servicio1.web.controller;

import com.example.servicio1.domain.dto.UpdatePasswordRequest;
import com.example.servicio1.domain.dto.UsuarioDTO;
import com.example.servicio1.domain.service.UsuarioService;
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
import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/usuarios")
@Tag(name = "Usuarios", description = "API para la gestion de usuarios")
public class UsuarioController {

    @Autowired
    private UsuarioService usuarioService;

    //Obtener todos los usuarios
    @Operation(summary = "Obtener todos los usuarios", description = "Retorna una lista de usuarios")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200"),
            @ApiResponse(responseCode = "500")
    })
    @GetMapping("/all")
    public ResponseEntity<Iterable<UsuarioDTO>> getAllUsuarios() {
        Iterable<UsuarioDTO> usuarios = usuarioService.getAllUsuarios();
        return ResponseEntity.ok(usuarios);
    }

    //Obtener usuario por ID
    @Operation(summary = "Obtener usuario por ID", description = "Retorna un admin segun el ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Usuario encontrado", content = @Content(mediaType = "application/json", schema = @Schema(implementation = UsuarioDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/{id}")
    public ResponseEntity<UsuarioDTO> getUsuarioById(@PathVariable @Parameter(description = "ID del usuario") long id) {
        UsuarioDTO usuario = usuarioService.getUsuarioById(id);
        return ResponseEntity.ok(usuario);
    }

    //Guardar un usuario
    @Operation(summary = "Crear un nuevo usuario", description = "Guardar un nuevo usuario")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Usuario creado exitosamente", content = @Content(mediaType = "application/json", schema = @Schema(implementation = UsuarioDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @PostMapping("/save")
    public ResponseEntity<UsuarioDTO> saveUsuario(@Valid @RequestBody @Parameter(description = "Datos del usuario") UsuarioDTO usuario) {
        UsuarioDTO usuarioDTO = usuarioService.saveUsuario(usuario);
        return ResponseEntity.status(HttpStatus.CREATED).body(usuarioDTO);
    }

    //Actualizar un usuario
    @Operation(summary = "Actualizar un usuario por ID", description = "Actializa los datos de un usuario existente")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Usuario actualizado correctamente", content =  @Content(mediaType = "application/json", schema = @Schema(implementation = UsuarioDTO.class))),
            @ApiResponse(responseCode = "400", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "404", description = "Usuario no encontrado", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @PutMapping("update/{id}")
    public ResponseEntity<UsuarioDTO> updateUsuario(@RequestBody @Parameter(description = "Datos actualizados del usuario") UsuarioDTO usuario,
                                                    @PathVariable @Parameter(description = "ID del usuario") long id) {
        usuario.setId(id);
        UsuarioDTO usuarioDTO = usuarioService.updateUsuario(usuario);
        return ResponseEntity.ok(usuarioDTO);
    }

    //Actualizar contraseña de un usuario por ID
    @Operation(summary = "Actualizar contraseña de usuario por ID", description = "Actualiza la contraseña de un usuaio existente")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Usuario actualizado correctamente", content =  @Content(mediaType = "application/json", schema = @Schema(implementation = UsuarioDTO.class))),
            @ApiResponse(responseCode = "400", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "404", description = "Usuario no encontrado", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @PatchMapping("/updatePassword/{id}")
    public ResponseEntity<UsuarioDTO> updatePassword(@PathVariable @Parameter(description = "ID del usuario") long id,
                                                     @Valid @RequestBody @Parameter(description = "Contraseña actualizada")UpdatePasswordRequest updatePasswordRequest){
        UsuarioDTO updateUsuario = usuarioService.PutContrasenia(id,updatePasswordRequest.getPassword());
        return ResponseEntity.ok(updateUsuario);
    }

    //Eliminar un usuario
    @Operation(summary = "Eliminar un usuario por ID", description = "Elimina un usuario del sistema segun el ID")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Usuario eliminado correctamente", content = @Content),
            @ApiResponse(responseCode = "404", description = "Usuario no encontrado", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @DeleteMapping("/delete/{id}")
    public ResponseEntity<UsuarioDTO> deleteUsuario(@PathVariable @Parameter(description = "ID del usuario") long id) {
        usuarioService.deleteUsuario(id);
        return  ResponseEntity.ok().build();
    }

    //Contar el numero total de admins
    @Operation(summary = "Contar la cantidad total de usuarios", description = "Retorna el total de usuarios")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Cantidad de registros", content = @Content(mediaType = "application/json"))
    })
    @GetMapping("/count")
    public ResponseEntity<Long> count() {
        long count = usuarioService.countUsuarios();
        return ResponseEntity.ok(count);
    }

    //Obtener un usuario por email
    @Operation(summary = "Obtener un usuario por email proporcionado", description = "Retorna un usuario segun el email")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Usuario encontrado", content = @Content(mediaType = "application/json", schema = @Schema(implementation = UsuarioDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/email/{email}")
    public ResponseEntity<UsuarioDTO> getUsuarioByEmail(@PathVariable @Parameter(description = "Email del usuario") String email) {
        UsuarioDTO usuarioDTO = usuarioService.getUsuarioByEmail(email);
        return ResponseEntity.ok(usuarioDTO);
    }

    //Obtener un usuario por cedula
    @Operation(summary = "Obtener un usuario por cedula proporcionada", description = "Retorna un usuario segun la cedula")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Usuario encontrado", content = @Content(mediaType = "application/json", schema = @Schema(implementation = UsuarioDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/cedula/{cedula}")
    public ResponseEntity<UsuarioDTO> getUsuarioByECedula(@PathVariable @Parameter(description = "Cedula del usuario") String cedula) {
        UsuarioDTO usuarioDTO = usuarioService.getUsuarioByCedula(cedula);
        return ResponseEntity.ok(usuarioDTO);
    }


}
