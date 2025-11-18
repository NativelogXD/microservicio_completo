import { EstadoMantenimiento } from "./enums/estadoMantenimiento";

export interface Mantenimiento{
    id:number|null,
    avion_id:string,
    tipo:string,
    descripcion:string,
    fecha:Date,
    responsable:string,
    costo:number,
    estado:EstadoMantenimiento
}