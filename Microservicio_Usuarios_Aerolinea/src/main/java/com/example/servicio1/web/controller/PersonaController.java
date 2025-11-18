package com.example.servicio1.web.controller;

import com.example.servicio1.configs.token.JwtUtil;
import com.example.servicio1.domain.dto.LoginRequest;
import com.example.servicio1.domain.dto.PersonaDTO;
import com.example.servicio1.domain.dto.UpdatePasswordRequest;
import com.example.servicio1.domain.service.PersonaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@RestController
@RequestMapping("/api/personas")
@Tag(name = "Personas", description = "API para la gestion de personas")
public class PersonaController {

    @Autowired
    private PersonaService personaService;

    @Autowired
    private JwtUtil jwtUtil;

    @Value("${app.security.cookie.secure:false}")
    private boolean cookieSecure;

    @Value("${app.security.cookie.same-site:Strict}")
    private String cookieSameSite;

    // Obtener todas las personas
    @Operation(summary = "obtener todas las personas", description = "Retorna una lista de las personas registradas")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Listado de personas", content = @Content(mediaType = "application/json", schema = @Schema(implementation = PersonaDTO.class))),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/all")
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<Iterable<PersonaDTO>> getAllPersonas(){
        Iterable<PersonaDTO> personas = personaService.getAllPersonas();
        return ResponseEntity.ok(personas);
    }

    //Obtener la Persona por ID
    @Operation(summary = "Obtener una persona por ID", description = "Retorna la persona correspondiente al ID proporcionado")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Persona encontrada", content = @Content(mediaType = "application/json", schema = @Schema(implementation = PersonaDTO.class))),
            @ApiResponse(responseCode = "404", description = "Persona no encontrada", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/{id}")
    public ResponseEntity<PersonaDTO> getPersonaById(@PathVariable @Parameter(description = "ID de la persona") Long id){
        Optional<PersonaDTO> personaOpt = personaService.getPersonaById(id);
        PersonaDTO personaDTO = personaOpt.orElseThrow(
                () -> new RuntimeException("No se encontro el persona con el ID " + id)
        );
        return  ResponseEntity.ok(personaDTO);
    }

    //Guardar una nueva persona
    @Operation(summary = "Crear una nueva persona", description = "Guarda una nueva persona en el sistema")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Persona creada exitosamente", content = @Content(mediaType = "application/json", schema = @Schema(implementation = PersonaDTO.class))),
            @ApiResponse(responseCode = "404", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidar", content = @Content)
    })
    @PostMapping("/save")
    public ResponseEntity<PersonaDTO> savePersona(@RequestBody @Parameter(description = "Datos de la persona a crear") PersonaDTO personaDTO){
        PersonaDTO savePersonaDTO = personaService.savePersona(personaDTO);
        return  ResponseEntity.status(HttpStatus.CREATED).body(savePersonaDTO);
    }

    //Actualizar una persona existente
    @Operation(summary = "Actualizar una persona existente", description = "Actualiza los datos de una persona existente")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Persona actualizada exitosamente", content = @Content(mediaType = "application/json", schema = @Schema(implementation = PersonaDTO.class))),
            @ApiResponse(responseCode = "400", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "404", description = "Persona no encontrada", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @PutMapping("/update/{id}")
    public ResponseEntity<PersonaDTO> updatePersona(@PathVariable @Parameter(description = "ID de la persona") Long id,
                                                    @RequestBody @Parameter(description = "Datos de la persona actualizados") PersonaDTO personaDTO){
        personaDTO.setId(id);
        PersonaDTO updatePersonaDTO = personaService.updatePersona(personaDTO);
        return  ResponseEntity.ok(updatePersonaDTO);
    }

    //Actualizar la contraseña de una persona por ID
    @Operation(summary = "Actualizar contraseña de un usuario por ID", description = "Actualiza la contraseña de una persona existente")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Persona actualizada correctamente", content = @Content(mediaType = "application/json", schema = @Schema(implementation = PersonaDTO.class))),
            @ApiResponse(responseCode = "400", description = "Solicitud invalida", content = @Content),
            @ApiResponse(responseCode = "404", description = "Persona no encontrada", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @PatchMapping("/updatePassword/{id}")
    public ResponseEntity<PersonaDTO> updatePassword(@PathVariable @Parameter(description = "ID de la persona") long id,
                                                     @RequestBody @Parameter(description = "Contraseña actualizada")UpdatePasswordRequest updatePasswordRequest){
        PersonaDTO updatePersona = personaService.PutContrasenia(id,updatePasswordRequest.getPassword());
        return  ResponseEntity.ok(updatePersona);
    }
    //Eliminar una persona por ID
    @Operation(summary = "Eliminar una persona por ID", description = "Elimina la persona correspondiente al ID proporcionado")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Persona eliminada exitosamente", content =  @Content),
            @ApiResponse(responseCode = "404", description = "Persona no encontrada", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @DeleteMapping("/delete/{id}")
    public ResponseEntity<PersonaDTO> deletePersona(@PathVariable @Parameter(description = "ID de la persona") Long id){
        personaService.deletePersona(id);
        return  ResponseEntity.ok().build();
    }

    //Contar el numero total de personas
    @Operation(summary = "Contar la cantidad de personas", description = "Retorna el total de personas registradas")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Cantidad de registros", content = @Content(mediaType = "application/json"))
    })
    @GetMapping("/count")
    public ResponseEntity<Long> countPersonas(){
        long count = personaService.countPersonas();
        return ResponseEntity.ok(count);
    }

    //Obtener una persona por email
    @Operation(summary = "Obtener una persona por email", description = "Retorna una persona segun el email proporcionado")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Persona encontrada", content = @Content(mediaType = "application/json", schema = @Schema(implementation = PersonaDTO.class))),
            @ApiResponse(responseCode = "404", description = "Persona no encontrada", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @GetMapping("/email/{email}")
    public ResponseEntity<PersonaDTO> getPersonaByEmail(@PathVariable @Parameter(description = "Email de la persona") String email){
        Optional<PersonaDTO> personaOpt = personaService.getPersonaByEmail(email);
        PersonaDTO personaDTO = personaOpt.orElseThrow(
                () -> new RuntimeException("No se encontro el persona con el email " + email)
        );
        return  ResponseEntity.ok(personaDTO);
    }

    @Operation(summary = "Verificar si existe una persona por email y contraseña", description = "Verifica en el sistema si existe una persona con email y contraseña proporcionada")
    @ApiResponses(value = {
            @ApiResponse(responseCode = "200", description = "Login exitoso",
                    content = @Content(mediaType = "application/json",
                            schema = @Schema(implementation = PersonaDTO.class))),
            @ApiResponse(responseCode = "401", description = "Credenciales inválidas", content = @Content),
            @ApiResponse(responseCode = "404", description = "Usuario no encontrado", content = @Content),
            @ApiResponse(responseCode = "500", description = "Error interno del servidor", content = @Content)
    })
    @PostMapping("/login")
    public ResponseEntity<PersonaDTO> login(@RequestBody @Parameter(description = "Credenciales de login") LoginRequest loginRequest, HttpServletResponse response) {
        PersonaDTO personaDTO = personaService.authenticate(loginRequest);
        String token = jwtUtil.generateToken(personaDTO.getId(), personaDTO.getRol(), personaDTO.getEmail());

        long maxAgeSeconds = jwtUtil.getExpirationMs() / 1000; // mantener coherencia con exp del JWT

        StringBuilder cookieHeader = new StringBuilder();
        cookieHeader.append("JWT_TOKEN=").append(token)
                .append("; Path=/")
                .append("; Max-Age=").append(maxAgeSeconds)
                .append("; HttpOnly");

        if (cookieSecure) {
            cookieHeader.append("; Secure");
        }

        cookieHeader.append("; SameSite=").append(cookieSameSite);

        response.addHeader("Set-Cookie", cookieHeader.toString());
        return ResponseEntity.ok(personaDTO);
    }

    @GetMapping("/me")
    public ResponseEntity<PersonaDTO> getCurrentUser(
            @CookieValue(value = "JWT_TOKEN", required = false) String token) {
        if (token == null || !jwtUtil.isTokenValid(token)) {
            // No hay token o es inválido → 401 Unauthorized
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
        // Extraer ID de la persona desde el token
        Long id = jwtUtil.extractId(token);
        // Buscar persona en la base de datos
        PersonaDTO persona = personaService.getPersonaById(id)
                .orElseThrow(() -> new RuntimeException("Usuario no encontrado"));
        // Retornar la persona
        return ResponseEntity.ok(persona);
    }

}
