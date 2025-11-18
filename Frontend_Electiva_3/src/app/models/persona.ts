export interface Persona{
    id:number|null,
    cedula:string,
    nombre:string,
    apellido:string,
    telefono:string,
    email:string,
    rol?:string,
    contrasenia:string
}