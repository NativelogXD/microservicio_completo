import {
  ArgumentsHost,
  Catch,
  ExceptionFilter,
  HttpException,
} from '@nestjs/common';
import { Response } from 'express';

@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const status = exception.getStatus();
    const res: any = exception.getResponse();

    // Normalizar detalles del error (Nest puede retornar string o objeto)
    const details = Array.isArray(res?.message)
      ? res.message
      : res?.message
      ? [res.message]
      : [];

    const code = status === 400 ? 'VALIDATION_ERROR' : 'HTTP_ERROR';

    response.status(status).json({
      status,
      code,
      message:
        status === 400
          ? 'Error de validación en la solicitud'
          : res?.error || exception.message || 'Error HTTP',
      details,
      timestamp: new Date().toISOString(),
    });
  }
}