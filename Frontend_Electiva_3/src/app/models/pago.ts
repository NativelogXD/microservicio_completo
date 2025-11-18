import { EstadoPago } from "./enums/estadoPago"
import { MetodoPago } from "./enums/MetodoPago"

export interface Pago{
    id:null|number,
    monto: number,
    fecha: Date
    estado: EstadoPago,
    moneda: string,
    metodo_pago: MetodoPago,
    reserva:string,
    usuario:string
}