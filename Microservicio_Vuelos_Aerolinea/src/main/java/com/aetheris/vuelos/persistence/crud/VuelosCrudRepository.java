package com.aetheris.vuelos.persistence.crud;

import com.aetheris.vuelos.persistence.entity.Vuelo;
import org.springframework.data.repository.CrudRepository;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface VuelosCrudRepository extends CrudRepository<Vuelo, String> {

    // Métodos que necesitas agregar:
    Optional<Vuelo> findByCodigoVueloIgnoreCase(String codigoVuelo);
    List<Vuelo> findByOrigenIgnoreCaseAndDestinoIgnoreCase(String origen, String destino);
    List<Vuelo> findByEstadoIgnoreCase(String estado);
    List<Vuelo> findByFecha(LocalDate fecha);
    List<Vuelo> findByFechaBetween(LocalDate start, LocalDate end);
    @Query("SELECT v FROM Vuelo v WHERE v.id_avion = :idAvion")
    List<Vuelo> findByIdAvion(@Param("idAvion") String id_avion);
    @Query("SELECT v FROM Vuelo v WHERE v.id_piloto = :idPiloto")
    List<Vuelo> findByIdPiloto(@Param("idPiloto") String id_piloto);
    List<Vuelo> findByOrigenAndDestinoAndFecha(String origen, String destino, LocalDate fecha);
    List<Vuelo> findByPrecioBaseBetween(double min, double max);
    List<Vuelo> findByFechaAndHoraBetween(LocalDate fecha, LocalTime start, LocalTime end);

    // Métodos para estadísticas
    long countByEstado(String estado);
    Optional<Vuelo> findFirstByOrderByPrecioBaseAsc();
    List<Vuelo> findTop5ByOrderByDuracionMinutosDesc();

    // Métodos adicionales
    List<Vuelo> findByOrigenIgnoreCase(String origen);
    List<Vuelo> findByDestinoIgnoreCase(String destino);
    boolean existsByCodigoVueloIgnoreCase(String codigoVuelo);
    long countByOrigenAndDestino(String origen, String destino);
}