package com.example.servicio1.domain.service;

import com.example.servicio1.domain.dto.EmpleadoDTO;

public interface EmpleadoService {

    Iterable<EmpleadoDTO> getAllEmpleados();

    EmpleadoDTO getEmpleadoById(Long id);

    EmpleadoDTO saveEmpleado(EmpleadoDTO empleadoDTO);

    EmpleadoDTO updateEmpleado(EmpleadoDTO empleadoDTO);

    void deleteEmpleado(Long id);

    long countEmpleado();

    EmpleadoDTO getEmpleadoByEmail(String email);

    EmpleadoDTO getEmpleadoByCedula(String cedula);

    EmpleadoDTO PutContrasenia(Long id, String contrasenia);

    EmpleadoDTO getEmpleadoByCargo(String cargo);
}
