package com.example.servicio1.domain.dto;

import jakarta.validation.constraints.NotBlank;

public class UpdatePasswordRequest {

    @NotBlank(message = "La contraseña no puede estar vacia")
    private String password;

    public UpdatePasswordRequest() {}

    public UpdatePasswordRequest(String password) {
        this.password = password;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
