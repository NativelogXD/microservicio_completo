import { Column, Entity, PrimaryGeneratedColumn } from 'typeorm';
import { EstadoPago, MetodoPago } from '../../domain/dto/PagoDTO';

@Entity()
export class Pago {
  @PrimaryGeneratedColumn()
  id: number;

  @Column({ type: 'numeric' })
  monto: number;

  @Column({ type: 'timestamptz' })
  fecha: Date;

  @Column({ type: 'enum', enum: EstadoPago })
  estado: EstadoPago;

  @Column({ type: 'varchar', length: 10 })
  moneda: string;
  @Column({ type: 'enum', enum: MetodoPago, nullable: true })
  metodo_pago?: MetodoPago;

  @Column({ type: 'varchar', length: 100 })
  id_reserva: string;
}
