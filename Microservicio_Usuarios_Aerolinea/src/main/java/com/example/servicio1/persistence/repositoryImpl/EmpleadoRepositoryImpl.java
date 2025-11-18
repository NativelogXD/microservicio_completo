package com.example.servicio1.persistence.repositoryImpl;

import com.example.servicio1.domain.dto.EmpleadoDTO;
import com.example.servicio1.domain.repository.EmpleadoRepository;
import com.example.servicio1.exceptions.CedulaFoundException;
import com.example.servicio1.exceptions.EmpleadoNotFoundException;
import com.example.servicio1.exceptions.GmailFoundException;
import com.example.servicio1.persistence.crud.EmpleadoCrudRepository;
import com.example.servicio1.persistence.crud.PersonaCrudRepository;
import com.example.servicio1.persistence.entity.Empleado;
import com.example.servicio1.persistence.mapper.EmpleadoMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Repository
public class EmpleadoRepositoryImpl implements EmpleadoRepository {

    @Autowired
    private EmpleadoCrudRepository empleadoCrudRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private PersonaCrudRepository personaCrudRepository;

    @Autowired
    private EmpleadoMapper empleadoMapper;

    @Override
    public Iterable<EmpleadoDTO> findAll() {
        Iterable<Empleado>  empleados = empleadoCrudRepository.findAll();
        return ((List<Empleado>) empleados).stream().map(empleadoMapper::toDTO)
                .collect(Collectors.toList());
    }

    @Override
    public Optional<EmpleadoDTO> findById(Long id) {
        return empleadoCrudRepository.findById(id)
                .map(empleadoMapper::toDTO);
    }

    @Override
    public EmpleadoDTO save(EmpleadoDTO empleadoDTO) {
        Empleado empleado = empleadoMapper.toEntity(empleadoDTO);
        validateForSave(empleado);
        String hashed = passwordEncoder.encode(empleadoDTO.getContrasenia());
        empleado.setContrasenia(hashed);

        Empleado empleadoSaved = empleadoCrudRepository.save(empleado);
        return empleadoMapper.toDTO(empleadoSaved);

    }

    @Override
    public EmpleadoDTO update(EmpleadoDTO empleadoDTO) {
        Empleado empleado = empleadoMapper.toEntity(empleadoDTO);
        validateForUpdate(empleado);
        String hashed = passwordEncoder.encode(empleadoDTO.getContrasenia());
        empleado.setContrasenia(hashed);

        Empleado empleadoUpdate = empleadoCrudRepository.save(empleado);
        return empleadoMapper.toDTO(empleadoUpdate);
    }

    @Override
    public void delete(Long id) {
        validateEmpleadoExists(id);
        empleadoCrudRepository.deleteById(id);
    }

    @Override
    public boolean existsById(Long id) {
        return empleadoCrudRepository.existsById(id);
    }

    @Override
    public long count() {
        return empleadoCrudRepository.count();
    }

    @Override
    public Optional<EmpleadoDTO> findByEmail(String email) {
        return empleadoCrudRepository.findByEmail(email)
                .map(empleadoMapper::toDTO);
    }

    @Override
    public Optional<EmpleadoDTO> findByCedula(String cedula) {
        return empleadoCrudRepository.findByCedula(cedula)
                .map(empleadoMapper::toDTO);
    }

    @Override
    @Transactional
    public Optional<EmpleadoDTO> PutContrasenia(long id, String contrasenia) {
        validateEmpleadoExists(id);
        return empleadoCrudRepository.findById(id).map(empleado -> {
            String hashed = passwordEncoder.encode(contrasenia);
            empleado.setContrasenia(hashed);
            Empleado updateEmpleado = empleadoCrudRepository.save(empleado);
            return empleadoMapper.toDTO(updateEmpleado);
        });
    }

    @Override
    public Optional<EmpleadoDTO> findByCargo(String cargo) {
        return empleadoCrudRepository.findByCargo(cargo)
                .map(empleadoMapper::toDTO);
    }

    // Métodos de validación privados

    private void validateForSave(Empleado empleado) {
        validateNoDuplicateEmail(empleado.getEmail());
        validateNoDuplicateCedula(empleado.getCedula());
    }

    private void validateForUpdate(Empleado empleado) {
        validateEmpleadoExists(empleado.getId());
        validateNoDuplicateEmailForOtherAdmins(empleado);
        validateNoDuplicateCedulaForOtherAdmins(empleado);
    }

    private void validateEmpleadoExists(Long id) {
        if (!existsById(id)) {
            throw new EmpleadoNotFoundException("admin", "admin id", id);
        }
    }

    private void validateNoDuplicateEmail(String email) {
        if (personaCrudRepository.findByEmail(email).isPresent()) {
            throw new GmailFoundException();
        }
    }

    private void validateNoDuplicateCedula(String cedula) {
        if (personaCrudRepository.findByCedula(cedula).isPresent()) {
            throw new CedulaFoundException();
        }
    }

    private void validateNoDuplicateEmailForOtherAdmins(Empleado empleado) {
        empleadoCrudRepository.findByEmail(empleado.getEmail())
                .filter(a -> !a.getId().equals(empleado.getId()))
                .ifPresent(a -> { throw new GmailFoundException(); });
    }

    private void validateNoDuplicateCedulaForOtherAdmins(Empleado empleado) {
        empleadoCrudRepository.findByCedula(empleado.getCedula())
                .filter(a -> !a.getId().equals(empleado.getId()))
                .ifPresent(a -> { throw new CedulaFoundException(); });
    }
}
