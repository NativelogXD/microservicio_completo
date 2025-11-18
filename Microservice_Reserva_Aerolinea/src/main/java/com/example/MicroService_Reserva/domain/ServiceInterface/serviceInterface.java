package com.example.MicroService_Reserva.domain.ServiceInterface;


import com.example.MicroService_Reserva.domain.dto.ReservaDTO;

public interface serviceInterface {


    Iterable<ReservaDTO> getAllReservas();

    ReservaDTO getReservaById(String id);

    ReservaDTO saveReserva(ReservaDTO reserva);

    ReservaDTO updateReserva(String id, ReservaDTO reserva);

    void deleteReserva(String id);

    long countReservas();

    ReservaDTO getReservaByUsuario(String usuario);

    ReservaDTO getReservaByVuelo(String id_vuelo);


}
