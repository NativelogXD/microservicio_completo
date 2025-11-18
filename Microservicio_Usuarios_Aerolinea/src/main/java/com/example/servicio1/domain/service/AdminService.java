package com.example.servicio1.domain.service;

import com.example.servicio1.domain.dto.AdminDTO;

public interface AdminService {

    Iterable<AdminDTO> getAllAdmins();

    AdminDTO getAdminById(Long id);

    AdminDTO saveAdmin(AdminDTO admin);

    AdminDTO updateAdmin(AdminDTO admin);

    void deleteAdmin(Long id);

    long countAdmins();

    AdminDTO getAdminByEmail(String email);

    AdminDTO getAdminByCedula(String cedula);

    AdminDTO PutContrasenia(Long id, String contrasenia);
}
