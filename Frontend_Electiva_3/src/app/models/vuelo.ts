export interface Vuelo{
    id:null|number
    codigoVuelo:string
    origen:string
    destino:string
    avionId:string
    pilotoId:string
    fecha: Date | string;
    hora: Date | string;
    duracionMinutos:number
    estado:string
    precioBase:number
}