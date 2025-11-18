package com.example.MicroService_Reserva.persistencia.Entity;


import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "reserva")
public class Reserva {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;   // identificador autogenerado

    @Column(nullable = false)
    private String usuario;   // nombre del usuario

    
    @Column(name = "vuelo", nullable = false)
    private String id_vuelo;     

    @Column(nullable = false)
    private String estado;    // estado de la reserva

    @Column(name = "num_asiento", nullable = false)
    private String Numasiento; // número de asiento




    //aa
}