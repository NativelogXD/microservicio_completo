import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import { HttpExceptionFilter } from './exceptions/HttpExceptionFilter';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Configurar CORS para permitir comunicación entre microservicios
  app.enableCors({
    origin: true,
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
    credentials: true,
  });

  // Configurar prefijo global para las rutas API
  app.setGlobalPrefix('api');

  // Validación global de DTOs (class-validator)
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true, // elimina propiedades no declaradas en DTO
      forbidNonWhitelisted: true, // lanza error si vienen propiedades extra
      transform: true, // transforma tipos (por ejemplo strings a number)
    }),
  );

  // Filtro global para estandarizar errores HTTP (incluye 400 de validación)
  app.useGlobalFilters(new HttpExceptionFilter());

  // Obtener puerto desde variables de entorno o usar 3000 por defecto
  const port = process.env.PORT || 3000;
  
  await app.listen(port);
  console.log(`🚀 Microservice Pago running on port ${port}`);
  console.log(`📡 API available at: http://localhost:${port}/api`);
}

bootstrap().catch((error) => {
  console.error('❌ Error starting application:', error);
  process.exit(1);
});