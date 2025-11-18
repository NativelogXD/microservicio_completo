package com.example.servicio1.persistence.repositoryImpl;

import com.example.servicio1.domain.dto.UsuarioDTO;
import com.example.servicio1.domain.repository.UsuarioRepository;
import com.example.servicio1.exceptions.AdminNotFoundException;
import com.example.servicio1.exceptions.CedulaFoundException;
import com.example.servicio1.exceptions.GmailFoundException;
import com.example.servicio1.persistence.crud.PersonaCrudRepository;
import com.example.servicio1.persistence.crud.UsuarioCrudRepository;
import com.example.servicio1.persistence.entity.Admin;
import com.example.servicio1.persistence.entity.Usuario;
import com.example.servicio1.persistence.mapper.UsuarioMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Repository
public class UsuarioRepositoryImpl implements UsuarioRepository {

    @Autowired
    private UsuarioCrudRepository usuarioCrudRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private PersonaCrudRepository personaCrudRepository;

    @Autowired
    private UsuarioMapper usuarioMapper;


    @Override
    public Iterable<UsuarioDTO> findAll() {
        Iterable<Usuario> usuarios = usuarioCrudRepository.findAll();
        return ((List<Usuario>) usuarios).stream()
                .map(usuarioMapper::toDTO).collect(Collectors.toList());
    }

    @Override
    public Optional<UsuarioDTO> findById(Long id) {
        return usuarioCrudRepository.findById(id).map(usuarioMapper::toDTO);
    }

    @Override
    public UsuarioDTO save(UsuarioDTO usuarioDTO) {
        Usuario usuario = usuarioMapper.toEntity(usuarioDTO);
        validateForSave(usuario);
        String hashed = passwordEncoder.encode(usuarioDTO.getContrasenia());
        usuario.setContrasenia(hashed);

        Usuario savedUsuario = usuarioCrudRepository.save(usuario);
        return usuarioMapper.toDTO(savedUsuario);
    }

    @Override
    public UsuarioDTO update(UsuarioDTO usuarioDTO) {
        Usuario usuario = usuarioMapper.toEntity(usuarioDTO);
        validateForUpdate(usuario);
        String hashed = passwordEncoder.encode(usuarioDTO.getContrasenia());
        usuario.setContrasenia(hashed);

        Usuario updateUsuario = usuarioCrudRepository.save(usuario);
        return  usuarioMapper.toDTO(updateUsuario);
    }

    @Override
    public void delete(Long id) {
        validateUsuarioExists(id);
        usuarioCrudRepository.deleteById(id);
    }

    @Override
    public boolean existsById(Long id) {
        return usuarioCrudRepository.existsById(id);
    }

    @Override
    public long count() {
        return usuarioCrudRepository.count();
    }

    @Override
    public Optional<UsuarioDTO> findByEmail(String email) {
        return usuarioCrudRepository.findByEmail(email)
                .map(usuarioMapper::toDTO);
    }

    @Override
    public Optional<UsuarioDTO> findByCedula(String cedula) {
        return usuarioCrudRepository.findByCedula(cedula)
                .map(usuarioMapper::toDTO);
    }

    @Override
    public Optional<UsuarioDTO> PutContrasenia(long id, String contrasenia) {
        validateUsuarioExists(id);
        return usuarioCrudRepository.findById(id).map(usuario -> {
            String hashed = passwordEncoder.encode(contrasenia);
            usuario.setContrasenia(hashed);
            Usuario updateUsuario = usuarioCrudRepository.save(usuario);
            return usuarioMapper.toDTO(updateUsuario);
        });
    }

    // Métodos de validación privados

    private void validateForSave(Usuario usuario) {
        validateNoDuplicateEmail(usuario.getEmail());
        validateNoDuplicateCedula(usuario.getCedula());
    }

    private void validateForUpdate(Usuario usuario) {
        validateUsuarioExists(usuario.getId());
        validateNoDuplicateEmailForOtherAdmins(usuario);
        validateNoDuplicateCedulaForOtherAdmins(usuario);
    }

    private void validateUsuarioExists(Long id) {
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

    private void validateNoDuplicateEmailForOtherAdmins(Usuario usuario) {
        usuarioCrudRepository.findByEmail(usuario.getEmail())
                .filter(a -> !a.getId().equals(usuario.getId()))
                .ifPresent(a -> { throw new GmailFoundException(); });
    }

    private void validateNoDuplicateCedulaForOtherAdmins(Usuario usuario) {
        usuarioCrudRepository.findByCedula(usuario.getCedula())
                .filter(a -> !a.getId().equals(usuario.getId()))
                .ifPresent(a -> { throw new CedulaFoundException(); });
    }
}
