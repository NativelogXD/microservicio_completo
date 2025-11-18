import { Injectable } from '@nestjs/common';
import { PagoService } from '../../domain/service/PagoService';
import { PagoDTO } from '../../domain/dto/PagoDTO';
import PagoRepositoryImpl from '../repositoryImpl/pagoRepositoryImpl';

@Injectable()
export class PagoServiceImpl implements PagoService {
  constructor(private readonly pagoRepository: PagoRepositoryImpl) {}

  async create(pago: PagoDTO): Promise<PagoDTO> {
    return this.pagoRepository.create(pago);
  }

  async findAll(): Promise<PagoDTO[]> {
    return this.pagoRepository.findAll();
  }

  async findById(id: number): Promise<PagoDTO> {
    return this.pagoRepository.findById(id);
  }

  async update(id: number, pago: PagoDTO): Promise<PagoDTO> {
    return this.pagoRepository.update(id, pago);
  }

  async delete(id: number): Promise<void> {
    return this.pagoRepository.delete(id);
  }

  async findByMoneda(moneda: string): Promise<PagoDTO[]> {
    return this.pagoRepository.findByMoneda(moneda);
  }

  async findByMonto(monto: number): Promise<PagoDTO[]> {
    return this.pagoRepository.findByMonto(monto);
  }

  async findByFecha(fecha: Date): Promise<PagoDTO[]> {
    return this.pagoRepository.findByFecha(fecha);
  }

  async findByMetodoPago(metodo_pago: string): Promise<PagoDTO[]> {
    return this.pagoRepository.findByMetodoPago(metodo_pago);
  }

  async findByEstado(
    estado: 'PENDIENTE' | 'COMPLETADO' | 'CANCELADO',
  ): Promise<PagoDTO[]> {
    return this.pagoRepository.findByEstado(estado);
  }

  async findByReserva(reserva: string): Promise<PagoDTO> {
    return this.pagoRepository.findByReserva(reserva);
  }
}
