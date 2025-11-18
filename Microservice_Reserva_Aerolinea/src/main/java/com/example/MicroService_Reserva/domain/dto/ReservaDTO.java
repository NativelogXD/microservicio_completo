package com.example.MicroService_Reserva.domain.dto;

public class ReservaDTO {
    private String id;
    private String usuario;
    private String id_vuelo;
    private String estado;
    private String Numasiento;

    public ReservaDTO() {}

    public ReservaDTO(String id, String usuario, String id_vuelo, String estado, String Numasiento) {
        this.id = id;
        this.usuario = usuario;
        this.id_vuelo = id_vuelo;
        this.estado = estado;
        this.Numasiento = Numasiento;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getUsuario() { return usuario; }
    public void setUsuario(String usuario) { this.usuario = usuario; }

    public String getId_vuelo() { return id_vuelo; }
    public void setId_vuelo(String id_vuelo) { this.id_vuelo = id_vuelo; }

    public String getEstado() { return estado; }
    public void setEstado(String estado) { this.estado = estado; }

    public String getNumasiento() { return Numasiento; }
    public void setNumasiento(String numasiento) { this.Numasiento = numasiento; }

    @Override
    public String toString() {
        return "ReservaDTO{" +
                "id='" + id + '\'' +
                ", usuario='" + usuario + '\'' +
                ", id_vuelo='" + id_vuelo + '\'' +
                ", estado='" + estado + '\'' +
                ", Numasiento='" + Numasiento + '\'' +
                '}';
    }
}

