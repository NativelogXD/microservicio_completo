import { TypeOrmModuleOptions } from '@nestjs/typeorm';
import { Pago } from '../persistence/entity/Pago';
import dotenv from 'dotenv';

// Carga variables de entorno desde .env (si existe)
dotenv.config();

export function getDatabaseConfig(): TypeOrmModuleOptions {
  const host = process.env.POSTGRES_HOST;
  const port = parseInt(process.env.POSTGRES_PORT || '5432', 10);
  const username = process.env.POSTGRES_USER;
  const password = process.env.POSTGRES_PASSWORD;
  const database = process.env.POSTGRES_DB;

  return {
    type: 'postgres',
    host,
    port,
    username,
    password,
    database,
    entities: [Pago],
    synchronize: true, // Sólo para desarrollo; en producción usar migraciones
    // logging: ['error', 'warn'],
  };
}
