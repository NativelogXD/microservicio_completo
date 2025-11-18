import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  HttpStatus,
  HttpCode,
  ParseIntPipe,
  Inject,
} from '@nestjs/common';
import type { PagoService } from '../../domain/service/PagoService';
import { PagoDTO } from '../../domain/dto/PagoDTO';

@Controller('pagos')
export class PagoController {
  constructor(
    @Inject('PagoService') private readonly pagoService: PagoService,
  ) {}

  @Post('crear')
  @HttpCode(HttpStatus.CREATED)
  async createPago(@Body() pago: PagoDTO): Promise<PagoDTO> {
    return await this.pagoService.create(pago);
  }

  @Get('get-all')
  async getAllPagos(): Promise<PagoDTO[]> {
    return await this.pagoService.findAll();
  }

  @Get('get/:id')
  async getPagoById(@Param('id', ParseIntPipe) id: number): Promise<PagoDTO> {
    return await this.pagoService.findById(id);
  }

  @Put('update/:id')
  async updatePago(
    @Param('id', ParseIntPipe) id: number,
    @Body() pago: PagoDTO,
  ): Promise<PagoDTO> {
    return await this.pagoService.update(id, pago);
  }

  @Delete('delete/:id')
  @HttpCode(HttpStatus.NO_CONTENT)
  async deletePago(@Param('id', ParseIntPipe) id: number): Promise<void> {
    return await this.pagoService.delete(id);
  }

  @Get('buscar/moneda/:moneda')
  async getPagosByMoneda(@Param('moneda') moneda: string): Promise<PagoDTO[]> {
    return await this.pagoService.findByMoneda(moneda);
  }

  @Get('buscar/monto/:monto')
  async getPagosByMonto(
    @Param('monto', ParseIntPipe) monto: number,
  ): Promise<PagoDTO[]> {
    return await this.pagoService.findByMonto(monto);
  }

  @Get('buscar/fecha/:fecha')
  async getPagosByFecha(@Param('fecha') fecha: Date): Promise<PagoDTO[]> {
    const fechaDate = new Date(fecha);
    return await this.pagoService.findByFecha(fechaDate);
  }

  @Get('buscar/metodo/:metodo')
  async getPagosByMetodo(@Param('metodo') metodo: string): Promise<PagoDTO[]> {
    return await this.pagoService.findByMetodoPago(metodo);
  }

  @Get('buscar/estado/:estado')
  async getPagosByEstado(
    @Param('estado') estado: 'PENDIENTE' | 'COMPLETADO' | 'CANCELADO',
  ): Promise<PagoDTO[]> {
    return await this.pagoService.findByEstado(estado);
  }

  @Get('buscar/reserva/:id_reserva')
  async getPagoByReserva(@Param('id_reserva') id_reserva: string): Promise<PagoDTO> {
    return await this.pagoService.findByReserva(id_reserva);
  }
}
