import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Pago } from './persistence/entity/Pago';
import PagoRepositoryImpl from './persistence/repositoryImpl/pagoRepositoryImpl';
import { PagoController } from './web/controller/pagoController';
import { PagoServiceImpl } from './persistence/serviceImpl/pagoServiceImpl';
import { getDatabaseConfig } from './database/database.config';
import { HttpModule } from '@nestjs/axios';
import { ConfigModule } from '@nestjs/config';

import ReservaClientService from './domain/client/ReservaClientService';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    HttpModule.register({
      timeout: parseInt(process.env.HTTP_TIMEOUT || '5000', 10),
      maxRedirects: 5,
    }),
    TypeOrmModule.forRoot(getDatabaseConfig()),
    TypeOrmModule.forFeature([Pago]),
  ],
  controllers: [PagoController],
  providers: [
    // Registrar clases concretas
    PagoRepositoryImpl,
    PagoServiceImpl,
    ReservaClientService,
    // Alias sólo para el servicio usado en el controlador
    { provide: 'PagoService', useExisting: PagoServiceImpl },
  ],
})
export class AppModule {}
