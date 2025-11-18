import {
  IsDate,
  IsInt,
  IsNumber,
  IsOptional,
  IsPositive,
  IsString,
  IsNotEmpty,
  IsEnum,
} from 'class-validator';
import { Type } from 'class-transformer';

// Enum para los estados permitidos
export enum EstadoPago {
  PENDIENTE = 'PENDIENTE',
  COMPLETADO = 'COMPLETADO',
  CANCELADO = 'CANCELADO',
}

// Enum para los métodos de pago permitidos
export enum MetodoPago {
  TARJETA = 'TARJETA',
  EFECTIVO = 'EFECTIVO',
  TRANSFERENCIA = 'TRANSFERENCIA',
  PAYPAL = 'PAYPAL',
  CRYPTO = 'CRYPTO',
}

export class PagoDTO {
  @IsInt()
  @IsOptional()
  id: number;

  @IsNumber({ allowInfinity: false, allowNaN: false })
  @IsPositive()
  monto: number;

  @Type(() => Date)
  @IsDate()
  fecha: Date;

  @IsString()
  @IsNotEmpty({ message: 'El estado no puede estar vacío' })
  @IsEnum(EstadoPago, {
    message: 'El estado debe ser PENDIENTE, COMPLETADO o CANCELADO',
  })
  estado: EstadoPago;

  @IsString()
  @IsNotEmpty({ message: 'La moneda no puede estar vacía' })
  moneda: string;

  @IsString()
  @IsOptional()
  @IsNotEmpty({
    message: 'El método de pago no puede estar vacío si se proporciona',
  })
  @IsEnum(MetodoPago, {
    message:
      'El método de pago debe ser TARJETA, EFECTIVO, TRANSFERENCIA, PAYPAL o CRYPTO',
  })
  metodo_pago?: MetodoPago;

  @IsString()
  @IsNotEmpty({ message: 'El id_reserva no puede estar vacío' })
  id_reserva: string;
}
