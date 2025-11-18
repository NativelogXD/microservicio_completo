import { PagoDTO } from '../dto/PagoDTO';

interface PagoRepository {
  create(pago: PagoDTO): Promise<PagoDTO>;

  findAll(): Promise<PagoDTO[]>;

  findById(id: number): Promise<PagoDTO>;

  update(id: number, pago: PagoDTO): Promise<PagoDTO>;

  delete(id: number): Promise<void>;

  findByMoneda(moneda: string): Promise<PagoDTO[]>;

  findByMonto(monto: number): Promise<PagoDTO[]>;

  findByFecha(fecha: Date): Promise<PagoDTO[]>;

  findByMetodoPago(metodo_pago: string): Promise<PagoDTO[]>;

  findByEstado(
    estado: 'PENDIENTE' | 'COMPLETADO' | 'CANCELADO',
  ): Promise<PagoDTO[]>;

  findByReserva(id_reserva: string): Promise<PagoDTO>;
}
export default PagoRepository;
