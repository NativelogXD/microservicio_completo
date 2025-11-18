package com.example.servicio1.persistence.serviceImpl;

import com.example.servicio1.clients.NotificationClient;
import com.example.servicio1.domain.dto.EmpleadoDTO;
import com.example.servicio1.domain.repository.EmpleadoRepository;
import com.example.servicio1.domain.service.EmpleadoService;
import com.example.servicio1.exceptions.EmpleadoNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class EmpleadoServiceImpl implements EmpleadoService {

    @Autowired
    private EmpleadoRepository empleadoRepository;

    @Autowired
    private NotificationClient notificationClient;

    @Override
    public Iterable<EmpleadoDTO> getAllEmpleados() {
        return empleadoRepository.findAll();
    }

    @Override
    public EmpleadoDTO getEmpleadoById(Long id) {
        return empleadoRepository.findById(id)
                .orElseThrow(() -> new EmpleadoNotFoundException("empleado","empleado id", id));
    }

    @Override
    public EmpleadoDTO saveEmpleado(EmpleadoDTO empleadoDTO) {
        EmpleadoDTO newEmpleado = empleadoRepository.save(empleadoDTO);
        notificationClient.enviarNotificacion(String.valueOf(newEmpleado.getId()),newEmpleado.getEmail(),newEmpleado.getNombre());
        return newEmpleado;
    }

    @Override
    public EmpleadoDTO updateEmpleado(EmpleadoDTO empleadoDTO) {
        return empleadoRepository.update(empleadoDTO);
    }

    @Override
    public void deleteEmpleado(Long id) {
        if(!empleadoRepository.existsById(id)){
            throw new EmpleadoNotFoundException("empleado","empleado id", id);
        } else {
            empleadoRepository.delete(id);
        }
    }

    @Override
    public long countEmpleado() {
        return empleadoRepository.count();
    }

    @Override
    public EmpleadoDTO getEmpleadoByEmail(String email) {
        return empleadoRepository.findByEmail(email)
                .orElseThrow(() -> new EmpleadoNotFoundException("empleado","empleado email", email));
    }

    @Override
    public EmpleadoDTO getEmpleadoByCedula(String cedula) {
        return empleadoRepository.findByCedula(cedula)
                .orElseThrow(() -> new EmpleadoNotFoundException("empleado","empleado cedula", cedula));
    }

    @Override
    public EmpleadoDTO PutContrasenia(Long id, String password) { return empleadoRepository.PutContrasenia(id,password).orElseThrow(() -> new EmpleadoNotFoundException("empleado","empleado id", id)); }

    @Override
    public EmpleadoDTO getEmpleadoByCargo(String cargo) {
        return empleadoRepository.findByCargo(cargo)
                .orElseThrow(() -> new EmpleadoNotFoundException("empleado","empleado cargo", cargo));
    }
}
