package com.example.microservicionotificaciones.persistence.serviceImpl;

import com.example.microservicionotificaciones.domain.dto.NotificacionDTO;
import com.example.microservicionotificaciones.domain.repository.NotificacionRepository;
import com.example.microservicionotificaciones.domain.service.NotificacionService;
import com.example.microservicionotificaciones.exceptions.NotificacionNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.io.IOException;

@Service
public class NotificacionServiceImpl implements NotificacionService {

    @Autowired
    private NotificacionRepository notificacionRepository;

    @Autowired
    private EmailService emailService;

    @Override
    public Iterable<NotificacionDTO> findAll() {
        return notificacionRepository.findAll();
    }

    @Override
    public NotificacionDTO findById(Long id) {
        return notificacionRepository.findById(id).orElseThrow(() -> new NotificacionNotFoundException("notificacion", "notificacion id", id));
    }

    @Override
    public NotificacionDTO save(NotificacionDTO notificacionDTO) {
        emailService.enviarNotificacion(notificacionDTO);
       return notificacionRepository.save(notificacionDTO);
    }

    @Override
    public void deleteById(Long id) {
        if(!notificacionRepository.existsById(id)){
            throw new NotificacionNotFoundException("notificacion", "notificacion id", id);
        } else {
            notificacionRepository.deleteById(id);
        }
    }

    @Override
    public long countNotificaciones() {
        return notificacionRepository.count();
    }

    @Override
    public Iterable<NotificacionDTO> findAllByPersonaId(Long id) {
        return notificacionRepository.findAllByIdPersona(String.valueOf(id));
    }
}
