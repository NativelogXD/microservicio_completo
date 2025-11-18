package com.example.servicio1.domain.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class PersonaDTO {

    private Long id;

    @Pattern(regexp = "\\d{10}", message = "La cedula debe tener exactamente 10 digitos")
    private String cedula;

    @NotBlank(message = "El nombre de la persona no puede estar vacio")
    private String nombre;

    @NotBlank(message = "El apellido de la persona no puede estar vacio")
    private String apellido;

    @NotBlank(message = "El numero de la persona no puede estar vacio")
    private String telefono;

    @Email(message = "El correo electronico no es valido")
    @NotBlank(message = "El correo de la persona no puede estar vacio")
    private String email;

    private String rol;
    @NotBlank(message = "La contraseña no puede estar vacia")
    private String contrasenia;
}
