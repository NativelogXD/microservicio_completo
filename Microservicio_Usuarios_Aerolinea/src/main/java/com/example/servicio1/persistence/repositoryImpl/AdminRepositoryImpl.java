package com.example.servicio1.persistence.repositoryImpl;

import com.example.servicio1.domain.dto.AdminDTO;
import com.example.servicio1.domain.repository.AdminRepository;
import com.example.servicio1.exceptions.AdminNotFoundException;
import com.example.servicio1.exceptions.CedulaFoundException;
import com.example.servicio1.exceptions.GmailFoundException;
import com.example.servicio1.persistence.crud.AdminCrudRepository;
import com.example.servicio1.persistence.crud.PersonaCrudRepository;
import com.example.servicio1.persistence.entity.Admin;
import com.example.servicio1.persistence.mapper.AdminMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Repository
public class AdminRepositoryImpl implements AdminRepository {

    @Autowired
    private AdminCrudRepository  adminCrudRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private PersonaCrudRepository personaCrudRepository;

    @Autowired
    private AdminMapper adminMapper;

    @Override
    public Iterable<AdminDTO> findAll() {
        Iterable<Admin> admins = adminCrudRepository.findAll();
        return ((List<Admin>) admins).stream().map(adminMapper::toDTO).collect(Collectors.toList());
    }

    @Override
    public  Optional<AdminDTO> findById(Long id) {
        return adminCrudRepository.findById(id)
                .map(adminMapper::toDTO);
    }

    @Override
    public AdminDTO save(AdminDTO adminDTO) {
        Admin admin = adminMapper.toEntity(adminDTO);
        validateForSave(admin);
        String hashed = passwordEncoder.encode(adminDTO.getContrasenia());
        admin.setContrasenia(hashed);

        Admin savedAdmin = adminCrudRepository.save(admin);
        return adminMapper.toDTO(savedAdmin);
    }

    @Override
    public AdminDTO update(AdminDTO adminDTO) {
        Admin admin = adminMapper.toEntity(adminDTO);
        validateForUpdate(admin);
        String hashed = passwordEncoder.encode(adminDTO.getContrasenia());
        admin.setContrasenia(hashed);

        Admin updateAdmin = adminCrudRepository.save(admin);
        return adminMapper.toDTO(updateAdmin);
    }

    @Override
    public void delete(Long id){
        validateAdminExists(id);
        adminCrudRepository.deleteById(id);
    }

    @Override
    public boolean existsById(Long id){ return adminCrudRepository.existsById(id); }

    @Override
    public long count(){ return adminCrudRepository.count(); }

    @Override
    public Optional<AdminDTO> findByEmail(String email) {
        return adminCrudRepository.findByEmail(email)
                .map(adminMapper::toDTO);
    }

    @Override
    public Optional<AdminDTO> findByCedula(String cedula) {
        return adminCrudRepository.findByCedula(cedula)
                .map(adminMapper::toDTO);
    }

    @Override
    @Transactional
    public Optional<AdminDTO> PutContrasenia(long id, String contrasenia) {
        validateAdminExists(id);
        return adminCrudRepository.findById(id).map(admin -> {
            String hashed = passwordEncoder.encode(contrasenia);
            admin.setContrasenia(hashed);
            Admin updatedAdmin = adminCrudRepository.save(admin);
            return adminMapper.toDTO(updatedAdmin);
        });
    }


    // Métodos de validación privados

    private void validateForSave(Admin admin) {
        validateNoDuplicateEmail(admin.getEmail());
        validateNoDuplicateCedula(admin.getCedula());
    }

    private void validateForUpdate(Admin admin) {
        validateAdminExists(admin.getId());
        validateNoDuplicateEmailForOtherAdmins(admin);
        validateNoDuplicateCedulaForOtherAdmins(admin);
    }

    private void validateAdminExists(Long id) {
        if (!existsById(id)) {
            throw new AdminNotFoundException("admin", "admin id", id);
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

    private void validateNoDuplicateEmailForOtherAdmins(Admin admin) {
        adminCrudRepository.findByEmail(admin.getEmail())
                .filter(a -> !a.getId().equals(admin.getId()))
                .ifPresent(a -> { throw new GmailFoundException(); });
    }

    private void validateNoDuplicateCedulaForOtherAdmins(Admin admin) {
        adminCrudRepository.findByCedula(admin.getCedula())
                .filter(a -> !a.getId().equals(admin.getId()))
                .ifPresent(a -> { throw new CedulaFoundException(); });
    }
}
