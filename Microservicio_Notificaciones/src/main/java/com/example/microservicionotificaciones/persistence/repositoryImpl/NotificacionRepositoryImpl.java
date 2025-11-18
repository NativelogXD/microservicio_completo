package com.example.microservicionotificaciones.persistence.repositoryImpl;

import com.example.microservicionotificaciones.domain.dto.NotificacionDTO;
import com.example.microservicionotificaciones.domain.repository.NotificacionRepository;
import com.example.microservicionotificaciones.persistence.crud.NotificacionCrudRepository;
import com.example.microservicionotificaciones.persistence.entity.Notificacion;
import com.example.microservicionotificaciones.persistence.mapper.NotificacionMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Repository
public class NotificacionRepositoryImpl implements NotificacionRepository {

    @Autowired
    private NotificacionCrudRepository notificacionCrudRepository;

    @Autowired
    private NotificacionMapper notificacionMapper;

    @Override
    public Iterable<NotificacionDTO> findAll() {
        Iterable<Notificacion> notificaciones = notificacionCrudRepository.findAll();
        return ((List<Notificacion>) notificaciones).stream().map(notificacionMapper::toDTO)
                .collect(Collectors.toList());
    }

    @Override
    public Optional<NotificacionDTO> findById(Long id) {
        return notificacionCrudRepository.findById(id)
                .map(notificacionMapper::toDTO);
    }

    @Override
    public NotificacionDTO save(NotificacionDTO notificacionDTO) {
        Notificacion notificacion = notificacionMapper.toEntity(notificacionDTO);
        if(notificacion.getId() != null && existsById(notificacion.getId())){
            throw new IllegalArgumentException("La notificacion ya existe");
        }
        Notificacion notificacionSaved = notificacionCrudRepository.save(notificacion);
        return notificacionMapper.toDTO(notificacionSaved);
    }

    @Override
    public void deleteById(Long id) {
        if(existsById(id)){
            notificacionCrudRepository.deleteById(id);
        } else {
            throw new IllegalArgumentException("La notificacion no existe");
        }
    }

    @Override
    public boolean existsById(Long id) {
        return notificacionCrudRepository.existsById(id);
    }

    @Override
    public long count() {
        return notificacionCrudRepository.count();
    }

    @Override
    public Iterable<NotificacionDTO> findAllByIdPersona(String id) {
        Iterable<Notificacion> notificaciones = notificacionCrudRepository.findByIdPersona(String.valueOf(Long.valueOf(id)));
        return ((List<Notificacion>) notificaciones).stream().map(notificacionMapper::toDTO)
                .collect(Collectors.toList());
    }
}
