package com.example.servicio1.domain.service;

import com.example.servicio1.domain.dto.UsuarioDTO;

public interface UsuarioService {

    Iterable<UsuarioDTO> getAllUsuarios();

    UsuarioDTO getUsuarioById(Long id);

    UsuarioDTO saveUsuario(UsuarioDTO usuario);

    UsuarioDTO updateUsuario(UsuarioDTO usuario);

    void deleteUsuario(Long id);

    long countUsuarios();

    UsuarioDTO getUsuarioByEmail(String email);

    UsuarioDTO getUsuarioByCedula(String cedula);

    UsuarioDTO PutContrasenia(Long id, String contrasenia);
}
