import PagoRepository from '../../domain/repository/PagoRepository';
import { Pago } from '../entity/Pago';
import { PagoDTO } from '../../domain/dto/PagoDTO';
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import {
  PagoNotFoundException,
  PagoAlreadyExistsException,
  PagoByReservaNotFoundException,
} from '../../exceptions/PagoExceptions';

@Injectable()
class PagoRepositoryImpl implements PagoRepository {
  constructor(
    @InjectRepository(Pago)
    private readonly pagoRepository: Repository<Pago>,
  ) {}

  private dtoToEntity(dto: PagoDTO): Pago {
    const entity = new Pago();
    entity.id = dto.id;
    entity.monto = dto.monto;
    entity.fecha = dto.fecha;
    entity.estado = dto.estado;
    entity.moneda = dto.moneda;
    entity.metodo_pago = dto.metodo_pago;
    entity.id_reserva = dto.id_reserva;
    return entity;
  }

  private entityToDTO(entity: Pago): PagoDTO {
    return {
      id: entity.id,
      monto: Number(entity.monto) as unknown as number,
      fecha: entity.fecha,
      estado: entity.estado,
      moneda: entity.moneda,
      metodo_pago: entity.metodo_pago,
      id_reserva: entity.id_reserva,
    };
  }

  async create(pago: PagoDTO): Promise<PagoDTO> {
    if (pago.id) {
      const existing = await this.pagoRepository.findOne({
        where: { id: pago.id },
      });
      if (existing) {
        throw new PagoAlreadyExistsException(existing.id);
      }
    }
    const entity = this.pagoRepository.create(this.dtoToEntity(pago));
    const saved = await this.pagoRepository.save(entity);
    return this.entityToDTO(saved);
  }

  async findAll(): Promise<PagoDTO[]> {
    const items = await this.pagoRepository.find();
    return items.map((e) => this.entityToDTO(e));
  }

  async findById(id: number): Promise<PagoDTO> {
    const entity = await this.pagoRepository.findOne({ where: { id } });
    if (!entity) {
      throw new PagoNotFoundException(id);
    }
    return this.entityToDTO(entity);
  }

  async update(id: number, pago: PagoDTO): Promise<PagoDTO> {
    const existing = await this.pagoRepository.findOne({ where: { id } });
    if (!existing) {
      throw new PagoNotFoundException(id);
    }
    const merged = this.pagoRepository.merge(existing, this.dtoToEntity(pago));
    merged.id = id;
    const saved = await this.pagoRepository.save(merged);
    return this.entityToDTO(saved);
  }

  async delete(id: number): Promise<void> {
    const result = await this.pagoRepository.delete(id);
    if (result.affected === 0) {
      throw new PagoNotFoundException(id);
    }
  }

  async findByMoneda(moneda: string): Promise<PagoDTO[]> {
    const items = await this.pagoRepository.find({ where: { moneda } });
    return items.map((e) => this.entityToDTO(e));
  }

  async findByMonto(monto: number): Promise<PagoDTO[]> {
    const items = await this.pagoRepository.find({ where: { monto } as any });
    return items.map((e) => this.entityToDTO(e));
  }

  async findByFecha(fecha: Date): Promise<PagoDTO[]> {
    const start = new Date(fecha);
    start.setHours(0, 0, 0, 0);
    const end = new Date(fecha);
    end.setHours(23, 59, 59, 999);
    const items = await this.pagoRepository
      .createQueryBuilder('p')
      .where('p.fecha BETWEEN :start AND :end', { start, end })
      .getMany();
    return items.map((e) => this.entityToDTO(e));
  }

  async findByMetodoPago(metodo_pago: string): Promise<PagoDTO[]> {
    const items = await this.pagoRepository.find({
      where: { metodo_pago } as any,
    });
    return items.map((e) => this.entityToDTO(e));
  }

  async findByEstado(
    estado: 'PENDIENTE' | 'COMPLETADO' | 'CANCELADO',
  ): Promise<PagoDTO[]> {
    const items = await this.pagoRepository.find({ where: { estado } as any });
    return items.map((e) => this.entityToDTO(e));
  }

  async findByReserva(id_reserva: string): Promise<PagoDTO> {
    const entity = await this.pagoRepository.findOne({ where: { id_reserva } });
    if (!entity) {
      throw new PagoByReservaNotFoundException(id_reserva);
    }
    return this.entityToDTO(entity);
  }
}

export default PagoRepositoryImpl;
