import { Persona } from "./persona";

export interface Admin extends Persona{
    nivelAcceso:string
    sueldo:number
    permiso:string
}