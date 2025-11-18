package com.example.servicio1.persistence.serviceImpl;

import com.example.servicio1.clients.NotificationClient;
import com.example.servicio1.domain.dto.AdminDTO;
import com.example.servicio1.domain.repository.AdminRepository;
import com.example.servicio1.domain.service.AdminService;
import com.example.servicio1.exceptions.AdminNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class AdminServiceImpl implements AdminService {

    @Autowired
    private AdminRepository adminRepository;

    @Autowired
    private NotificationClient notificationClient;

    @Override
    public Iterable<AdminDTO> getAllAdmins() {
        return adminRepository.findAll();
    }

    @Override
    public AdminDTO getAdminById(Long id) {
        return adminRepository.findById(id).orElseThrow(() -> new AdminNotFoundException("admin","admin id",id));
    }

    @Override
    public AdminDTO saveAdmin(AdminDTO admin) {
        AdminDTO newAdmin = adminRepository.save(admin);
        notificationClient.enviarNotificacion(String.valueOf(newAdmin.getId()),newAdmin.getEmail(),newAdmin.getNombre());
        return newAdmin;
    }

    @Override
    public AdminDTO updateAdmin(AdminDTO admin) {
        return adminRepository.update(admin);
    }

    @Override
    public void deleteAdmin(Long id) {
        if(!adminRepository.existsById(id)){
            throw new AdminNotFoundException("admin","admin id",id);
        } else {
            adminRepository.delete(id);
        }
    }

    @Override
    public long countAdmins() {
        return adminRepository.count();
    }

    @Override
    public AdminDTO getAdminByEmail(String email) {
        return adminRepository.findByEmail(email).orElseThrow(() -> new AdminNotFoundException("admin","email",email));
    }

    @Override
    public AdminDTO getAdminByCedula(String cedula) {
        return adminRepository.findByCedula(cedula).orElseThrow(() -> new AdminNotFoundException("admin","cedula",cedula));
    }

    @Override
    public AdminDTO PutContrasenia(Long id, String password) { return adminRepository.PutContrasenia(id,password).orElseThrow(() -> new AdminNotFoundException("admin","admin id",id)); }
}
