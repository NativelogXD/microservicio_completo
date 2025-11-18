import { Persona } from "./persona";

export interface Usuario extends Persona{
    direccion:string,
    reservaId:string
}