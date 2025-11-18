import { EstadoAvion } from "./enums/estadoAvion";

export interface Avion {
    id: number|null;
    modelo: string;
    capacidad: number;
    aerolinea: string;
    estado: EstadoAvion;
    fecha_fabricacion: string;
}