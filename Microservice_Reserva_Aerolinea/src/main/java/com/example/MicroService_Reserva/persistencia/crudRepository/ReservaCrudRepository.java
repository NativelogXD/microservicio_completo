package com.example.MicroService_Reserva.persistencia.crudRepository;

import com.example.MicroService_Reserva.persistencia.Entity.Reserva;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ReservaCrudRepository extends JpaRepository<Reserva, Long> {

    List<Reserva> findByUsuarioContaining(String usuario);

    List<Reserva> findByEstado(String estado);

    List<Reserva> findByIdVuelo(String id_vuelo);

    List<Reserva> findAll ();

    long countByEstado(String estado);

}
