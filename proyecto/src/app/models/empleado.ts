import { Persona } from "./persona";

export interface Empleado extends Persona{
    salario:number
    cargo:string
}