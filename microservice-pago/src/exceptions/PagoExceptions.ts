// --- 404: NO SE ENCONTRÓ EL RECURSO ---
export class PagoNotFoundException extends Error {
  public readonly statusCode: number = 404;
  public readonly error: string = 'PAGO_NOT_FOUND';

  constructor(id: number) {
    super(`Pago con id ${id} no encontrado`);
    this.name = 'PagoNotFoundException';
  }
}

export class PagoByReservaNotFoundException extends Error {
  public readonly statusCode: number = 404;
  public readonly error: string = 'PAGO_BY_RESERVA_NOT_FOUND';

  constructor(reserva: string) {
    super(`Pago con reserva ${reserva} no encontrado`);
    this.name = 'PagoByReservaNotFoundException';
  }
}

// --- 409: CONFLICTO - RECURSO YA EXISTE ---
export class PagoAlreadyExistsException extends Error {
  public readonly statusCode: number = 409;
  public readonly error: string = 'PAGO_ALREADY_EXISTS';

  constructor(id: number) {
    super(`Pago con id ${id} ya existe`);
    this.name = 'PagoAlreadyExistsException';
  }
}

// --- 400: BAD REQUEST - DATOS INVÁLIDOS ---
export class PagoInvalidDataException extends Error {
  public readonly statusCode: number = 400;
  public readonly error: string = 'PAGO_INVALID_DATA';

  constructor(message: string) {
    super(message);
    this.name = 'PagoInvalidDataException';
  }
}

// --- 422: UNPROCESSABLE ENTITY - VALIDACIÓN FALLIDA ---
export class PagoValidationException extends Error {
  public readonly statusCode: number = 422;
  public readonly error: string = 'PAGO_VALIDATION_FAILED';

  constructor(message: string) {
    super(message);
    this.name = 'PagoValidationException';
  }
}
