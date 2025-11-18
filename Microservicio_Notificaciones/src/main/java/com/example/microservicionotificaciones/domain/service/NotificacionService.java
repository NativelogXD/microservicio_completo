package com.example.microservicionotificaciones.domain.service;

import com.example.microservicionotificaciones.domain.dto.NotificacionDTO;

import java.io.IOException;

public interface NotificacionService {

    Iterable<NotificacionDTO> findAll();

    NotificacionDTO findById(Long id);

    NotificacionDTO save(NotificacionDTO notificacionDTO) throws IOException, InterruptedException;

    void deleteById(Long id);

    long countNotificaciones();

    Iterable<NotificacionDTO> findAllByPersonaId(Long id);
}
